import csv
import json
from datetime import datetime
from io import StringIO
from flask import request, jsonify

from function.db import get_db
from function.GetClassSchoolyear import GetClassSchoolyear
from function.isCET import isCET


from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    Email = get_jwt_identity()['email']
    conn = get_db()
    cursor = conn.cursor()
    
    # Parse JSON data from the request
    data = json.loads(request.form.get('CSV_data'))
    CSV_data = data["CSV_data"]
    CSYID = data["CSYID"]

    if not isCET(conn, cursor, Email, CSYID):
        jsonify({
            'success': False,
            'msg': "You don't have permission.",
            'data': {}
        }), 200
    
    ClassID, SchoolYear = GetClassSchoolyear(conn, cursor, CSYID) 
    
    # Specify the initial fieldnames
    fieldnames = ['ID', 'Name (English)', 'Section', 'Group', 'Score', 'MaxScore']

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

    # Create an in-memory binary stream for the final output
    output = StringIO(temp_csv_data)
    
    return jsonify({
        'success': True,
        'msg': '',
        'data': {
            'csv': output.getvalue(),
            'filename': f"{ClassID}_{SchoolYear}_{datetime.now().strftime('%d-%m-%YT%H-%M-%S')}.csv"
        }
    })