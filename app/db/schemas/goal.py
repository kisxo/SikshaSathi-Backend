from pydantic import BaseModel, Json
from pydantic.types import date
from typing import Optional

class GoalBase(BaseModel):
    user_id: int
    data: Json

class GoalCreate(GoalBase):
    pass

class GoalGenerationForm(BaseModel):
    exam_name: Optional[str] = None
    target_date: Optional[date] = None