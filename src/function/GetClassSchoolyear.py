def GetClassSchoolyear(dbCLS,cursor,CSYID):
    try:
        query = """SELECT ClassID,SchoolYear FROM class CLS WHERE CSYID=%s"""
        cursor.execute(query,(CSYID))
        # Fetch all rows
        data = cursor.fetchall()[0]
        return data
    except Exception as e:
        dbCLS.rollback()
        return False