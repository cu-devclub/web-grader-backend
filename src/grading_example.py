import function.grader as grader
import time

addition = [
    "files/addfile/move1.txt",
    "files/addfile/move1a.txt",
    "files/addfile/move2.txt",
    "files/addfile/move2a.txt",
    "files/addfile/move3.txt",
    "files/addfile/move3a.txt",
    "files/addfile/move4.txt",
    "files/addfile/move4a.txt"
]

source_Q1 = "files/source/Lab7_Q1.ipynb"
source_Q2 = "files/source/Lab7_Q2.ipynb"
source_Q3 = "files/source/Lab7_Q3.ipynb"

submit_Q1 = "files/submit/6634473123-Q1.ipynb"
submit_Q2 = "files/submit/6634473123-Q2.ipynb"
submit_Q3 = "files/submit/6634473123-Q3.ipynb"


AS = []
times = []

i = time.perf_counter()
err, data = grader.grade(source_Q1, submit_Q1, addfile=addition, validate=False)
if(err):
    print("ERROR:", data)
else:
    AS.append(data)

times.append(time.perf_counter() - i)
print("L1", times[0], "Seconds")

err, data = grader.grade(source_Q2, submit_Q2, addfile=addition, validate=False)
if(err):
    print("ERROR:", data)
else:
    AS.append(data)

times.append(time.perf_counter() - i)
print("L2", times[1], "Seconds")

err, data = grader.grade(source_Q3, submit_Q3, addfile=addition, validate=False, check_keyword="True")
# err, data = grader.grade(source_Q3, "source/Lab-1.ipynb", addfile=addition, validate=False, check_keyword="True")
if(err):
    print("ERROR:", data)
    AS.append([0,0])
else:
    AS.append(data) 

times.append(time.perf_counter() - i)
print("L3", times[2], "Seconds")
print("Average", sum(times)/len(times))

print()
for i in AS:
    if len(i) == 1:
        print(f"Points: {i[0][0]}\nMax Points: {i[0][1]}")
    else:
        for j in range(len(i)):
            print(f"Q{j+1}\nPoints: {i[j][0]}\nMax Points: {i[j][1]}")