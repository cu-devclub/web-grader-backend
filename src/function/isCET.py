def isCET(db, cursor, Email, CSYID):
    try:
        query = """
            SELECT 
                id
            FROM 
                classeditor
            WHERE 
                Email = %s AND CSYID = %s 
        """
        cursor.execute(query,(Email, CSYID))
        row = cursor.fetchone()
        return row != None
    except Exception as e:
        db.rollback()
        return False