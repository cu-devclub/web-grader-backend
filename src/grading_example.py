import grader
import time

addition = [
    "addfile/move1.txt",
    "addfile/move1a.txt",
    "addfile/move2.txt",
    "addfile/move2a.txt",
    "addfile/move3.txt",
    "addfile/move3a.txt",
    "addfile/move4.txt",
    "addfile/move4a.txt"
]

source_Q1 = "source/Lab7_Q1.ipynb"
source_Q2 = "source/Lab7_Q2.ipynb"
source_Q3 = "source/Lab7_Q3.ipynb"

submit_Q1 = "submit/6634473123-Q1.ipynb"
submit_Q2 = "submit/6634473123-Q2.ipynb"
submit_Q3 = "submit/6634473123-Q3.ipynb"

source_TA = "source/sec1-A.ipynb"
source_TB = "source/sec1-B.ipynb"

submit_A1 = "submit/6431254323-sec1-A - Suwaphat Tantarach.ipynb"
submit_A2 = "submit/6631064623-sec1-A - Sukanya Khooha.ipynb"
submit_B1 = "submit/6631046323-sec1-B - Phatarakrit Sangsuriyan.ipynb"
submit_B2 = "submit/6631037723-sec1-B - Punnisa Srisamer.ipynb"

AS = []
times = []

i = time.perf_counter()
n = 1

err, data = grader.grade(source_TA, submit_A1, addfile=addition, validate=False, check_keyword="ok")
if(err):
    print("ERROR:", data)
else:
    AS.append(data)
print(f"{submit_A1}")
if len(data) == 1:
    print(f"Points: {data[0][0]}\nMax Points: {data[0][1]}")
else:
    for j in range(len(data)):
        print(f"Q{j+1}\nPoints: {data[j][0]}\nMax Points: {data[j][1]}")


times.append(time.perf_counter() - i)
print(f"Test{n}", times[0], "Seconds\n")
n += 1

err, data = grader.grade(source_TA, submit_A2, addfile=addition, validate=False, check_keyword="ok")
if(err):
    print("ERROR:", data)
else:
    AS.append(data)
print(f"{submit_A2}")
if len(data) == 1:
    print(f"Points: {data[0][0]}\nMax Points: {data[0][1]}")
else:
    for j in range(len(data)):
        print(f"Q{j+1}\nPoints: {data[j][0]}\nMax Points: {data[j][1]}")


times.append(time.perf_counter() - i)
print(f"Test{n}", times[0], "Seconds\n")
n += 1

err, data = grader.grade(source_TB, submit_B1, addfile=addition, validate=False, check_keyword="ok")
if(err):
    print("ERROR:", data)
else:
    AS.append(data)
print(f"{submit_B1}")
if len(data) == 1:
    print(f"Points: {data[0][0]}\nMax Points: {data[0][1]}")
else:
    for j in range(len(data)):
        print(f"Q{j+1}\nPoints: {data[j][0]}\nMax Points: {data[j][1]}")


times.append(time.perf_counter() - i)
print(f"Test{n}", times[0], "Seconds\n")
n += 1

err, data = grader.grade(source_TB, submit_B2, addfile=addition, validate=False, check_keyword="ok")
if(err):
    print("ERROR:", data)
else:
    AS.append(data)
print(f"{submit_B2}")
if len(data) == 1:
    print(f"Points: {data[0][0]}\nMax Points: {data[0][1]}")
else:
    for j in range(len(data)):
        print(f"Q{j+1}\nPoints: {data[j][0]}\nMax Points: {data[j][1]}")


times.append(time.perf_counter() - i)
print(f"Test{n}", times[0], "Seconds\n")
n += 1






# err, data = grader.grade(source_Q1, submit_Q1, addfile=addition, validate=False)
# if(err):
#     print("ERROR:", data)
# else:
#     AS.append(data)

# times.append(time.perf_counter() - i)
# print("L1", times[0], "Seconds")

# err, data = grader.grade(source_Q2, submit_Q2, addfile=addition, validate=False)
# if(err):
#     print("ERROR:", data)
# else:
#     AS.append(data)

# times.append(time.perf_counter() - i)
# print("L2", times[1], "Seconds")

# err, data = grader.grade(source_Q3, submit_Q3, addfile=addition, validate=False, check_keyword="True")
# # err, data = grader.grade(source_Q3, "source/Lab-1.ipynb", addfile=addition, validate=False, check_keyword="True")
# if(err):
#     print("ERROR:", data)
#     AS.append([0,0])
# else:
#     AS.append(data) 

# times.append(time.perf_counter() - i)
# print("L3", times[2], "Seconds")
print("Average", sum(times)/len(times))

# print()
# for i in AS:
#     if len(i) == 1:
#         print(f"Points: {i[0][0]}\nMax Points: {i[0][1]}")
#     else:
#         for j in range(len(i)):
#             print(f"Q{j+1}\nPoints: {i[j][0]}\nMax Points: {i[j][1]}")