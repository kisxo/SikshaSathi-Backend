from pydantic import BaseModel

# JSON payload containing access token
class Token(BaseModel):
    access_token: str = "JWT-token"
    token_type: str = "bearer"

class StaffLoginForm(BaseModel):
    phone: str = "phone"
    mpin: str = "mpin"

class OfficerLoginForm(BaseModel):
    email: str = "email"
    password: str = "password"

class AdminLoginForm(BaseModel):
    email: str = "email"
    password: str = "password"