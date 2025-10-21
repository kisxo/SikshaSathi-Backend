from app.db.models.ration_model import Rations
from app.db.session import SessionDep
from fastapi import HTTPException
from sqlalchemy import select


def list_rations(session: SessionDep):
    try:
        statement = select(Rations)
        result =  session.execute(statement).mappings().all()
        rations = []
        for row in result:
            rations.append(row.Rations.__dict__)

        return result
    except Exception as e:
        print(e)

def list_rations_by_center(center_id: int, session: SessionDep):
    try:
        statement = select(Rations).where(Rations.ration_center_id == center_id)
        result =  session.execute(statement).mappings().all()
        rations = []
        for row in result:
            rations.append(row.Rations.__dict__)

        return result
    except Exception as e:
        print(e)