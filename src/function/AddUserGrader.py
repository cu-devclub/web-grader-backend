from function.db import get_db

def AddUserGrader(SID, Email, Name):
    try:
        # Connect to database
        db = get_db()
        cursor = db.cursor()

        # Execute INSERT query
        insert_user = "INSERT INTO user (EmailName, Email, Name) VALUES (%s, %s, %s)"
        cursor.execute(insert_user, (SID, Email, Name))

        # Commit the transaction
        db.commit()

        # Close cursor and database connection
        cursor.close()
        db.close()

        # Return success response
        return True
    except Exception as e:
        # Rollback the transaction in case of an error
        db.rollback()
        # Close cursor and database connection
        cursor.close()
        db.close()
        # Return error response
        return False