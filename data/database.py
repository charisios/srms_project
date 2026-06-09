
import sqlite3
import os
from student import Student

DB_FILE = os.path.join("data", "students.db")


def get_connection():
    """
    Create and return a connection to the SQLite database.
    Creates the data/ folder if it does not exist.
    """

    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_FILE)

def create_table():
    """
    Create the students table if it does not already exist.
    Called once when the program starts.

    Schema:
        student_id  TEXT  PRIMARY KEY
        name        TEXT  NOT NULL
        scores      TEXT  NOT NULL  (semicolon-separated floats)
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name       TEXT NOT NULL,
            scores     TEXT NOT NULL
            )
            """
    )

    conn.commit()
    conn.close()


def save_record(student):
    """
    Insert a new student record into the database.
    Uses INSERT OR REPLACE to handle any duplicates safely.

    Parameters:
        student (Student) : Student object to save
    """

    conn = get_connection()
    cursor = conn.cursor()

    scores_str = ";".join(str(s) for s in student.scores)

    cursor.execute("""
        INSERT OR REPLACE INTO students (student_id, name, scores)
        VALUES (?, ?, ?)
        """, (student.student_id, student.name, scores_str))
    
    conn.commit()
    conn.close()


def load_records():
    """
    Load all student records from the database.
    Returns a list of Student objects.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT student_id, name, scores FROM students")
    rows = cursor.fetchall()
    conn.close()

    student_list = []
    for row in rows:
        student_id = row[0]
        name = row[1]
        scores = [float(x) for x in row[2].split(";") if x]
        student_list.append(Student(student_id, name, scores))
    
    return student_list


def delete_record(student_id):
    """
    Delete a student record from the database by student ID.

    Parameters:
        student_id (str) : The ID of the student to delete
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM students WHERE student_id = ?", (student_id,)
    )

    conn.commit()
    conn.close()


def record_exists(student_id):
    """
    Check whether a student ID already exists in the database.
    Returns True if found, False otherwise.

    Parameters:
        student_id (str) : The ID to check
    """
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM students WHERE student_id = ?",
        (student_id,)
    )

    result = cursor.fetchone()
    conn.close()

    return result is not None