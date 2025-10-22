from datetime import timedelta
from fastapi import HTTPException
from sqlalchemy import select, func
from app.db.session import SessionDep
from app.db.models.google_account_model import GoogleAccount
from app.services.user_service import get_user_by_email
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