from flask import request, jsonify, g

def main():
    
    CSYID = request.args.get('CSYID')
    cur = g.db.cursor()
    StudentList_query ="""
        SELECT 
            STD.UID,
            USR.Name,
            SCT.Section,
            COALESCE(SUM(SMT.Score), 0) AS Score
        FROM 
            student STD
            LEFT JOIN user USR ON USR.UID = STD.UID
            LEFT JOIN submitted SMT ON SMT.UID = STD.UID
            INNER JOIN section SCT ON STD.CSYID = SCT.CSYID AND SCT.CID = STD.CID
        WHERE
            STD.CSYID = %s
        GROUP BY 
            STD.UID, USR.Name, SCT.Section
        ORDER BY
            Section ASC,UID ASC;
        """
    cur.execute(StudentList_query,(CSYID))
    ListResult = cur.fetchall()
    
    transformed_data = []

    for row in ListResult:
        transformed_data.append({'ID': row[0], 'Name (English)': row[1], 'Section': row[2], "Score": row[3]})

    MaxScore_query = """ 
        SELECT
            COALESCE(SUM(QST.MaxScore), 0) as TotalMax 
        FROM
            question QST
        WHERE
            QST.CSYID = %s
        GROUP BY
            QST.CSYID
        """
    cur.execute(MaxScore_query,(CSYID))
    TotalMaxCur = cur.fetchall()
    if(len(TotalMaxCur) > 0):
        TotalMax = TotalMaxCur[0][0]
    else:
        TotalMax = 0

    return jsonify({
        'success': True,
        'msg': '',
        'data': {
            'Students': transformed_data,
            'MaxScore': TotalMax
        }
    })