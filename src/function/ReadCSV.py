import os
import csv
from function.AddUserClass import AddUserClass
from function.AddUserGrader import AddUserGrader

def ReadCSV(ClassID, SchoolYear):
    SYFile = SchoolYear.replace("/", "T")
    UPLOAD_FOLDER = 'files/CSV'
    filename = ClassID + "-" + SYFile + ".csv"
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            # Skip the header row if it exists
            next(reader, None)
            for row in reader:
                # Assuming the CSV columns are SID, Name, and Section
                SID, Name, Section = row
                # Concatenate "@student.chula.ac.th" to the end of each SID to form an Email
                Email = SID + "@student.chula.ac.th"
                # Call your functions to add data to the database
                AddUserGrader(SID, Email, Name)
                AddUserClass(Email, ClassID, SchoolYear, Section)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")