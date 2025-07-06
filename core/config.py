from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    debug: bool = True
    secret_key: str = "your-secret-key"
    database_url: str = "postgresql://postgres:admin@localhost:5432/lifehub"

    class Config:
        env_file = ".env"

settings = Settings() 