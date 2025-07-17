# Database Fix Scripts

This directory contains scripts for fixing various database issues and data inconsistencies.

## Scripts Overview

### `fix_meal_types.py`
- **Purpose**: Fix meal type data inconsistencies
- **Usage**: `python fix_meal_types.py`
- **Description**: Corrects meal type values in the database to ensure consistency

### `fix_migrations_table.py`
- **Purpose**: Fix migration table schema issues
- **Usage**: `python fix_migrations_table.py`
- **Description**: Repairs the migrations table structure and data integrity

### `fix_null_moods.py`
- **Purpose**: Fix null mood values in the database
- **Usage**: `python fix_null_moods.py`
- **Description**: Replaces null mood values with appropriate default values

### `fix_null_moods_sql.py`
- **Purpose**: SQL-based fix for null mood values
- **Usage**: `python fix_null_moods_sql.py`
- **Description**: Alternative SQL approach to fixing null mood values

### `check_moods_data.py`
- **Purpose**: Validate mood data integrity
- **Usage**: `python check_moods_data.py`
- **Description**: Checks for data inconsistencies in the moods table

## Usage Guidelines

1. **Backup First**: Always backup your database before running fix scripts
2. **Test Environment**: Test scripts in a development environment first
3. **Review Changes**: Review the changes made by each script
4. **Run Sequentially**: Some scripts may depend on others being run first

## Running Scripts

```bash
# Navigate to the fixes directory
cd backend/scripts/fixes

# Run a specific fix script
python fix_meal_types.py

# Run all fix scripts (if needed)
python fix_migrations_table.py
python fix_null_moods.py
python check_moods_data.py
```

## Safety Notes

- These scripts modify database data directly
- Always run in a controlled environment
- Monitor the output for any errors or warnings
- Consider the impact on related data before running 