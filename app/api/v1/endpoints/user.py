from fastapi import APIRouter, HTTPException, Depends
from app.core.security import authx_security, auth_scheme
from authx import TokenPayload
from app.db.session import SessionDep
from app.db.schemas.user import User, UserCreate, UserPublic, UsersPublic
from app.core.security import hash_password
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




@router.get("/",
    response_model = UsersPublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def list_users(
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):

    if not payload.user_is_admin:
        raise HTTPException(status_code=400, detail="Does not have permission to get user!")

    users = user_service.list_users(session=session)

    if not users:
        # Return 404 if not found
        raise HTTPException(status_code=404, detail="User not found")

    return {'data': users}



@router.get("/self",
    response_model = UserPublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def get_my_account(
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):

    user = user_service.get_user(user_id=payload.user_id, session=session)

    if not user:
        # Return 404 if not found
        raise HTTPException(status_code=404, detail="User not found")

    return user



@router.get("/{user_id}",
    response_model = UserPublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def get_user(
    user_id: int,
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):

    if not payload.user_admin:
        raise HTTPException(status_code=400, detail="Does not have permission to get user!")

    user = user_service.get_user(user_id=user_id, session=session)

    if not user:
        # Return 404 if not found
        raise HTTPException(status_code=404, detail="User not found")

    return user