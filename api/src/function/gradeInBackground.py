import json
import function.grader as grader
from function.db import get_puredb


def gradeInBackground(Source, addfiles, filepath, QID, MaxScore, UID, LID, upload_time, CSYID, OriginalFileName, Qinfo):
    conn = get_puredb()
    cursor = conn.cursor()
    if Qinfo is None:
        Qinfo = grader.QinfoGenerate(Source, addfile=addfiles)
        Qinfo_query = "UPDATE `question` SET `Qinfo`=%s WHERE `QID`=%s"
        cursor.execute(Qinfo_query, (json.dumps(Qinfo), QID))
        conn.commit()

    err, data = grader.grade(Source, filepath, addfile=addfiles, validate=False, check_keyword="ok", timeout=2, Qinfo=Qinfo)
    if err:
        data = [[0, 1]]
    
    s, m = 0, 0

    if len(data) == 1:
        s += float(data[0][0])  # Ensure data is converted to float
        m += float(data[0][1])  # Ensure data is converted to float
    else:
        for j in range(len(data)):
            s += float(data[j][0])  # Ensure data is converted to float
            m += float(data[j][1])  # Ensure data is converted to float

    # Check if m is zero to avoid division by zero
    if m == 0:
        Score = 0
    else:
        Score = float("{:.2f}".format((s / m) * float(MaxScore)))  # Ensure MaxScore is converted to float

    # Define the insert or update query
    upsert_query = """
        INSERT INTO submitted (UID, LID, QID, SummitedFile, Score, Timestamp, CSYID, OriginalName)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            SummitedFile = VALUES(SummitedFile),
            Score = VALUES(Score),
            Timestamp = VALUES(Timestamp),
            OriginalName = VALUES(OriginalName)
    """

    # Execute the query with the provided values
    cursor.execute(upsert_query, (UID, LID, QID, filepath, Score, upload_time, CSYID, OriginalFileName))
    conn.commit()
    conn.close()
    return