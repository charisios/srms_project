
from grade import compute_grade


def show_summary(students):
    """ 
    Given a list of students, returns a summary (Total students, Class average, Highest and Lowest scorer) 
    of the class.
    """
    
    print("\n--- CLASS SUMMARY REPORT ---")

    if len(students) == 0:
        print("No records to summarise.")
        return
    
    averages = [s.get_average() for s in students]

    class_avg = sum(averages) / len(averages)
    max_avg = max(averages)
    min_avg = min(averages)
    top_idx = averages.index(max_avg)
    bottom_idx = averages.index(min_avg)

    print(f"  Toatal Students   : {len(students)}")
    print(f"  Class Average     : {class_avg:.2f}%")
    print(f"  Highest Scorer    : {students[top_idx].name} ({max_avg:.2f}%)")
    print(f"  Lowest Scorer     : {students[bottom_idx].name} ({min_avg:.2f}%)")

    # Grade distribution
    distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0}
    for s in students:
        grade, _, _ = compute_grade(s.get_average())
        distribution[grade] += 1

    print("\n Grade Distribution:")
    for grade, count in distribution.items():
        bar = "#" * count
        print(f"   {grade} : {bar} ({count})")

    print("-" * 40)
