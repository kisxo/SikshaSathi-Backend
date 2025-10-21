from fastapi import APIRouter
from app.api.v1.endpoints import auth, student, anganwadi, attendance, staff, image, officer, ration, beneficiary, daily_tracking

router = APIRouter()

router.include_router(auth.router, prefix="/v1/auth", tags=["Authentication"])
router.include_router(officer.router, prefix="/v1/officers", tags=["Officers"])
router.include_router(staff.router, prefix="/v1/staffs", tags=["Staffs"])
router.include_router(student.router, prefix="/v1/students", tags=["Students"])
router.include_router(beneficiary.router, prefix="/v1/beneficiaries", tags=["Beneficiaries"])
router.include_router(anganwadi.router, prefix="/v1/anganwadi", tags=["Anganwadi Centers"])
router.include_router(ration.router, prefix="/v1/rations", tags=["Anganwadi Centers"])
router.include_router(attendance.router, prefix="/v1/attendance", tags=["Attendance"])
router.include_router(daily_tracking.router, prefix="/v1/daily-tracking", tags=["Anganwadi Centers"])
router.include_router(image.router, prefix="/v1/images", tags=["Images"])
