def GetCSYID(dbCLS,cursor,ClassID,SchoolYear):
    try:
        query = """SELECT CSYID FROM class CLS WHERE CLS.ClassID = %s AND CLS.SchoolYear = %s"""
        cursor.execute(query,(ClassID,SchoolYear))
        # Fetch all rows
        dbCLS = cursor.fetchone()
        return dbCLS[0]
    except Exception as e:
        dbCLS.rollback()
        return False