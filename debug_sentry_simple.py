#!/usr/bin/env python3
"""
Simplified diagnostic script to troubleshoot Sentry production issues.
This script uses only built-in Python modules and checks basic Sentry configuration.
"""

import os
import sys
import socket
import json
import datetime
from urllib.parse import urlparse

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
    """Validate Sentry DSN format"""
    print("🔍 Validating Sentry DSN")
    print("=" * 50)
    
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        print("❌ SENTRY_DSN not set")
        return False
    
    # Check DSN format
    if not dsn.startswith('http'):
        print(f"❌ Invalid DSN format: {dsn[:20]}...")
        print("   DSN should start with 'https://'")
        return False
    
    try:
        # Parse DSN
        parsed = urlparse(dsn)
        print(f"✅ DSN format valid")
        print(f"   Protocol: {parsed.scheme}")
        print(f"   Host: {parsed.hostname}")
        print(f"   Port: {parsed.port or 'default'}")
        print(f"   Path: {parsed.path}")
        
        return True
        
    except Exception as e:
        print(f"❌ DSN validation failed: {e}")
        return False

def test_network_connectivity():
    """Test network connectivity for Sentry using socket"""
    print("\n🔍 Checking Network Connectivity")
    print("=" * 50)
    
    # Common Sentry endpoints
    sentry_hosts = [
        ("sentry.io", 443),
        ("ingest.sentry.io", 443),
        ("o450000000000000.ingest.sentry.io", 443)
    ]
    
    for host, port in sentry_hosts:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ {host}:{port} - Accessible")
            else:
                print(f"❌ {host}:{port} - Blocked (Error code: {result})")
        except Exception as e:
            print(f"❌ {host}:{port} - Error: {e}")

def test_dns_resolution():
    """Test DNS resolution for Sentry domains"""
    print("\n🔍 Checking DNS Resolution")
    print("=" * 50)
    
    sentry_domains = [
        "sentry.io",
        "ingest.sentry.io",
        "o450000000000000.ingest.sentry.io"
    ]
    
    for domain in sentry_domains:
        try:
            ip = socket.gethostbyname(domain)
            print(f"✅ {domain} -> {ip}")
        except socket.gaierror as e:
            print(f"❌ {domain} - DNS resolution failed: {e}")

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
                debug=False  # Disable debug to avoid spam
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

def check_system_info():
    """Check system information"""
    print("\n🔍 System Information")
    print("=" * 50)
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    print(f"Debug mode: {os.getenv('DEBUG', 'false')}")

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

def main():
    """Main diagnostic function"""
    print("🚀 Sentry Production Troubleshooting Tool (Simple)")
    print("=" * 60)
    
    check_environment_variables()
    validate_sentry_dsn()
    test_dns_resolution()
    test_network_connectivity()
    check_system_info()
    test_sentry_initialization()
    generate_troubleshooting_report()
    
    print("\n✅ Diagnostic complete!")
    print("Check the output above for any issues and apply the suggested solutions.")

if __name__ == "__main__":
    main() 