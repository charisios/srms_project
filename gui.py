import csv
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from student import Student
from grade import compute_grade
from data.database import create_table, load_records, save_record, delete_record, record_exists
from report import get_summary_text


def parse_scores(scores_text):
    scores = [part.strip() for part in scores_text.split(",") if part.strip()]
    if not scores:
        raise ValueError("Please enter at least one score.")

    parsed = []
    for score in scores:
        value = float(score)
        if value < 0 or value > 100:
            raise ValueError("Each score must be between 0 and 100.")
        parsed.append(value)

    return parsed


class SRMSApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SRMS Student Results Manager")
        self.geometry("1200x700")

        create_table()
        self.students = load_records()
        self.displayed_students = list(self.students)
        self.sort_reverse = {
            "id": False,
            "name": False,
            "average": False,
            "grade": False,
            "gpa": False,
            "remark": False,
        }

        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_menu()
        self._build_header()
        self._build_body()
        self.refresh_student_table()

    def _build_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Export Records...", command=self.export_records_csv)
        file_menu.add_command(label="Export Summary...", command=self.export_summary_text)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.configure(menu=menubar)

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, corner_radius=10)
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure((0, 1), weight=1)

        title_label = ctk.CTkLabel(
            header_frame,
            text="Student Results Management System",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w",
        )
        title_label.grid(row=0, column=0, padx=20, pady=16, sticky="w")

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Add records, view grades, delete students, and review class summary.",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 16), sticky="w")

        theme_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        theme_frame.grid(row=0, column=1, rowspan=2, padx=20, pady=16, sticky="e")

        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Theme:",
            font=ctk.CTkFont(size=12),
            anchor="e",
        )
        theme_label.grid(row=0, column=0, padx=(0, 8))

        self.theme_selector = ctk.CTkSegmentedButton(
            theme_frame,
            values=["System", "Light", "Dark"],
            command=self.change_theme,
            width=220,
        )
        self.theme_selector.set("System")
        self.theme_selector.grid(row=0, column=1)

    def _build_body(self):
        paned_frame = ttk.PanedWindow(self, orient="horizontal")
        paned_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_table_section(paned_frame)
        self._build_form_section(paned_frame)
        self._build_details_section(paned_frame)

    def _build_table_section(self, parent):
        table_frame = ctk.CTkFrame(parent, corner_radius=10)
        parent.add(table_frame, weight=3)
        table_frame.grid_rowconfigure(1, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        table_label = ctk.CTkLabel(
            table_frame,
            text="Student Records",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        table_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        search_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        search_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(search_frame, text="Search:", anchor="w").grid(row=0, column=0, padx=(0, 8), pady=2, sticky="w")
        self.search_text_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_text_var, placeholder_text="Student ID or name")
        self.search_entry.grid(row=0, column=1, padx=(0, 8), pady=2, sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda event: self.filter_students())

        self.clear_search_button = ctk.CTkButton(search_frame, text="Clear", width=80, command=self.clear_search)
        self.clear_search_button.grid(row=0, column=2, padx=(0, 8), pady=2)

        self.student_table = ttk.Treeview(
            table_frame,
            columns=("id", "name", "average", "grade", "gpa", "remark"),
            show="headings",
            selectmode="browse",
            height=18,
        )
        search_frame.grid_columnconfigure(1, weight=1)
        self.student_table.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")

        style = ttk.Style()
        style.configure(
            "Custom.Treeview",
            font=("Segoe UI", 10),
            rowheight=28,
            background="#F7F9FC",
            fieldbackground="#F7F9FC",
            foreground="#333333",
        )
        style.configure("Custom.Treeview.Heading", font=("Segoe UI", 11, "bold"))
        self.student_table.configure(style="Custom.Treeview")

        self.student_table.heading(
            "id",
            text="Student ID",
            command=lambda c="id": self.sort_by_column(c),
        )
        self.student_table.heading(
            "name",
            text="Name",
            command=lambda c="name": self.sort_by_column(c),
        )
        self.student_table.heading(
            "average",
            text="Average",
            command=lambda c="average": self.sort_by_column(c),
        )
        self.student_table.heading(
            "grade",
            text="Grade",
            command=lambda c="grade": self.sort_by_column(c),
        )
        self.student_table.heading(
            "gpa",
            text="GPA",
            command=lambda c="gpa": self.sort_by_column(c),
        )
        self.student_table.heading(
            "remark",
            text="Remark",
            command=lambda c="remark": self.sort_by_column(c),
        )

        self.student_table.column("id", width=150, anchor="w")
        self.student_table.column("name", width=220, anchor="w")
        self.student_table.column("average", width=100, anchor="center")
        self.student_table.column("grade", width=80, anchor="center")
        self.student_table.column("gpa", width=80, anchor="center")
        self.student_table.column("remark", width=160, anchor="w")

        self.student_table.tag_configure("oddrow", background="#F9FAFB")
        self.student_table.tag_configure("evenrow", background="#FFFFFF")

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.student_table.yview)
        self.student_table.configure(yscroll=scroll.set)
        scroll.grid(row=2, column=1, sticky="ns", pady=(0, 20), padx=(0, 10))

        hscroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.student_table.xview)
        self.student_table.configure(xscroll=hscroll.set)
        hscroll.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))

    def _build_form_section(self, parent):
        form_frame = ctk.CTkFrame(parent, corner_radius=10)
        parent.add(form_frame, weight=1)
        form_frame.grid_rowconfigure(1, weight=1)
        form_frame.grid_columnconfigure(0, weight=1)

        form_title = ctk.CTkLabel(
            form_frame,
            text="Add New Student",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        form_title.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        scrollable_form = ctk.CTkScrollableFrame(form_frame, fg_color="transparent")
        scrollable_form.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
        scrollable_form.grid_columnconfigure(0, weight=1)

        self.entry_student_id = ctk.CTkEntry(scrollable_form, placeholder_text="Student ID")
        self.entry_student_id.grid(row=0, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.entry_name = ctk.CTkEntry(scrollable_form, placeholder_text="Student Name")
        self.entry_name.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        scores_label = ctk.CTkLabel(
            scrollable_form,
            text="Scores (comma-separated)",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        scores_label.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")

        self.entry_scores = ctk.CTkEntry(scrollable_form, placeholder_text="e.g. 78, 92, 65")
        self.entry_scores.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.form_message = ctk.CTkLabel(
            scrollable_form,
            text="",
            text_color="#EF4444",
            anchor="w",
            wraplength=200,
        )
        self.form_message.grid(row=4, column=0, padx=20, pady=(0, 12), sticky="w")

        self.add_button = ctk.CTkButton(
            scrollable_form,
            text="Add Student",
            command=self.add_student,
            fg_color="#3B82F6",
            hover_color="#2563EB",
        )
        self.add_button.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.delete_button = ctk.CTkButton(
            scrollable_form,
            text="Delete Selected",
            command=self.delete_selected_student,
            fg_color="#EF4444",
            hover_color="#DC2626",
        )
        self.delete_button.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.summary_button = ctk.CTkButton(
            scrollable_form,
            text="Show Class Summary",
            command=self.show_summary,
            fg_color="#10B981",
            hover_color="#059669",
        )
        self.summary_button.grid(row=7, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.clear_button = ctk.CTkButton(
            scrollable_form,
            text="Clear Form",
            command=self.clear_form,
            fg_color="#64748B",
            hover_color="#475569",
        )
        self.clear_button.grid(row=8, column=0, padx=20, pady=(0, 10), sticky="ew")

    def _build_details_section(self, parent):
        details_frame = ctk.CTkFrame(parent, corner_radius=10)
        parent.add(details_frame, weight=1)
        details_frame.grid_rowconfigure(1, weight=1)
        details_frame.grid_columnconfigure(0, weight=1)

        details_label = ctk.CTkLabel(
            details_frame,
            text="Record Details",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        details_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        self.details_box = ctk.CTkTextbox(details_frame, width=300, height=500)
        self.details_box.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
        self.details_box.configure(state="disabled")

        self.student_table.bind("<<TreeviewSelect>>", self.on_row_select)

    def refresh_student_table(self):
        for item in self.student_table.get_children():
            self.student_table.delete(item)

        for index, student in enumerate(self.displayed_students):
            average = student.get_average()
            grade, gpa, remark = compute_grade(average)
            self.student_table.insert(
                "",
                "end",
                values=(
                    student.student_id,
                    student.name,
                    f"{average:.2f}%",
                    grade,
                    f"{gpa:.1f}",
                    remark,
                ),
                tags=("evenrow",) if index % 2 == 0 else ("oddrow",),
            )

    def filter_students(self):
        query = self.search_text_var.get().strip().lower()
        if query == "":
            self.displayed_students = list(self.students)
        else:
            self.displayed_students = [
                s for s in self.students
                if query in s.student_id.lower() or query in s.name.lower()
            ]
        self.refresh_student_table()

    def clear_search(self):
        self.search_text_var.set("")
        self.filter_students()

    def on_row_select(self, event):
        selected = self.student_table.selection()
        if not selected:
            self.update_detail_text(None)
            return

        item = selected[0]
        values = self.student_table.item(item, "values")
        selected_id = values[0]
        student = next((s for s in self.students if s.student_id == selected_id), None)
        self.update_detail_text(student)

    def update_detail_text(self, student):
        if student is None:
            detail = "Select a row to show details."
        else:
            avg = student.get_average()
            grade, gpa, remark = compute_grade(avg)
            detail = (
                f"Student ID: {student.student_id}\n"
                f"Name: {student.name}\n"
                f"Scores: {', '.join(str(s) for s in student.scores)}\n"
                f"Average: {avg:.2f}%\n"
                f"Grade: {grade}\n"
                f"GPA: {gpa:.1f}\n"
                f"Remark: {remark}"
            )
        self.details_box.configure(state="normal")
        self.details_box.delete("0.0", "end")
        self.details_box.insert("0.0", detail)
        self.details_box.configure(state="disabled")

    def export_records_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export student records to CSV"
        )
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["student_id", "name", "scores", "average", "grade", "gpa", "remark"])
            for student in self.displayed_students:
                average = student.get_average()
                grade, gpa, remark = compute_grade(average)
                writer.writerow([
                    student.student_id,
                    student.name,
                    ";".join(str(score) for score in student.scores),
                    f"{average:.2f}",
                    grade,
                    f"{gpa:.1f}",
                    remark,
                ])

        messagebox.showinfo("Export Complete", f"Records exported to {path}")

    def export_summary_text(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            title="Export summary text"
        )
        if not path:
            return

        summary_text = get_summary_text(self.students)
        with open(path, "w", encoding="utf-8") as outfile:
            outfile.write(summary_text)

        messagebox.showinfo("Export Complete", f"Summary exported to {path}")

    def show_about(self):
        messagebox.showinfo(
            "About SRMS",
            "SRMS Student Results Management System\nClassic mode with menu, search, details, and export.\nBuilt with customtkinter."
        )

    def sort_by_column(self, column):
        sort_keys = {
            "id": lambda s: s.student_id.lower(),
            "name": lambda s: s.name.lower(),
            "average": lambda s: s.get_average(),
            "grade": lambda s: compute_grade(s.get_average())[0],
            "gpa": lambda s: compute_grade(s.get_average())[1],
            "remark": lambda s: compute_grade(s.get_average())[2],
        }
        reverse = self.sort_reverse.get(column, False)
        self.displayed_students.sort(key=sort_keys[column], reverse=reverse)
        if self.search_text_var.get().strip() == "":
            self.students = list(self.displayed_students)
        self.sort_reverse[column] = not reverse
        self.refresh_student_table()

    def update_form_message(self, message="", text_color="#EF4444"):
        self.form_message.configure(text=message, text_color=text_color)

    def change_theme(self, option):
        ctk.set_appearance_mode(option)

    def add_student(self):
        student_id = self.entry_student_id.get().strip()
        name = self.entry_name.get().strip()
        scores_text = self.entry_scores.get().strip()

        if not student_id:
            self.update_form_message("Student ID is required.")
            return
        if not name:
            self.update_form_message("Student name is required.")
            return

        if record_exists(student_id):
            self.update_form_message("This student ID already exists.")
            return

        try:
            scores = parse_scores(scores_text)
        except ValueError as exc:
            self.update_form_message(str(exc))
            return

        student = Student(student_id, name, scores)
        self.students.append(student)
        save_record(student)
        self.refresh_student_table()
        self.clear_form()
        self.update_form_message("", text_color="#EF4444")
        messagebox.showinfo("Student Added", f"{name} has been added successfully.")

    def delete_selected_student(self):
        selected = self.student_table.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a student record to delete.")
            return

        item = selected[0]
        values = self.student_table.item(item, "values")
        student_id = values[0]
        student_name = values[1]

        if messagebox.askyesno("Confirm Delete", f"Delete {student_name} ({student_id})?"):
            self.students = [s for s in self.students if s.student_id != student_id]
            delete_record(student_id)
            self.filter_students()
            self.update_detail_text(None)
            messagebox.showinfo("Deleted", f"Record for {student_name} has been deleted.")

    def show_summary(self):
        if len(self.students) == 0:
            messagebox.showinfo("Class Summary", "No records to summarise.")
            return

        averages = [s.get_average() for s in self.students]
        class_avg = sum(averages) / len(averages)
        max_avg = max(averages)
        min_avg = min(averages)
        top_student = self.students[averages.index(max_avg)]
        bottom_student = self.students[averages.index(min_avg)]

        distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0}
        for s in self.students:
            grade, _, _ = compute_grade(s.get_average())
            distribution[grade] += 1

        summary_window = ctk.CTkToplevel(self)
        summary_window.title("Class Summary")
        summary_window.geometry("700x520")
        summary_window.grab_set()

        top_frame = ctk.CTkFrame(summary_window, corner_radius=12)
        top_frame.pack(fill="x", padx=20, pady=(20, 10))
        top_frame.grid_columnconfigure((0, 1, 2), weight=1)

        metric_style = {"font": ctk.CTkFont(size=12), "anchor": "w"}

        stat_box1 = ctk.CTkFrame(top_frame, fg_color="#1F2937", corner_radius=12)
        stat_box1.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        ctk.CTkLabel(stat_box1, text="Total Students", **metric_style).pack(anchor="w", padx=16, pady=(16, 8))
        ctk.CTkLabel(stat_box1, text=str(len(self.students)), font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", padx=16, pady=(0, 16))

        stat_box2 = ctk.CTkFrame(top_frame, fg_color="#1F2937", corner_radius=12)
        stat_box2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(stat_box2, text="Class Average", **metric_style).pack(anchor="w", padx=16, pady=(16, 8))
        ctk.CTkLabel(stat_box2, text=f"{class_avg:.2f}%", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", padx=16, pady=(0, 16))

        stat_box3 = ctk.CTkFrame(top_frame, fg_color="#1F2937", corner_radius=12)
        stat_box3.grid(row=0, column=2, padx=(10, 0), pady=10, sticky="nsew")
        ctk.CTkLabel(stat_box3, text="Highest Scorer", **metric_style).pack(anchor="w", padx=16, pady=(16, 8))
        ctk.CTkLabel(stat_box3, text=f"{top_student.name} ({max_avg:.2f}%)", wraplength=200).pack(anchor="w", padx=16, pady=(0, 16))

        detail_frame = ctk.CTkFrame(summary_window, corner_radius=12)
        detail_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        detail_frame.grid_columnconfigure(0, weight=1)
        detail_frame.grid_columnconfigure(1, weight=1)

        performance_frame = ctk.CTkFrame(detail_frame, corner_radius=12)
        performance_frame.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        ctk.CTkLabel(performance_frame, text="Performance Details", font=ctk.CTkFont(size=16, weight="bold"), anchor="w").pack(anchor="w", padx=16, pady=(16, 10))
        ctk.CTkLabel(performance_frame, text=f"Lowest Scorer: {bottom_student.name} ({min_avg:.2f}%)", anchor="w").pack(anchor="w", padx=16, pady=(0, 6))
        ctk.CTkLabel(performance_frame, text=f"Highest Scorer: {top_student.name} ({max_avg:.2f}%)", anchor="w").pack(anchor="w", padx=16, pady=(0, 6))
        ctk.CTkLabel(performance_frame, text=f"Number of Records: {len(self.students)}", anchor="w").pack(anchor="w", padx=16, pady=(0, 6))

        distribution_frame = ctk.CTkFrame(detail_frame, corner_radius=12)
        distribution_frame.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
        ctk.CTkLabel(distribution_frame, text="Grade Distribution", font=ctk.CTkFont(size=16, weight="bold"), anchor="w").pack(anchor="w", padx=16, pady=(16, 10))

        bar_colors = {
            "A": "#10B981",
            "B": "#3B82F6",
            "C": "#F59E0B",
            "D": "#F97316",
            "E": "#EAB308",
            "F": "#EF4444",
        }
        total = max(len(self.students), 1)
        for grade, count in distribution.items():
            row_frame = ctk.CTkFrame(distribution_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=16, pady=6)
            ctk.CTkLabel(row_frame, text=f"{grade}", width=24).pack(side="left")
            progress = ctk.CTkProgressBar(row_frame, width=280)
            progress.set(count / total)
            progress.pack(side="left", padx=(12, 6), pady=2)
            ctk.CTkLabel(row_frame, text=f"{count}").pack(side="left")

        close_button = ctk.CTkButton(summary_window, text="Close", command=summary_window.destroy)
        close_button.pack(pady=(0, 20))

    def clear_form(self):
        self.entry_student_id.delete(0, "end")
        self.entry_name.delete(0, "end")
        self.entry_scores.delete(0, "end")
        self.update_form_message("")


if __name__ == "__main__":
    app = SRMSApp()
    app.mainloop()
