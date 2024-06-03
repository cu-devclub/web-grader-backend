import csv
import json
from datetime import datetime
from io import StringIO
from flask import request, jsonify

from function.db import get_db
from function.GetClassSchoolyear import GetClassSchoolyear


def main():   
    conn = get_db()
    cursor = conn.cursor()
    
    # Parse JSON data from the request
    data = json.loads(request.form.get('CSV_data'))
    CSV_data = data["CSV_data"]
    MaxTotal = data["MaxTotal"]
    CSYID = data["CSYID"]
    
    ClassID, SchoolYear = GetClassSchoolyear(conn, cursor, CSYID) 
    
    # Specify the initial fieldnames
    fieldnames = ['ID', 'Name (English)', 'Section', 'Group', 'Score']

    # Create a temporary in-memory buffer to store the CSV data
    temp_output = StringIO()
    
    # Create a DictWriter object and write the CSV data to the temporary buffer
    writer = csv.DictWriter(temp_output, fieldnames=fieldnames)
    writer.writeheader()
    for row in CSV_data:
        writer.writerow(row)

    # Read the CSV data from the temporary buffer
    temp_output.seek(0)
    temp_csv_data = temp_output.getvalue()
    temp_output.close()

    # Modify the header names in the CSV data
    modified_csv_data = temp_csv_data.replace('Score', f'Score ({MaxTotal})')

    # Create an in-memory binary stream for the final output
    output = StringIO(modified_csv_data)

    # Set response headers to indicate CSV content
    # headers = {
    #     "Content-Disposition": f"attachment; filename={ClassID}-{SchoolYear}-{datetime.now()}.csv",
    #     "Content-Type": "text/csv"
    # }

    # Return the content of the final output stream as a Flask response
    # print(output.getvalue())
    return jsonify({
        'success': True,
        'msg': '',
        'data': {
            'csv': output.getvalue(),
            'filename': f"{ClassID}_{SchoolYear}_{datetime.now().strftime('%d-%m-%YT%H-%M-%S')}.csv"
        }
    })