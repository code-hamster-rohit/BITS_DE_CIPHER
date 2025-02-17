from pydantic import BaseModel

class GenerateOtp(BaseModel):
    email: str

class Login(BaseModel):
    email: str
    otp: str

class Token(BaseModel):
    token: str