import subprocess
import json
import traceback
from io import StringIO
from contextlib import redirect_stdout
import stopit

def __filter_escapes(string):
    return string.translate(str.maketrans({
        '\n': '', '\r': '', '\t': '', '\b': '', '\f': '', '\a': '', '\\': ''
    }))

def __validate(filename):
    cmd = ['python', '-m', 'nbgrader', 'validate', filename]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    output = __filter_escapes(result.stdout.decode("utf-8"))
    return not (output == "" or output.startswith("THE CONTENTS "))

def grade(Question, submit, addfile=[], validate=True, timeout=20, check_keyword="True"):
    if validate and not __validate(submit):
        return True, "This file is not pass validation."

    try:
        with open(submit, "r", encoding="utf-8") as f:
            submitfile = json.load(f)

        code_cells = [
            cell for cell in submitfile["cells"]
            if cell.get("cell_type") == "code" and "nbgrader" in cell["metadata"]
        ]

        solution_cells = [
            (i, cell["source"]) for i, cell in enumerate(code_cells)
            if cell["metadata"]["nbgrader"].get("solution")
        ]

        for _, solution in solution_cells:
            for line in solution:
                if ".write(" in line:
                    return True, "This file contains file write method, it may break the additional assignment files"

        tester_index, tester_code = next(
            ((i, cell["source"]) for i, cell in enumerate(code_cells)
             if not cell["metadata"]["nbgrader"].get("solution")
             and cell["metadata"]["nbgrader"].get("points") is None
             and "mock_stdout.getvalue()" in "".join(cell["source"])),
            (None, None)
        )

        testcase_locations = []
        points_list = []
        temp_locations = []

        for i, cell in enumerate(code_cells):
            if cell["metadata"]["nbgrader"].get("points") is not None:
                points_list.append(cell["metadata"]["nbgrader"].get("points"))
                temp_locations.append(i)
            elif temp_locations:
                testcase_locations.append(temp_locations)
                temp_locations = []

        if temp_locations:
            testcase_locations.append(temp_locations)

        with open(Question, "r", encoding="utf-8") as f:
            question_file = json.load(f)

        question_code_cells = [
            "".join(cell["source"]) for cell in question_file["cells"]
            if cell.get("cell_type") == "code"
        ]

        if len(testcase_locations) != len(solution_cells):
            return True, f"Number of testcase and solution is not match. ({len(testcase_locations)} testcase with {len(solution_cells)} solution)"

        scores = []
        for sol_index, solution in solution_cells:
            solution_code = "\n\n".join(solution)  # Ensure solution code is a single string
            max_points = 0
            correct_points = 0
            for testcase_index in testcase_locations[sol_index]:
                max_points += points_list[testcase_index]
                test_code = question_code_cells[testcase_index]
                for filepath in addfile:
                    test_code = test_code.replace(filepath.split("/")[-1], filepath)
                try:
                    exec_code = "\n\n".join(
                        [solution_code, tester_code, test_code] if tester_index is not None else [solution_code, test_code]
                    )
                    output_buffer = StringIO()

                    with stopit.ThreadingTimeout(timeout) as context_manager:
                        with redirect_stdout(output_buffer):
                            exec(exec_code, {})

                    if context_manager.state == context_manager.TIMED_OUT:
                        return True, f"This submission got stuck in a loop running longer than {timeout} seconds"

                    output_lines = output_buffer.getvalue().strip("\n").split("\n")
                    if all(line == check_keyword for line in output_lines):
                        correct_points += points_list[testcase_index]
                except Exception as e:
                    traceback.print_exc()
                    continue

            scores.append([correct_points, max_points])

        return False, scores
    except Exception as e:
        traceback.print_exc()
        return True, f"An error occurred: {e}"
