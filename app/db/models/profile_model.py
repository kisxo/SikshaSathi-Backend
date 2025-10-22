from __future__ import annotations
from typing import List, Optional, Dict, Any
from sqlalchemy import String, Integer, Float, JSON, ForeignKey, TIMESTAMP, func, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    profile_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), unique=True)

    # --- Academic Information ---
    education_level: Mapped[Optional[str]] = mapped_column(String(100))
    institution: Mapped[Optional[str]] = mapped_column(String(150))
    board_or_university: Mapped[Optional[str]] = mapped_column(String(150))
    current_semester: Mapped[Optional[int]] = mapped_column(Integer)
    subjects_enrolled: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    target_exam: Mapped[Optional[str]] = mapped_column(String(100))

    # --- Learning Preferences ---
    learning_style: Mapped[Optional[str]] = mapped_column(String(50))
    preferred_content_type: Mapped[Optional[str]] = mapped_column(String(50))
    language_preference: Mapped[Optional[str]] = mapped_column(String(20), default="English")
    study_time_preference: Mapped[Optional[str]] = mapped_column(String(20))
    session_duration_preference: Mapped[Optional[int]] = mapped_column(Integer, default=45)
    reminder_frequency: Mapped[Optional[str]] = mapped_column(String(20), default="Daily")
    focus_level: Mapped[Optional[str]] = mapped_column(String(20))

    # --- Study Schedule & Motivation ---
    available_hours_per_week: Mapped[Optional[int]] = mapped_column(Integer, default=10)
    study_days: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), server_default=text("ARRAY['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']")
    )
    motivation_level: Mapped[Optional[float]] = mapped_column(Float, default=5.0)
    preferred_breaks: Mapped[Optional[str]] = mapped_column(String(50))
    study_goals: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    # --- Knowledge Profile ---
    strong_subjects: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    weak_subjects: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    previous_scores: Mapped[Optional[Dict[str, int]]] = mapped_column(JSON)
    learning_gaps: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    # --- Career Goals ---
    career_goal: Mapped[Optional[str]] = mapped_column(String(100))
    desired_skills: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    job_preference: Mapped[Optional[str]] = mapped_column(String(100))
    certifications_interest: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    # --- Metadata ---
    profile_created_date: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    profile_updated_date: Mapped[Optional[TIMESTAMP]] = mapped_column(
        TIMESTAMP(timezone=True), onupdate=func.now()
    )

    # --- Relationship ---
    user: Mapped["User"] = relationship(back_populates="profile")