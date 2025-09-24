from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    """Schema para requisição de login"""
    username: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "admin123"
            }
        }

class TokenResponse(BaseModel):
    """Schema para resposta de token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # em segundos
    user_info: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user_info": {
                    "username": "admin",
                    "role": "admin"
                }
            }
        }

class RefreshTokenRequest(BaseModel):
    """Schema para requisição de refresh token"""
    refresh_token: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            }
        }

class UserInfo(BaseModel):
    """Schema para informações do usuário"""
    username: str
    role: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "role": "admin"
            }
        }