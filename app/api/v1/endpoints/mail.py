from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from authx import TokenPayload
import httpx, base64, json
from app.db.session import SessionDep
from app.core.security import authx_security, auth_scheme
from app.services.google_account_service import fetch_user_gmail_messages, get_user_google_account
from app.services.google_account_service import get_valid_google_access_token
from app.services import mail_service, user_service


from fastapi.responses import StreamingResponse
import asyncio
import datetime

router = APIRouter()

@router.get(
    "/me",
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def get_user_gmail_messages(
    session: SessionDep,
    max_results: int = Query(10, description="Number of emails to fetch"),
    payload: TokenPayload = Depends(authx_security.access_token_required),
):
    """
    Fetch Gmail messages for a specific user.
    Automatically refreshes the token if expired.
    Only accessible by the user themselves or an admin.
    """
    # TODO role based access

    try:

        # Fetch valid access token (refresh if needed)
        access_token = get_valid_google_access_token(payload.user_id, session)

        result = fetch_user_gmail_messages(access_token, max_results)
        return {
            "success": True,
            "message": "Fetched Gmail messages successfully",
            "data": result,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print("Error fetching Gmail messages:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )



@router.post(
    "/gmail/watch",
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def start_user_gmail_watch(
    session: SessionDep,
    payload = Depends(authx_security.access_token_required)
):
    """
    Start Gmail push notifications for a user.
    Uses the user's stored access token.
    """

    # Fetch valid access token (refresh if needed)
    access_token = get_valid_google_access_token(payload.user_id, session)
    if not access_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid access token found")

    topic_name = "projects/sikshasathi/topics/gmail-notifications"

    try:
        response = mail_service.start_gmail_watch(access_token, topic_name)
        return {
            "success": True,
            "message": "Gmail watch started successfully",
            "data": response
        }
    except Exception as e:
        print("Error starting Gmail watch:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to start Gmail watch")



@router.post("/gmail/webhook")
async def gmail_webhook(
    request: Request,
    session: SessionDep
):
    """
    Receives Gmail notifications (callback) when a new email arrives.
    Gmail Pub/Sub will call this endpoint.
    """
    try:
        envelope = await request.json()
        message = envelope.get("message", {})
        data_b64 = message.get("data")

        if not data_b64:
            raise HTTPException(status_code=400, detail="No message data")

        payload = json.loads(base64.b64decode(data_b64).decode("utf-8"))
        email_address = payload.get("emailAddress")
        history_id = payload.get("historyId")

        print("Gmail callback received:", payload)

        if not email_address or not history_id:
            raise HTTPException(status_code=400, detail="Missing emailAddress or historyId")

        user = user_service.get_user_by_email(email_address, session)
        # Get valid (refreshed if needed) access token for this user
        access_token = get_valid_google_access_token(user.get("user_id"), session)
        if not access_token:
            raise HTTPException(status_code=404, detail="No linked Google account found")

        # Fetch new emails
        latest_message_id = mail_service.fetch_user_gmail_latest_message_id(access_token)

        latest_mail = mail_service.fetch_gmail_message(access_token, latest_message_id)
        print("New emails fetched:", latest_mail)

        mail_service.save_gmail(user.get("user_id"), latest_mail, session)

        return {"success": True}

    except Exception as e:
        print("Error in Gmail webhook:", e)
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {e}")



@router.get(
    "/message/{message_id}",
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def get_user_gmail_messages(
    session: SessionDep,
    message_id: str,
    payload: TokenPayload = Depends(authx_security.access_token_required),
):

    google_access_token = get_valid_google_access_token(payload.user_id, session)

    if not google_access_token:
        raise HTTPException(status_code=404, detail="No linked Google account found")

    message = mail_service.fetch_gmail_message(google_access_token, message_id)

    return message


async def event_generator():
    n = 0
    while n < 5:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yield f"data: Current time is {current_time}\n\n"
        n+=1
        await asyncio.sleep(1)  # Send update every second

@router.get("/stream_time")
async def stream_time():
    return StreamingResponse(event_generator(), media_type="text/event-stream")