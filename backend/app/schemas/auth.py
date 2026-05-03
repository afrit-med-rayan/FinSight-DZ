from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    wilaya_code: Optional[int] = 16

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    wilaya_code: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
