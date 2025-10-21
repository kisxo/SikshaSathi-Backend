from fastapi import APIRouter, HTTPException
from app.core.security import authx_security
from app.db.session import SessionDep
from app.db.models.staff_model import Staff
from app.db.models.officer_model import Officer
from app.db.models.admin_model import Admin
from app.db.schemas.auth import Token, StaffLoginForm, OfficerLoginForm, AdminLoginForm
from app.core.security import verify_password
from sqlalchemy import select
from pathlib import Path

router = APIRouter()

@router.post("/staff/token",
    response_model=Token
)
async def staff_login(
    input_data: StaffLoginForm,
    session: SessionDep
):
    statement = select(Staff).where(Staff.staff_phone== input_data.phone)
    result = session.execute(statement).first()

    if result is None:
        raise HTTPException(status_code=400, detail="Phone and MPIN does not match!")

    # Select the User object
    staff_in_db = result[0]

    if staff_in_db.staff_role.value != "Worker":
        raise HTTPException(status_code=403, detail="Forbidden !")

    if not verify_password(input_data.mpin, staff_in_db.staff_hashed_mpin):
        raise HTTPException(status_code=400, detail="Phone and MPIN does not match!")

    # Used 'user_in_db.user_role.value' to get the actual string value from the Enum
    token_data = {
        'user_type': 'staff',
        'user_id' : staff_in_db.staff_id,
        'user_role' : staff_in_db.staff_role.value,
        'user_center_id': staff_in_db.staff_center_id
    }

    token = authx_security.create_access_token(uid=str(staff_in_db.staff_id), data=token_data)

    return {"access_token": token}


@router.post("/officer/token",
    response_model=Token
)
async def officer_login(
    input_data: OfficerLoginForm,
    session: SessionDep
):
    statement = select(Officer).where(Officer.officer_email== input_data.email)
    result = session.execute(statement).first()

    if result is None:
        raise HTTPException(status_code=400, detail="Email and password does not match!")

    # Select the User object
    officer_in_db = result[0]

    if not verify_password(input_data.password, officer_in_db.officer_hashed_password):
        raise HTTPException(status_code=400, detail="Email and password does not match!")

    # Used 'user_in_db.user_role.value' to get the actual string value from the Enum
    token_data = {
        'user_type': 'officer',
        'user_id' : officer_in_db.officer_id,
        'user_role' : officer_in_db.officer_role.value
    }

    token = authx_security.create_access_token(uid=str(officer_in_db.officer_id), data=token_data)

    return {"access_token": token}

@router.post("/admin/token",
    response_model=Token
)
async def admin_login(
    input_data: AdminLoginForm,
    session: SessionDep
):
    statement = select(Admin).where(Admin.admin_email== input_data.email)
    result = session.execute(statement).first()

    if result is None:
        raise HTTPException(status_code=400, detail="Email and password does not match!")

    # Select the User object
    admin_in_db = result[0]

    if not verify_password(input_data.password, admin_in_db.admin_hashed_password):
        raise HTTPException(status_code=400, detail="Email and password does not match!")

    # Used 'user_in_db.user_role.value' to get the actual string value from the Enum
    token_data = {
        'user_type': 'admin',
        'user_id' : admin_in_db.admin_id,
        'user_role' : 'Admin'
    }

    token = authx_security.create_access_token(uid=str(admin_in_db.admin_id), data=token_data)

    return {"access_token": token}