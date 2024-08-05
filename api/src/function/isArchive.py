def isArchive(conn, cursor, CSYID):

    query = "SELECT `Archive` FROM class WHERE CSYID = %s"
    cursor.execute(query, (CSYID,))
    result = cursor.fetchone()
    if result is None or result[0] is None:
        return False
    return bool(result[0])