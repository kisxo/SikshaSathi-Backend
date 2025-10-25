from __future__ import annotations
from sqlalchemy import String, Text, Date, ForeignKey, Enum, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from sqlalchemy import TIMESTAMP, func, JSON


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    data: Mapped[JSON] = mapped_column(JSON, nullable=False)
    resource_type: Mapped[str] = mapped_column(String, nullable=False)
    created_date: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())