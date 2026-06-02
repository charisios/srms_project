
def compute_grade(average):
    """
    Given a numeric average (0–100), returns a tuple:
    (letter_grade, gpa_point, remark)

    Example:
        compute_grade(72.5) → ("A", 4.0, "Distinction")
    """

    if average >= 70:
        return ("A", 4.0, "Distinction")
    elif average >= 60:
        return ("B", 3.0, "Credit")
    elif average >= 50:
        return ("C", 2.0, "Pass")
    elif average >= 45:
        return ("D", 1.0, "Pass")
    elif average >= 40:
        return ("E", 0.5, "Marginal Fail")
    else:
        return ("F", 0.0, "Fail")
    
def get_grade_summary(student):
    """
    Given a Student object, return a formatted summary string
    showing all grade information.
    """

    avg = student.get_average()
    grade, gpa, remark = compute_grade(avg)

    summary = (
        f"Student  : {student.name}\n"
        f"Average  : {avg:.2f}%\n"
        f"Grade    : {grade}\n"
        f"GPA      : {gpa}\n"
        f"Remark   : {remark}"
    )
    return summary

# #TEMPORARY TEST
# if __name__ == "__main__":
#     from student import Student
#     s = Student("EEE/26/001", "Parsley Sakyi", [72.5, 65.0, 80.0])
#     print(get_grade_summary(s))
