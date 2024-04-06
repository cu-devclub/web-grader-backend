def isCSV(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'