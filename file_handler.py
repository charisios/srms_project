
import csv
import os
from student import Student

DATA_FILE = os.path.join("data", "students.csv")



def save_records(students):
    """ Saves students data to database. """

    os.makedirs("data", exist_ok=True)

    with open(DATA_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        # Write header row
        writer.writerow(["student_id", "name", "scores"])

        for s in students:
            # Joining scores into a semicolon-seperated string
            scores_str = ";".join(str(score) for score in s.scores)
            writer.writerow([s.student_id, s.name, scores_str])


def load_records():
    """ Fetches students records from database on startup (When called). """
    
    student_list = []

    if not os.path.exists(DATA_FILE):
        return student_list # No file yet
    
    with open(DATA_FILE, mode="r", newline="") as f:
        reader = csv.reader(f)
        next(reader) # Skip the header row

        for row in reader:
            if len(row) < 3:
                continue  # Skip malformed rows

            student_id = row[0]
            name = row[1]

            scores = [float(x) for x in row[2].split(";") if x]

            student_list.append(Student(student_id, name, scores))

        return student_list


# # TEMPORARY TEST
# if __name__ == "__main__":
#     from student import Student
#     test_students = [
#         Student("EEE/24/001", "Kwame Mensah", [72.5, 65.0, 80.0]),
#         Student("EEE/24/002", "Abena Owusu",  [88.0, 91.5, 75.0]),
#     ]
#     save_records(test_students)
#     print("Saved. Now loading...")
#     loaded = load_records()
#     for s in loaded:
#         print(s)
