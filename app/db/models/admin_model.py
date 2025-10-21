from app.db.database import Base
from sqlalchemy import String, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column

class Admin(Base):
    __tablename__ = "admins"

    admin_id: Mapped[int] = mapped_column(primary_key=True)
    admin_full_name: Mapped[str] = mapped_column(String(100))
    admin_phone: Mapped[str] = mapped_column(String(10), unique=True)
    admin_email: Mapped[str] = mapped_column(String(250), unique=True)
    admin_hashed_password: Mapped[str] = mapped_column(String())
    admin_created_date: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())