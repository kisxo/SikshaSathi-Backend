from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EmailSummaryBase(BaseModel):
    user_id: int
    message_id: str
    summary: str


class EmailSummaryCreate(EmailSummaryBase):
    pass

class EmailSummary(EmailSummaryBase):
    pass

class EmailSummaryPublic(EmailSummaryBase):
    id: int
    created_at: datetime


class EmailSummariesPublic(BaseModel):
    data: Optional[list[EmailSummaryPublic]]