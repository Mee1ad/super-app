#!/usr/bin/env python3
"""
Database Configuration Test Script
This script helps debug database configuration issues in production.
"""

import os
from core.config import settings

def test_configuration():
    """Test the current database configuration"""
    print("=== Database Configuration Test ===")
    print(f"Environment: {settings.environment}")
    print(f"Is Production: {settings.is_production}")
    print(f"Is Development: {settings.is_development}")
    print(f"Debug Mode: {settings.debug}")
    print()
    
    print("=== Environment Variables ===")
    print(f"ENVIRONMENT: {os.getenv('ENVIRONMENT', 'NOT SET')}")
    print(f"DB_HOST: {os.getenv('DB_HOST', 'NOT SET')}")
    print(f"DB_PORT: {os.getenv('DB_PORT', 'NOT SET')}")
    print(f"DB_NAME: {os.getenv('DB_NAME', 'NOT SET')}")
    print(f"DB_USER: {os.getenv('DB_USER', 'NOT SET')}")
    print(f"DB_PASSWORD: {'SET' if os.getenv('DB_PASSWORD') else 'NOT SET'}")
    print(f"DB_PASSWORD_FILE: {os.getenv('DB_PASSWORD_FILE', 'NOT SET')}")
    print()
    
    print("=== Settings Object ===")
    print(f"db_host: {settings.db_host}")
    print(f"db_port: {settings.db_port}")
    print(f"db_name: {settings.db_name}")
    print(f"db_user: {settings.db_user}")
    print(f"db_password: {'SET' if settings.db_password and settings.db_password != 'admin' else 'NOT SET or DEFAULT'}")
    print(f"db_password_file: {settings.db_password_file}")
    print()
    
    print("=== Secret File Test ===")
    secret_path = settings.db_password_file
    if os.path.exists(secret_path):
        try:
            with open(secret_path, 'r') as f:
                secret_content = f.read().strip()
                print(f"Secret file exists: {secret_path}")
                print(f"Secret content length: {len(secret_content)} characters")
                print(f"Secret content: {'***' if secret_content else 'EMPTY'}")
        except Exception as e:
            print(f"Error reading secret file: {e}")
    else:
        print(f"Secret file does not exist: {secret_path}")
    print()
    
    print("=== Database URL ===")
    db_url = settings.get_database_url()
    print(f"Database URL: {db_url}")
    
    # Mask password in URL for security
    if '@' in db_url:
        parts = db_url.split('@')
        if ':' in parts[0]:
            user_pass = parts[0].split(':')
            if len(user_pass) >= 3:  # postgresql://user:pass@host
                masked_url = f"{user_pass[0]}:***@{parts[1]}"
                print(f"Masked URL: {masked_url}")
    
    print()
    print("=== Recommendations ===")
    
    if not settings.is_production:
        print("⚠️  Environment is not set to 'production'")
        print("   Set ENVIRONMENT=production in your .env file or environment variables")
    
    if not os.getenv('DB_PASSWORD'):
        print("⚠️  DB_PASSWORD environment variable is not set")
        print("   Set DB_PASSWORD in your .env file or environment variables")
    
    if not os.path.exists(secret_path):
        print("⚠️  Docker secret file does not exist")
        print(f"   Expected path: {secret_path}")
        print("   Make sure the secret file is created during deployment")
    
    if settings.db_password == 'admin':
        print("⚠️  Using default password 'admin'")
        print("   This might indicate the environment variable is not set correctly")

if __name__ == "__main__":
    test_configuration() 