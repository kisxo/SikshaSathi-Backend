from csv import excel

from fastapi import APIRouter, HTTPException, Response, Depends, Form
from typing import Annotated

from sqlalchemy import except_

from app.db.session import SessionDep
from app.core.security import authx_security, auth_scheme
from authx import TokenPayload
from app.services import staff_service
from app.db.schemas.staff import StaffPublic, StaffCreate, Staff,StaffsPublic
from app.db.models import staff_model
from app.services.image import save_image
from app.services.face_id import generate_face_id
from app.db.schemas.face_id import FaceID
from app.core.security import hash_password
from app.services.anganwadi_service import get_anganwadi


router = APIRouter()


@router.get("/self/",
    response_model=StaffPublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def get_self(
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):
    if payload.user_type != "staff":
        raise HTTPException(status_code=400, detail="Not a staff!")
    result = staff_service.get_staff(staff_id=payload.user_id,session=session)
    return result


@router.get("/",
    response_model=StaffsPublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def list_staffs(
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):
    if payload.user_type == "staff":
        result = staff_service.list_staffs_by_center(payload.user_center_id, session=session)
        return {'data': result}

    result = staff_service.list_staffs(session=session)
    return {'data': result}


@router.get("/{staff_id}",
    response_model = StaffPublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def get_staff(
    staff_id: int,
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):
    # TODO implement RBAC
    result = staff_service.get_staff(staff_id=staff_id,session=session)
    return result


@router.post("/",
    response_model=StaffPublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def create_staff(
    input_data: StaffCreate,
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):

    if payload.user_type == "staff" and input_data.staff_role.value == "Worker":
        raise HTTPException(status_code=400, detail="Does not have permission to create staff!")

    if payload.user_type == "staff":
        input_data.staff_center_id = payload.user_center_id

    # check's if anganwadi center exists
    get_anganwadi(input_data.staff_center_id, session)

    # generates a unique face signature from input image
    face_id: FaceID = generate_face_id(image_group="staffs", image_id=input_data.staff_image)
    try:

        validated_staff = Staff(
            **input_data.model_dump(),
            staff_hashed_mpin=hash_password(input_data.staff_mpin),
            staff_face_id= face_id.model_dump_json(),
        )

        new_staff = staff_model.Staff(**validated_staff.model_dump())

        session.add(new_staff)
        session.commit()
        session.refresh(new_staff)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Something went wrong!")

    return new_staff


@router.patch("/",
    response_model=StaffPublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def update_staff_phone(
    input_phone: int,
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):
    if payload.user_type != "staff":
        raise HTTPException(status_code=400, detail="Something went wrong!")

    try:
        staff_in_db = session.get(staff_model.Staff, payload.user_id)

        staff_in_db.staff_phone = input_phone
        session.commit()
        session.refresh(staff_in_db)
        return staff_in_db
    except Exception as e:
        raise HTTPException(status_code=400, detail="Phone number already exists!")