from app.db.database import Base
from sqlalchemy import String, ForeignKey, TIMESTAMP, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

class AnganwadiCenters(Base):
    __tablename__ = "anganwadi_centers"

    center_id: Mapped[int] = mapped_column(primary_key=True)
    center_code: Mapped[str] = mapped_column(String(100), unique=True)
    center_name: Mapped[str] = mapped_column(String(100))
    center_address: Mapped[str] = mapped_column(String(500))
    center_supervisor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("officers.officer_id"))
    center_ration_id: Mapped[Optional[int]] = mapped_column(ForeignKey("rations.ration_id"))
    center_created_date: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())