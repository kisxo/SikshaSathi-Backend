from pydantic import BaseModel
from datetime import datetime


class EmailSummaryBase(BaseModel):
    user_id: int
    summary: str


class EmailSummaryCreate(EmailSummaryBase):
    pass


class EmailSummaryPublic(EmailSummaryBase):
    id: int
    created_at: datetime


class EmailSummariesPublic(EmailSummaryBase):
    data: list[EmailSummaryPublic]