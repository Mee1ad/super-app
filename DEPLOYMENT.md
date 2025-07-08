# Deployment Guide

This guide explains how to deploy the Super App Backend using the provided Ansible playbook and GitHub Actions workflow.

## Prerequisites

1. **Ubuntu Server**: A clean Ubuntu server accessible via IP address
2. **GitHub Repository**: Your code must be in a GitHub repository
3. **SSH Key Pair**: Generate an SSH key pair for server access
4. **GitHub Secrets**: Configure the required secrets in your GitHub repository

## Setup Instructions

### 1. Generate SSH Key Pair

```bash
ssh-keygen -t rsa -b 4096 -f ./secrets/id_rsa -N ""
```

### 2. Create Secret Files

Create the following files in the `./secrets/` directory:

- `api_key`: Your API key
- `db_password`: Your database password
- `id_rsa`: SSH private key (generated above)
- `id_rsa.pub`: SSH public key (generated above)

### 3. Configure GitHub Secrets

In your GitHub repository, go to Settings > Secrets and variables > Actions, and add the following secrets:

- `SERVER_IP`: Your server's IP address
- `SERVER_USER`: SSH user (usually `root`)
- `SSH_PRIVATE_KEY`: Content of your SSH private key
- `SSH_PUBLIC_KEY`: Content of your SSH public key
- `API_KEY`: Your API key
- `DB_PASSWORD`: Your database password

### 4. Update Repository References

Update the following files with your actual GitHub repository name:

- `docker-compose.yml`: Replace `your-username/super-app-backend` with your actual repository
- `ansible/deploy.yml`: The `github_repository` variable will be set automatically by GitHub Actions

## Deployment Process

### Automatic Deployment (Recommended)

1. Push your code to the `main` branch
2. GitHub Actions will automatically:
   - Build the Docker image
   - Push it to GitHub Container Registry
   - SSH into your server
   - Run the Ansible playbook to deploy

### Manual Deployment

If you need to deploy manually:

```bash
# Set environment variables
export SERVER_IP="your-server-ip"
export SERVER_USER="root"
export SSH_KEY_PATH="./secrets/id_rsa"
export GITHUB_REPOSITORY="your-username/super-app-backend"

# Run the Ansible playbook
ansible-playbook -i ansible/inventory.yml ansible/deploy.yml
```

## What the Deployment Does

The Ansible playbook performs the following tasks:

1. **System Updates**: Updates all system packages
2. **User Setup**: Creates a new `superapp` user with sudo privileges
3. **SSH Configuration**: Sets up SSH key authentication
4. **Docker Installation**: Installs Docker and Docker Compose
5. **Secrets Management**: Creates `/run/secrets/` directory and copies secret files
6. **Application Deployment**: Pulls the latest Docker image and runs it with docker-compose
7. **Health Check**: Verifies the application is running

## Accessing Your Application

After successful deployment, your application will be available at:

```
http://YOUR_SERVER_IP:8000
```

You can test the health endpoint:
```
http://YOUR_SERVER_IP:8000/ping
```

## Troubleshooting

### Common Issues

1. **SSH Connection Failed**: Ensure your SSH key is properly configured and the server allows key-based authentication
2. **Docker Permission Issues**: The playbook adds the user to the docker group, but you may need to log out and back in
3. **Port Not Accessible**: Ensure your server's firewall allows traffic on port 8000

### Manual Commands

To manually check the deployment:

```bash
# SSH into your server
ssh -i ./secrets/id_rsa superapp@YOUR_SERVER_IP

# Check Docker containers
docker ps

# Check application logs
docker logs super-app-api

# Check if the application is responding
curl http://localhost:8000/ping
```

## Security Notes

- The deployment creates a dedicated user (`superapp`) with limited privileges
- Docker secrets are used for sensitive data
- SSH keys are properly secured with appropriate permissions
- The application runs as a non-root user inside the container

## Next Steps

Once your basic deployment is working, consider:

1. **Domain and SSL**: Set up a domain name and SSL certificates
2. **Load Balancer**: Add a load balancer for high availability
3. **Monitoring**: Implement application monitoring and logging
4. **Backup Strategy**: Set up database backups and disaster recovery 