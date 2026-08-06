# Student Management System (GUI + Machine Learning)

A simple desktop app to manage student records, built with:
- **Tkinter** — GUI (built into Python, no extra install needed)
- **SQLite** — local database (`students.db`, created automatically)
- **scikit-learn** — Random Forest models that predict a student's likely
  final marks and Pass/Fail outcome from attendance, study hours,
  previous score, and internal marks

## 1. Setup

Requires Python 3.8+.

```bash
# (recommended) create a virtual environment
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

# install dependencies
pip install -r requirements.txt
```

## 2. (Optional) Load sample data

To try the ML predictor right away without typing in records by hand:

```bash
python seed_sample_data.py
```

This adds 20 randomly generated but realistic-looking student records.

## 3. Run the app

```bash
python main.py
```

## 4. Using the app

### Manage Students tab
- Fill in the form (Roll No, Name, Gender, Age, Attendance %, Study Hours/day,
  Previous Score, Internal Marks, Final Marks) and click **Add Student**.
- Click any row in the table to load it into the form, then **Update Selected**
  or **Delete Selected**.
- Use the search box to filter by name or roll number.

### ML Performance Predictor tab
1. Click **Train / Retrain Model on Current Data** — this trains a
   RandomForestRegressor (predicts final marks) and RandomForestClassifier
   (predicts Pass/Fail) on whatever students are currently in the database,
   and shows accuracy metrics plus which features matter most.
   - You need at least 6 complete student records to train.
2. Enter a hypothetical (or real) student's Attendance, Study Hours,
   Previous Score, and Internal Marks, then click **Predict Outcome** to see
   the predicted final marks and Pass/Fail result.
3. You can also select a student row in the Manage tab and click
   **Load Selected Student's Values** to pre-fill the predictor with their data.

## Project structure

```
student_management_system/
├── main.py               # Tkinter GUI application (entry point)
├── database.py            # SQLite database layer (CRUD)
├── ml_model.py             # scikit-learn training + prediction logic
├── seed_sample_data.py    # optional script to generate sample records
├── requirements.txt
└── README.md
```

## Notes & possible extensions
- The database file `students.db` is created automatically in the project
  folder the first time you run the app.
- "Result" (Pass/Fail) is auto-derived from Final Marks (>= 40 = Pass) when
  you add/update a record — this is what the classifier learns to predict.
- Ideas to extend: subject-wise marks instead of a single final mark,
  attendance trend charts (matplotlib), CSV import/export, login/authentication,
  or swapping SQLite for a networked database for multi-user use.
