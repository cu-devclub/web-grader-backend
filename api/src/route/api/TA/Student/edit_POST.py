from flask import request, jsonify, g

from function.db import get_db
from function.isCET import isCET

from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    try:
        Email = get_jwt_identity()['email']
        conn = get_db()
        cur = conn.cursor()
        Data = request.get_json()
        UID = Data.get("SID")
        CSYID = Data.get("CSYID")
        Name = Data.get("Name")
        Section = Data.get("Section")
        Group = Data.get("Group")

        cur.execute("SELECT useGroup FROM class WHERE CSYID=%s", (CSYID))
        UGF = cur.fetchone()
        if(len(UGF) == 0):
            return jsonify({
                'success': False,
                'msg': "Class not found.",
                'data': {}
            })
        
        useGroup = UGF[0]

        if(not isCET(g.db, g.db.cursor(), Email, CSYID)):
            return jsonify({
                'success': False,
                'msg': "You don't have permission",
                'data': {}
            }), 200

        cur.execute("SELECT UID FROM student WHERE UID=%s AND CSYID=%s", (UID, CSYID))
        if(len(cur.fetchall()) == 0):
            return jsonify({
                'success': False,
                'msg': "Student not found.",
                'data': {}
            })
        
        
        isGroup = bool(useGroup)
        GID = None
        if Group not in ['', '-'] and isGroup:
            cur.execute("SELECT GID FROM `group` WHERE CSYID=%s AND `Group`=%s", (CSYID, Group))
            group_data = cur.fetchone()
            if group_data:
                GID = group_data[0]
            else:
                cur.execute("INSERT INTO `group` (CSYID, `Group`) VALUES (%s, %s)", (CSYID, Group))
                GID = cur.lastrowid

        cur.execute("SELECT CID FROM section WHERE CSYID=%s AND Section=%s", (CSYID, Section))
        section_data = cur.fetchone()
        if section_data:
            CID = section_data[0]  # Access by index
        else:
            cur.execute("INSERT INTO section (CSYID, Section) VALUES (%s, %s)", (CSYID, Section))
            CID = cur.lastrowid

        cur.execute("UPDATE student SET CID=%s, GID=%s WHERE UID=%s AND CSYID=%s", (CID, GID, UID, CSYID))

        cur.execute("UPDATE user SET Name=%s WHERE Email=%s", (Name, UID + f"@{'student.' if UID.isnumeric() else ''}chula.ac.th"))
        conn.commit()

        return jsonify({
            'success': True,
            'msg': "Student edited successfully.",
            'data': {}
        })

    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'msg': "There is problem on server side. please contact admin.",
            'data': {
                'Error': str(e)
            }
        })