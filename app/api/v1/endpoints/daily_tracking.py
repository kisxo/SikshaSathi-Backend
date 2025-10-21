from fastapi import APIRouter, Depends, HTTPException
from app.core.security import authx_security, auth_scheme
from app.db.schemas import beneficiary
from app.db.session import SessionDep
from authx import TokenPayload
from app.db.models import daily_tracking_model
from app.db.schemas.daily_tracking import DailyTrackingCreate
from app.services import daily_tracking_service
from datetime import date


router = APIRouter()


@router.post("/",
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def create_daily_tracking(
    input_data: DailyTrackingCreate,
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):
    if payload.user_role != "Worker":
        raise HTTPException(status_code=400, detail="Only Anganwadi worker can add a beneficiary!")

    try:
        new_daily_tracking = daily_tracking_model.DailyTracking(
            **input_data.model_dump(),
            daily_tracking_center_id = payload.user_center_id,
            daily_tracking_date=date.today()
        )

        session.add(new_daily_tracking)
        session.commit()
        session.refresh(new_daily_tracking)
        return new_daily_tracking

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Failed adding Daily Tracking!")

@router.get("/",
    # response_model=student.StudentsPublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def list_daily_tracking(
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):
    if payload.user_type == "staff":
        result = daily_tracking_service.list_daily_tracking_by_center(center_id=payload.user_center_id, session=session)
        return {'data': result}

    result = daily_tracking_service.list_daily_tracking(session=session)
    return {'data': result}
