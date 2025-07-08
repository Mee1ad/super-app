# SSH Key Setup for Ansible Deployment

This document explains how to set up SSH keys for secure Ansible deployment on Windows.

## Security Overview

**Important**: SSH keys are stored in your user's SSH directory (`~/.ssh/`) for better security, NOT in the project directory. This prevents accidental exposure and follows security best practices.

## Quick Setup

### Option 1: Using the Setup Script (Recommended)

```powershell
# Run the SSH setup script
.\scripts\setup_ssh.ps1

# To force regenerate existing keys
.\scripts\setup_ssh.ps1 -Force
```

### Option 2: Manual Setup

```powershell
# Generate Ed25519 SSH key pair in user's SSH directory
ssh-keygen -t ed25519 -f ~/.ssh/super-app-backend -N '""'
```

## File Structure

```
~/.ssh/
├── super-app-backend     # Private key (DO NOT SHARE)
├── super-app-backend.pub # Public key (safe to share)
└── ... (other SSH keys)
```

**Note**: Keys are NOT stored in the project directory for security reasons.

## Environment Variables

Set these environment variables for Ansible deployment:

```powershell
# Required
$env:SERVER_IP = "your-server-ip"
$env:SERVER_USER = "ubuntu"  # or your SSH username
$env:GITHUB_REPOSITORY = "your-username/your-repo"

# Optional (defaults shown)
$env:SSH_KEY_PATH = "~/.ssh/super-app-backend"
$env:SSH_DIR = "~/.ssh"
```

## Server Setup

1. Copy the public key to your server:
   ```bash
   # On your server
   mkdir -p ~/.ssh
   chmod 700 ~/.ssh
   echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIyXkJ4cxFDzyYNv7M4Zbkr1cv+4Im2GKMxsYXbLqvkH soheil@DESKTOP-HM4PJ3D" >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```

2. Test SSH connection:
   ```powershell
   ssh -i ~/.ssh/super-app-backend ubuntu@your-server-ip
   ```

## Ansible Configuration

The inventory file (`ansible/inventory.yml`) is configured to use the SSH keys from the user's SSH directory:

```yaml
ansible_ssh_private_key_file: "{{ lookup('env', 'SSH_KEY_PATH', default='~/.ssh/super-app-backend') }}"
ssh_directory: "{{ lookup('env', 'SSH_DIR', default='~/.ssh') }}"
ssh_private_key: "{{ lookup('env', 'SSH_KEY_PATH', default='~/.ssh/super-app-backend') }}"
ssh_public_key: "{{ lookup('env', 'SSH_KEY_PATH', default='~/.ssh/super-app-backend') }}.pub"
```

## Security Best Practices

1. **Keys in user SSH directory** - Keys are stored in `~/.ssh/` not project directory
2. **Never commit private keys** - Keys are outside project scope
3. **Use strong passphrases** - Consider adding a passphrase for production keys
4. **Rotate keys regularly** - Generate new keys periodically
5. **Limit key access** - Only use keys for specific servers/services
6. **Monitor access** - Check server logs for SSH access
7. **Environment-specific keys** - Use different keys for different environments

## Why Not Project Directory?

Storing SSH keys in project directories is **not recommended** because:

- **Accidental exposure** - Keys could be committed if `.gitignore` is modified
- **Project lifecycle** - Keys tied to project rather than user identity
- **Deployment risks** - Keys copied to multiple environments
- **Access control** - Anyone with project access gets key access

## Troubleshooting

### Permission Issues
```powershell
# Fix SSH key permissions on Windows
icacls ~/.ssh/super-app-backend /inheritance:r /grant:r "$env:USERNAME:(R)"
```

### Connection Issues
```powershell
# Test SSH connection with verbose output
ssh -v -i ~/.ssh/super-app-backend ubuntu@your-server-ip
```

### Ansible Connection Issues
```powershell
# Test Ansible connectivity
ansible all -m ping -i ansible/inventory.yml
```

## Key Management

### Backup Keys
```powershell
# Create backup of SSH keys
Copy-Item ~/.ssh/super-app-backend ~/.ssh/super-app-backend.backup
Copy-Item ~/.ssh/super-app-backend.pub ~/.ssh/super-app-backend.pub.backup
```

### Regenerate Keys
```powershell
# Remove old keys and generate new ones
Remove-Item ~/.ssh/super-app-backend*
.\scripts\setup_ssh.ps1 -Force
```

### Multiple Environments
```powershell
# Generate environment-specific keys
ssh-keygen -t ed25519 -f ~/.ssh/super-app-prod -N '""'
ssh-keygen -t ed25519 -f ~/.ssh/super-app-staging -N '""'
```

Remember to update the public key on your server after regenerating keys. 