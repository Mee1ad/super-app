# Ansible Inventory Usage

## Overview
The `inventory.yml` file contains all inventory configurations in a single file with different groups for different use cases.

## Groups

### `production` (Default)
- **User**: `superapp` (with sudo privileges)
- **SSH Key**: `/mnt/c/Users/Soheil/.ssh/super-app-backend`
- **Use Case**: Regular deployments and maintenance
- **Command**: `ansible-playbook -i ansible/inventory.yml ansible/deploy.yml`

### `initial_setup`
- **User**: `root`
- **SSH Key**: `/mnt/c/Users/Soheil/.ssh/id_rsa`
- **Use Case**: Initial server setup and user creation
- **Command**: `ansible-playbook -i ansible/inventory.yml --limit initial_setup ansible/deploy.yml`

### `local_dev`
- **Connection**: Local
- **Use Case**: Local development and testing
- **Command**: `ansible-playbook -i ansible/inventory.yml --limit local_dev ansible/deploy.yml`

## Environment Variables

You can override defaults using environment variables:

```bash
export SERVER_IP="your-server-ip"
export ANSIBLE_USER="your-user"
export SSH_KEY_FILE="~/.ssh/your-key"
```

## Examples

### Production Deployment
```bash
# Uses production group by default
ansible-old-playbook -i ansible-old/inventory.yml ansible-old/deploy.yml
```

### Initial Server Setup
```bash
# Use root user for initial setup
ansible-old-playbook -i ansible-old/inventory.yml --limit initial_setup ansible-old/deploy.yml
```

### GitHub Actions
```bash
# Set environment variables in GitHub Actions
export SERVER_IP="${{ secrets.SERVER_IP }}"
export ANSIBLE_USER="superapp"
export SSH_KEY_FILE="~/.ssh/deploy_key"

ansible-old-playbook -i ansible-old/inventory.yml ansible-old/deploy.yml
``` 