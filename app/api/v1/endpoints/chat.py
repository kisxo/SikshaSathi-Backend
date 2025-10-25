from app.db.schemas.chat import ChatForm, ChatCreate
from app.core.ai import AI_Client
from app.db.models import chat_model
from app.core.config import settings
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from authx import TokenPayload
import httpx, base64, json
from app.db.session import SessionDep
from app.core.security import authx_security, auth_scheme
from app.services import mail_service, user_service
from app.services import profile_service, chat_service

router = APIRouter()



@router.get("/",
     dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
     )
async def get_ai_chats(
        session: SessionDep,
        payload: TokenPayload = Depends(authx_security.access_token_required),
):
    chats = chat_service.list_user_chats(payload.user_id, session=session)
    if not chats:
        # Return 404 if not found
        raise HTTPException(status_code=404, detail="Chats not found")

    return {'data': chats}


@router.post("/",
     dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
     )
async def chat_with_ai(
        input_data: ChatForm,
        session: SessionDep,
        payload: TokenPayload = Depends(authx_security.access_token_required),
):
    user = user_service.get_user(payload.user_id, session)
    profile = profile_service.get_profile_by_user_id(payload.user_id, session)

    system_prompt = f"""
    You are Siksha Sathi AI, a smart study assistant. Your goal is to help the user (always referred to as 'You') plan, learn, and revise their study topics efficiently. Always break complex topics into simple, step-by-step explanations that a beginner can understand. Give study plans, summaries, examples, and exercises where appropriate. 

    Contex / Data:
    - Chat history for contex: {input_data.chat_history}
    - User details: { user.__dict__ } and {profile.__dict__}
    
    Guidelines:
    - Always use simple, clear English.
    - Always refer to the recipient as 'You'.
    - Include actionable tips like "Read this first", "Then practice", "Revise daily".
    - When providing multiple steps, number or bullet them clearly.
    - Never include anything unrelated to studying or the topic.
    - Always be encouraging and motivational.
    - Do not use Markdown formatting.
    """

    if input_data.save_chat:
        chat_data = {
            "chat_history": json.loads(input_data.chat_history) if isinstance(input_data.chat_history,
                                                                              str) else input_data.chat_history or [],
            "query": input_data.query,
            "save_chat": input_data.save_chat,
        }

        # Extract first query safely
        first_query = None
        if input_data.chat_history and input_data.chat_history:
            first_query = input_data.chat_history[0].get("user")
        else:
            first_query = input_data.query  # fallback

        try:

            # Validate with Pydantic model
            validated_chat = ChatCreate(
                data=chat_data,
                chat_title=first_query[:100],
                user_id=payload.user_id
            )

            # Save to database
            new_chat = chat_model.Chat(**validated_chat.model_dump())
            session.add(new_chat)
            session.commit()
            session.refresh(new_chat)

        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Chat Data is not valid JSON")

        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail="Something went wrong!")

        return {"message": "Chat save successful"}



    chat_completion = AI_Client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": input_data.query,
            },
        ],
        model="llama-3.1-8b-instant",
    )

    history_list = input_data.chat_history.copy() if input_data.chat_history else []
    history_list.append({
        "system": chat_completion.choices[0].message.content,
        "user": input_data.query
    })

    return {
        "chat_history": history_list,
        "query": input_data.query,
        "save_chat": False
    }


@router.get("/",
            dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
            )
async def get_ai_chats_history(
        session: SessionDep,
        payload: TokenPayload = Depends(authx_security.access_token_required),
):
    chats = chat_service.list_user_chats(payload.user_id, session=session)
    if not chats:
        # Return 404 if not found
        raise HTTPException(status_code=404, detail="Chats not found")

    return {'data': chats}


@router.post("/public"
             )
async def chat_with_public_ai(
        input_data: ChatForm,
        session: SessionDep,
):

    system_prompt = f"""
    You are Siksha Sathi AI, a smart study assistant. Your goal is to help the user (always referred to as 'You') plan, learn, and revise their study topics efficiently. Always break complex topics into simple, step-by-step explanations that a beginner can understand. Give study plans, summaries, examples, and exercises where appropriate. 

    Contex / Data:
    - Chat history for contex: {input_data.chat_history}

    Guidelines:
    - Always use simple, clear English.
    - Always refer to the recipient as 'You'.
    - Include actionable tips like "Read this first", "Then practice", "Revise daily".
    - When providing multiple steps, number or bullet them clearly.
    - Never include anything unrelated to studying or the topic.
    - Always be encouraging and motivational.
    - Do not use Markdown formatting.
    """

    chat_completion = AI_Client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": input_data.query,
            },
        ],
        model="llama-3.1-8b-instant",
    )

    history_list = input_data.chat_history.copy() if input_data.chat_history else []
    history_list.append({
        "system": chat_completion.choices[0].message.content,
        "user": input_data.query
    })

    return {
        "chat_history": history_list,
        "query": input_data.query,
        "save_chat": False
    }