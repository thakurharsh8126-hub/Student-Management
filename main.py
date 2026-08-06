"""
main.py
Student Management System with a Tkinter GUI and a scikit-learn
powered performance predictor.

Run with:  python main.py
"""

import tkinter as tk
from tkinter import ttk, messagebox

from database import Database
from ml_model import StudentPerformanceModel

APP_TITLE = "Student Management System (with ML Performance Predictor)"

COLUMNS = (
    "id", "roll_no", "name", "gender", "age", "attendance",
    "study_hours", "previous_score", "internal_marks", "final_marks", "result"
)
COLUMN_LABELS = (
    "ID", "Roll No", "Name", "Gender", "Age", "Attendance %",
    "Study Hrs/day", "Prev Score", "Internal Marks", "Final Marks", "Result"
)


class StudentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1150x650")
        self.minsize(1000, 600)

        self.db = Database()
        self.model = StudentPerformanceModel()
        self.selected_id = None

        self._build_style()
        self._build_layout()
        self.refresh_table()

    # ---------------------------------------------------------------- UI
    def _build_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=5)
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))

    def _build_layout(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.manage_tab = ttk.Frame(notebook)
        self.predict_tab = ttk.Frame(notebook)
        notebook.add(self.manage_tab, text="  Manage Students  ")
        notebook.add(self.predict_tab, text="  ML Performance Predictor  ")

        self._build_manage_tab(self.manage_tab)
        self._build_predict_tab(self.predict_tab)

    # ------------------------------------------------------- Manage Tab
    def _build_manage_tab(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)

        ttk.Label(parent, text="Student Records", style="Header.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )

        # --- form ---
        form = ttk.LabelFrame(parent, text="Add / Update Student")
        form.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        for i in range(8):
            form.columnconfigure(i, weight=1)

        self.entries = {}
        fields = [
            ("roll_no", "Roll No"), ("name", "Name"), ("gender", "Gender (M/F/O)"),
            ("age", "Age"), ("attendance", "Attendance %"), ("study_hours", "Study Hrs/day"),
            ("previous_score", "Previous Score"), ("internal_marks", "Internal Marks"),
            ("final_marks", "Final Marks"),
        ]
        for idx, (key, label) in enumerate(fields):
            row, col = divmod(idx, 5)
            ttk.Label(form, text=label).grid(row=row * 2, column=col, sticky="w", padx=5, pady=(6, 0))
            ent = ttk.Entry(form, width=16)
            ent.grid(row=row * 2 + 1, column=col, sticky="ew", padx=5, pady=(0, 6))
            self.entries[key] = ent

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=4, column=0, columnspan=5, sticky="w", padx=5, pady=8)
        ttk.Button(btn_frame, text="Add Student", command=self.add_student).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Update Selected", command=self.update_student).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_student).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_form).pack(side="left", padx=4)

        # --- search ---
        search_frame = ttk.Frame(parent)
        search_frame.grid(row=1, column=0, sticky="ne", padx=5)
        # placed inside a corner via separate row below instead for clarity
        search_bar = ttk.Frame(parent)
        search_bar.grid(row=1, column=0, sticky="e")

        # --- table ---
        table_frame = ttk.Frame(parent)
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(1, weight=1)

        top_bar = ttk.Frame(table_frame)
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        ttk.Label(top_bar, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top_bar, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self.refresh_table())
        ttk.Button(top_bar, text="Refresh", command=self.refresh_table).pack(side="left", padx=5)
        self.count_label = ttk.Label(top_bar, text="")
        self.count_label.pack(side="right")

        self.tree = ttk.Treeview(table_frame, columns=COLUMNS, show="headings", selectmode="browse")
        for col, label in zip(COLUMNS, COLUMN_LABELS):
            self.tree.heading(col, text=label)
            width = 130 if col in ("name",) else 90
            self.tree.column(col, width=width, anchor="center")
        self.tree.grid(row=1, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    # ------------------------------------------------------ Predict Tab
    def _build_predict_tab(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)

        ttk.Label(parent, text="Predict Student Performance", style="Header.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5)
        )
        ttk.Label(
            parent,
            text=("Trains a Random Forest model on your current student records, then predicts\n"
                  "the likely final marks and Pass/Fail outcome for a given profile."),
            wraplength=1000, justify="left"
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 10))

        # left: train + metrics
        left = ttk.LabelFrame(parent, text="1. Train Model")
        left.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        parent.rowconfigure(2, weight=1)

        ttk.Button(left, text="Train / Retrain Model on Current Data", command=self.train_model).pack(
            anchor="w", padx=10, pady=10
        )
        self.metrics_text = tk.Text(left, height=16, width=48, wrap="word", state="disabled",
                                     font=("Consolas", 10))
        self.metrics_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # right: predict form
        right = ttk.LabelFrame(parent, text="2. Predict for a Student Profile")
        right.grid(row=2, column=1, sticky="nsew", padx=10, pady=5)
        for i in range(2):
            right.columnconfigure(i, weight=1)

        self.pred_entries = {}
        pred_fields = [
            ("attendance", "Attendance % (0-100)"),
            ("study_hours", "Study Hours/day (0-12)"),
            ("previous_score", "Previous Score (0-100)"),
            ("internal_marks", "Internal Marks (0-100)"),
        ]
        for idx, (key, label) in enumerate(pred_fields):
            ttk.Label(right, text=label).grid(row=idx, column=0, sticky="w", padx=10, pady=6)
            ent = ttk.Entry(right, width=14)
            ent.grid(row=idx, column=1, sticky="e", padx=10, pady=6)
            self.pred_entries[key] = ent

        ttk.Button(right, text="Predict Outcome", command=self.predict_outcome).grid(
            row=len(pred_fields), column=0, columnspan=2, pady=12
        )

        self.pred_result_label = ttk.Label(
            right, text="No prediction yet.", font=("Segoe UI", 12, "bold"), justify="left"
        )
        self.pred_result_label.grid(row=len(pred_fields) + 1, column=0, columnspan=2, sticky="w", padx=10, pady=10)

        self.load_data_hint = ttk.Label(
            right,
            text="Tip: use 'Load Selected Student' from the Manage tab selection to prefill values.",
            wraplength=380, foreground="#555"
        )
        self.load_data_hint.grid(row=len(pred_fields) + 2, column=0, columnspan=2, sticky="w", padx=10)

        ttk.Button(right, text="Load Selected Student's Values", command=self.load_selected_into_predict).grid(
            row=len(pred_fields) + 3, column=0, columnspan=2, pady=10
        )

    # ------------------------------------------------------------ Logic
    def _get_form_values(self):
        try:
            roll_no = self.entries["roll_no"].get().strip()
            name = self.entries["name"].get().strip()
            gender = self.entries["gender"].get().strip()
            age = int(self.entries["age"].get().strip())
            attendance = float(self.entries["attendance"].get().strip())
            study_hours = float(self.entries["study_hours"].get().strip())
            previous_score = float(self.entries["previous_score"].get().strip())
            internal_marks = float(self.entries["internal_marks"].get().strip())
            final_marks = float(self.entries["final_marks"].get().strip())
        except ValueError:
            raise ValueError("Please fill Age, Attendance, Study Hours, Previous Score, "
                              "Internal Marks and Final Marks with valid numbers.")
        if not roll_no or not name:
            raise ValueError("Roll No and Name are required.")
        return (roll_no, name, gender, age, attendance, study_hours,
                previous_score, internal_marks, final_marks)

    def add_student(self):
        try:
            values = self._get_form_values()
            self.db.add_student(*values)
            messagebox.showinfo("Success", "Student added successfully.")
            self.clear_form()
            self.refresh_table()
        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))
        except Exception as e:
            if "UNIQUE" in str(e):
                messagebox.showerror("Duplicate", "A student with this Roll No already exists.")
            else:
                messagebox.showerror("Error", str(e))

    def update_student(self):
        if self.selected_id is None:
            messagebox.showwarning("No selection", "Select a student in the table first.")
            return
        try:
            values = self._get_form_values()
            self.db.update_student(self.selected_id, *values)
            messagebox.showinfo("Success", "Student updated successfully.")
            self.clear_form()
            self.refresh_table()
        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_student(self):
        if self.selected_id is None:
            messagebox.showwarning("No selection", "Select a student in the table first.")
            return
        if messagebox.askyesno("Confirm delete", "Delete the selected student record?"):
            self.db.delete_student(self.selected_id)
            self.clear_form()
            self.refresh_table()

    def clear_form(self):
        for ent in self.entries.values():
            ent.delete(0, tk.END)
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())

    def on_row_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        self.selected_id = int(values[0])
        keys = ["roll_no", "name", "gender", "age", "attendance",
                "study_hours", "previous_score", "internal_marks", "final_marks"]
        for key, val in zip(keys, values[1:10]):
            self.entries[key].delete(0, tk.END)
            self.entries[key].insert(0, val)

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        keyword = self.search_var.get().strip() if hasattr(self, "search_var") else ""
        rows = self.db.search_students(keyword) if keyword else self.db.get_all_students()
        for r in rows:
            self.tree.insert("", "end", values=r)
        total = self.db.count_students()
        self.count_label.config(text=f"Total students: {total}")

    # ------------------------------------------------------------ ML
    def train_model(self):
        rows = self.db.get_all_students()
        success, message = self.model.train(rows)
        self.metrics_text.configure(state="normal")
        self.metrics_text.delete("1.0", tk.END)
        if success:
            self.metrics_text.insert(tk.END, self.model.get_metrics_text())
        else:
            self.metrics_text.insert(tk.END, message)
        self.metrics_text.configure(state="disabled")
        if success:
            messagebox.showinfo("Training complete", "Model trained successfully.")
        else:
            messagebox.showwarning("Not enough data", message)

    def predict_outcome(self):
        if not self.model.is_trained:
            messagebox.showwarning("Model not trained", "Please train the model first (button on the left).")
            return
        try:
            attendance = float(self.pred_entries["attendance"].get().strip())
            study_hours = float(self.pred_entries["study_hours"].get().strip())
            previous_score = float(self.pred_entries["previous_score"].get().strip())
            internal_marks = float(self.pred_entries["internal_marks"].get().strip())
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter valid numbers in all prediction fields.")
            return

        marks, result, confidence = self.model.predict(attendance, study_hours, previous_score, internal_marks)
        conf_text = f"  (confidence: {confidence*100:.0f}%)" if confidence is not None else ""
        color = "#1a7f37" if result == "Pass" else "#c0392b"
        self.pred_result_label.config(
            text=f"Predicted Final Marks: {marks:.1f}\nPredicted Result: {result}{conf_text}",
            foreground=color,
        )

    def load_selected_into_predict(self):
        if self.selected_id is None:
            messagebox.showwarning("No selection", "Select a student in the Manage tab table first.")
            return
        row = self.db.get_student(self.selected_id)
        if not row:
            return
        mapping = {
            "attendance": row[5],
            "study_hours": row[6],
            "previous_score": row[7],
            "internal_marks": row[8],
        }
        for key, val in mapping.items():
            self.pred_entries[key].delete(0, tk.END)
            self.pred_entries[key].insert(0, val)

    def on_close(self):
        self.db.close()
        self.destroy()


def main():
    app = StudentApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()


if __name__ == "__main__":
    main()
