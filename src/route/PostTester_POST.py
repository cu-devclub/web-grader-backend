from flask import request, jsonify

def main():

    # Get form data
    data = request.get_json()
    class_name = data.get('ClassName')
    class_id = data.get('ClassID')
    school_year = data.get('SchoolYear')
    print('name:',class_name)
    print('id:',class_id)
    print('schoolyear:',school_year)
    # Perform any processing with the form data
    # For example, you can save it to a database or perform validations

    # Construct a response
    response = {
        "message": "Data received successfully",
        "Status": True,
        "ClassName": class_name,
        "ClassID": class_id,
        "SchoolYear": school_year
    }
    return jsonify(response)