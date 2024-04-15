from flask import request, jsonify, g

def main():
    
    CSYID = request.args.get('CSYID')
    cur = g.db.cursor()
    StudentList_query = """ 
        SELECT
            STD.UID,
            USR.Name,
            SCT.Section
        FROM
            class CLS
            INNER JOIN section SCT ON CLS.CSYID = SCT.CSYID
            INNER JOIN student STD ON SCT.CID = STD.CID
            INNER JOIN user USR ON STD.UID = USR.UID
        WHERE
            CLS.CSYID = %s
        ORDER BY
            Section ASC,UID ASC
    """
    cur.execute(StudentList_query,(CSYID))
    ListResult = cur.fetchall()
    
    transformed_data = []

    for row in ListResult:
        UID , Name, Section = row
        transformed_data.append({'UID': UID, 'Name': Name, 'Section': Section})

    return jsonify(transformed_data)   