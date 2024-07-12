import json
from datetime import datetime

from flask import request, jsonify, g

def main():
    conn = g.db
    cursor = conn.cursor()

    LID = request.args.get('LID')
    if not LID:
        return jsonify({
            'success': False,
            'msg': 'LID is required',
            'data': {}
        }), 400

    try:
        # Get lab details
        query = """
            SELECT
                LB.CID,
                LB.GID,
                LB.Due
            FROM
                lab LB
            WHERE 
                LB.LID = %s
        """
        cursor.execute(query, (LID,))
        lab_details = cursor.fetchone()
        if not lab_details:
            return jsonify({
                'success': False,
                'msg': 'Lab not found',
                'data': {}
            }), 404

        CID_list = json.loads(lab_details[0]) if lab_details[0] else []
        GID_list = json.loads(lab_details[1]) if lab_details[1] else []
        due_date = lab_details[2]

        # Get questions
        query = """
            SELECT QST.QID, QST.MaxScore
            FROM question QST
            WHERE QST.LID = %s
            ORDER BY QST.QID ASC
        """
        cursor.execute(query, (LID,))
        questions = cursor.fetchall()
        if not questions:
            return jsonify({
                'success': False,
                'msg': 'No questions found for the lab',
                'data': {}
            }), 404

        all_max_score = sum([int(q[1]) for q in questions])

        # Get students
        cid_condition = "ST.CID IN (%s)" % ','.join(map(str, CID_list)) if CID_list else "1=0"
        gid_condition = "ST.GID IN (%s)" % ','.join(map(str, GID_list)) if GID_list else "1=0"

        query = f"""
            SELECT ST.UID, ST.CID, ST.GID, US.Name
            FROM student ST
            JOIN user US ON ST.UID = US.UID
            WHERE {cid_condition} OR {gid_condition}
        """
        cursor.execute(query)
        students = cursor.fetchall()

        student_data = []
        for student in students:
            UID, CID, GID, Name = student
            student_smt = []
            all_score = 0

            for question in questions:
                QID, MaxScore = question

                query = """
                    SELECT Score, Timestamp
                    FROM submitted
                    WHERE UID = %s AND QID = %s AND LID = %s
                """
                cursor.execute(query, (UID, QID, LID))
                submission = cursor.fetchone()
                score = submission[0] if submission and submission[0] is not None else 0
                timestamp = submission[1] if submission else None

                if timestamp:
                    timestamp_str = timestamp.strftime("%d/%m/%Y %H:%M")
                    late = timestamp > due_date
                else:
                    timestamp_str = "-"
                    late = datetime.now() > due_date

                student_smt.append({
                    "Time": timestamp_str,
                    "Late": late,
                    "Score": int(score),
                    "MaxScore": int(MaxScore)
                })
                all_score += score

            student_data.append({
                "UID": UID,
                "Name": Name,
                "SMT": student_smt,
                "AllScore": int(all_score)
            })

        return jsonify({
            'success': True,
            'msg': '',
            'data': {
                'Students': student_data,
                'AllMaxScore': int(all_max_score)
            }
        }), 200

    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({
            'success': False,
            'msg': 'Please contact admin',
            'data': str(e)
        }), 500