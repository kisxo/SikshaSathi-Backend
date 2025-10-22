from app.db.database import Base
from sqlalchemy import String, TIMESTAMP, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    user_full_name: Mapped[str] = mapped_column(String(100))
    user_email: Mapped[str] = mapped_column(String(250), unique=True)
    user_phone: Mapped[str] = mapped_column(String(10))
    user_hashed_password: Mapped[str] = mapped_column(String())
    user_is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    user_data: Mapped[bool] = mapped_column(Boolean, default=False)
    user_created_date: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())