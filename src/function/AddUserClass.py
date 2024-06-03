from function.GetCID import GetCID
from function.GetGID import GetGID

def AddUserClass(db, cursor, UID, CSYID, Section, Group):
    GID = None if Group is None else GetGID(db, cursor, Group, CSYID)
    try:
        #adduser
        query_insertUSC = """INSERT INTO student (CID, UID, CSYID, GID) VALUES (%s, %s, %s, %s)"""
        cursor.execute(query_insertUSC, (GetCID(db, cursor, Section, CSYID), UID, CSYID, GID))
        db.commit()    
        return True
    except Exception as e:
        print("An error occurred:", e)   
        db.rollback()
        return False