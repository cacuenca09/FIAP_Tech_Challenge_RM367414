from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
from auth import (
    authenticate_user, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user,
    USERS_DB
)
from auth_schemas import LoginRequest, TokenResponse, RefreshTokenRequest, UserInfo

# Router para as rotas de autenticação
auth_router = APIRouter(prefix="/api/v1/auth", tags=["Autenticação"])

@auth_router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest):
    """
    Autentica usuário e retorna tokens de acesso e refresh
    
    - **username**: Nome de usuário (admin ou user)
    - **password**: Senha do usuário (admin123 ou user123)
    
    Retorna:
    - Token de acesso (válido por 30 minutos)
    - Token de refresh (válido por 7 dias)
    - Informações do usuário
    
    **Usuários disponíveis:**
    - admin/admin123 (role: admin)
    - user/user123 (role: user)
    """
    # Autentica o usuário
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Cria os tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}, 
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # em segundos
        user_info={
            "username": user["username"],
            "role": user["role"]
        }
    )

@auth_router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_data: RefreshTokenRequest):
    """
    Renova token de acesso usando refresh token
    
    - **refresh_token**: Token de refresh válido obtido no login
    
    Retorna:
    - Novo token de acesso (válido por 30 minutos)
    - Novo token de refresh (válido por 7 dias)
    - Informações do usuário
    
    O refresh token deve ser válido e não expirado.
    """
    try:
        # Verifica se é um refresh token válido
        payload = verify_token(refresh_data.refresh_token, token_type="refresh")
        username = payload.get("sub")
        
        # Busca o usuário
        user = USERS_DB.get(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Cria novos tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            data={"sub": user["username"], "role": user["role"]}, 
            expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(
            data={"sub": user["username"], "role": user["role"]}
        )
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # em segundos
            user_info={
                "username": user["username"],
                "role": user["role"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

@auth_router.get("/me", response_model=UserInfo)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Retorna informações do usuário autenticado
    
    Requer token de acesso válido no header Authorization: Bearer <token>
    """
    return UserInfo(
        username=current_user["username"],
        role=current_user["role"]
    )

@auth_router.post("/logout")
def logout():
    """
    Endpoint de logout (informativo)
    
    Como JWT é stateless, o logout deve ser implementado no frontend
    removendo o token do storage local. Este endpoint serve apenas
    para documentação da API.
    """
    return {
        "message": "Logout realizado com sucesso",
        "detail": "Remova o token do storage do cliente para completar o logout"
    }