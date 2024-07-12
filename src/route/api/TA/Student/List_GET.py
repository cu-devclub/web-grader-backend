from flask import request, jsonify, g
import json

def main():
    CSYID = request.args.get('CSYID')
    cur = g.db.cursor()

    # Query to get the list of students and their scores
    StudentList_query = """
    SELECT 
        STD.UID,
        USR.Name,
        SCT.Section,
        COALESCE(SUM(SMT.Score), 0) AS Score,
        COALESCE(GRP.Group, '-') AS `Group`
    FROM 
        student STD
        LEFT JOIN user USR ON USR.UID = STD.UID
        LEFT JOIN submitted SMT ON SMT.UID = STD.UID AND SMT.CSYID = STD.CSYID
        INNER JOIN section SCT ON STD.CSYID = SCT.CSYID AND SCT.CID = STD.CID
        LEFT JOIN `group` GRP ON GRP.GID = STD.GID
    WHERE
        STD.CSYID = %s
    GROUP BY 
        STD.UID, USR.Name, SCT.Section, GRP.Group
    ORDER BY
        Section ASC, UID ASC;
    """
    cur.execute(StudentList_query, (CSYID,))
    ListResult = cur.fetchall()

    # Query to get the maximum score of all questions
    MaxScore_query = """
    SELECT
        QST.QID,
        QST.MaxScore,
        L.CID,
        L.GID
    FROM
        question QST
        JOIN lab L ON QST.LID = L.LID
    WHERE
        QST.CSYID = %s
    """
    cur.execute(MaxScore_query, (CSYID,))
    MaxScoreResult = cur.fetchall()

    # Calculate total MaxScore for each student
    student_max_scores = {}
    for row in ListResult:
        UID, _, _, _, _ = row
        student_max_scores[UID] = 0

    for QID, MaxScore, CID_json, GID_json in MaxScoreResult:
        CID_list = json.loads(CID_json) if CID_json else []
        GID_list = json.loads(GID_json) if GID_json else []
        
        for row in ListResult:
            UID, _, _, _, _ = row
            cur.execute("SELECT CID, GID FROM student WHERE UID = %s AND CSYID = %s", (UID, CSYID))
            student_data = cur.fetchone()
            student_CID, student_GID = student_data

            if student_CID in CID_list or (student_GID and student_GID in GID_list):
                student_max_scores[UID] += int(MaxScore)

    # Transform data to required format
    transformed_data = []
    for row in ListResult:
        UID, Name, Section, Score, Group = row
        transformed_data.append({
            'ID': UID,
            'Name (English)': Name,
            'Section': Section,
            'Group': Group,
            'Score': Score,
            'MaxScore': student_max_scores[UID]
        })

    return jsonify({
        'success': True,
        'msg': '',
        'data': {
            'Students': transformed_data
        }
    }), 200