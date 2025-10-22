from fastapi import APIRouter, HTTPException
from app.core.security import authx_security
from app.db.session import SessionDep
from app.db.models.user_model import User
from app.db.schemas.auth import Token, LoginForm
from app.core.security import verify_password
from sqlalchemy import select

router = APIRouter()


@router.post("/token",
    response_model=Token
)
async def login(
    input_data: LoginForm,
    session: SessionDep
):
    statement = select(User).where(User.user_email== input_data.email)
    user = session.execute(statement).scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=400, detail="Email and password does not match!")

    if not verify_password(input_data.password, user.user_hashed_password):
        raise HTTPException(status_code=400, detail="Email and password does not match!")

    # Used 'user_in_db.user_role.value' to get the actual string value from the Enum
    token_data = {
        'user_is_admin': user.user_is_admin,
        'user_id' : user.user_id,
        'user_data' : user.user_data
    }

    token = authx_security.create_access_token(uid=str(user.user_id), data=token_data)

    return {"access_token": token}