def isPF(db, cursor, Email):
    try:
        query = """
            SELECT 
                Role
            FROM 
                user
            WHERE 
                Email = %s
        """
        cursor.execute(query,(Email))
        row = cursor.fetchone()
        return (row != None and row[0] == '2')
    except Exception as e:
        db.rollback()
        return False