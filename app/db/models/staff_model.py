from app.db.database import Base
from sqlalchemy import String, Enum as SqlEnum, TIMESTAMP, func, ForeignKey, JSON, Boolean, DATE
from sqlalchemy.orm import Mapped, mapped_column
from app.db.schemas.staff import StaffRole
from typing import Optional

class Staff(Base):
    __tablename__ = "staffs"

    staff_id: Mapped[int] = mapped_column(primary_key=True)
    staff_full_name: Mapped[str] = mapped_column(String(100))
    staff_phone: Mapped[str] = mapped_column(String(10), unique=True)
    staff_last_attendance: Mapped[Optional[DATE]] = mapped_column(DATE)
    staff_aadhar: Mapped[str] = mapped_column(String(12), unique=True)
    staff_hashed_mpin: Mapped[str] = mapped_column(String())
    staff_role: Mapped[SqlEnum] = mapped_column(SqlEnum(StaffRole))
    staff_center_id: Mapped[int] = mapped_column(ForeignKey("anganwadi_centers.center_id"))
    staff_image: Mapped[str] = mapped_column(String())
    staff_face_id: Mapped[[JSON]] = mapped_column(JSON())
    staff_created_date: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())