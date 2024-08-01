import pytz
import datetime

def isLock(conn, cursor, LID):
    # Define the time zone for GMT+7
    tz = pytz.timezone('Asia/Bangkok')
    
    # Get the current time in GMT+7
    current_time = datetime.datetime.now(tz)
    
    # Query to get the Lock time from the database for the given LID
    query = "SELECT `Lock` FROM lab WHERE LID = %s"
    cursor.execute(query, (LID,))
    result = cursor.fetchone()
    
    # If the Lock column is NULL, return False
    if result is None or result[0] is None:
        return False
    
    # Get the Lock time from the result and make it timezone-aware
    lock_time = result[0]
    if lock_time.tzinfo is None:
        lock_time = tz.localize(lock_time)
    
    # Compare current time with the Lock time
    if current_time > lock_time:
        return True
    else:
        return False