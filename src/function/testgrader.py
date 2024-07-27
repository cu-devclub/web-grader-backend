import subprocess
import json
import traceback
from io import StringIO
from contextlib import redirect_stdout
import stopit


def validate(filename):
    cmd = f'python -m nbgrader validate {filename}'
    with subprocess.Popen(cmd.split(), stdout=subprocess.PIPE) as process:
        out = process.communicate()[0].decode("utf-8").strip()
    return out == "" or out.startswith("THE CONTENTS ")


def grade(question, submit, addfile=[], validate=True, timeout=20, check_keyword="True"):
    if validate and not validate(submit):
        return True, "This file is not pass validation."

    with open(submit, "r", encoding="utf-8") as f:
        submit_data = json.load(f)

    code_cells = [cell for cell in submit_data["cells"] if cell.get("cell_type") == "code" and cell["metadata"].get("nbgrader") is not None]
    solutions = []
    solution_locations = []
    for i, cell in enumerate(code_cells):
        if cell["metadata"]["nbgrader"]["solution"]:
            solutions.append(cell["source"])
            solution_locations.append(i)

    if any(".write(" in solution for solution in solutions):
        return True, "This file contains file write method and may break the additional assignment files"

    tester_location = None
    for i, cell in enumerate(code_cells):
        if (
            not cell["metadata"]["nbgrader"]["solution"]
            and cell["metadata"].get("points") is None
            and "mock_stdout.getvalue()" in "".join(cell["source"])
        ):
            tester_location = "".join(cell["source"])
            break

    testcases = []
    points = []
    is_on = False
    temp = []
    for i, cell in enumerate(code_cells):
        if (
            not cell["metadata"]["nbgrader"]["solution"]
            and cell["metadata"].get("points") is not None
        ):
            if not is_on:
                is_on = True
            points.append(cell["metadata"]["nbgrader"].get("points"))
            temp.append(i)
        else:
            if is_on:
                testcases.append(temp)
                temp = []
                is_on = False
    if is_on:
        testcases.append(temp)

    with open(question, "r", encoding="utf-8") as f:
        question_data = json.load(f)

    question_cells = [cell["source"] for cell in question_data["cells"] if cell.get("cell_type") == "code"]

    if len(testcases) != len(solution_locations):
        return True, f"Number of testcases and solutions do not match. ({len(testcases)} testcases with {len(solution_locations)} solutions)"

    scores = []
    for i, solution_location in enumerate(solution_locations):
        max_points = 0
        correct_points = 0
        for case_index in testcases[i]:
            max_points += points[case_index]
            test = question_cells[case_index]
            if addfile:
                for filename in addfile:
                    test = test.replace(filename.split("/")[-1], filename)
            try:
                if not tester_location:
                    final_exec = [tester_location, solutions[i], test]
                else:
                    final_exec = [solutions[i], tester_location, test]
                with StringIO() as f, stopit.ThreadingTimeout(timeout) as context_manager:
                    with redirect_stdout(f):
                        exec("\n\n".join(final_exec), {})
                    if context_manager.state == context_manager.TIMED_OUT:
                        return True, f"Submission stuck in a loop for more than {timeout} seconds"
                output = f.getvalue().strip("\n").split("\n")
                passed = all(line == check_keyword for line in output)
                if passed:
                    correct_points += points[case_index]
            except Exception:
                pass
        scores.append([correct_points, max_points])
    return False, scores