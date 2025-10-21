from app.db.database import Base
from sqlalchemy import String, Enum as SqlEnum, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.schemas.officer import OfficerRole

class Officer(Base):
    __tablename__ = "officers"

    officer_id: Mapped[int] = mapped_column(primary_key=True)
    officer_full_name: Mapped[str] = mapped_column(String(100))
    officer_phone: Mapped[str] = mapped_column(String(10), unique=True)
    officer_email: Mapped[str] = mapped_column(String(250), unique=True)
    officer_aadhar: Mapped[str] = mapped_column(String(12), unique=True)
    officer_hashed_password: Mapped[str] = mapped_column(String())
    officer_role: Mapped[SqlEnum] = mapped_column(SqlEnum(OfficerRole))
    officer_created_date: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())