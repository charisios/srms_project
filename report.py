
from grade import compute_grade


def get_summary_text(students):
    """Return a formatted class summary for the given student list."""

    if len(students) == 0:
        return "No records to summarise."

    averages = [s.get_average() for s in students]
    class_avg = sum(averages) / len(averages)
    max_avg = max(averages)
    min_avg = min(averages)
    top_idx = averages.index(max_avg)
    bottom_idx = averages.index(min_avg)

    distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0}
    for s in students:
        grade, _, _ = compute_grade(s.get_average())
        distribution[grade] += 1

    lines = [
        "--- CLASS SUMMARY REPORT ---",
        f"Total Students   : {len(students)}",
        f"Class Average    : {class_avg:.2f}%",
        f"Highest Scorer   : {students[top_idx].name} ({max_avg:.2f}%)",
        f"Lowest Scorer    : {students[bottom_idx].name} ({min_avg:.2f}%)",
        "",
        "Grade Distribution:",
    ]

    for grade, count in distribution.items():
        lines.append(f"  {grade} : {'#' * count} ({count})")

    lines.append("".join(["-" * 40]))

    return "\n".join(lines)


def show_summary(students):
    print(get_summary_text(students))
