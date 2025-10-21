from app.db.models.officer_model import Officer
from app.db.session import SessionDep
from fastapi import HTTPException

def get_officer(officer_id: int, session: SessionDep):
    officer_in_db = None
    try:
        officer_in_db = session.get(Officer, officer_id)
    except Exception as e:
        print(e)

    if not officer_in_db:
        raise HTTPException(status_code=404, detail="Officer not found!")

    return officer_in_db