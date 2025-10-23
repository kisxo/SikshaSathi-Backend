from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy import select, func
from app.db.session import SessionDep
from app.db.models.google_account_model import GoogleAccount
from app.services.user_service import get_user_by_email, get_user
import httpx
from google.oauth2 import id_token
from google.auth.transport import requests
from app.core.config import settings

def save_oauth_tokens(google_user_info: dict, tokens: dict, session: SessionDep):
    """
    Save or update essential Google OAuth tokens for a user.
    Only stores access_token, refresh_token, token_expiry, and google_email.
    """
    google_email = google_user_info.get("email")

    # Ensure Google email matches logged-in user
    user_in_db = get_user_by_email(google_email, session)
    if not user_in_db:
        raise HTTPException(status_code=403, detail="Google account email does not match any account")

    print(user_in_db)
    expires_in = tokens.get("expires_in", 3600)

    try:
        # Check if GoogleAccount already exists for this user
        statement = select(GoogleAccount).where(GoogleAccount.user_id == user_in_db.get("user_id"))
        google_account = session.execute(statement).scalar_one_or_none()

        if not google_account:
            # Create new record
            google_account = GoogleAccount(
                user_id=user_in_db.get("user_id"),
                google_email=google_email,
                access_token=tokens["access_token"],
                refresh_token=tokens.get("refresh_token"),
                token_expiry=func.now() + timedelta(seconds=expires_in)
            )
            session.add(google_account)
        else:
            # Update existing record
            google_account.access_token = tokens["access_token"]
            google_account.refresh_token = tokens.get("refresh_token", google_account.refresh_token)
            google_account.token_expiry = func.now() + timedelta(seconds=expires_in)

        session.commit()
        return google_account.__dict__

    except Exception as e:
        print("Error saving OAuth tokens:", e)
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to save Google OAuth tokens")



def exchange_code_for_tokens(code: str):
    """
    Exchange authorization code for access and refresh tokens.
    """
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    response = httpx.post(settings.GOOGLE_TOKEN_URI, data=data)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get Google OAuth tokens")

    return response.json()



def verify_id_token(id_token_str: str):
    """
    Verify ID token and extract user info.
    """
    try:
        user_info = id_token.verify_oauth2_token(
            id_token_str,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        return user_info
    except ValueError as e:
        raise Exception(f"Invalid ID token: {e}")


def get_user_google_account(user_id: int, session: SessionDep):
    """
    Retrieve the Google account record for the currently logged-in user.
    """
    statement = select(GoogleAccount).where(GoogleAccount.user_id == user_id)
    account = session.execute(statement).scalar_one_or_none()
    return account



def fetch_user_gmail_messages(access_token: str, max_results: int = 10):
    """
    Fetch Gmail messages using an always-valid token.
    """

    headers = {"Authorization": f"Bearer {access_token}"}
    gmail_api_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages"
    params = {"maxResults": max_results}

    response = httpx.get(gmail_api_url, headers=headers, params=params, timeout=10.0)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()



def get_valid_google_access_token(user_id: int, session: SessionDep) -> str:
    """
    Ensure the Google access token for a user is valid.
    If expired or near expiry, refresh it automatically.
    Returns a valid access token string.
    """
    statement = select(GoogleAccount).where(GoogleAccount.user_id == user_id)
    google_account = session.execute(statement).scalar_one_or_none()

    if not google_account:
        raise HTTPException(status_code=404, detail="Google account not linked")

    now = datetime.now(timezone.utc)

    # Normalize DB-stored expiry to UTC-aware datetime
    token_expiry = google_account.token_expiry
    if token_expiry and token_expiry.tzinfo is None:
        token_expiry = token_expiry.replace(tzinfo=timezone.utc)

    # Check expiry (with 1 minute grace)
    if token_expiry and token_expiry > now + timedelta(minutes=1):
        return google_account.access_token  # still valid

    # Otherwise refresh using refresh_token
    if not google_account.refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token. Please re-link Google account.")

    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "refresh_token": google_account.refresh_token,
        "grant_type": "refresh_token",
    }

    try:
        response = httpx.post(token_url, data=payload, timeout=10.0)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Failed to refresh token: {response.text}")

        new_tokens = response.json()
        access_token = new_tokens.get("access_token")
        expires_in = new_tokens.get("expires_in", 3600)

        if not access_token:
            raise HTTPException(status_code=400, detail="No access token returned by Google")

        # Update DB with new token + expiry
        google_account.access_token = access_token
        google_account.token_expiry = func.now() + timedelta(seconds=expires_in)
        session.commit()

        return access_token

    except Exception as e:
        print("Error refreshing Google token:", e)
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to refresh Google access token")



def get_gmail_message(access_token: str, message_id: str):
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"format": "metadata", "metadataHeaders": ["From", "Subject", "Date"]}
    response = httpx.get(url, headers=headers, params=params)
    return response.json()