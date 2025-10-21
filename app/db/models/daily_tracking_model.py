from app.db.database import Base
from sqlalchemy import String, ForeignKey, TIMESTAMP, func, JSON, DATE
from sqlalchemy.orm import Mapped, mapped_column
class DailyTracking(Base):
    __tablename__ = "daily_tracking"

    daily_tracking_id: Mapped[int] = mapped_column(primary_key=True)
    daily_tracking_center_id: Mapped[int] = mapped_column(ForeignKey("anganwadi_centers.center_id", ondelete="CASCADE"))
    daily_tracking_date: Mapped[DATE] = mapped_column(DATE)
    daily_tracking_data: Mapped[[JSON]] = mapped_column(JSON())
    daily_tracking_created_date: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())