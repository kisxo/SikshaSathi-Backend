from app.db.database import Base
from sqlalchemy import String, ForeignKey, TIMESTAMP, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

class Rations(Base):
    __tablename__ = "rations"

    ration_id: Mapped[int] = mapped_column(primary_key=True)
    ration_center_id: Mapped[int] = mapped_column(ForeignKey("anganwadi_centers.center_id", ondelete="CASCADE"))
    ration_note: Mapped[str] = mapped_column(String())
    ration_items: Mapped[[JSON]] = mapped_column(JSON())
    ration_created_date: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())