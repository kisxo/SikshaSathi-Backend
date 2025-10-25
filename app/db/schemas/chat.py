from pydantic import BaseModel, Json
from typing import List, Dict, Any, Optional
from typing import Optional


class Talk(BaseModel):
    system: str
    user: str

class ChatForm(BaseModel):
    chat_history: Optional[List[Dict[str, Any]]] = []
    query: str
    save_chat: bool = False


class ChatCreate(BaseModel):
    user_id: int
    data: dict
    chat_title: str