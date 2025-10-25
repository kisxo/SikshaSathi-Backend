from app.db.session import SessionDep
from fastapi import HTTPException
from sqlalchemy import select
from app.db.models.user_model import User
from pydantic import EmailStr
from app.db.models.resources_model import Resource


def list_user_resources(user_id: int, session: SessionDep):
    try:
        statement = select(Resource).where(Resource.user_id == user_id)
        result =  session.execute(statement).mappings().all()
        resources = []
        for row in result:
            resources.append(row.Resource.__dict__)

        return resources
    except Exception as e:
        print(e)
