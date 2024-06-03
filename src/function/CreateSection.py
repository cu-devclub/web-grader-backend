def CreateSection(db, cursor, CSYID, Section):
    try:
        insert_section = "INSERT IGNORE INTO section (CSYID, Section) VALUES (%s, %s)"
        cursor.execute(insert_section, (CSYID, Section))
        db.commit()
        return True
    except Exception as e:
        print("An error occurred:", e)  
        db.rollback()
        return False