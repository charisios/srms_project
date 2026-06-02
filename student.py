
class Student:
    """
    Rpresents a single student record.
    Attributes: student_id, name, scores (list of floats)
    """

    def __init__(self, student_id, name, scores):
        """
        Constructor — called when a new Student object is created.
        Parameters:
            student_id (str)  : Unique identifier e.g. "EEE/26/001"
            name       (str)  : Full name of the student
            scores     (list) : List of float scores e.g. [72.5, 65.0, 80.0]
        """

        self.student_id = student_id
        self.name = name
        self.scores = scores

    def get_average(self):
        """Compute and return the average of all scores."""
        if len(self.scores) == 0:
            return 0.0
        return sum(self.scores) / len(self.scores)
    
    def __str__(self):
        """
        Returns a readable string representation of the student.
        Called automatically when you print(student_object).
        """

        avg = self.get_average()
        return (f"ID: {self.student_id} | "
                f"Name: {self.name} | "
                f"Scores: {self.scores} | "
                f"Average: {avg:.2f}%")
    
# # TEMPORARY TEST
# if __name__ == "__main__":
#      s = Student("EEE/26/001", "Parsley Sakyi", [72.5, 65.0, 80.0])
#      print(s)
#      print("Average:", s.get_average())