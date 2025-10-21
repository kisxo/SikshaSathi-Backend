from app.db.database import Base
from sqlalchemy import String, Enum as SqlEnum, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.schemas.officer import OfficerRole

class Beneficiaries(Base):
    __tablename__ = "beneficiaries"

    beneficiary_id: Mapped[int] = mapped_column(primary_key=True)
    beneficiary_full_name: Mapped[str] = mapped_column(String(100))
    beneficiary_address: Mapped[str] = mapped_column(String(300))
    beneficiary_husband_name: Mapped[str] = mapped_column(String(100))
    beneficiary_phone: Mapped[str] = mapped_column(String(10))
    beneficiary_center_id: Mapped[int] = mapped_column(ForeignKey("anganwadi_centers.center_id"))
    officer_created_date: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())