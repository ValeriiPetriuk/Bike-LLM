from pathlib import Path

from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent / "auth"

class BikeQueryInput(BaseModel):
    text: str

class BikeQueryOutput(BaseModel):
    input: str
    output: str
    intermediate_steps: list[str]


class UserModel(BaseModel):
    model_config = ConfigDict(strict=True)
    username: str
    password: str | bytes

class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"

class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

class Settings(BaseSettings):
    auth_jwt: AuthJWT = AuthJWT()


settings = Settings()

