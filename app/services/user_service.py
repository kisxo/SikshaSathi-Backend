from app.db.models.staff_model import Staff
from app.db.session import SessionDep
from fastapi import HTTPException
from sqlalchemy import select
from app.db.models.user_model import User
from pydantic import EmailStr

def get_user(user_id: int, session: SessionDep):
    user_in_db = None
    try:
        user_in_db = session.get(User, user_id)
    except Exception as e:
        print(e)

    if not user_in_db:
        raise HTTPException(status_code=404, detail="User not found!")

    return user_in_db



def get_user_by_email(email: EmailStr, session: SessionDep):
    try:
        statement = select(User).where(User.user_email == email)
        user_in_db = session.execute(statement).scalar_one_or_none()
        if user_in_db:
            return user_in_db.__dict__
        return None
    except Exception as e:
        print("Error fetching user by email:", e)
        return None


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