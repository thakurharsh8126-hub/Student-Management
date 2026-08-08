import streamlit as st
import pandas as pd

from database import Database
from ml_model import StudentPerformanceModel

st.set_page_config(
    page_title="Student Management + ML Predictor",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 Student Management System")
st.caption("A Streamlit version of the student dashboard with ML-based performance prediction")


@st.cache_resource
def get_db():
    return Database()


@st.cache_resource
def get_model():
    return StudentPerformanceModel()


db = get_db()
model = get_model()


def get_student_rows():
    rows = db.get_all_students()
    if not rows:
        return pd.DataFrame(columns=[
            "id", "roll_no", "name", "gender", "age", "attendance",
            "study_hours", "previous_score", "internal_marks", "final_marks", "result"
        ])

    return pd.DataFrame(
        rows,
        columns=[
            "id", "roll_no", "name", "gender", "age", "attendance",
            "study_hours", "previous_score", "internal_marks", "final_marks", "result"
        ],
    )


def get_form_defaults(student_id):
    if student_id is None:
        return {
            "roll_no": "",
            "name": "",
            "gender": "",
            "age": 18,
            "attendance": 75.0,
            "study_hours": 3.0,
            "previous_score": 70.0,
            "internal_marks": 65.0,
            "final_marks": 70.0,
        }

    student = db.get_student(student_id)
    if not student:
        return get_form_defaults(None)

    return {
        "roll_no": student[1],
        "name": student[2],
        "gender": student[3] or "",
        "age": student[4] or 18,
        "attendance": student[5] or 75.0,
        "study_hours": student[6] or 3.0,
        "previous_score": student[7] or 70.0,
        "internal_marks": student[8] or 65.0,
        "final_marks": student[9] or 70.0,
    }


student_df = get_student_rows()
student_options = [("New Student", None)] + [
    (f"{row['name']} ({row['roll_no']})", row["id"]) for _, row in student_df.iterrows()
]

selected_student_id = st.sidebar.selectbox(
    "Select a student to edit/delete",
    options=[option[1] for option in student_options],
    format_func=lambda value: next(label for label, item in student_options if item == value),
)

st.sidebar.markdown("---")
st.sidebar.caption("Use this panel to manage records and train the prediction model")

with st.expander("Add / Update Student", expanded=True):
    defaults = get_form_defaults(selected_student_id)

    with st.form("student_form"):
        col1, col2 = st.columns(2)

        with col1:
            roll_no = st.text_input("Roll No", value=defaults["roll_no"])
            name = st.text_input("Name", value=defaults["name"])
            gender = st.text_input("Gender (M/F/O)", value=defaults["gender"])
            age = st.number_input("Age", min_value=1, max_value=100, value=int(defaults["age"]))

        with col2:
            attendance = st.number_input("Attendance %", min_value=0.0, max_value=100.0, value=float(defaults["attendance"]))
            study_hours = st.number_input("Study Hours/day", min_value=0.0, max_value=12.0, value=float(defaults["study_hours"]))
            previous_score = st.number_input("Previous Score", min_value=0.0, max_value=100.0, value=float(defaults["previous_score"]))
            internal_marks = st.number_input("Internal Marks", min_value=0.0, max_value=100.0, value=float(defaults["internal_marks"]))
            final_marks = st.number_input("Final Marks", min_value=0.0, max_value=100.0, value=float(defaults["final_marks"]))

        submitted = st.form_submit_button("Save Student")

        if submitted:
            if not roll_no or not name:
                st.error("Roll No and Name are required.")
            else:
                if selected_student_id is None:
                    db.add_student(roll_no, name, gender, age, attendance, study_hours, previous_score, internal_marks, final_marks)
                    st.success("Student added successfully.")
                else:
                    db.update_student(selected_student_id, roll_no, name, gender, age, attendance, study_hours, previous_score, internal_marks, final_marks)
                    st.success("Student updated successfully.")

                st.session_state.pop("selected_student_id", None)
                st.rerun()

    if selected_student_id is not None:
        if st.button("Delete Selected Student"):
            db.delete_student(selected_student_id)
            st.success("Student deleted.")
            st.rerun()

st.subheader("Student Records")
if student_df.empty:
    st.info("No students added yet. Use the form above to add the first record.")
else:
    st.dataframe(student_df, use_container_width=True, hide_index=True)

st.divider()

st.subheader("🧠 ML Performance Predictor")

if st.button("Train / Retrain Model"):
    success, message = model.train(db.get_all_students())
    if success:
        st.success(message)
    else:
        st.warning(message)

if not model.is_trained:
    st.info("Train the model first to enable predictions.")
    st.stop()

col1, col2 = st.columns(2)
with col1:
    st.markdown("### Model Metrics")
    st.code(model.get_metrics_text(), language="text")

with col2:
    st.markdown("### Make a Prediction")
    attendance_input = st.number_input("Attendance %", min_value=0.0, max_value=100.0, value=75.0, key="pred_attendance")
    study_hours_input = st.number_input("Study Hours/day", min_value=0.0, max_value=12.0, value=3.0, key="pred_study")
    previous_score_input = st.number_input("Previous Score", min_value=0.0, max_value=100.0, value=70.0, key="pred_prev")
    internal_marks_input = st.number_input("Internal Marks", min_value=0.0, max_value=100.0, value=65.0, key="pred_internal")

    if st.button("Predict Outcome"):
        predicted_marks, predicted_result, confidence = model.predict(
            attendance_input,
            study_hours_input,
            previous_score_input,
            internal_marks_input,
        )

        st.metric("Predicted Final Marks", f"{predicted_marks:.1f}")
        st.metric("Predicted Result", predicted_result)
        if confidence is not None:
            st.metric("Classification Confidence", f"{confidence * 100:.1f}%")
