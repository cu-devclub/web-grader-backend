def CreateSection(dbCST, cursor, CSYID, Section):
    try:
        insert_section = "INSERT INTO section (CSYID, Section) VALUES (%s, %s)"
        cursor.execute(insert_section, (CSYID, Section))
        dbCST.commit()
        return True
    except Exception as e:
        dbCST.rollback()
        print(e)
        return False