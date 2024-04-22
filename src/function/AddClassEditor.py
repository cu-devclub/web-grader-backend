def AddClassEditor(dbACE,cursor,Email,CSYID):
    try:
        
        insert_user = "INSERT INTO classeditor (Email, CSYID) VALUES (%s, %s)"
        cursor.execute(insert_user, (Email, CSYID))
        dbACE.commit()
        return True
    except Exception as e:
        dbACE.rollback()
        return False