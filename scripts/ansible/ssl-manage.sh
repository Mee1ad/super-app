#!/bin/bash

# SSL Certificate Management Script for api.todomodo.ir
# This script provides various SSL management functions

set -e

DOMAIN="api.todomodo.ir"
CERTBOT_EMAIL="admin@todomodo.ir"
NGINX_CONFIG="/etc/nginx/sites-available/${DOMAIN}"
CERT_PATH="/etc/letsencrypt/live/${DOMAIN}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

# Function to check SSL certificate status
check_cert_status() {
    print_status "Checking SSL certificate status for ${DOMAIN}..."
    
    if [[ -d "${CERT_PATH}" ]]; then
        print_success "Certificate directory exists"
        
        # Check certificate expiration
        local expiry_date=$(openssl x509 -in "${CERT_PATH}/fullchain.pem" -noout -enddate | cut -d= -f2)
        local expiry_epoch=$(date -d "$expiry_date" +%s)
        local current_epoch=$(date +%s)
        local days_remaining=$(( (expiry_epoch - current_epoch) / 86400 ))
        
        print_status "Certificate expires on: $expiry_date"
        
        if [[ $days_remaining -gt 30 ]]; then
            print_success "Certificate is valid for $days_remaining days"
        elif [[ $days_remaining -gt 7 ]]; then
            print_warning "Certificate expires in $days_remaining days"
        else
            print_error "Certificate expires in $days_remaining days - RENEWAL NEEDED!"
        fi
    else
        print_error "Certificate directory not found"
        return 1
    fi
}

# Function to renew SSL certificate
renew_cert() {
    print_status "Renewing SSL certificate for ${DOMAIN}..."
    
    # Test nginx configuration first
    if nginx -t; then
        print_success "Nginx configuration is valid"
    else
        print_error "Nginx configuration is invalid"
        return 1
    fi
    
    # Renew certificate
    if certbot renew --quiet --deploy-hook "systemctl reload nginx"; then
        print_success "SSL certificate renewed successfully"
        systemctl reload nginx
        print_success "Nginx reloaded"
    else
        print_error "Failed to renew SSL certificate"
        return 1
    fi
}

# Function to obtain new SSL certificate
obtain_cert() {
    print_status "Obtaining new SSL certificate for ${DOMAIN}..."
    
    # Check if domain is accessible
    if ! nslookup "${DOMAIN}" > /dev/null 2>&1; then
        print_error "Domain ${DOMAIN} is not resolvable"
        return 1
    fi
    
    # Obtain certificate
    if certbot certonly --webroot -w /var/www/certbot -d "${DOMAIN}" --email "${CERTBOT_EMAIL}" --agree-tos --non-interactive; then
        print_success "SSL certificate obtained successfully"
        
        # Test and reload nginx
        if nginx -t; then
            systemctl reload nginx
            print_success "Nginx configuration updated and reloaded"
        else
            print_error "Nginx configuration is invalid after certificate installation"
            return 1
        fi
    else
        print_error "Failed to obtain SSL certificate"
        return 1
    fi
}

# Function to check nginx configuration
check_nginx() {
    print_status "Checking nginx configuration..."
    
    if nginx -t; then
        print_success "Nginx configuration is valid"
    else
        print_error "Nginx configuration is invalid"
        return 1
    fi
    
    # Check if SSL site is enabled
    if [[ -L "/etc/nginx/sites-enabled/${DOMAIN}" ]]; then
        print_success "SSL site is enabled in nginx"
    else
        print_warning "SSL site is not enabled in nginx"
    fi
}

# Function to setup automatic renewal
setup_auto_renewal() {
    print_status "Setting up automatic SSL certificate renewal..."
    
    # Create cron job for renewal
    cat > /etc/cron.d/certbot-renew << EOF
# SSL Certificate Auto-renewal for ${DOMAIN}
0 12 * * * root /usr/bin/certbot renew --quiet --deploy-hook "systemctl reload nginx"
EOF
    
    print_success "Automatic renewal cron job created"
    print_status "Certificates will be renewed daily at 12:00 PM if needed"
}

# Function to show usage
show_usage() {
    echo "SSL Certificate Management Script for ${DOMAIN}"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  status     - Check SSL certificate status and expiration"
    echo "  renew      - Renew SSL certificate"
    echo "  obtain     - Obtain new SSL certificate"
    echo "  nginx      - Check nginx configuration"
    echo "  auto       - Setup automatic renewal"
    echo "  all        - Run all checks and setup"
    echo "  help       - Show this help message"
    echo ""
}

# Main script logic
main() {
    check_root
    
    case "${1:-help}" in
        "status")
            check_cert_status
            ;;
        "renew")
            renew_cert
            ;;
        "obtain")
            obtain_cert
            ;;
        "nginx")
            check_nginx
            ;;
        "auto")
            setup_auto_renewal
            ;;
        "all")
            print_status "Running comprehensive SSL check and setup..."
            check_nginx
            check_cert_status
            setup_auto_renewal
            print_success "SSL management setup completed"
            ;;
        "help"|*)
            show_usage
            ;;
    esac
}

# Run main function with all arguments
main "$@" 