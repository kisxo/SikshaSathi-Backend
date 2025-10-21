from fastapi import APIRouter, HTTPException, Response, Depends, Form
from typing import Annotated
from app.db.session import SessionDep
from app.core.security import authx_security, auth_scheme
from authx import TokenPayload
from app.db.schemas import ration
from app.db.models import ration_model
from app.services import ration_service

router = APIRouter()


@router.post("/",
    response_model= ration.RationPublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def record_ration(
    input_data: ration.RationCreate,
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):
    # return input_data
    if payload.user_role != "Worker":
        raise HTTPException(status_code=400, detail="Only Workers can enter ration details!")

    try:

        new_ration = ration_model.Rations(
            **input_data.model_dump(),
            ration_center_id=payload.user_center_id,
        )

        session.add(new_ration)
        session.commit()
        session.refresh(new_ration)
        return new_ration
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Ration data saving failed!")


@router.get("/",
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def list_rations(
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):
    if payload.user_type == "staff":
        result = ration_service.list_rations_by_center(payload.user_center_id, session=session)
        return {"data": result}

    result = ration_service.list_rations(session=session)
    return {'data': result}
