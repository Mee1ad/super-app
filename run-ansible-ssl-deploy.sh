#!/bin/bash

# SSL-Enabled Ansible Deployment Script
# This script deploys the application with SSL configuration for api.todomodo.ir

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if running in WSL
check_wsl() {
    if [[ ! -f /proc/version ]] || ! grep -q Microsoft /proc/version; then
        print_error "This script must be run from WSL environment"
        print_status "Please run this script from WSL, not directly from Windows"
        exit 1
    fi
}

# Check if Ansible is installed
check_ansible() {
    if ! command -v ansible-playbook &> /dev/null; then
        print_error "Ansible is not installed"
        print_status "Please install Ansible first: sudo apt install ansible"
        exit 1
    fi
}

# Check if vault file exists
check_vault() {
    if [[ ! -f "ansible/group_vars/vault.yml" ]]; then
        print_error "Vault file not found: ansible/group_vars/vault.yml"
        print_status "Please create the vault file with required variables"
        exit 1
    fi
}

# Check domain DNS resolution
check_domain() {
    print_status "Checking domain resolution for api.todomodo.ir..."
    if nslookup api.todomodo.ir > /dev/null 2>&1; then
        print_success "Domain api.todomodo.ir is resolvable"
    else
        print_warning "Domain api.todomodo.ir is not resolvable"
        print_status "Make sure DNS is configured before deployment"
    fi
}

# Run Ansible deployment
run_deployment() {
    print_status "Starting SSL-enabled deployment..."
    
    cd ansible
    
    # Run with verbose output and check mode first
    print_status "Running deployment check..."
    if ansible-playbook -i inventories/production.ini playbook.yml --check --verbose; then
        print_success "Deployment check passed"
    else
        print_error "Deployment check failed"
        exit 1
    fi
    
    # Ask for confirmation
    echo
    print_warning "Deployment check completed successfully."
    read -p "Do you want to proceed with the actual deployment? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Running actual deployment..."
        if ansible-playbook -i inventories/production.ini playbook.yml --verbose; then
            print_success "SSL-enabled deployment completed successfully!"
        else
            print_error "Deployment failed"
            exit 1
        fi
    else
        print_status "Deployment cancelled by user"
        exit 0
    fi
}

# Main execution
main() {
    print_status "SSL-Enabled Ansible Deployment Script"
    print_status "Domain: api.todomodo.ir"
    echo
    
    # Run checks
    check_wsl
    check_ansible
    check_vault
    check_domain
    
    # Run deployment
    run_deployment
}

# Run main function
main "$@" 