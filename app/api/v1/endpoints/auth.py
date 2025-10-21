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

router = APIRouter()

@router.post("/users",
    response_model=UserPublic
)
async def create_users(
    input_data: UserCreate,
    session: SessionDep
):
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