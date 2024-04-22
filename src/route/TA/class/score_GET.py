import mysql.connector
from flask import request, jsonify, g

def main():
    try:
        
        cursor = g.db.cursor()
        
        CSYID = request.args.get('CSYID')
        Lab = request.args.get('Lab')
                
        query = """ 
            SELECT 
                STD.UID,
                USR.Name,
                QST.Lab,
                QST.Question,
                LB.Name as LabName,
                ASN.Due,
                SMT.Timestamp,
                QST.MaxScore,
                SMT.Score,
                CASE WHEN SMT.Timestamp IS NOT NULL THEN TRUE ELSE FALSE END As TurnIn,
                CASE WHEN ASN.Due <= SMT.Timestamp THEN TRUE ELSE FALSE END AS Late,
                SCT.section,
                SMT.LastEdit
            FROM
                question QST
                INNER JOIN lab LB ON QST.CSYID = LB.CSYID AND QST.Lab = LB.lab 
                INNER JOIN section SCT ON SCT.CSYID = QST.CSYID
                INNER JOIN assign ASN ON SCT.CID = ASN.CID AND QST.Lab = ASN.Lab AND ASN.Lab = LB.Lab AND ASN.CSYID = LB.CSYID
                INNER JOIN student STD ON STD.CID = ASN.CID
                LEFT JOIN submitted SMT ON QST.CSYID = SMT.CSYID AND QST.Lab = SMT.Lab AND QST.Question = SMT.Question AND SMT.UID = STD.UID
                INNER JOIN user USR ON USR.UID = STD.UID
            WHERE
                QST.CSYID = %s
                AND LB.Lab = %s
            """ 
        cursor.execute(query, (CSYID, Lab))
        
        data = cursor.fetchall()
        transformed_data = {}

        for entry in data:
            uid, name, lab, question, lab_name, due, timestamp, max_score, score, turn_in, late, section, last_edit = entry
            if lab not in transformed_data:
                transformed_data[lab] = {'LabName': lab_name, 'Due': due, 'Questions': {}}
            if question not in transformed_data[lab]['Questions']:
                transformed_data[lab]['Questions'][question] = {'MaxScore': max_score, 'Scores': {}}
            transformed_data[lab]['Questions'][question]['Scores'][uid] = {'Name':name,'Score': score, 'Timestamp': timestamp,'Late':bool(late),'Section':section,'LastEdit':last_edit}


        return jsonify(transformed_data[Lab])
        
    except mysql.connector.Error as error:
        return jsonify({"error": f"An error occurred: {error}"}), 500