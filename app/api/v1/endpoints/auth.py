from fastapi import APIRouter, HTTPException
from app.core.security import authx_security
from app.db.session import SessionDep
from app.db.models.user_model import User
from app.db.schemas.auth import Token, LoginForm
from app.core.security import verify_password
from sqlalchemy import select
from app.core.config import settings
from urllib.parse import urlencode
from app.services.google_account_service import exchange_code_for_tokens, verify_id_token, save_oauth_tokens
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.post("/token",
             response_model=Token
             )
async def login(
        input_data: LoginForm,
        session: SessionDep
):
    statement = select(User).where(User.user_email == input_data.email)
    user = session.execute(statement).scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=400, detail="Email and password does not match!")

    if not verify_password(input_data.password, user.user_hashed_password):
        raise HTTPException(status_code=400, detail="Email and password does not match!")

    # Used 'user_in_db.user_role.value' to get the actual string value from the Enum
    token_data = {
        'user_is_admin': user.user_is_admin,
        'user_id': user.user_id,
        'user_data': user.user_data
    }

    token = authx_security.create_access_token(uid=str(user.user_id), data=token_data)

    return {"access_token": token}


@router.get("/google",
            # response_model=Token
            )
async def login_with_google(
        session: SessionDep
):
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    return RedirectResponse(url)


@router.get("/google/callback")
async def google_callback(
        code: str,
        session: SessionDep
):
    # Exchange code for tokens
    tokens = exchange_code_for_tokens(code)

    # Verify ID token to get Google user info
    google_user_info = verify_id_token(tokens.get("id_token"))

    # Save OAuth tokens in DB
    saved_account = save_oauth_tokens(google_user_info, tokens, session)

    return {
        "message": "Google OAuth tokens saved successfully",
        "google_account": saved_account
    }