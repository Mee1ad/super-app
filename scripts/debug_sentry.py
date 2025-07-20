#!/usr/bin/env python3
"""
Diagnostic script to troubleshoot Sentry production issues.
This script will check all Sentry-related configurations and test connectivity.
"""

import os
import sys
import requests
from urllib.parse import urlparse
import json

def check_environment_variables():
    """Check all Sentry-related environment variables"""
    print("🔍 Checking Sentry Environment Variables")
    print("=" * 50)
    
    sentry_vars = [
        "SENTRY_DSN",
        "SENTRY_ENVIRONMENT", 
        "SENTRY_TRACES_SAMPLE_RATE",
        "SENTRY_PROFILES_SAMPLE_RATE",
        "SENTRY_RELEASE",
        "SENTRY_SERVER_NAME"
    ]
    
    for var in sentry_vars:
        value = os.getenv(var)
        if value:
            if var == "SENTRY_DSN":
                # Mask DSN for security
                masked_value = value[:20] + "..." if len(value) > 20 else value
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
    
    print()

def validate_sentry_dsn():
    """Validate Sentry DSN format and connectivity"""
    print("🔍 Validating Sentry DSN")
    print("=" * 50)
    
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        print("❌ SENTRY_DSN not set")
        return False
    
    # Check DSN format
    if not dsn.startswith('http'):
        print(f"❌ Invalid DSN format: {dsn[:20]}...")
        return False
    
    try:
        # Parse DSN
        parsed = urlparse(dsn)
        print(f"✅ DSN format valid")
        print(f"   Protocol: {parsed.scheme}")
        print(f"   Host: {parsed.hostname}")
        print(f"   Port: {parsed.port or 'default'}")
        print(f"   Path: {parsed.path}")
        
        # Test connectivity to Sentry
        test_url = f"{parsed.scheme}://{parsed.hostname}"
        if parsed.port:
            test_url += f":{parsed.port}"
        
        print(f"\n🌐 Testing connectivity to Sentry...")
        response = requests.get(test_url, timeout=10)
        print(f"✅ Sentry server reachable (Status: {response.status_code})")
        
        return True
        
    except Exception as e:
        print(f"❌ DSN validation failed: {e}")
        return False

def test_sentry_initialization():
    """Test Sentry SDK initialization"""
    print("\n🔍 Testing Sentry SDK Initialization")
    print("=" * 50)
    
    try:
        # Import and test Sentry
        import sentry_sdk
        from core.config import settings
        
        print(f"✅ Sentry SDK imported successfully")
        print(f"   Environment: {settings.sentry_environment}")
        print(f"   DSN configured: {bool(settings.sentry_dsn)}")
        print(f"   Debug mode: {settings.debug}")
        
        # Test initialization
        if settings.sentry_dsn:
            sentry_sdk.init(
                dsn=settings.sentry_dsn,
                environment=settings.sentry_environment,
                traces_sample_rate=0.1,
                profiles_sample_rate=0.1,
                debug=True
            )
            print("✅ Sentry SDK initialized successfully")
            
            # Test message sending
            try:
                sentry_sdk.capture_message("Diagnostic test message", level="info")
                print("✅ Test message sent successfully")
            except Exception as e:
                print(f"❌ Failed to send test message: {e}")
        else:
            print("❌ Cannot test initialization - DSN not configured")
            
    except ImportError as e:
        print(f"❌ Failed to import Sentry SDK: {e}")
        return False
    except Exception as e:
        print(f"❌ Sentry initialization failed: {e}")
        return False

def check_network_connectivity():
    """Check network connectivity for Sentry"""
    print("\n🔍 Checking Network Connectivity")
    print("=" * 50)
    
    # Common Sentry endpoints
    sentry_endpoints = [
        "https://o450000000000000.ingest.sentry.io",
        "https://sentry.io",
        "https://ingest.sentry.io"
    ]
    
    for endpoint in sentry_endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            print(f"✅ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

def check_firewall_proxy():
    """Check for firewall/proxy issues"""
    print("\n🔍 Checking for Firewall/Proxy Issues")
    print("=" * 50)
    
    # Test common ports
    ports = [80, 443, 8080]
    dsn = os.getenv("SENTRY_DSN")
    
    if dsn and dsn.startswith('http'):
        try:
            parsed = urlparse(dsn)
            host = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            
            print(f"Testing connection to {host}:{port}")
            
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ Port {port} is accessible")
            else:
                print(f"❌ Port {port} is blocked")
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")

def generate_troubleshooting_report():
    """Generate a troubleshooting report"""
    print("\n📋 Troubleshooting Report")
    print("=" * 50)
    
    report = {
        "timestamp": str(datetime.datetime.now()),
        "environment": os.getenv("SENTRY_ENVIRONMENT", "unknown"),
        "dsn_configured": bool(os.getenv("SENTRY_DSN")),
        "debug_mode": os.getenv("DEBUG", "false").lower() in ("1", "true", "yes", "on"),
        "python_version": sys.version,
        "platform": sys.platform
    }
    
    print(json.dumps(report, indent=2))
    
    # Common solutions
    print("\n🔧 Common Solutions for Production Sentry Issues:")
    print("1. Ensure SENTRY_DSN is set correctly in production environment")
    print("2. Check if SENTRY_ENVIRONMENT is set to 'production'")
    print("3. Verify network connectivity to Sentry servers")
    print("4. Check firewall/proxy settings")
    print("5. Ensure proper DNS resolution")
    print("6. Check if the server has outbound HTTPS access")
    print("7. Verify the DSN is for the correct Sentry project")
    print("8. Check Sentry project settings for environment filtering")

if __name__ == "__main__":
    import datetime
    
    print("🚀 Sentry Production Troubleshooting Tool")
    print("=" * 60)
    
    check_environment_variables()
    validate_sentry_dsn()
    test_sentry_initialization()
    check_network_connectivity()
    check_firewall_proxy()
    generate_troubleshooting_report()
    
    print("\n✅ Diagnostic complete!")
    print("Check the output above for any issues and apply the suggested solutions.") 