from function.db import get_db

def AddUserGrader(dbAUG, cursor, SID, Email, Name):
    try:

        # Execute INSERT query
        insert_user = "INSERT INTO user (EmailName, Email, Name) VALUES (%s, %s, %s)"
        cursor.execute(insert_user, (SID, Email, Name))

        # Commit the transaction
        dbAUG.commit()

        # Close cursor and database connection
        cursor.close()
        dbAUG.close()

        # Return success response
        return True
    except Exception as e:
        # Rollback the transaction in case of an error
        dbAUG.rollback()
        # Close cursor and database connection
        cursor.close()
        dbAUG.close()
        # Return error response
        return False