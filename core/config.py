from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    debug: bool = True
    secret_key: str = "your-secret-key"
    database_url: str = "sqlite:///./test.db"

    class Config:
        env_file = ".env"

settings = Settings() 