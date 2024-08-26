import subprocess
import json
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
    


# Question information generator (for faster proccessing)
def QinfoGenerate(Question, addfile=[]) -> dict:
    temporarySplitWord = "+|spliter|+"
    template = {
        "Tester": "",
        "TesterLoc": 0,
        "Testcase":[],
        "Points": []
    }

    # Read question file
    with open(Question, "r", encoding= "utf-8") as f:
        Qfile = json.loads(f.read())

    # Filter code cell
    ScodeCell = [i for i in Qfile["cells"] if (i.get("cell_type") == "code" and i["metadata"].get("nbgrader") != None)]

    # Tester
    for i in range(len(ScodeCell)):
        if (ScodeCell[i]["metadata"]["nbgrader"]["solution"] == False) and (ScodeCell[i]["metadata"]["nbgrader"].get("points") == None) and "mock_stdout.getvalue()" in "".join(ScodeCell[i]["source"]):
            template["TesterLoc"] = i
            template["Tester"] = "".join(ScodeCell[i]["source"])
        

    # Testcase
    isPeriod = False
    temporaryTestcase = ""
    for i in range(len(ScodeCell)):
        if (ScodeCell[i]["metadata"]["nbgrader"]["solution"] == False) and (ScodeCell[i]["metadata"]["nbgrader"].get("points") != None):
            if not isPeriod:
                isPeriod = not isPeriod
            template["Points"].append(ScodeCell[i]["metadata"]["nbgrader"].get("points"))
            temporaryTestcase += "".join(ScodeCell[i]["source"]) + temporarySplitWord
            if i != len(ScodeCell)-1:
                continue

        if isPeriod or i == len(ScodeCell)-1:
            if temporaryTestcase == "":
                continue

            # replacing file path
            if(len(addfile) != 0):
                for afpath in addfile:
                    afname = afpath.split("/")[-1]
                    temporaryTestcase = temporaryTestcase.replace(afname, afpath)

            template["Testcase"].append(temporaryTestcase.strip(temporarySplitWord).split(temporarySplitWord))
            temporaryTestcase = ""
            isPeriod = not isPeriod

    return template
    


# Public grade method    
def grade(Question, submit, addfile=[], validate=True, timeout=20, check_keyword="True", Qinfo=None, protectWrite=True):
    # Validating submittion
    if validate:
        if not __validate(submit): return True, "This file is not pass validation."

    # Read submited file
    with open(submit, "r", encoding= "utf-8") as f:
        submitfile = json.loads(f.read())
 
    # Filter code cell
    codeCell = [i for i in submitfile["cells"] if (i.get("cell_type") == "code" and i["metadata"].get("nbgrader") != None)]

    # Get solution cell
    temporarySplitWord = "+|spliter|+"
    solution = []
    for i in range(len(codeCell)):
        if codeCell[i]["metadata"]["nbgrader"]["solution"]:
            TempSol = temporarySplitWord.join(codeCell[i]["source"])

            # Write method protection
            if(protectWrite):
                if ".write(" in TempSol: return True, "This file contain file write method it may broke the additional assignment files"
            
            solution.append("".join(TempSol.split(temporarySplitWord)))         

    if Qinfo is None:
        Qinfo = QinfoGenerate(Question, addfile)

    # if len(Qinfo) == 0:
    # return True, json.dumps(Qinfo)
    
    #check number of testcase list and solution
    if len(Qinfo["Testcase"]) != len(solution):
        return True, f"Number of testcase and solution is not match. ({len(Qinfo["Testcase"])} testcase with {len(solution)} solution)"

    score = []
    num = 0
    for solIndex in range(len(solution)):
        temp_max_p = 0
        temp_cor_p = 0
        for test in Qinfo["Testcase"][solIndex]:
            temp_max_p += Qinfo["Points"][num]
            try:
                if(Qinfo["TesterLoc"] == 0):
                    finalexec = [Qinfo["Tester"], solution[solIndex], test]
                else:
                    finalexec = [solution[solIndex], Qinfo["Tester"], test]

                output = StringIO()

                with stopit.ThreadingTimeout(timeout) as context_manager:
                    with redirect_stdout(output):
                        exec("\n\n".join(finalexec), {})
                        
                if context_manager.state == context_manager.TIMED_OUT:
                    return True, f"This submittion have stuck in loop that run longer than {timeout} seconds"
                results = output.getvalue().strip("\n").split("\n")
                isPass = True
                for result in results:
                    if(result != check_keyword):
                        isPass = False
                        break
                if(isPass): temp_cor_p += Qinfo["Points"][num]

            except Exception:
                pass

            num += 1
        score.append([temp_cor_p, temp_max_p])
    return False, score