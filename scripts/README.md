# Scripts Directory

This directory contains all utility scripts organized by their purpose and functionality.

## Directory Structure

### `/ansible/`
Ansible deployment and automation scripts
- `run-ansible-check.sh` - Check Ansible configuration
- `run-ansible-deploy.sh` - Deploy using Ansible
- `run-ansible-initial-setup.sh` - Initial server setup
- `run-ansible-ssl-deploy.sh` - SSL certificate deployment
- `run-ansible-check.ps1` - Windows version of check script
- `run-ansible-deploy.ps1` - Windows version of deploy script

### `/database/`
Database management and migration scripts
- `migrate_to_incremental.py` - Convert to incremental migrations
- `run-migrations.sh` - Run database migrations
- `wipe_db.py` - Clear database (use with caution)

### `/deployment/`
Server deployment and configuration scripts
- `add_github_auth.ps1` - Add GitHub authentication
- `generate-secrets.ps1` - Generate secure secrets
- `secure-db-access.ps1` - Secure database access
- `setup_ssh.ps1` - Setup SSH configuration
- `test-ssh-windows.ps1` - Test SSH connection on Windows

### `/fixes/`
Database fix and data correction scripts
- `check_moods_data.py` - Validate mood data integrity
- `fix_meal_types.py` - Fix meal type inconsistencies
- `fix_migrations_table.py` - Fix migration table issues
- `fix_moods_table.py` - Fix moods table issues
- `fix_null_moods.py` - Fix null mood values
- `fix_null_moods_sql.py` - SQL-based null mood fixes
- `fix-migrations-table.sql` - SQL script for migration fixes
- `fix_moods_table.sql` - SQL script for mood table fixes

### `/testing/`
Testing and validation scripts
- `debug_edgy.py` - Debug Edgy ORM issues
- `main.py` - Main application entry point
- `routers.py` - Router configuration
- `test-db-config.py` - Test database configuration
- `test_changelog.py` - Test changelog functionality
- `test_database_integration.py` - Test database integration
- `test_docker_build.sh` - Test Docker build process
- `test_endpoints.py` - Test API endpoints
- `test_hash_logging.py` - Test hash logging
- `test_ideas_api.py` - Test ideas API
- `test_imports.py` - Test import statements
- `test_incremental_migration.py` - Test incremental migrations
- `test_latest_changelog_behavior.py` - Test changelog behavior
- `test-db-connection.ps1` - Test database connection
- `validate_cors.py` - Validate CORS configuration

## Root Level Scripts

### Testing Scripts
- `run-tests.ps1` - Run tests on Windows
- `run-tests.sh` - Run tests on Linux/macOS
- `run-tests.bat` - Run tests on Windows (batch)
- `setup-test-db.ps1` - Setup test database on Windows
- `setup-test-db.sh` - Setup test database on Linux/macOS

### Environment Setup
- `setup-env.ps1` - Setup environment on Windows
- `setup-env.sh` - Setup environment on Linux/macOS

## Usage

### Running Scripts by Category

```bash
# Database operations
cd scripts/database
./run-migrations.sh

# Fix data issues
cd scripts/fixes
python fix_meal_types.py

# Deploy with Ansible
cd scripts/ansible
./run-ansible-deploy.sh

# Test functionality
cd scripts/testing
python test_endpoints.py
```

### Cross-Platform Scripts

Most scripts have both PowerShell (`.ps1`) and Bash (`.sh`) versions for cross-platform compatibility.

## Safety Notes

- **Database scripts**: Always backup before running
- **Fix scripts**: Test in development environment first
- **Deployment scripts**: Review configuration before production use
- **Testing scripts**: Safe to run, designed for validation only

## Contributing

When adding new scripts:
1. Place them in the appropriate subdirectory
2. Update this README with description and usage
3. Include both Windows and Unix versions if applicable
4. Add proper error handling and documentation 