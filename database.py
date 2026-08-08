```python
import sqlite3
import os

DB_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "students.db"
)


class Database:
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file

        # FIX: Allows SQLite connection to work with Streamlit threads
        self.conn = sqlite3.connect(
            self.db_file,
            check_same_thread=False
        )

        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()

    def _create_tables(self):
        cur = self.conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_no TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                gender TEXT,
                age INTEGER,
                attendance REAL,
                study_hours REAL,
                previous_score REAL,
                internal_marks REAL,
                final_marks REAL,
                result TEXT
            )
        """)

        self.conn.commit()

    def add_student(
        self,
        roll_no,
        name,
        gender,
        age,
        attendance,
        study_hours,
        previous_score,
        internal_marks,
        final_marks
    ):
        result = self._derive_result(final_marks)

        cur = self.conn.cursor()

        cur.execute("""
            INSERT INTO students
            (
                roll_no,
                name,
                gender,
                age,
                attendance,
                study_hours,
                previous_score,
                internal_marks,
                final_marks,
                result
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            roll_no,
            name,
            gender,
            age,
            attendance,
            study_hours,
            previous_score,
            internal_marks,
            final_marks,
            result
        ))

        self.conn.commit()
        return cur.lastrowid

    def update_student(
        self,
        student_id,
        roll_no,
        name,
        gender,
        age,
        attendance,
        study_hours,
        previous_score,
        internal_marks,
        final_marks
    ):
        result = self._derive_result(final_marks)

        cur = self.conn.cursor()

        cur.execute("""
            UPDATE students SET
                roll_no=?,
                name=?,
                gender=?,
                age=?,
                attendance=?,
                study_hours=?,
                previous_score=?,
                internal_marks=?,
                final_marks=?,
                result=?
            WHERE id=?
        """, (
            roll_no,
            name,
            gender,
            age,
            attendance,
            study_hours,
            previous_score,
            internal_marks,
            final_marks,
            result,
            student_id
        ))

        self.conn.commit()

    def delete_student(self, student_id):
        cur = self.conn.cursor()

        cur.execute(
            "DELETE FROM students WHERE id=?",
            (student_id,)
        )

        self.conn.commit()

    def get_all_students(self):
        cur = self.conn.cursor()

        cur.execute(
            "SELECT * FROM students ORDER BY id"
        )

        return cur.fetchall()

    def get_student(self, student_id):
        cur = self.conn.cursor()

        cur.execute(
            "SELECT * FROM students WHERE id=?",
            (student_id,)
        )

        return cur.fetchone()

    def search_students(self, keyword):
        cur = self.conn.cursor()

        like = f"%{keyword}%"

        cur.execute("""
            SELECT * FROM students
            WHERE name LIKE ? OR roll_no LIKE ?
            ORDER BY id
        """, (like, like))

        return cur.fetchall()

    def count_students(self):
        cur = self.conn.cursor()

        cur.execute(
            "SELECT COUNT(*) FROM students"
        )

        return cur.fetchone()[0]

    @staticmethod
    def _derive_result(final_marks):
        try:
            return "Pass" if float(final_marks) >= 40 else "Fail"
        except (TypeError, ValueError):
            return "N/A"

    def close(self):
        self.conn.close()
```
