from http.client import responses

from fastapi import APIRouter, HTTPException
from app.core.security import authx_security
from app.db.schemas.auth import Token
from app.db.session import SessionDep
from app.db.models.staff_model import Staff
from app.db.models.officer_model import Officer
from app.db.models.admin_model import Admin
from app.db.schemas.user import UserBase, User, UserCreate, UserPublic
from app.core.security import verify_password, hash_password
from sqlalchemy import select
from pathlib import Path
from app.db.models import user_model
from app.services import user_service

router = APIRouter()

@router.post("/",
    response_model=UserPublic
)
async def create_user(
    input_data: UserCreate,
    session: SessionDep
):
    user = user_service.get_user_by_email(input_data.user_email, session)
    if user:
        raise HTTPException(status_code=400, detail="Email Already exists!")

    try:

        validated_user = User(
            **input_data.model_dump(),
            user_hashed_password=hash_password(input_data.user_password),
        )

        new_user = user_model.User(**validated_user.model_dump())

        session.add(new_user)
        session.commit()
        session.refresh(new_user)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Something went wrong!")

    return new_user


@router.get("/{user_id}",
    response_model = UserPublic,
    # dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def get_user(
    user_id: int,
    session: SessionDep,
    # payload: TokenPayload = Depends(authx_security.access_token_required)
):
    user = user_service.get_user(user_id=user_id, session=session)

    if not user:
        # Return 404 if not found
        raise HTTPException(status_code=404, detail="User not found")

    return user