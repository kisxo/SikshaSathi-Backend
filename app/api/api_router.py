from fastapi import APIRouter
from app.api.v1.endpoints import auth, user, profile, mail, goal, chat

router = APIRouter()


router.include_router(auth.router, prefix="/v1/auth", tags=["Authentication"])
router.include_router(user.router, prefix="/v1/users", tags=["User"])
router.include_router(profile.router, prefix="/v1/profiles", tags=["Profile"])
router.include_router(mail.router, prefix="/v1/mails", tags=["Mail"])
# router.include_router(ai.router, prefix="/v1/ai", tags=["Ai"])
router.include_router(goal.router, prefix="/v1/goals", tags=["Goal"])
router.include_router(chat.router, prefix="/v1/chat", tags=["Chat"])
# router.include_router(student.router, prefix="/v1/students", tags=["Students"])
# router.include_router(beneficiary.router, prefix="/v1/beneficiaries", tags=["Beneficiaries"])
# router.include_router(anganwadi.router, prefix="/v1/anganwadi", tags=["Anganwadi Centers"])
# router.include_router(ration.router, prefix="/v1/rations", tags=["Anganwadi Centers"])
# router.include_router(attendance.router, prefix="/v1/attendance", tags=["Attendance"])
# router.include_router(daily_tracking.router, prefix="/v1/daily-tracking", tags=["Anganwadi Centers"])
# router.include_router(image.router, prefix="/v1/images", tags=["Images"])
