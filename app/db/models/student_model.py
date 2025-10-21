from app.db.database import Base
from sqlalchemy import String, Enum as SqlEnum, DATE, TIMESTAMP, ForeignKey, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.schemas.student import StudentGender
from typing import Optional

class Student(Base):
    __tablename__ = "students"

    student_id: Mapped[int] = mapped_column(primary_key=True)
    student_full_name: Mapped[str] = mapped_column(String(100))
    student_dob: Mapped[DATE] = mapped_column(DATE)
    student_last_attendance: Mapped[Optional[DATE]] = mapped_column(DATE)
    student_gender: Mapped[SqlEnum] = mapped_column(SqlEnum(StudentGender))
    student_mother_name: Mapped[str] = mapped_column(String(100))
    student_father_name: Mapped[str] = mapped_column(String(100))
    student_phone: Mapped[str] = mapped_column(String(10))
    student_aadhar: Mapped[str] = mapped_column(String(12), unique=True)
    student_image: Mapped[str] = mapped_column(String())
    student_face_id: Mapped[[JSON]] = mapped_column(JSON())
    student_center_id: Mapped[int] = mapped_column(ForeignKey("anganwadi_centers.center_id"))
    student_created_date: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())