from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from pydantic.types import datetime


# -------------------------------
# Base Schema
# -------------------------------
class ProfileBase(BaseModel):

    # --- Academic Information ---
    education_level: Optional[str] = None
    institution: Optional[str] = None
    board_or_university: Optional[str] = None
    current_semester: Optional[int] = None
    subjects_enrolled: Optional[List[str]] = None
    target_exam: Optional[str] = None

    # --- Learning Preferences ---
    learning_style: Optional[str] = None
    preferred_content_type: Optional[str] = None
    language_preference: Optional[str] = "English"
    study_time_preference: Optional[str] = None
    session_duration_preference: Optional[int] = 45
    reminder_frequency: Optional[str] = "Daily"
    focus_level: Optional[str] = None

    # --- Study Schedule & Motivation ---
    available_hours_per_week: Optional[int] = 10
    study_days: Optional[List[str]] = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    motivation_level: Optional[float] = 5.0
    preferred_breaks: Optional[str] = None
    study_goals: Optional[Dict[str, Any]] = None

    # --- Knowledge Profile ---
    strong_subjects: Optional[List[str]] = None
    weak_subjects: Optional[List[str]] = None
    previous_scores: Optional[Dict[str, int]] = None
    learning_gaps: Optional[Dict[str, Any]] = None

    # --- Career Goals ---
    career_goal: Optional[str] = None
    desired_skills: Optional[List[str]] = None
    job_preference: Optional[str] = None
    certifications_interest: Optional[List[str]] = None


# -------------------------------
# Create Schema
# -------------------------------
class ProfileCreate(ProfileBase):
    user_id: int


# -------------------------------
# Update Schema
# -------------------------------
class ProfileUpdate(ProfileBase):
    pass


# -------------------------------
# Response Schema
# -------------------------------
class ProfilePublic(ProfileBase):
    profile_id: int
    user_id: int
    profile_created_date: Optional[datetime] = None
    profile_updated_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProfilesPublic(BaseModel):
    data: list[ProfilePublic]