from app.db.models.admin_model import Admin
from app.db.session import SessionDep
from fastapi import HTTPException

def get_admin(admin_id: int, session: SessionDep):
    admin_in_db = None
    try:
        admin_in_db = session.get(Admin, admin_id)
    except Exception as e:
        print(e)

    if not admin_in_db:
        raise HTTPException(status_code=404, detail="Admin not found!")

    return admin_in_db