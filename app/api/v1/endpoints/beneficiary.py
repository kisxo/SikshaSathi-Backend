from fastapi import APIRouter, Depends, UploadFile, HTTPException
from app.services.image import save_image
from app.core.security import authx_security, auth_scheme
from app.db.schemas import beneficiary
from app.db.session import SessionDep
from authx import TokenPayload
from app.db.models import beneficiary_model
from app.services import beneficiary_service


router = APIRouter()


@router.post("/",
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def create_beneficiary(
    input_data: beneficiary.BeneficiaryCreate,
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):
    if payload.user_role != "Worker":
        raise HTTPException(status_code=400, detail="Only Anganwadi worker can add a beneficiary!")

    try:
        new_beneficiary = beneficiary_model.Beneficiaries(
            **input_data.model_dump(),
            beneficiary_center_id = payload.user_center_id
        )

        session.add(new_beneficiary)
        session.commit()
        session.refresh(new_beneficiary)
        return new_beneficiary

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Failed adding beneficiary!")

@router.get("/",
    # response_model=student.StudentsPublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def list_beneficiaries(
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):
    if payload.user_type == "staff":
        result = beneficiary_service.list_beneficiaries_by_center(center_id=payload.user_center_id, session=session)
        return {'data': result}

    result = beneficiary_service.list_beneficiaries(session=session)
    return {'data': result}
