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


def list_users(session: SessionDep):
    try:
        statement = select(User)
        result =  session.execute(statement).mappings().all()
        users = []
        for row in result:
            users.append(row.User.__dict__)

        return users
    except Exception as e:
        print(e)