from datetime import datetime

from function.db import get_db
from flask import request, jsonify

def main():
    conn = get_db()
    cursor = conn.cursor()
    
    LID = request.args.get("LID")


    try:
        query = """ 
            SELECT
                LB.Lab,
                LB.Name,
                LB.Publish,
                LB.Due,
                LB.CID,
                LB.GID,
                LB.CSYID
            FROM
                lab LB
            WHERE 
                LB.LID = %s
            """
        cursor.execute(query, (LID))

        data = cursor.fetchall()[0]

        isGroup = data[4] == None

        CSYID = data[6]

        if isGroup:
            query = """
            SELECT 
                GRP.GID,
                GRP.Group 
            FROM 
                `group` GRP 
            WHERE 
                GRP.CSYID = %s"""
        else:
            query = """
            SELECT 
                SCT.CID,
                SCT.Section 
            FROM 
                section SCT 
            WHERE 
                SCT.CSYID = %s
            """

        cursor.execute(query, (CSYID))
        data2 = cursor.fetchall()

        PreSelectList = {}
        for i in data2:
            PreSelectList[i[0]] = i[1]

        query = """
            SELECT
                QST.MaxScore
            FROM 
                question QST 
            WHERE 
                QST.LID = %s
            ORDER BY 
                QST.QID DESC;
            """
        
        cursor.execute(query, (LID))
        data2 = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'msg': '',
            'data': {
                'LabNum': data[0],
                'LabName': data[1],
                "PubDate": data[2].strftime("%Y-%m-%dT%H:%M:%S"),
                "DueDate": data[3].strftime("%Y-%m-%dT%H:%M:%S"),
                "IsGroup": isGroup,
                "Selected": [PreSelectList[int(i)] for i in [i.strip() for i in data[5].strip("[").strip("]").split(",")]],
                "SelectList": list(PreSelectList.values()),
                "Question": [{"id": i+1, "score": int(data2[i][0])} for i in range(len(data2))]
            }
        }), 200
    
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({
            'success': False,
            'msg': 'Please contact admin',
            'data': e
        }), 200



    
    # transformdata = {}
    
    # # Query for question datetime
    # question_datetime_query = """
    # SELECT
    #     SCT.Section,
    #     ASN.Publish,
    #     ASN.Due
    # FROM
    #     section SCT
    #     INNER JOIN assign ASN ON SCT.CID = ASN.CID
    # WHERE 
    #     SCT.CSYID = %s
    # """
    # cursor.execute(question_datetime_query, (CSYID, LabNumber))
    # datetime_data = cursor.fetchall()
    
    # transformdata['LabTime'] = {}
    # for row in datetime_data:
    #     section = row[0]
    #     publish = row[1]
    #     due = row[2]
    #     formatted_publish = publish.strftime("%Y-%m-%dT%H:%M")
    #     formatted_due = due.strftime("%Y-%m-%dT%H:%M")

    #     transformdata['LabTime'][section] = {'publishDate': formatted_publish, 'dueDate': formatted_due}
    
    # # Query for question and max score
    # question_questionsscore_query = """
    # SELECT
    #     QST.Question,
    #     QST.MaxScore
    # FROM
    #     question QST
    # WHERE 
    #     QST.CSYID = %s
    #     AND QST.Lab = %s
    # """
    # cursor.execute(question_questionsscore_query, (CSYID, LabNumber))
    # question_data = cursor.fetchall()
    
    # transformdata['Question'] = [{"id": q[0], "score": q[1]} for q in question_data]
    
    # # Query for additional files
    # question_addfile_query = """
    # SELECT
    #     ADF.PathToFile
    # FROM
    #     addfile ADF
    # WHERE
    #     ADF.CSYID = %s
    #     AND ADF.Lab = %s
    # """
    # cursor.execute(question_addfile_query, (CSYID, LabNumber))
    # file_data = cursor.fetchall()
    
    # transformdata['file'] = [f[0] for f in file_data]
    
    # # Query for Section
    # question_section_query = """
    # SELECT
    #     Section
    # FROM
    #     assign ASN
    #     INNER JOIN section SCT ON SCT.CID = ASN.CID
    # WHERE
    #     ASN.CSYID = %s
    #     AND ASN.Lab = %s
    # """
    # cursor.execute(question_section_query, (CSYID, LabNumber))
    # section = cursor.fetchall()

    # transformdata['section'] = [f[0] for f in section]
    
    # return jsonify(transformdata)