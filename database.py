import os
import sqlite3

DB_FILE = os.path.join(
os.path.dirname(os.path.abspath(**file**)),
"students.db"
)

class Database:


def __init__(self, db_file=DB_FILE):
    self.db_file = db_file
    self._create_tables()

def _connect(self):
    conn = sqlite3.connect(self.db_file)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def _create_tables(self):
    conn = self._connect()

    try:
        cursor = conn.cursor()

        cursor.execute("""
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

        conn.commit()

    finally:
        conn.close()

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
    conn = self._connect()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO students (
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

        conn.commit()
        return cursor.lastrowid

    finally:
        conn.close()

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
    conn = self._connect()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE students
            SET
                roll_no = ?,
                name = ?,
                gender = ?,
                age = ?,
                attendance = ?,
                study_hours = ?,
                previous_score = ?,
                internal_marks = ?,
                final_marks = ?,
                result = ?
            WHERE id = ?
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

        conn.commit()

    finally:
        conn.close()

def delete_student(self, student_id):
    conn = self._connect()

    try:
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM students WHERE id = ?",
            (student_id,)
        )

        conn.commit()

    finally:
        conn.close()

def get_all_students(self):
    conn = self._connect()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
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
            FROM students
            ORDER BY id
        """)

        return cursor.fetchall()

    finally:
        conn.close()

def get_student(self, student_id):
    conn = self._connect()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
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
            FROM students
            WHERE id = ?
        """, (student_id,))

        return cursor.fetchone()

    finally:
        conn.close()

def search_students(self, keyword):
    conn = self._connect()

    try:
        cursor = conn.cursor()

        keyword = str(keyword).strip()
        like = f"%{keyword}%"

        cursor.execute("""
            SELECT
                id,
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
            FROM students
            WHERE name LIKE ?
               OR roll_no LIKE ?
            ORDER BY id
        """, (like, like))

        return cursor.fetchall()

    finally:
        conn.close()

def count_students(self):
    conn = self._connect()

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students")
        return cursor.fetchone()[0]

    finally:
        conn.close()

@staticmethod
def _derive_result(final_marks):
    try:
        return "Pass" if float(final_marks) >= 40 else "Fail"
    except (TypeError, ValueError):
        return "N/A"

def close(self):
    pass

