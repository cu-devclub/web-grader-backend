def isSTD(db, cursor, Email, CSYID):
    try:
        query = """
            SELECT 
                ID
            FROM 
                student
            WHERE 
                UID = %s AND CSYID = %s 
        """
        cursor.execute(query,(Email.split("@")[0], CSYID))
        row = cursor.fetchone()
        return row != None
    except Exception as e:
        db.rollback()
        return False