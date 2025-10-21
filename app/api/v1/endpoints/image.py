from fastapi import APIRouter, Depends, UploadFile
from app.services.image import save_image
from app.core.security import authx_security, auth_scheme
router = APIRouter()


@router.post("/students/",
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def save_student_image(
    image_file: UploadFile
):
    image_id = await save_image(image_file, "students")
    return image_id

@router.post("/staffs/",
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def save_staff_image(
    image_file: UploadFile
):
    image_id = await save_image(image_file, "staffs")
    return image_id