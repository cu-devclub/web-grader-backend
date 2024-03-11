import subprocess
import json
import traceback
from io import StringIO
from contextlib import redirect_stdout
import stopit

def __filter_escapes(string):
    string = (
    string
        .replace('\n', '')  # Newline
        .replace('\r', '')  # Carriage return
        .replace('\t', '')  # Tab
        .replace('\b', '')  # Backspace
        .replace('\f', '')  # Form feed
        .replace('\a', '')  # Alert sound
        .replace('\\', '')  # Literal backslash
    )
    return string

# Validation by nbgrader
def __validate(filename):
    cmd = f'python -m nbgrader validate {filename}'
    temp_f = StringIO()
    with redirect_stdout(temp_f):
        res = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
    out = __filter_escapes(res.stdout.decode("utf-8"))
    if(out == "" or out.startswith("THE CONTENTS ")):
        return False
    else:
        return True
    
# Public grade method    
def grade(Question, submit, addfile=[], validate=True, timeout=20, check_keyword="True"):
    # Validating submittion
    if validate:
        if not __validate(submit): return True, "This file is not pass validation."

    # Read submited file
    with open(submit, "r", encoding= "utf-8") as f:
        submitfile = json.loads(f.read())
 
    # Filter code cell
    codeCell = [i for i in submitfile["cells"] if i.get("cell_type") == "code"]

    # Get solution cell
    solution = []
    solutionLocation = []
    for i in range(len(codeCell)):
        if codeCell[i]["metadata"]["nbgrader"]["solution"]:
            solution.append(codeCell[i]["source"])
            solutionLocation.append(i)

    # Write method protection
    for i in range(len(solution)):
        for j in range(len(solution[i])):
            if ".write(" in solution[i][j]: return True, "This file contain file write method it may broke the additional assignment files"

    # Tester Location
    testerL = []
    for i in range(len(codeCell)):
        if (codeCell[i]["metadata"]["nbgrader"]["solution"] == False) and (codeCell[i]["metadata"]["nbgrader"].get("points") == None) and len(codeCell[i]["source"]) >= 5:
            testerL.append(i)

    # s
    testcaseL = []
    pointsL = []
    isOn = False
    temp = []
    for i in range(len(codeCell)):
        if (codeCell[i]["metadata"]["nbgrader"]["solution"] == False) and (codeCell[i]["metadata"]["nbgrader"].get("points") != None):
            if not isOn:
                isOn = not isOn
            pointsL.append(codeCell[i]["metadata"]["nbgrader"].get("points"))
            temp.append(i)
        else:
            if isOn:
                testcaseL.append(temp)
                temp = []
                continue
        if i == len(codeCell)-1:
            testcaseL.append(temp)
            temp = []

    # Read question file
    with open(Question, "r", encoding= "utf-8") as f:
        Qfile = json.loads(f.read())

    # Filter code cell
    ScodeCell = [i["source"] for i in Qfile["cells"] if i.get("cell_type") == "code"]


    # making dict of tester that belong to each solution section
    tester = {}
    if len(solutionLocation) == len(testerL):
        for i in range(len(solutionLocation)):
            tester[solutionLocation[i]] = testerL[i]
    else:
        for i in range(len(solutionLocation)):
            key = solutionLocation[i]
            value = -1
            for j in range(len(testerL)):
                if(i < len(solutionLocation)-1):
                    if key < testerL[j] < solutionLocation[i+1]:
                        value = testerL[j]
                        break
                else:
                    if key < testerL[j]:
                        value = testerL[j]
                        break
            tester[key] = value
    
    #check number of testcase list and solution
    if len(testcaseL) != len(solutionLocation):
        return True, f"Number of testcase and solution is not match. ({len(testcaseL)} testcase with {len(solutionLocation)} solution)"
    
    score = []
    num = 0
    for i in range(len(solutionLocation)):
        tr = ""
        if tester[solutionLocation[i]] != -1:
            tr = "".join(ScodeCell[tester[solutionLocation[i]]])
        temp_max_p = 0
        temp_cor_p = 0
        for j in testcaseL[i]:
            temp_max_p += pointsL[num]
            test = "".join(ScodeCell[j])
            if(len(addfile) != 0):
                for k in addfile:
                    x = k.split("/")
                    test = test.replace(x[-1], k)
            try:
                finalexec = ["".join(solution[i]), tr, test]
                f = StringIO()

                with stopit.ThreadingTimeout(timeout) as context_manager:
                    with redirect_stdout(f):
                        exec("\n\n".join(finalexec), {})
                if context_manager.state == context_manager.TIMED_OUT:
                    return True, f"This submittion have stuck in loop that run longer than {timeout} seconds"
                s = f.getvalue().strip("\n").split("\n")
                p = True
                for k in s:
                    if(k != check_keyword):
                        p = False
                        break
                if(p): temp_cor_p += pointsL[num]
            except Exception:
                print(traceback.format_exc())
            num += 1
        score.append([temp_cor_p, temp_max_p])
    return False, score