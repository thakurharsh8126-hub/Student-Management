

import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score

FEATURE_NAMES = ["attendance", "study_hours", "previous_score", "internal_marks"]
MIN_SAMPLES_TO_TRAIN = 6  # need a handful of rows before ML is meaningful


class StudentPerformanceModel:
    def __init__(self):
        self.regressor = None
        self.classifier = None
        self.is_trained = False
        self.metrics = {}

    def _rows_to_xy(self, rows):
        """
        rows: list of sqlite Row/tuples matching the `students` table schema:
        (id, roll_no, name, gender, age, attendance, study_hours,
         previous_score, internal_marks, final_marks, result)
        """
        X, y_reg, y_clf = [], [], []
        for r in rows:
            attendance, study_hours, previous_score, internal_marks, final_marks, result = (
                r[5], r[6], r[7], r[8], r[9], r[10]
            )
            if None in (attendance, study_hours, previous_score, internal_marks, final_marks):
                continue
            X.append([attendance, study_hours, previous_score, internal_marks])
            y_reg.append(final_marks)
            y_clf.append(1 if result == "Pass" else 0)
        return np.array(X, dtype=float), np.array(y_reg, dtype=float), np.array(y_clf, dtype=int)

    def train(self, rows):
        """Train regressor + classifier from current DB rows. Returns (success, message)."""
        X, y_reg, y_clf = self._rows_to_xy(rows)

        if len(X) < MIN_SAMPLES_TO_TRAIN:
            self.is_trained = False
            return False, (
                f"Need at least {MIN_SAMPLES_TO_TRAIN} complete student records to train "
                f"the model (currently have {len(X)})."
            )

        # Guard against a single-class classification problem (all Pass or all Fail)
        can_classify = len(set(y_clf.tolist())) > 1

        test_size = 0.25 if len(X) >= 12 else max(1, int(len(X) * 0.2)) / len(X)
        X_train, X_test, yr_train, yr_test, yc_train, yc_test = train_test_split(
            X, y_reg, y_clf, test_size=test_size, random_state=42
        )

        self.regressor = RandomForestRegressor(n_estimators=200, random_state=42)
        self.regressor.fit(X_train, yr_train)
        pred_reg = self.regressor.predict(X_test)
        mae = mean_absolute_error(yr_test, pred_reg) if len(X_test) > 0 else float("nan")

        acc = None
        if can_classify:
            self.classifier = RandomForestClassifier(n_estimators=200, random_state=42)
            self.classifier.fit(X_train, yc_train)
            pred_clf = self.classifier.predict(X_test)
            acc = accuracy_score(yc_test, pred_clf) if len(X_test) > 0 else float("nan")
        else:
            self.classifier = None

        self.is_trained = True
        self.metrics = {
            "n_samples": len(X),
            "n_test": len(X_test),
            "mae": mae,
            "accuracy": acc,
            "feature_importance": dict(zip(FEATURE_NAMES, self.regressor.feature_importances_)),
        }
        return True, "Model trained successfully."

    def predict(self, attendance, study_hours, previous_score, internal_marks):
        """Predict (predicted_final_marks, predicted_result, confidence_or_None)."""
        if not self.is_trained or self.regressor is None:
            raise RuntimeError("Model has not been trained yet.")

        features = np.array([[attendance, study_hours, previous_score, internal_marks]], dtype=float)
        predicted_marks = float(self.regressor.predict(features)[0])
        predicted_marks = max(0.0, min(100.0, predicted_marks))

        if self.classifier is not None:
            pred_class = int(self.classifier.predict(features)[0])
            proba = self.classifier.predict_proba(features)[0]
            confidence = float(max(proba))
            predicted_result = "Pass" if pred_class == 1 else "Fail"
        else:
            predicted_result = "Pass" if predicted_marks >= 40 else "Fail"
            confidence = None

        return predicted_marks, predicted_result, confidence

    def get_metrics_text(self):
        if not self.is_trained:
            return "Model not trained yet."
        m = self.metrics
        lines = [
            f"Training samples used: {m['n_samples']} (test split: {m['n_test']})",
            f"Final-marks prediction MAE: {m['mae']:.2f} marks" if m['mae'] == m['mae'] else "MAE: n/a",
        ]
        if m["accuracy"] is not None and m["accuracy"] == m["accuracy"]:
            lines.append(f"Pass/Fail classification accuracy: {m['accuracy']*100:.1f}%")
        else:
            lines.append("Pass/Fail classification accuracy: n/a (not enough class variety)")
        lines.append("Feature importance (higher = more influence on predicted marks):")
        for feat, imp in sorted(m["feature_importance"].items(), key=lambda x: -x[1]):
            lines.append(f"   - {feat}: {imp*100:.1f}%")
        return "\n".join(lines)
