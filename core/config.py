from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import os
import sys

class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    debug: bool = os.getenv("DEBUG", "false").lower() in ("1", "true", "yes", "on")
    
    # Security
    secret_key: str = "your-secret-key"
    
    # Database Configuration (all from env)
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", 5432))
    db_name: str = os.getenv("DB_NAME", "superapp")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "admin")
    db_password_file: str = "/run/secrets/db_password"

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
        
        # Determine password: environment variable first, then Docker secret file
        if self.db_password and self.db_password != "admin":  # Check if DB_PASSWORD is set and not default
            password = self.db_password
            if self.debug:
                print(f"Using DB_PASSWORD from environment variable")
        elif self.is_production:
            # In production, try Docker secret file as fallback
            secret_password = self._read_secret_file(self.db_password_file)
            password = secret_password or self.db_password
            if self.debug:
                print(f"Production mode: secret file {'found' if secret_password else 'not found'}, using {'secret' if secret_password else 'fallback'}")
        else:
            password = self.db_password
            if self.debug:
                print(f"Development mode: using DB_PASSWORD from environment")
            
        return f"postgresql://{self.db_user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = Settings() 