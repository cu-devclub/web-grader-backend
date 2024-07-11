import mysql.connector
from datetime import datetime
from flask import request, jsonify,g

def main():
    try:
        cursor = g.db.cursor()
        CSYID = request.args.get('CSYID')

        query = """ 
            SELECT
                LB.LID,
                LB.Lab,
                LB.Name,
                LB.Publish,
                LB.Due,
                CASE
                    WHEN `Lock` IS NULL THEN FALSE
                    WHEN CONVERT_TZ(NOW(), @@session.time_zone, '+07:00') > `Lock` THEN 1
                    ELSE 0
                END AS is_locked
            FROM
                lab LB
            WHERE 
                LB.CSYID = %s
            ORDER BY
                Publish ASC,Lab DESC;
            """
        cursor.execute(query, (CSYID))

        data = cursor.fetchall()

        assignments = []

        for i in data:
            assignments.append({
                "LID": i[0],
                "Lab": i[1],
                "Name": i[2],
                "Publish": datetime.strptime(str(i[3]), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M"),
                "Due": datetime.strptime(str(i[4]), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M"),
                "Lock": bool(i[5])
            })

        return jsonify({
            'success': True,
            'msg': '',
            'data': {
                'Assignment': assignments
            }
        }), 200
        
    except mysql.connector.Error as error:

        return jsonify({
            'success': False,
            'msg': 'Please contact admin',
            'data': error
        }), 200