def GetGID(db, cursor, Group, CSYID):
    try:
        query = """SELECT GID FROM `group` GRP WHERE GRP.Group = %s AND GRP.CSYID = %s """
        cursor.execute(query, (Group, CSYID))
        # Fetch all rows
        db = cursor.fetchone()
        return db[0]
    except Exception as e:
        print(e)
        db.rollback()
        return False