from app.db.models.student_attendance_model import StudentAttendance
from app.db.models.student_model import Student
from app.db.session import SessionDep
from fastapi import HTTPException
from sqlalchemy import select, join, text
from datetime import date
from app.db.database import engine

def list_attendance(session: SessionDep):
    try:
        statement = text("""
        SELECT 
            attendance_id, 
            attendance_date, 
            student_id, 
            student_full_name,
            attendance_center_id 
        FROM 
            student_attendance 
        JOIN 
            students 
        ON 
            attendance_student_id = student_id;
        """)
        results = session.execute(statement).mappings()

        attendances = []
        for row in  results:
            attendances.append(row)

        return attendances

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Failed to load student attendance list!")

def list_attendance_by_center(center_id: int, session: SessionDep):
    try:
        statement = text("""
        SELECT 
            attendance_id, 
            attendance_date, 
            student_id, 
            student_full_name, 
            attendance_center_id 
        FROM 
            student_attendance 
        JOIN 
            students 
        ON 
            attendance_student_id = student_id 
        where 
            attendance_center_id = :center_id;
        """)

        results = session.execute(statement, {"center_id": center_id}).mappings()

        attendances = []
        for row in  results:
            attendances.append(row)

        return attendances

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Failed to load student attendance list!")


def list_attendance_by_student_id_and_date(student_id: int, input_date: date, session: SessionDep):
    try:
        statement = select(StudentAttendance).where(StudentAttendance.attendance_student_id == student_id, StudentAttendance.attendance_date == input_date)
        result =  session.execute(statement).mappings().all()
        attendances = []
        for row in result:
            attendances.append(row.StudentAttendance.__dict__)

        return attendances
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Failed to load student attendance list!")