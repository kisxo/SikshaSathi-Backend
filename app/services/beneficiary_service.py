from app.db.models.beneficiary_model import Beneficiaries
from app.db.session import SessionDep
from fastapi import HTTPException
from sqlalchemy import select


def list_beneficiaries_by_center(center_id: int, session: SessionDep):
    try:
        statement = select(Beneficiaries).where(Beneficiaries.beneficiary_center_id == center_id)
        result =  session.execute(statement).mappings().all()
        beneficiaries = []
        for row in result:
            beneficiaries.append(row.Beneficiaries.__dict__)

        return beneficiaries
    except Exception as e:
        print(e)

def list_beneficiaries(session: SessionDep):
    try:
        statement = select(Beneficiaries)
        result =  session.execute(statement).mappings().all()
        beneficiaries = []
        for row in result:
            beneficiaries.append(row.Beneficiaries.__dict__)

        return beneficiaries
    except Exception as e:
        print(e)