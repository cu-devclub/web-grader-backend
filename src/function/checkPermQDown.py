import json

def checkPermQDown(QID, Email, level, cur):
    if level == 0:
        # Retrieve UID based on Email from the user table
        query_user = "SELECT UID FROM user WHERE Email = %s"
        cur.execute(query_user, (Email,))
        result_user = cur.fetchone()
        
        # If no UID found, return False
        if not result_user:
            return False
        
        UID = result_user[0]
        
        # Retrieve LID, CID, GID, and CSYID from question and lab tables
        query_question = """
            SELECT q.LID, l.CID, l.GID, q.CSYID
            FROM question q
            JOIN lab l ON q.LID = l.LID
            WHERE q.QID = %s
        """
        cur.execute(query_question, (QID,))
        result_question = cur.fetchone()
        
        if not result_question:
            return False
        
        LID, CID_json, GID_json, CSYID = result_question
        
        # Convert CID and GID from JSON to lists
        CID_list = json.loads(CID_json) if CID_json else []
        GID_list = json.loads(GID_json) if GID_json else []
        
        # Check if the student's CID or GID matches
        query_student = "SELECT CID, GID FROM student WHERE UID = %s AND CSYID = %s"
        cur.execute(query_student, (UID, CSYID))
        result_student = cur.fetchone()
        
        if result_student:
            student_CID, student_GID = result_student

            if student_CID in CID_list or (student_GID and student_GID in GID_list):
                return True

        # Check if Email is in classeditor with the same CSYID
        query_classeditor = "SELECT 1 FROM classeditor WHERE Email = %s AND CSYID = %s"
        cur.execute(query_classeditor, (Email, CSYID))
        result_classeditor = cur.fetchone()
        
        return result_classeditor is not None
        
    elif level == 1:
        # Retrieve CSYID from question table
        query_question = "SELECT CSYID FROM question WHERE QID = %s"
        cur.execute(query_question, (QID,))
        result_question = cur.fetchone()
        
        if not result_question:
            return False
        
        CSYID = result_question[0]
        # Check if Email is in classeditor with the same CSYID
        query_classeditor = "SELECT 1 FROM classeditor WHERE Email = %s AND CSYID = %s"
        cur.execute(query_classeditor, (Email, CSYID))
        result_classeditor = cur.fetchone()
        return result_classeditor is not None
    
    return False
