from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

class GoogleAccount(Base):
    __tablename__ = "google_accounts"

    google_account_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    google_email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    access_token: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String, nullable=False)
    token_expiry: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationship to User
    user: Mapped["User"] = relationship("User", back_populates="google_account")
