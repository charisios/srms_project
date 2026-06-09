
from student import Student
from grade import compute_grade
from data.database import create_table, save_record, load_records, delete_record, record_exists
from report import show_summary

students = [] # This list holds all Student objects while the program is running.


def add_student():
    """Prompts user for a new Student details and adds to the list."""

    student_id = input(f"Enter Student ID (e.g EEE/26/001): ").strip()

    # Validate Student for duplicates.
    if record_exists(student_id):
        print(f"ERROR: Student ID '{student_id}' already exists.")
        return
        
    name = input("Enter Student Name: ").strip()
    # Checks for invalid student names
    if name == "":
        print("ERROR: Name cannot be empty.")
        return
    
    scores = []
    try:
        num_courses = int(input("How many courses? "))
        for i in range(num_courses):
            score = float(input(f" Score for Course {i + 1} (0-100): "))
            if score < 0 or score > 100: # Checks for invalid scores (Must be between 1 and 100)
                print("ERROR: Score must be between 0 and 100.")
                return
            scores.append(score)

    except ValueError: # Ensures numeric values are entered for scores
        print("ERROR: Please enter numeric values for scores.")
        return
    
    # Creating student object and adding it to the list
    new_student = Student(student_id, name, scores)
    students.append(new_student)
    save_record(new_student)
    print(f"SUCCESS: Student '{name}' added.")


def view_all():
    """ Prints to the terminal all students' records. """

    print("\n--- ALL STUDENT RECORDS ---")

    if len(students) == 0:
        print("No records found.")
        return
    
    print(f"{'ID':<15} {'Nmae':<25} {'Average':>10} {'Grade':>8} {'GPA':>6} {'Remark':<15}")
    print("-" * 80)

    for s in students:
        avg = s.get_average()
        grade, gpa, remark = compute_grade(avg)
        print(f"{s.student_id:<15} {s.name:<25} {avg:>9.2f}% {grade:>8} {gpa:>6.1f} {remark:<15}")

    print("-" * 80)
    print(f"Total Records: {len(students)}")

def delete_student():
    """ Deletes a student object using student ID. """

    print("\n--- DELETE STUDENT RECORD ---")
    target_id = input("Enter Student ID to delete: ").strip()

    for i, s in enumerate(students):
        if s.student_id == target_id: # Checks whether student with specified ID exists.
            confirm = input(f"Confirm delete '{s.name}'? (yes/no): ").strip().lower()
            if confirm == "yes":
                students.pop(i)
                delete_record(target_id)
                print(f"Record for '{s.name}' deleted.")
            else:
                print("Deletion Cancelled.")
            return
        print(f"ERROR: No student found with ID '{target_id}'.")


def main_menu():
    """ Prints the main menu into the terminal when app is launched. """

    print("\n" + "=" * 50)
    print(" STUDENT RESULTS MANAGEMENT SYSTEM")
    print(" KNUST Obuasi | EEE Department")
    print("=" * 50)
    print("  [1] Add New Student")
    print("  [2] View All Records")
    print("  [3] Delete Student Record")
    print("  [4] Show Summary Report")
    print("  [5] Exit")
    print("=" * 50)


def run():
    """ Runs the main application. """

    create_table()
    loaded = load_records() # Loads records from database at startup.
    students.extend(loaded)
    print(f"[INFO] {len(loaded)} record(s) loaded from database.")

    while True:
        main_menu()
        choice = input("Enter choice (1-5): ").strip()

        if choice == "1":
            add_student()
        elif choice == "2":
            view_all()
        elif choice == "3":
            delete_student()
        elif choice == "4":
            show_summary(students)
        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("Invalid option. Please enter 1-6.")

# Running the application
if __name__ == "__main__":
    run()


# # TEMPORARY TEST
# add_student()
# view_all()