from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from auth.dependency import (
validate_auth_user, get_current_token_payload, get_current_auth_user,
get_current_auth_user_for_refresh
)
from auth.helpers import (
    create_access_token,
    create_refresh_token
)
from models.bike_rag_query import UserModel, TokenInfo


http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix="/user",
    tags=["JWT"],
    dependencies=[Depends(http_bearer)],
)

@router.post("/login", response_model=TokenInfo)
def auth_user(user: UserModel = Depends(validate_auth_user)):
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return TokenInfo(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh", response_model=TokenInfo, response_model_exclude_none=True)
def auth_refresh_jwt(user: UserModel = Depends(get_current_auth_user_for_refresh)):
    access_token = create_access_token(user)
    return TokenInfo(access_token=access_token)
@router.get("/")
def auth_user_check_self_info(
        payload: dict = Depends(get_current_token_payload),
        user: UserModel = Depends(get_current_auth_user),
):
    iat = payload.get('iat')
    return {
        "username": user.username,
        "logged_in_iat": iat,
    }
