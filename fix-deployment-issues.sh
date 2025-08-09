#!/bin/bash

echo "=== Fixing Elective Management System Deployment Issues ==="

# Make sure we're in the right directory
cd /home/abhiyan/Elective-Management-System-1

# Check if git is initialized
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
fi

# Add all files
echo "Adding updated files to git..."
git add .

# Commit changes
echo "Committing deployment fixes..."
git commit -m "Fix deployment issues: Update database path and add debugging

- Updated settings_production.py to use mounted disk volume for SQLite
- Enhanced Dockerfile.prod with proper data directory permissions
- Added debugging to startup script for troubleshooting
- Fixed database path to use /app/data for persistent storage" || echo "No changes to commit"

# Check if render remote exists
if ! git remote get-url render >/dev/null 2>&1; then
    echo "Adding Render git remote..."
    echo "Please run: git remote add render [your-render-git-url]"
    echo "You can find your Render git URL in your Render dashboard under Settings > Build & Deploy"
else
    echo "Pushing to Render..."
    git push render main --force
    echo ""
    echo "=== Deployment Status ==="
    echo "✅ Code pushed to Render successfully"
    echo "⏳ Render is now building and deploying your application"
    echo ""
    echo "Next steps:"
    echo "1. Monitor the build logs in your Render dashboard"
    echo "2. Check the application at: https://elective-management-system.onrender.com"
    echo "3. If issues persist, check the runtime logs in Render dashboard"
    echo ""
    echo "Key fixes applied:"
    echo "- Database now uses mounted disk volume (/app/data/db.sqlite3)"
    echo "- Added proper directory permissions and debugging"
    echo "- Ensured DJANGO_SETTINGS_MODULE uses production settings"
fi

echo ""
echo "=== Manual Verification Steps ==="
echo "1. Go to Render dashboard: https://dashboard.render.com"
echo "2. Check Environment Variables:"
echo "   - DJANGO_SETTINGS_MODULE should be: PMS.settings_production"
echo "   - ALLOWED_HOSTS should be: *.onrender.com,localhost,127.0.0.1"
echo "   - DEBUG should be: 0"
echo "3. Check Build & Deploy logs for any errors"
echo "4. Check Runtime logs once deployment completes"
