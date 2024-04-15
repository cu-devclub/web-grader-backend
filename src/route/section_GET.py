from function.db import get_db
from flask import jsonify, request

def main():
    conn = get_db()
    cursor = conn.cursor()
    
    CSYID = request.args.get("CSYID")
    section_query = """SELECT SCT.Section FROM section SCT WHERE SCT.CSYID = %s"""
    cursor.execute(section_query, (CSYID,))
    data = cursor.fetchall()
    
    # Transform the fetched data into a list of section values
    transformdata = [row[0] for row in data]
    
    return jsonify(transformdata)