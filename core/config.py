from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import os
import sys

class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    debug: bool = os.getenv("DEBUG", "false").lower() in ("1", "true", "yes", "on")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "localhost")
    
    # JWT Configuration
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # Google OAuth Configuration
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    google_redirect_uri: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/callback")
    
    # DeepSeek AI Configuration
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    
    # Client Configuration
    client_url: str = os.getenv("CLIENT_URL", "http://localhost:3000")
    
    # Database Configuration (all from env)
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", 5432))
    db_name: str = os.getenv("DB_NAME", "postgres")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "admin")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "allow"
    }
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() in ["development", "dev", "local"]
    
    @property
    def is_testing(self) -> bool:
        return self.environment == "test" or "pytest" in sys.modules
    
    def _read_secret_file(self, file_path: str) -> str:
        """Read secret from Docker secret file"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return f.read().strip()
        except Exception:
            pass
        return ""
    
    def get_database_url(self) -> str:
        """Get database URL from separate components"""
        if self.is_testing:
            # Use SQLite file for testing (better for migrations and CI)
            return "sqlite:///./test.db"
        
        # Use environment variable for password
        password = self.db_password
        if self.debug:
            if self.is_production:
                print(f"Production mode: using DB_PASSWORD from environment variable")
            else:
                print(f"Development mode: using DB_PASSWORD from environment")
            
        return f"postgresql://{self.db_user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}"

# Create settings instance
settings = Settings() 