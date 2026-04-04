from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FastAPI JWT Notes"
    database_url: str = "sqlite:///./app.db"
    jwt_secret_key: str = "change_me_to_a_long_random_secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = ConfigDict(env_file=".env")


settings = Settings()
