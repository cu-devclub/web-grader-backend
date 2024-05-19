def AddUserGrader(dbAUG, cursor, UID, Email, Name):
    try:
        insert_user = "INSERT INTO user (Email, UID, Name, Role) VALUES (%s, %s, %s, 1)"
        cursor.execute(insert_user, (Email, UID, Name))
        dbAUG.commit()
        return True
    except Exception as e:
        dbAUG.rollback()
        return False