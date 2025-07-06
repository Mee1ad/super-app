#!/usr/bin/env python3
"""
CORS Configuration Validator
Validates CORS configuration before server startup to prevent runtime issues
"""
import sys
import os
import asyncio
from typing import List, Dict, Any

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from esmerald import CORSConfig
    from main import app
    print("✅ CORSConfig import successful")
except ImportError as e:
    print(f"❌ CORSConfig import failed: {e}")
    print("💡 Solution: Check Esmerald version and CORSConfig availability")
    sys.exit(1)

def validate_cors_config() -> bool:
    """Validate CORS configuration"""
    try:
        # Check if app has cors_config
        if not hasattr(app, 'cors_config'):
            print("❌ App does not have cors_config attribute")
            return False
        
        cors_config = app.cors_config
        
        # Validate required attributes
        required_attrs = ['allow_origins', 'allow_credentials', 'allow_methods', 'allow_headers']
        for attr in required_attrs:
            if not hasattr(cors_config, attr):
                print(f"❌ CORS config missing required attribute: {attr}")
                return False
        
        # Validate origins
        origins = cors_config.allow_origins
        if not isinstance(origins, list) or len(origins) == 0:
            print("❌ CORS allow_origins must be a non-empty list")
            return False
        
        expected_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
        for origin in expected_origins:
            if origin not in origins:
                print(f"❌ Missing expected origin: {origin}")
                return False
        
        print("✅ CORS configuration validation passed")
        return True
        
    except Exception as e:
        print(f"❌ CORS validation failed: {e}")
        return False

def validate_imports() -> bool:
    """Validate all required imports"""
    required_imports = [
        ('esmerald', 'Esmerald'),
        ('esmerald', 'CORSConfig'),
        ('esmerald', 'Gateway'),
        ('esmerald', 'get'),
    ]
    
    for module, item in required_imports:
        try:
            __import__(module)
            print(f"✅ {module}.{item} import successful")
        except ImportError as e:
            print(f"❌ {module}.{item} import failed: {e}")
            return False
    
    return True

def main():
    """Main validation function"""
    print("🔍 Validating CORS configuration...")
    
    # Validate imports
    if not validate_imports():
        print("❌ Import validation failed")
        sys.exit(1)
    
    # Validate CORS config
    if not validate_cors_config():
        print("❌ CORS configuration validation failed")
        sys.exit(1)
    
    print("✅ All validations passed - CORS should work correctly")

if __name__ == "__main__":
    main() 