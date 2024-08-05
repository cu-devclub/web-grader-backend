import json

def checkPermAddDown(ID, Email, cur):
    try:
        # Retrieve UID based on Email from the user table
        query_user = "SELECT UID FROM user WHERE Email = %s"
        cur.execute(query_user, (Email,))
        result_user = cur.fetchone()
        
        # If no UID found, return False
        if not result_user:
            return False
        
        UID = result_user[0]

        # Retrieve LID and CSYID from addfile table for the given ID
        query_addfile = "SELECT LID, CSYID FROM addfile WHERE ID = %s"
        cur.execute(query_addfile, (ID,))
        result_addfile = cur.fetchone()
        
        if not result_addfile:
            return False
        
        LID, CSYID = result_addfile

        # Retrieve CID and GID from lab table for the given LID
        query_lab = "SELECT CID, GID FROM lab WHERE LID = %s"
        cur.execute(query_lab, (LID,))
        result_lab = cur.fetchone()

        if not result_lab:
            return False

        CID_json, GID_json = result_lab

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

    except Exception as e:
        print(f"Error in checkPermAddDown: {e}")
        return False