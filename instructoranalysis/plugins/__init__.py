from requests import get

BLOCKPY_URL = 'https://think.cs.vt.edu/blockpy/'

def blockpy_grade(assignment_id, student_code):
    data = {'assignment_id': assignment_id}
    response = get(BLOCKPY_URL+'load_assignment_give_feedback', data=data)
    result = response.json()
    if result['success']:
        return exec(result['give_feedback'])
    else:
        return ""