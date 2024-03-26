import os
from werkzeug.utils import secure_filename

def save_thumbnail_file(file):
    if file and file.filename != '':
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join("files", 'Thumbnail', filename)
            file.save(filepath)
            return True, filename  # Success flag and filename
        except Exception as e:
            print(f"Error saving thumbnail file: {e}")
            return False, None  # Return False if saving failed
    return True, None