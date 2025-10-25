from pydantic import BaseModel, Json
from typing import List, Dict, Any, Optional
from typing import Optional


class ResourceForm(BaseModel):
    topic: str

class ResourceCreate(BaseModel):
    user_id: int
    data: dict
    resource_type: str