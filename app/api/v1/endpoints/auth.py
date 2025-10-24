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
from fastapi.responses import HTMLResponse

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
        "scope": "openid email profile https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.modify",
        "access_type": "offline",  # ensures you get a refresh_token
        "prompt": "consent"  # ensures user re-consents if already authorized
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    return RedirectResponse(url)


@router.get("/google/callback")
async def google_callback(
        code: str,
        session: SessionDep
):
    try:
        tokens = exchange_code_for_tokens(code)
        google_user_info = verify_id_token(tokens.get("id_token"))
        saved_account = save_oauth_tokens(google_user_info, tokens, session)

        # Your Android deep link (change scheme/host as needed)
        deep_link = (
            f"sikshasathi://"
            # f"email={google_user_info.get('email')}"
            # f"&name={google_user_info.get('name')}"
        )

        html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                <title>Google Sign-in Success</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        text-align: center;
                        padding: 60px;
                        background: linear-gradient(135deg, #f9f9f9, #e8f0fe);
                        color: #333;
                    }}
                    .card {{
                        background: white;
                        max-width: 400px;
                        margin: auto;
                        padding: 40px;
                        border-radius: 20px;
                        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
                    }}
                    h1 {{
                        color: #1a73e8;
                    }}
                    a.button {{
                        display: inline-block;
                        background: #1a73e8;
                        color: white;
                        padding: 12px 24px;
                        text-decoration: none;
                        border-radius: 8px;
                        margin-top: 20px;
                        font-size: 16px;
                        transition: background 0.3s;
                    }}
                    a.button:hover {{
                        background: #155ab6;
                    }}
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>Google Account Linked</h1>
                    <p>You can now continue in the app.</p>
                    <a class="button" href="{deep_link}">Open App</a>
                </div>
            </body>
            </html>
            """
        return HTMLResponse(content=html_content)

    except Exception as e:
        print("Error in Google callback:", e)
        return HTMLResponse(
            content=f"<h3 style='color:red;'>Something went wrong: {str(e)}</h3>",
            status_code=500,
        )