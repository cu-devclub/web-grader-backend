def CreateSection(dbCST, cursor, CSYID, Section):
    try:
        insert_section = "INSERT INTO section (CSYID, Section) VALUES (%s, %s)"
        cursor.execute(insert_section, (CSYID, Section))
        return True
    except Exception as e:
        dbCST.rollback()
        return False