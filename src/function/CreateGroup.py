def CreateGroup(db, cursor, CSYID, Group):
    try:
        insert_section = "INSERT IGNORE INTO `group` (CSYID, `Group`) VALUES (%s, %s)"
        cursor.execute(insert_section, (CSYID, Group))
        db.commit()
        return True
    except Exception as e:
        print("An error occurred:", e)  
        db.rollback()
        return False