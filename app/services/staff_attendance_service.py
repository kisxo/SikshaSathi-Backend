from app.db.models.staff_attendance_model import StaffAttendance
from app.db.session import SessionDep
from fastapi import HTTPException
from sqlalchemy import select, text
from datetime import date


def list_attendance(session: SessionDep):
    try:

        statement = text("""
        SELECT 
            attendance_id, 
            attendance_date, 
            staff_id, 
            staff_full_name,
            attendance_center_id
        FROM 
            staff_attendance
        JOIN 
            staffs
        ON
            attendance_staff_id = staff_id;
        """)
        results = session.execute(statement).mappings()

        attendances = []
        for row in  results:
            attendances.append(row)

        return attendances

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Failed to load staff attendance list!")


def list_attendance_by_center(center_id: int, session: SessionDep):
    try:
        statement = text("""
        SELECT 
            attendance_id, 
            attendance_date, 
            staff_id, 
            staff_full_name, 
            attendance_center_id 
        FROM 
            staff_attendance 
        JOIN 
            staffs 
        ON 
            attendance_staff_id = staff_id 
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
        raise HTTPException(status_code=400, detail="Failed to load staff attendance list!")


def list_attendance_by_staff_id_and_date(staff_id: int, input_date: date, session: SessionDep):
    try:
        statement = select(StaffAttendance).where(StaffAttendance.attendance_staff_id == staff_id, StaffAttendance.attendance_date == input_date)
        result =  session.execute(statement).mappings().all()
        print(result)
        attendances = []
        for row in result:
            attendances.append(row.StaffAttendance.__dict__)

        return attendances
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Failed to load staff attendance list!")