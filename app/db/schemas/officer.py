import enum
from pydantic import BaseModel, EmailStr, Field
from pydantic.types import datetime

class OfficerRole(enum.Enum):
    supervisor = "Supervisor"
    cdpo = "CDPO"
    dpo = "DPO"
    def __str__(self) -> str:
        return self.value

class OfficerBase(BaseModel):
    officer_full_name: str = Field(max_length=100)
    officer_phone: str = Field(min_length=10, max_length=10)
    officer_email: str = Field(max_length=250)
    officer_aadhar: str = Field(min_length=12, max_length=12)
    officer_role: OfficerRole

class OfficerPublic(OfficerBase):
    officer_id: int
    officer_created_date: datetime

class OfficersPublic(BaseModel):
    data: list[OfficerPublic]

class OfficerCreate(OfficerBase):
    officer_password: str

class Officer(OfficerBase):
    officer_hashed_password: str