from function.db import get_db
from flask import jsonify, request

def main():
    conn = get_db()
    cursor = conn.cursor()
    
    CSYID = request.args.get("CSYID")
    section_query = """SELECT GRP.Group FROM `group` GRP WHERE GRP.CSYID = %s"""
    cursor.execute(section_query, (CSYID,))
    data = cursor.fetchall()
    
    # Transform the fetched data into a list of section values
    transformdata = sorted([row[0] for row in data])
    
    return jsonify(transformdata)