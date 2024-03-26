from function.db import get_db

def AddUserClass(UserEmail, ClassID, SchoolYear, Section):
    try:
        conn = get_db()
        cursor = conn.cursor()

        # Execute the SQL query to fetch the IDClass
        query_getclass = """
            SELECT DISTINCT ID
            FROM Class
            WHERE ClassID = %s AND Section = %s AND SchoolYear = %s
        """
        cursor.execute(query_getclass, (ClassID, Section, SchoolYear))
        id_class = cursor.fetchone()

        if id_class:
            # Execute the SQL query to add the user to the class
            query_insertUSC = """
                INSERT INTO userclass (Email, IDClass)
                VALUES (%s, %s)
            """
            cursor.execute(query_insertUSC, (UserEmail, id_class[0]))
            conn.commit()
            return True  # Return True if user added successfully
        else:
            return False  # Return False if class not found

    except Exception as e:
        return False  # Return False if an error occurred
    finally:
        cursor.close()
        conn.close()