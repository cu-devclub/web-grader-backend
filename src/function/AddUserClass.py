from function.GetCID import GetCID

def AddUserClass(dbAUC, cursor, UID, CSYID, Section):
    try:
        #adduser
        query_insertUSC = """INSERT INTO student (CID, UID, CSYID) VALUES (%s, %s, %s)"""
        cursor.execute(query_insertUSC, ( GetCID(dbAUC, cursor, Section, CSYID), UID, CSYID))
        dbAUC.commit()    
        return True
    except Exception as e:
        dbAUC.rollback()
        print("An error occurred:", e)   
        return False