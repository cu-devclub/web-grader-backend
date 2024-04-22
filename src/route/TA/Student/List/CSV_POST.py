import csv
import pytz
import json
from io import StringIO
from flask import request, Response

from function.db import get_db
from function.GetClassSchoolyear import GetClassSchoolyear

gmt_timezone = pytz.timezone('GMT')

def main():   
    conn = get_db()
    cursor = conn.cursor()
    
    # Parse JSON data from the request
    data = json.loads(request.form.get('CSV_data'))
    CSV_data = data["CSV_data"]
    MaxTotal = data["MaxTotal"]
    CSYID = data["CSYID"]

    print(CSV_data)
    print(MaxTotal)
    print(CSYID)
    
    ClassID, SchoolYear = GetClassSchoolyear(conn, cursor, CSYID) 
    
    # Specify the initial fieldnames
    fieldnames = ['UID', 'Name', 'Section', 'Score']

    print('Fieldnames:', fieldnames)
    print('First row keys:', CSV_data[0].keys())

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
    headers = {
        "Content-Disposition": f"attachment; filename={ClassID}-{SchoolYear}.csv",
        "Content-Type": "text/csv"
    }

    # Return the content of the final output stream as a Flask response
    return Response(output.getvalue(), headers=headers)