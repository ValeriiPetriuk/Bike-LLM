from fastapi import Form, HTTPException, Depends
from jwt import InvalidTokenError
from starlette import status
from fastapi.security import OAuth2PasswordBearer
from auth.helpers import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE, TOKEN_TYPE_FIELD
from models.bike_rag_query import UserModel
from tools.db_user import db_user
from utils import auth_utils as utils


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login/")

def validate_auth_user(username:str = Form(), password:str = Form()):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )
    user = db_user.get_user_by_username(username)
    if not user:
        raise unauthed_exc
    if  not utils.validate_password(password, hashed_password=user.password):
        raise unauthed_exc
    return user




def get_current_token_payload(
        token: str = Depends(oauth2_scheme),
):
    try:
        payload = utils.decode_jwt(token=token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token error",
        )
    return payload


def validate_token_type(payload: dict, token_type: str) -> bool:
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Invalid token type {current_token_type!r} expected {token_type}",
    )


def get_user_by_token_sub(payload: dict) -> UserModel:
    username = payload.get('username')
    user = db_user.get_user_by_username(username)
    if user:
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="user not found",
    )


def get_auth_user_from_token_of_type(token_type: str):
    def get_auth_user_from_token(payload: dict = Depends(get_current_token_payload)):
        validate_token_type(payload, token_type)
        return get_user_by_token_sub(payload)
    return get_auth_user_from_token


class UerGetterFromToken:
    def __init__(self, token_type: str):
        self.token_type = token_type

    def __call__(self, payload: dict = Depends(get_current_token_payload)):
        validate_token_type(payload, self.token_type)
        return get_user_by_token_sub(payload)



get_current_auth_user = UerGetterFromToken(ACCESS_TOKEN_TYPE)
get_current_auth_user_for_refresh = UerGetterFromToken(REFRESH_TOKEN_TYPE)