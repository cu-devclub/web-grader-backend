from flask import Flask, request, jsonify, g
import json
from function.isSTD import isSTD

from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    Email = get_jwt_identity()['email']
    CSYID = request.args.get('CSYID')
    cur = g.db.cursor()

    if(not isSTD(g.db, cur, Email, CSYID)):
        return jsonify({
            'success': False,
            'msg': "You don't have permission",
            'data': {}
        }), 200

    # Fetch user UID from Email
    cur.execute("SELECT UID FROM user WHERE Email = %s", (Email,))
    user = cur.fetchone()
    if not user:
        return jsonify({'success': False, 'msg': 'User not found'}), 404

    UID = user[0]

    # Fetch student data
    cur.execute("SELECT CID, GID FROM student WHERE UID = %s AND CSYID = %s", (UID, CSYID))
    student_data = cur.fetchone()
    if not student_data:
        return jsonify({'success': False, 'msg': 'Student not found'}), 404

    student_CID, student_GID = student_data

    # Calculate total max score
    cur.execute("""
        SELECT
            SUM(QST.MaxScore)
        FROM
            question QST
            JOIN lab L ON QST.LID = L.LID
        WHERE
            QST.CSYID = %s AND (JSON_CONTAINS(L.CID, CAST(%s AS JSON), '$') OR JSON_CONTAINS(L.GID, CAST(%s AS JSON), '$')) AND CONVERT_TZ(NOW(), '+00:00', '+07:00') >= L.Publish
    """, (CSYID, student_CID, student_GID,))
    MaxScoreResult = cur.fetchall()

    total_max_score = int(MaxScoreResult[0][0])

    # Calculate student's score
    cur.execute("""
        SELECT
            COALESCE(SUM(CASE 
                WHEN JSON_CONTAINS(LB.CID, CAST(STD.CID AS CHAR), "$") OR JSON_CONTAINS(LB.GID, CAST(STD.GID AS CHAR), "$")
                THEN SMT.Score
                ELSE 0 
            END), 0) AS Score
        FROM
            submitted SMT
            LEFT JOIN lab LB ON SMT.LID = LB.LID
            LEFT JOIN student STD ON STD.UID = SMT.UID
        WHERE
            SMT.UID = %s AND SMT.CSYID = %s
    """, (UID, CSYID))
    student_score = cur.fetchone()[0]

    # Calculate scores for all students in the class
    cur.execute("""
        SELECT
            STD.UID,
            COALESCE(SUM(CASE 
                WHEN JSON_CONTAINS(LB.CID, CAST(STD.CID AS CHAR), "$") OR JSON_CONTAINS(LB.GID, CAST(STD.GID AS CHAR), "$")
                THEN SMT.Score
                ELSE 0 
            END), 0) AS Score
        FROM
            student STD
            LEFT JOIN submitted SMT ON SMT.UID = STD.UID AND SMT.CSYID = STD.CSYID
            LEFT JOIN lab LB ON SMT.LID = LB.LID
        WHERE
            STD.CSYID = %s
        GROUP BY
            STD.UID
    """, (CSYID,))
    scores = cur.fetchall()

    # Calculate rank
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    rank = next((i + 1 for i, (uid, score) in enumerate(sorted_scores) if uid == UID), None)

    # Calculate chart data
    chart = [0] * 10
    for uid, score in scores:
        percentage = (score / total_max_score) * 100 if total_max_score else 0
        index = min(int(percentage) // 10, 9)
        chart[index] += 1

    # Mark the student's score range in the chart
    student_percentage = (student_score / total_max_score) * 100 if total_max_score else 0
    student_index = min(int(student_percentage) // 10, 9)
    chart[student_index] += 1

    # Total number of students
    total_students = len(scores)

    return jsonify({
        'success': True,
        'msg': '',
        'data': {
            'Score': int(student_score),
            'MaxScore': int(total_max_score),
            'Rank': int(rank),
            'Amount': total_students,
            'Chart': chart
        }
    }), 200