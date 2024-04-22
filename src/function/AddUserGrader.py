def AddUserGrader(dbAUG, cursor, UID, Email, Name):
    try:
        insert_user = "INSERT INTO user (Email, UID, Name) VALUES (%s, %s, %s)"
        cursor.execute(insert_user, (Email, UID, Name))
        dbAUG.commit()
        return True
    except Exception as e:
        dbAUG.rollback()
        return False