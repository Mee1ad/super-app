# Incremental Database Migrations

## Overview

This project now uses a proper incremental migration system that follows database migration best practices. The system provides:

- **Versioned migrations** with proper dependency management
- **Rollback capability** to revert changes
- **Migration state tracking** to know what's been applied
- **Incremental execution** - only runs pending migrations
- **Dependency checking** to ensure migrations run in correct order

## Migration Structure

```
db/
├── migrations/
│   ├── __init__.py
│   ├── base.py                    # Base migration classes
│   ├── 001_initial_schema.py      # Initial database setup
│   ├── 002_add_user_authentication.py
│   ├── 003_add_changelog_publishing.py
│   ├── 004_seed_default_roles.py
│   └── 005_seed_initial_data.py
└── migrate_incremental.py         # Migration runner
```

## Migration Files

Each migration file contains a class that inherits from `Migration` and implements:

- `get_version()` - Returns migration version (e.g., "001")
- `get_name()` - Returns migration name
- `get_description()` - Returns migration description
- `get_dependencies()` - Returns list of required migration versions
- `up()` - Applies the migration
- `down()` - Rolls back the migration

### Example Migration

```python
from db.migrations.base import Migration
from db.session import database

class AddNewColumnMigration(Migration):
    def get_version(self) -> str:
        return "006"
    
    def get_name(self) -> str:
        return "add_new_column"
    
    def get_description(self) -> str:
        return "Add new_column to users table"
    
    def get_dependencies(self) -> list[str]:
        return ["001"]  # Depends on initial schema
    
    async def up(self) -> None:
        await database.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS new_column VARCHAR(255)
        """)
    
    async def down(self) -> None:
        await database.execute("""
            ALTER TABLE users 
            DROP COLUMN IF EXISTS new_column
        """)
```

## Usage

### Check Migration Status

```bash
python db/migrate_incremental.py status
```

### Run All Pending Migrations

```bash
python db/migrate_incremental.py migrate
```

### Run Migrations Up to Specific Version

```bash
python db/migrate_incremental.py migrate --target 003
```

### Rollback to Specific Version

```bash
python db/migrate_incremental.py rollback --target 002
```

### Dry Run (Show What Would Be Done)

```bash
python db/migrate_incremental.py migrate --dry-run
```

## Migration History

| Version | Name | Description | Dependencies |
|---------|------|-------------|--------------|
| 001 | initial_schema | Create initial database schema | None |
| 002 | add_user_authentication | Add auth fields to users table | 001 |
| 003 | add_changelog_publishing | Add publishing fields to changelog | 001 |
| 004 | seed_default_roles | Create default roles | 001 |
| 005 | seed_initial_data | Seed moods and meal types | 001 |

## Best Practices

### 1. Version Naming

- Use sequential numbers: 001, 002, 003, etc.
- Use leading zeros for proper sorting
- Keep versions simple and sequential

### 2. Dependencies

- Always specify dependencies explicitly
- Keep dependency chains as short as possible
- Avoid circular dependencies

### 3. Migration Content

- Make migrations idempotent (safe to run multiple times)
- Use `IF NOT EXISTS` and `IF EXISTS` clauses
- Include both `up()` and `down()` methods
- Test rollbacks before deploying

### 4. Data Migrations

- Separate schema changes from data changes
- Use separate migrations for seeding data
- Handle existing data gracefully

### 5. Testing

- Test migrations in development first
- Test rollbacks
- Test with production-like data

## Migration State

The system tracks migration state in a `migrations` table:

```sql
CREATE TABLE migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    dependencies TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Error Handling

- Migrations are atomic - if one fails, the entire batch is rolled back
- Failed migrations are not marked as applied
- Check logs for detailed error information
- Use `--dry-run` to preview changes

## Rollback Strategy

Rollbacks are performed in reverse order:

1. Find all applied migrations after target version
2. Execute `down()` methods in reverse order
3. Remove migration records from tracking table

**Warning**: Rollbacks can be destructive. Always backup data before rolling back.

## Integration with CI/CD

### Pre-deployment

```bash
# Check migration status
python db/migrate_incremental.py status

# Run migrations
python db/migrate_incremental.py migrate
```

### Post-deployment Verification

```bash
# Verify all migrations applied
python db/migrate_incremental.py status
```

## Troubleshooting

### Migration Already Applied

If a migration shows as already applied but shouldn't be:

```bash
# Check the migrations table
SELECT * FROM migrations ORDER BY version;

# Manually remove if needed (be careful!)
DELETE FROM migrations WHERE version = 'XXX';
```

### Dependency Issues

If migrations fail due to dependencies:

1. Check the dependency chain
2. Ensure all required migrations are applied
3. Run migrations in correct order

### Database Connection Issues

- Verify database configuration
- Check network connectivity
- Ensure database user has proper permissions

## Migration from Old System

To migrate from the old migration system:

1. **Backup your database**
2. Run the new migration system: `python db/migrate_incremental.py migrate`
3. The system will detect existing tables and skip initial migrations
4. Verify with: `python db/migrate_incremental.py status`

## Future Enhancements

- **Migration validation** - Validate migration files before running
- **Migration templates** - Generate migration boilerplate
- **Migration testing** - Automated testing of migrations
- **Migration documentation** - Auto-generate migration docs
- **Migration rollback testing** - Test rollbacks automatically 