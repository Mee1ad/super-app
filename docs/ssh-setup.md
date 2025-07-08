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
$env:SERVER_USER = "username"  # or your SSH username
$env:GITHUB_REPOSITORY = "your-username/your-repo"

# Optional (defaults shown)
$env:SSH_KEY_PATH = "~/.ssh/super-app-backend"
$env:SSH_DIR = "~/.ssh"
```