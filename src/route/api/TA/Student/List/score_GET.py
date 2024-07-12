from flask import request, jsonify, g

def main():
    CSYID = request.args.get('CSYID')
    cur = g.db.cursor()
    TotalScore_query = """ 
    SELECT
        BIG.UID,
        BIG.Name,
        BIG.Section,
        SUM(BIG.Score) AS TotalScore
    FROM
    (
    SELECT 
        STD.UID,
        USR.Name,
        SCT.Section,
        QST.Lab,
        QST.Question,
        LB.Name as LabName,
        ASN.Due,
        SMT.Timestamp,
        QST.MaxScore,
        SMT.Score,
        CASE WHEN SMT.Timestamp IS NOT NULL THEN TRUE ELSE FALSE END As TurnIn,
        CASE WHEN ASN.Due <= SMT.Timestamp THEN TRUE ELSE FALSE END AS Late
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
    ) as BIG
    GROUP BY
        BIG.UID, BIG.Section
    """
    cur.execute(TotalScore_query,(CSYID))
    TotalResult = cur.fetchall()
    
    transformed_data = []

    for row in TotalResult:
        UID , Name, Section, TotalScore= row
        transformed_data.append({'UID': UID, 'Name': Name, 'Section': Section, 'Score': TotalScore})
        
    MaxScore_query = """ 
        SELECT
            SUM(QST.MaxScore) as TotalMax 
        FROM
            question QST
        WHERE
            QST.CSYID = %s
        GROUP BY
            QST.CSYID
    """
    cur.execute(MaxScore_query,(CSYID))
    TotalMax = cur.fetchone()[0]
    
    Full_transformed_data = {'TotalMax': TotalMax, 'transformed_data': transformed_data}

    
    return jsonify(Full_transformed_data)