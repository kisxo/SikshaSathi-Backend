from fastapi import APIRouter, HTTPException, Response, Depends, Form
from typing import Annotated
from app.db.session import SessionDep
from app.core.security import authx_security, auth_scheme
from authx import TokenPayload
from app.db.schemas import student
from app.db.models import student_model
from app.services import staff_service, admin_service, student_service, anganwadi_service
from uuid import uuid4
import datetime
from app.services.face_id import generate_face_id
from app.db.schemas.face_id import FaceID
import base64
from app.services.image import save_image

router = APIRouter()

@router.post("/",
    response_model=student.StudentPublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def create_student(
    input_data: student.StudentCreate,
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):

    if payload.user_type == "staff":
        current_user = staff_service.get_staff(payload.user_id, session)
        input_data.student_center_id = current_user.staff_center_id

    # check's if anganwadi center exists
    anganwadi_service.get_anganwadi(input_data.student_center_id, session)

    # saves image and returns unique image ID

    # generates a unique face signature from input image
    face_id: FaceID = generate_face_id(image_group="students", image_id=input_data.student_image)
    try:

        validated_student = student.Student(
            **input_data.model_dump(),
            student_face_id=face_id.model_dump_json(),
        )

        new_student = student_model.Student(**validated_student.model_dump())

        session.add(new_student)
        session.commit()
        session.refresh(new_student)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Something went wrong!")

    return new_student


@router.get("/",
    response_model=student.StudentsPublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def list_students(
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):
    if payload.user_type == "staff":
        result = student_service.list_students_by_center(center_id=payload.user_center_id, session=session)
        return {'data': result}

    result = student_service.list_students(session=session)
    return {'data': result}


@router.get("/{student_id}",
    response_model=student.StudentPublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def get_student(
    student_id: int,
    session: SessionDep
):
    # TODO Check user permission

    result = student_service.get_student(student_id=student_id, session=session)
    return result


@router.patch("/{student_id}",
    response_model=student.StudentPublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def get_student(
    student_id: int,
    input_data: student.StudentUpdate,
    session: SessionDep
):
    student_in_db = None
    try:
        student_in_db = session.get(student_model.Student, student_id)
    except Exception as e:
        print(e)

    if not student_in_db:
        raise HTTPException(status_code=404, detail="Student not found!")

    try:
        student_in_db.student_full_name = input_data.student_full_name
        student_in_db.student_dob = input_data.student_dob
        student_in_db.student_gender = input_data.student_gender
        student_in_db.student_mother_name = input_data.student_mother_name
        student_in_db.student_father_name = input_data.student_father_name
        student_in_db.student_phone = input_data.student_phone
        student_in_db.student_aadhar = input_data.student_aadhar

        session.commit()
        session.refresh(student_in_db)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Invalid input!")

    return student_in_db