#!/bin/bash

# Database migration helper script
echo "=== DATABASE MIGRATION HELPER ==="

# Check if backup database exists
if [ -f "/app/data/database_backup.sqlite3" ]; then
    echo "✅ Found backup database file"
    
    # If production database doesn't exist, copy backup
    if [ ! -f "/app/data/pms_production.sqlite3" ]; then
        echo "📦 Copying backup database to production location..."
        cp /app/data/database_backup.sqlite3 /app/data/pms_production.sqlite3
        chown django:django /app/data/pms_production.sqlite3
        chmod 664 /app/data/pms_production.sqlite3
        echo "✅ Database copied successfully"
    else
        echo "⚠️  Production database already exists, skipping copy"
    fi
else
    echo "⚠️  No backup database found, will create fresh database"
fi
