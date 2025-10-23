from app.db.session import SessionDep
from fastapi import HTTPException
from sqlalchemy import select
from app.db.models.user_model import User
from pydantic import EmailStr
from app.db.models.goal_model import Goal


def list_user_goals(user_id: int, session: SessionDep):
    try:
        statement = select(Goal).where(Goal.user_id == user_id)
        result =  session.execute(statement).mappings().all()
        goals = []
        for row in result:
            goals.append(row.Goal.__dict__)

        return goals
    except Exception as e:
        print(e)