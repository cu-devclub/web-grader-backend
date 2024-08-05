def checkPermSubmitDown(SID, Email, cur):
    # Retrieve UID based on Email from the user table
    query_user = "SELECT UID FROM user WHERE Email = %s"
    cur.execute(query_user, (Email,))
    result_user = cur.fetchone()

    # If no UID found, return False
    if not result_user:
        return False

    UID = result_user[0]

    # Check if UID is associated with the specified SID in the submitted table
    query_submitted = "SELECT 1 FROM submitted WHERE SID = %s AND UID = %s"
    cur.execute(query_submitted, (SID, UID))
    result_submitted = cur.fetchone()

    # Return True if a row is found, else return False
    return result_submitted is not None
