from app.db.models.staff_model import Staff
from app.db.session import SessionDep
from fastapi import HTTPException
from sqlalchemy import select

def get_staff(staff_id: int, session: SessionDep):
    staff_in_db = None
    try:
        staff_in_db = session.get(Staff, staff_id)
    except Exception as e:
        print(e)

    if not staff_in_db:
        raise HTTPException(status_code=404, detail="Staff not found!")

    return staff_in_db


def list_staffs(session: SessionDep):
    try:
        statement = select(Staff)
        result =  session.execute(statement).mappings().all()
        staffs = []
        for row in result:
            staffs.append(row.Staff.__dict__)

        return staffs
    except Exception as e:
        print(e)

def list_staffs_by_center(center_id: int, session: SessionDep):
    try:
        statement = select(Staff).where(Staff.staff_center_id == center_id)
        result =  session.execute(statement).mappings().all()
        staffs = []
        for row in result:
            staffs.append(row.Staff.__dict__)

        return staffs
    except Exception as e:
        print(e)