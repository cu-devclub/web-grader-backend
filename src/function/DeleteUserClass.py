from flask import jsonify

def DeleteUserClass(conn,cursor,Email,class_id,school_year):
    try:
        delete_query = """
            DELETE SMT
            FROM submitted SMT
            INNER JOIN userclass USC on SMT.StudentID = LEFT(USC.Email, LOCATE('@', USC.Email) - 1)
            WHERE SMT.StudentID = %s
                AND SMT.ClassID = %s
                AND SMT.SchoolYear = %s
        """
        cursor.execute(delete_query, (Email, class_id, school_year))
        conn.commit()
        return jsonify({"message": "Rows deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500