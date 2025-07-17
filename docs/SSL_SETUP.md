# SSL Configuration for api.todomodo.ir

This document describes the SSL certificate setup and management for the `api.todomodo.ir` domain.

## Overview

The SSL configuration uses Let's Encrypt certificates with automatic renewal. The setup includes:

- Domain: `api.todomodo.ir`
- SSL Provider: Let's Encrypt (free certificates)
- Auto-renewal: Daily cron job
- Security: Modern SSL/TLS configuration with security headers

## Configuration Files

### Main Playbook
- `playbook.yml` - Main deployment playbook with SSL setup
- `ssl-renew.yml` - Dedicated SSL renewal playbook
- `ssl-manage.sh` - SSL management script

### Variables
- `group_vars/all.yml` - Contains domain and email configuration
- `group_vars/vault.yml` - Encrypted sensitive variables

## SSL Setup Process

### 1. Initial Deployment
The main playbook (`playbook.yml`) includes SSL setup:

```bash
# Run from WSL environment
./run-ansible-deploy.sh
```

This will:
- Install certbot and required packages
- Configure nginx for SSL
- Obtain SSL certificate from Let's Encrypt
- Setup automatic renewal

### 2. SSL Certificate Management

#### Check Certificate Status
```bash
# On the server
sudo ./ssl-manage.sh status
```

#### Manual Renewal
```bash
# On the server
sudo ./ssl-manage.sh renew
```

#### Obtain New Certificate
```bash
# On the server
sudo ./ssl-manage.sh obtain
```

#### Setup Auto-renewal
```bash
# On the server
sudo ./ssl-manage.sh auto
```

### 3. Ansible SSL Management

#### Check SSL Status
```bash
# From local machine
ansible-playbook -i inventories/production.ini ssl-renew.yml --tags ssl,status
```

#### Renew Certificates
```bash
# From local machine
ansible-playbook -i inventories/production.ini ssl-renew.yml --tags ssl,renew
```

## Nginx Configuration

The nginx configuration includes:

### SSL Security Settings
- TLS 1.2 and 1.3 only
- Strong cipher suites
- HSTS headers
- Security headers (X-Frame-Options, X-Content-Type-Options, etc.)

### Proxy Configuration
- WebSocket support
- Proper header forwarding
- Timeout settings
- Health check endpoint

### Let's Encrypt Integration
- ACME challenge support
- Automatic certificate deployment

## Automatic Renewal

### Cron Job
A daily cron job runs at 12:00 PM to check and renew certificates:

```bash
0 12 * * * root /usr/bin/certbot renew --quiet --deploy-hook "systemctl reload nginx"
```

### Monitoring
The renewal process:
1. Checks if certificates need renewal
2. Renews certificates if needed
3. Reloads nginx automatically
4. Logs all activities

## Security Features

### SSL/TLS Configuration
- Minimum TLS version: 1.2
- Preferred TLS version: 1.3
- Strong cipher suites
- Perfect Forward Secrecy (PFS)

### Security Headers
- `Strict-Transport-Security`: Forces HTTPS
- `X-Frame-Options`: Prevents clickjacking
- `X-Content-Type-Options`: Prevents MIME sniffing
- `X-XSS-Protection`: XSS protection
- `Referrer-Policy`: Controls referrer information

### Firewall Configuration
- Port 80: HTTP (redirects to HTTPS)
- Port 443: HTTPS
- Port 22: SSH

## Troubleshooting

### Common Issues

#### Certificate Not Obtained
1. Check domain DNS resolution
2. Verify port 80 is open
3. Check nginx configuration
4. Review certbot logs: `sudo journalctl -u certbot`

#### Certificate Renewal Fails
1. Check cron job: `sudo crontab -l`
2. Verify certbot is installed: `which certbot`
3. Check permissions: `ls -la /etc/letsencrypt/`
4. Review renewal logs: `sudo certbot renew --dry-run`

#### Nginx Configuration Issues
1. Test configuration: `sudo nginx -t`
2. Check syntax: `sudo nginx -T`
3. Review error logs: `sudo tail -f /var/log/nginx/error.log`

### Log Locations
- Certbot logs: `/var/log/letsencrypt/`
- Nginx logs: `/var/log/nginx/`
- System logs: `sudo journalctl -u nginx`

### SSL Testing
Test SSL configuration online:
- [SSL Labs](https://www.ssllabs.com/ssltest/)
- [Mozilla Observatory](https://observatory.mozilla.org/)

## Maintenance

### Regular Tasks
1. **Monthly**: Check certificate status
2. **Quarterly**: Review SSL configuration
3. **Annually**: Update SSL security settings

### Monitoring
- Certificate expiration dates
- Renewal success/failure
- SSL configuration changes
- Security header compliance

### Backup
Important files to backup:
- `/etc/letsencrypt/` - SSL certificates
- `/etc/nginx/sites-available/api.todomodo.ir` - Nginx config
- `/etc/cron.d/certbot-renew` - Renewal cron job

## Commands Reference

### SSL Management Script
```bash
sudo ./ssl-manage.sh status    # Check certificate status
sudo ./ssl-manage.sh renew     # Renew certificates
sudo ./ssl-manage.sh obtain    # Obtain new certificate
sudo ./ssl-manage.sh nginx     # Check nginx config
sudo ./ssl-manage.sh auto      # Setup auto-renewal
sudo ./ssl-manage.sh all       # Run all checks
```

### Certbot Commands
```bash
sudo certbot certificates              # List certificates
sudo certbot renew --dry-run          # Test renewal
sudo certbot renew --quiet            # Renew certificates
sudo certbot delete --cert-name DOMAIN # Delete certificate
```

### Nginx Commands
```bash
sudo nginx -t                         # Test configuration
sudo nginx -T                         # Show full configuration
sudo systemctl reload nginx           # Reload configuration
sudo systemctl restart nginx          # Restart nginx
```

## Environment Variables

Set these in your environment or vault:
- `certbot_email`: Email for Let's Encrypt notifications
- `domain`: Domain name (api.todomodo.ir)

## Notes

- Certificates are valid for 90 days
- Let's Encrypt has rate limits (50 certificates per domain per week)
- Always test configuration changes before applying
- Keep backup of SSL certificates and configurations
- Monitor certificate expiration dates proactively 