import os

def save_csv_file(ClassID, SchoolYear, file):
    if file and file.filename != '':
        try:
            
            filename = f"{ClassID}-{SchoolYear}{os.path.splitext(file.filename)[1]}"
            filepath = os.path.join("files", 'CSV', filename)
            file.save(filepath)
            return True, os.path.join('File1', filename)  # Success flag and relative path
        except Exception as e:
            print(f"Error saving CSV file: {e}")
            return False, None  # Return False if saving failed
    return True, None  # Return True if no file to save