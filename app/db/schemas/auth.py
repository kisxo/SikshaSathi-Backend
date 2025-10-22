from pydantic import BaseModel, EmailStr

# JSON payload containing access token
class Token(BaseModel):
    access_token: str = "JWT-token"
    token_type: str = "bearer"


class LoginForm(BaseModel):
    email: EmailStr
    password: str = "password"