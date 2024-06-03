def GetCID(db,cursor,section,CSYID):
    try:
        query = """SELECT CID FROM section SCT WHERE SCT.Section = %s AND SCT.CSYID = %s """
        cursor.execute(query,(section,CSYID))
        # Fetch all rows
        db = cursor.fetchone()
        return db[0]
    except Exception as e:
        db.rollback()
        return False