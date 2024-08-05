def AddUserGrader(db, cursor, UID, Email, Name):
    try:
        insert_user = "INSERT IGNORE INTO user (Email, UID, Name, Role) VALUES (%s, %s, %s, 1)"
        cursor.execute(insert_user, (Email, UID, Name))
        db.commit()
        return True
    except Exception as e:
        print("An error occurred:", e)  
        db.rollback()
        return False