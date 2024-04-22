def GetCID(dbSec,cursor,section,CSYID):
    try:
        query = """SELECT CID FROM section SCT WHERE SCT.Section = %s AND SCT.CSYID = %s """
        cursor.execute(query,(section,CSYID))
        # Fetch all rows
        dbSec = cursor.fetchone()
        return dbSec[0]
    except Exception as e:
        dbSec.rollback()
        return False