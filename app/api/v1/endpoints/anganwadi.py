from fastapi import APIRouter, HTTPException, Response, Depends
from app.db.session import SessionDep
from app.core.security import authx_security, auth_scheme
from authx import TokenPayload
from app.db.schemas.anganwadi import AnganwadiCreate, Anganwadi
from app.db.models import anganwadi_model
from app.services import admin_service, officer_service, anganwadi_service

router = APIRouter()

@router.post("/",
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def create_center(
    input_data: AnganwadiCreate,
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):
    if payload.user_type not in ["admin", "officer"]:
        raise HTTPException(status_code=403, detail="Does not have permission to create Anganwadi Center!!")

    if input_data.center_supervisor_id:
        # check if officer exists
        officer_service.get_officer(input_data.center_supervisor_id, session)

    else:
        input_data.center_supervisor_id = None

    center_in_db = anganwadi_service.get_anganwadi_by_code(input_data.center_code, session)
    if center_in_db:
        raise HTTPException(status_code=400, detail="Anganwadi Center already exists!")

    try:

        validated_center = Anganwadi(**input_data.model_dump())

        new_anganwadi_center = anganwadi_model.AnganwadiCenters(**validated_center.model_dump())

        session.add(new_anganwadi_center)
        session.commit()
        session.refresh(new_anganwadi_center)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Something went wrong!")

    return new_anganwadi_center

@router.get("/",
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def list_centers(
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):
    if payload.user_type == "staff":
        center_data = anganwadi_service.get_anganwadi(payload.user_center_id, session)
        return center_data

    result = anganwadi_service.list_anganwadi(session=session)
    return {'data': result}