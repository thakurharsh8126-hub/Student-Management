"""
seed_sample_data.py
Optional helper: populates students.db with sample records so you can
immediately try out the ML Performance Predictor tab without typing
in data by hand.

Run with:  python seed_sample_data.py
"""

import random
from database import Database

SAMPLE_NAMES = [
    "Aarav Sharma", "Priya Nair", "Rohan Gupta", "Sneha Iyer", "Kabir Khan",
    "Ananya Rao", "Vivaan Mehta", "Diya Patel", "Arjun Singh", "Ishita Joshi",
    "Karan Verma", "Meera Pillai", "Yash Kapoor", "Tara Bhatt", "Dev Malhotra",
    "Riya Chawla", "Sameer Ali", "Neha Kulkarni", "Aditya Roy", "Pooja Desai",
]


def make_row(i, name):
    attendance = round(random.uniform(50, 100), 1)
    study_hours = round(random.uniform(0.5, 8), 1)
    previous_score = round(random.uniform(30, 95), 1)
    internal_marks = round(random.uniform(30, 95), 1)

    # Final marks loosely driven by the other features + noise, so the
    # ML model has a real (but not perfectly linear) pattern to learn.
    base = (
        0.35 * attendance +
        4.0 * study_hours +
        0.25 * previous_score +
        0.25 * internal_marks
    ) / 1.35
    noise = random.uniform(-8, 8)
    final_marks = max(0, min(100, round(base + noise, 1)))

    return {
        "roll_no": f"R{1000 + i}",
        "name": name,
        "gender": random.choice(["M", "F"]),
        "age": random.randint(16, 22),
        "attendance": attendance,
        "study_hours": study_hours,
        "previous_score": previous_score,
        "internal_marks": internal_marks,
        "final_marks": final_marks,
    }


def main():
    db = Database()
    existing = db.count_students()
    if existing > 0:
        print(f"Database already has {existing} student(s). "
              f"Seeding will add more sample rows on top of them.")

    added = 0
    for i, name in enumerate(SAMPLE_NAMES):
        row = make_row(i, name)
        try:
            db.add_student(
                row["roll_no"], row["name"], row["gender"], row["age"],
                row["attendance"], row["study_hours"], row["previous_score"],
                row["internal_marks"], row["final_marks"]
            )
            added += 1
        except Exception:
            pass  # skip if roll number already exists (e.g. re-running the script)

    print(f"Seeded {added} sample student record(s) into {db.db_file}")
    db.close()


if __name__ == "__main__":
    main()
