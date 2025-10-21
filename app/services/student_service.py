from app.db.models.student_model import Student
from app.db.session import SessionDep
from fastapi import HTTPException
from sqlalchemy import select

def get_student(student_id: int, session: SessionDep):
    student_in_db = None
    try:
        student_in_db = session.get(Student, student_id)
    except Exception as e:
        print(e)

    if not student_in_db:
        raise HTTPException(status_code=404, detail="Student not found!")

    return student_in_db

def list_students_by_center(center_id: int, session: SessionDep):
    try:
        statement = select(Student).where(Student.student_center_id == center_id)
        result =  session.execute(statement).mappings().all()
        students = []
        for row in result:
            students.append(row.Student.__dict__)

        return students
    except Exception as e:
        print(e)

def list_students(session: SessionDep):
    try:
        statement = select(Student)
        result =  session.execute(statement).mappings().all()
        students = []
        for row in result:
            students.append(row.Student.__dict__)

        return students
    except Exception as e:
        print(e)