from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import Annotated
from app.db.session import SessionDep
from app.services.face_id import verify_face_id
from app.services import student_service, staff_service, staff_attendance_service, student_attendance_service
from app.core.security import authx_security, auth_scheme
from app.db.models import staff_attendance_model, student_attendance_model
from app.db.schemas.attendance import AttendanceModeChoice
from datetime import date
from authx import TokenPayload


router = APIRouter()

@router.post("/students/{student_id}",
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def log_student_attendance(
    student_id: int,
    image_file: Annotated[UploadFile, File()],
    session: SessionDep
):
    result = student_attendance_service.list_attendance_by_student_id_and_date(student_id=student_id, input_date=date.today(), session=session)
    if result:
        raise HTTPException(status_code=400, detail="Attendance already exists!")

    student_in_db = student_service.get_student(student_id, session)
    result = verify_face_id(image_file, student_in_db.student_face_id["face_signature"])

    if not result:
        raise HTTPException(status_code=400, detail="Face does not match!")

    try:
        new_attendance = student_attendance_model.StudentAttendance(
            attendance_student_id=student_in_db.student_id,
            attendance_center_id=student_in_db.student_center_id,
            attendance_date=date.today(),
            attendance_mode=AttendanceModeChoice.online
        )
        student_in_db.student_last_attendance = date.today()

        session.add(new_attendance)
        session.commit()
        session.refresh(new_attendance)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Failed to log attendance!")

    return new_attendance

@router.post("/staffs/{staff_id}",
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def log_staff_attendance(
    staff_id: int,
    image_file: Annotated[UploadFile, File()],
    session: SessionDep
):
    result = staff_attendance_service.list_attendance_by_staff_id_and_date(staff_id=staff_id, input_date=date.today(), session=session)
    if result:
        raise HTTPException(status_code=400, detail="Attendance already exists!")

    staff_in_db = staff_service.get_staff(staff_id, session)
    result = verify_face_id(image_file, staff_in_db.staff_face_id["face_signature"])

    if not result:
        raise HTTPException(status_code=400, detail="Face does not match!")

    try:
        new_attendance = staff_attendance_model.StaffAttendance(
            attendance_staff_id=staff_in_db.staff_id,
            attendance_center_id=staff_in_db.staff_center_id,
            attendance_date= date.today(),
            attendance_mode=AttendanceModeChoice.online
        )
        staff_in_db.staff_last_attendance = date.today()

        session.add(new_attendance)
        session.commit()
        session.refresh(new_attendance)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Failed to log attendance!")

    return new_attendance


@router.get("/staffs/",
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def get_staff_attendance_list(
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):
    if payload.user_type == "staff":
        result = staff_attendance_service.list_attendance_by_center(center_id=payload.user_center_id, session=session)
        return {"data": result}

    result = staff_attendance_service.list_attendance(session=session)
    return {'data': result}



@router.get("/students/",
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)]
)
async def get_student_attendance_list(
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required)
):
    if payload.user_type == "staff":
        result = student_attendance_service.list_attendance_by_center(center_id=payload.user_center_id, session=session)
        return {"data": result}

    result = student_attendance_service.list_attendance(session=session)
    return {'data': result}