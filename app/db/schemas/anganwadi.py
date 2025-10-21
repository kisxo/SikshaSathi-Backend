from symtable import Class
from typing import Optional

from pydantic import BaseModel, Field

class AnganwadiBase(BaseModel):
    center_code: str = Field(max_length=30)
    center_name: str = Field(max_length=100)
    center_address: str = Field(max_length=500)
    center_supervisor_id: Optional[int] = Field(default=None)

class Anganwadi(AnganwadiBase):
    center_ration_id: Optional[int] = Field(default=None)

class AnganwadiCreate(AnganwadiBase):
    pass