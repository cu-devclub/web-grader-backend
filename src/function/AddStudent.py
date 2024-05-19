from function.GetCID import GetCID

def AddStudent(dbAST, cursor, UID, section, CSYID):
    CID = GetCID(dbAST, cursor, section, CSYID)
    try:
        insert_user = "INSERT INTO student (CID, UID, CSYID) VALUES (%s, %s, %s)"
        cursor.execute(insert_user, (CID, UID, CSYID))
        dbAST.commit()
        return True
    except Exception as e:
        dbAST.rollback()
        return False