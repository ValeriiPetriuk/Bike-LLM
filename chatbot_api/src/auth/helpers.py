from datetime import timedelta

from models.bike_rag_query import UserModel

from utils import auth_utils as utils
from models.bike_rag_query import settings

TOKEN_TYPE_FIELD = 'type'
ACCESS_TOKEN_TYPE= 'access'
REFRESH_TOKEN_TYPE = 'refresh'

def create_jwt(
        token_type: str,
        payload: dict,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None
) -> str:
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(payload)
    return utils.encode_jwt(payload=jwt_payload, expire_minutes=expire_minutes, expire_timedelta=expire_timedelta)

def create_access_token(user: UserModel) -> str:
    jwt_payload = {
        "sub": user.username,
        "username": user.username
    }
    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        payload=jwt_payload,
        expire_minutes=settings.auth_jwt.access_token_expire_minutes
)

def create_refresh_token(
        user: UserModel) -> str:
    jwt_payload = {
        "sub": user.username,
        "username": user.username
    }
    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        payload=jwt_payload,
        expire_timedelta=timedelta(days=settings.auth_jwt.refresh_token_expire_days)
    )
