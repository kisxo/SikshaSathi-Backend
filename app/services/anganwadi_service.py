from app.db.models.anganwadi_model import AnganwadiCenters
from app.db.session import SessionDep
from fastapi import HTTPException
from sqlalchemy import select

def get_anganwadi(anganwadi_id: int, session: SessionDep):
    anganwadi_in_db = None
    try:
        anganwadi_in_db = session.get(AnganwadiCenters, anganwadi_id)
    except Exception as e:
        print(e)

    if not anganwadi_in_db:
        raise HTTPException(status_code=404, detail="Anganwadi Center not found!")

    return anganwadi_in_db


def get_anganwadi_by_code(center_code: str, session: SessionDep):
    try:
        statement = select(AnganwadiCenters).where(AnganwadiCenters.center_code == center_code)
        result =  session.execute(statement).mappings().all()
        anganwadi_centers = []
        for row in result:
            anganwadi_centers.append(row.AnganwadiCenters.__dict__)

        return anganwadi_centers
    except Exception as e:
        print(e)


def list_anganwadi(session: SessionDep):
    try:
        statement = select(AnganwadiCenters)
        result =  session.execute(statement).mappings().all()
        anganwadi_centers = []
        for row in result:
            anganwadi_centers.append(row.AnganwadiCenters.__dict__)

        return anganwadi_centers
    except Exception as e:
        print(e)