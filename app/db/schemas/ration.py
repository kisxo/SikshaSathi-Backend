from pydantic import BaseModel
from pydantic.types import datetime, Json

class RationItem(BaseModel):
    item: str
    quantity: str

class RationBase(BaseModel):
    ration_note: str
    ration_items: list[RationItem]

class RationCreate(RationBase):
    pass

class RationPublic(RationBase):
    ration_id: int
    ration_center_id: int
    ration_created_date: datetime

class RationsPublic(BaseModel):
    data: list[RationPublic]