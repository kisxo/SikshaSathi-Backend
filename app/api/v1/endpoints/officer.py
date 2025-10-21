from fastapi import APIRouter, HTTPException, Depends
from app.db.session import SessionDep
from app.core.security import authx_security, auth_scheme
from authx import TokenPayload
from app.db.schemas.officer import OfficerCreate, Officer, OfficerPublic
from app.db.models import staff_model
from app.core.security import hash_password
from app.db.models import officer_model
from app.services import officer_service


router = APIRouter()


@router.post("/",
    response_model=OfficerPublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def create_officer(
    input_data: OfficerCreate,
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):

    if payload.user_type != "admin":
        raise HTTPException(status_code=400, detail="Does not have permission to create officer!")

    try:

        validated_officer = Officer(
            **input_data.model_dump(),
            officer_hashed_password = hash_password(input_data.officer_password)
        )

        new_officer = officer_model.Officer(**validated_officer.model_dump())

        session.add(new_officer)
        session.commit()
        session.refresh(new_officer)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Something went wrong!")

    return new_officer


@router.get("/self/",
    response_model=OfficerPublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def create_officer(
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):
    if payload.user_type != "officer":
        raise HTTPException(status_code=400, detail="Not a Officer!")

    result = officer_service.get_officer(officer_id=payload.user_id,session=session)
    return result