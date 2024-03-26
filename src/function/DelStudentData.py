from function.db import get_db
import mysql.connector


#นักเรียนลด/ถอน => 1.ลบคะแนน SMT 2.ลบชั้นเรียน USC
#result = delete_student_data(student_id)
#if result:
#    print("Data deleted successfully!")
#else:
#    print("Failed to delete data.")
def delete_student_data(StudentID):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Begin transaction
        conn.start_transaction()
        
        # SQL query to delete data from submitted table
        delete_query_1 = """
            DELETE SMT
            FROM submitted SMT
            INNER JOIN userclass USC ON SMT.StudentID = LEFT(USC.Email, 10)
            WHERE SMT.studentID = %s
        """
        cursor.execute(delete_query_1, (StudentID,))
        
        # SQL query to delete data from userclass table
        delete_query_2 = """
            DELETE USC
            FROM userclass USC
            INNER JOIN submitted SMT ON SMT.StudentID = LEFT(USC.Email, 10)
            WHERE SMT.studentID = %s
        """
        cursor.execute(delete_query_2, (StudentID,))
        
        # Commit the transaction
        conn.commit()
        
        return True  # Return True if deletion is successful
    
    except mysql.connector.Error as error:
        # Rollback the transaction in case of an error
        conn.rollback()
        print("An error occurred while deleting data:", error)
        return False  # Return False if deletion fails
    
    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()