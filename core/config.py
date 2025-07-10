from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Security
    secret_key: str = "your-secret-key"
    
    # Database Configuration (separate components)
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "superapp"
    db_user: str = "postgres"
    db_password: str = "admin"
    
    # Docker Secrets (production)
    db_password_file: str = "/run/secrets/db_password"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() in ["production", "prod"]
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() in ["development", "dev", "local"]
    
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
        if self.is_production:
            # Read password from Docker secret if available
            password = self._read_secret_file(self.db_password_file) or self.db_password
        else:
            password = self.db_password
            
        return f"postgresql://{self.db_user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = Settings() 