from flask import request, jsonify, g
import json

from function.isCET import isCET

from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    Email = get_jwt_identity()['email']
    CSYID = request.args.get('CSYID')
    cur = g.dbdict.cursor()

    if not isCET(g.db, g.db.cursor(), Email, CSYID):
        jsonify({
            'success': False,
            'msg': "You don't have permission.",
            'data': {}
        }), 200

    # Query to get the list of students and their scores
    StudentList_query = """
    SELECT 
        STD.UID AS `ID`,
        USR.Name AS `Name (English)`,
        SCT.Section AS `Section`,
        TRUNCATE(COALESCE(SUM(CASE 
                WHEN JSON_CONTAINS(LB.CID, CAST(STD.CID AS CHAR), "$") OR JSON_CONTAINS(LB.GID, CAST(STD.GID AS CHAR), "$")
                THEN SMT.Score
                ELSE 0 
            END), 0), 2) AS Score,
        SUB.MaxScore AS `MaxScore`,
        COALESCE(GRP.Group, '-') AS `Group`
    FROM 
        student STD
        LEFT JOIN user USR ON USR.UID = STD.UID
        LEFT JOIN submitted SMT ON SMT.UID = STD.UID AND SMT.CSYID = STD.CSYID
        LEFT JOIN lab LB ON SMT.LID = LB.LID
        INNER JOIN section SCT ON STD.CSYID = SCT.CSYID AND SCT.CID = STD.CID
        LEFT JOIN `group` GRP ON GRP.GID = STD.GID
        LEFT JOIN (
            SELECT 
                STD.UID,
                SUM(QST.MaxScore) AS MaxScore
            FROM 
                question QST
                LEFT JOIN lab LB on QST.LID = LB.LID
                LEFT JOIN student STD on (JSON_CONTAINS(LB.CID, CAST(STD.CID AS CHAR), "$") OR JSON_CONTAINS(LB.GID, CAST(STD.GID AS CHAR), "$"))
            WHERE
                QST.CSYID = %s
            GROUP BY 
                STD.UID
        ) SUB ON STD.UID = SUB.UID
    WHERE
        STD.CSYID = %s
    GROUP BY 
        STD.UID, USR.Name, SCT.Section, GRP.Group, SCT.CID, GRP.GID, SUB.MaxScore
    ORDER BY
        Section ASC, ID ASC;
    """
    cur.execute(StudentList_query, (CSYID, CSYID,))
    ListResult = cur.fetchall()

    return jsonify({
        'success': True,
        'msg': '',
        'data': {
            'Students': ListResult
        }
    }), 200