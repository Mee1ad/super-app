#!/bin/bash
cd /mnt/e/Dev/super-app-backend

# Load environment variables from .envrc if present
if [ -f .envrc ]; then
  source .envrc
else
  echo "Warning: .envrc file not found. Please create one with the required variables."
fi

source ~/ansible-venv/bin/activate
ansible-playbook -i ansible/inventory.yml ansible/deploy.yml --check 