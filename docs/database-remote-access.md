# Remote Database Access Guide

## Current Configuration

Your production database is configured with the following settings:

- **Server IP**: `65.108.157.187`
- **Database**: `superapp`
- **Username**: `superapp`
- **Password**: `superapp123`
- **Port**: `5432` (PostgreSQL default)

## Remote Access Status

**⚠️ Remote access is NOT currently enabled** - The database is only accessible locally on the server.

## Enabling Remote Access

To enable remote database access, you need to deploy the updated Ansible configuration:

```bash
# Run the deployment to enable remote access
.\scripts\run-ansible-old-deploy.ps1
```

This will:
1. Configure PostgreSQL to listen on all interfaces
2. Add remote access rules to `pg_hba.conf`
3. Open port 5432 in the firewall
4. Restart PostgreSQL to apply changes

## Testing Remote Access

After deployment, test the connection:

```bash
# Test connection using the provided script
.\scripts\test-db-connection.ps1
```

## Manual Connection

Once remote access is enabled, you can connect using:

### Using psql (WSL/Linux)
```bash
PGPASSWORD='superapp123' psql -h 65.108.157.187 -p 5432 -U superapp -d superapp
```

### Using Python
```python
import psycopg2

conn = psycopg2.connect(
    host='65.108.157.187',
    port=5432,
    database='superapp',
    user='superapp',
    password='superapp123'
)
```

### Using Node.js
```javascript
const { Client } = require('pg');

const client = new Client({
  host: '65.108.157.187',
  port: 5432,
  database: 'superapp',
  user: 'superapp',
  password: 'superapp123',
});

await client.connect();
```

## Security Considerations

⚠️ **Important Security Notes:**

1. **Firewall**: Only port 5432 is opened for database access
2. **Authentication**: Uses MD5 password authentication
3. **Network**: Access is restricted to the `superapp` user only
4. **Recommendations**:
   - Use a stronger password in production
   - Consider using SSL connections
   - Restrict access to specific IP addresses if needed
   - Use a VPN for additional security

## Troubleshooting

### Connection Refused
- Check if PostgreSQL is running: `sudo systemctl status postgresql`
- Verify firewall rules: `sudo ufw status`
- Check PostgreSQL logs: `sudo tail -f /var/log/postgresql/postgresql-16-main.log`

### Authentication Failed
- Verify username and password
- Check `pg_hba.conf` configuration
- Ensure the `superapp` user exists: `sudo -u postgres psql -c "\du"`

### Port Not Accessible
- Check if port 5432 is open: `sudo netstat -tlnp | grep 5432`
- Verify firewall configuration: `sudo ufw status numbered`
- Test locally first: `psql -h localhost -U superapp -d superapp`

## Database Management

### Common Commands
```sql
-- List all tables
\dt

-- Show database size
SELECT pg_size_pretty(pg_database_size('superapp'));

-- Show active connections
SELECT * FROM pg_stat_activity;

-- Backup database
pg_dump -h 65.108.157.187 -U superapp superapp > backup.sql

-- Restore database
psql -h 65.108.157.187 -U superapp superapp < backup.sql
```

### Monitoring
```sql
-- Check database statistics
SELECT * FROM pg_stat_database WHERE datname = 'superapp';

-- Check table statistics
SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del 
FROM pg_stat_user_tables;
``` 