from fastapi import APIRouter, HTTPException
from app.core.security import authx_security
from app.db.session import SessionDep
from app.db.models.user_model import User
from app.db.schemas.auth import Token, LoginForm
from app.core.security import verify_password
from sqlalchemy import select
from app.core.config import settings
from urllib.parse import urlencode
import httpx
from google.oauth2 import id_token
from google.auth.transport import requests

router = APIRouter()


@router.post("/token",
    response_model=Token
)
async def login(
    input_data: LoginForm,
    session: SessionDep
):
    statement = select(User).where(User.user_email== input_data.email)
    user = session.execute(statement).scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=400, detail="Email and password does not match!")

    if not verify_password(input_data.password, user.user_hashed_password):
        raise HTTPException(status_code=400, detail="Email and password does not match!")

    # Used 'user_in_db.user_role.value' to get the actual string value from the Enum
    token_data = {
        'user_is_admin': user.user_is_admin,
        'user_id' : user.user_id,
        'user_data' : user.user_data
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
    return url


@router.get("/google/callback")
def google_callback(code: str):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    # Exchange authorization code for tokens
    response = httpx.post(token_url, data=data)
    if response.status_code != 200:
        print(response.json())
        raise HTTPException(status_code=400, detail="Failed to fetch tokens from Google")

    tokens = response.json()
    id_token_str = tokens.get("id_token")

    if not id_token_str:
        raise HTTPException(status_code=400, detail="Missing ID token in Google response")

    # Verify and decode ID token
    try:
        user_info = id_token.verify_oauth2_token(
            id_token_str,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID token: {e}")

    # Example user info you’ll get
    # {
    #   "sub": "110169484474386276334",
    #   "email": "user@gmail.com",
    #   "email_verified": True,
    #   "name": "User Name",
    #   "picture": "https://lh3.googleusercontent.com/a-/..."
    # }

    return {
        "user": {
            "name": user_info.get("name"),
            "email": user_info.get("email"),
            "picture": user_info.get("picture"),
            "sub": user_info.get("sub")
        },
        "tokens": tokens
    }