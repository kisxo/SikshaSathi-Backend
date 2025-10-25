from app.db.session import SessionDep
from fastapi import HTTPException
from sqlalchemy import select
from app.db.models.user_model import User
from pydantic import EmailStr
from app.db.models.chat_model import Chat


def list_user_chats(user_id: int, session: SessionDep):
    try:
        statement = select(Chat).where(Chat.user_id == user_id)
        result =  session.execute(statement).mappings().all()
        chats = []
        for row in result:
            chats.append(row.Chat.__dict__)

        return chats
    except Exception as e:
        print(e)
