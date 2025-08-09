#!/bin/bash

echo "=== Deploying Elective Management System Fixes to Render ==="

# Make sure we're in the right directory
cd /home/abhiyan/Elective-Management-System-1

# Check git status
echo "Current git status:"
git status

# Add all the modified files
echo ""
echo "Adding deployment fixes to git..."
git add PMS/PMS/settings_production.py
git add Dockerfile.prod
git add start.sh
git add render.yaml
git add DEPLOYMENT_FIXES.md
git add fix-deployment-issues.sh

# Show what we're about to commit
echo ""
echo "Files to be committed:"
git diff --cached --name-only

# Commit the changes
echo ""
echo "Committing deployment fixes..."
git commit -m "Fix deployment issues for Render.com

Key fixes applied:
- Updated database path to use mounted disk volume (/app/data)
- Enhanced Dockerfile.prod with proper data directory permissions  
- Added comprehensive debugging to startup script
- Fixed settings_production.py for production environment
- Updated render.yaml configuration

These changes resolve:
- ALLOWED_HOSTS error (wrong Django settings module)
- SQLite database path issues in production
- Container permission problems with persistent storage"

# Check if render remote exists, if not, provide instructions
if git remote get-url render >/dev/null 2>&1; then
    echo ""
    echo "Found Render remote. Pushing fixes..."
    git push render main
    echo ""
    echo "✅ Successfully pushed fixes to Render!"
else
    echo ""
    echo "⚠️  Render remote not found. Please add it manually:"
    echo ""
    echo "1. Go to your Render dashboard: https://dashboard.render.com"
    echo "2. Select your service: elective-management-system"
    echo "3. Go to Settings > Build & Deploy"
    echo "4. Copy the Git Repository URL (should end with .git)"
    echo "5. Run: git remote add render [YOUR_RENDER_GIT_URL]"
    echo "6. Then run: git push render main"
    echo ""
    echo "Alternatively, you can push to your GitHub repository:"
    echo "git push origin main"
    echo ""
    echo "Then trigger a redeploy from the Render dashboard."
fi

echo ""
echo "=== Next Steps ==="
echo ""
echo "1. 🔄 Monitor deployment in Render dashboard"
echo "   - Go to: https://dashboard.render.com"
echo "   - Check Build & Deploy logs"
echo ""
echo "2. ✅ Verify environment variables in Render:"
echo "   - DJANGO_SETTINGS_MODULE = PMS.settings_production"
echo "   - ALLOWED_HOSTS = *.onrender.com,localhost,127.0.0.1"
echo "   - DEBUG = 0"
echo ""
echo "3. 🚀 Test the application:"
echo "   - Main site: https://elective-management-system.onrender.com"
echo "   - Admin panel: https://elective-management-system.onrender.com/admin/"
echo "   - Login: admin / adminpassword123"
echo ""
echo "4. 📊 Monitor logs for any remaining issues"
echo ""
echo "=== Key Fixes Applied ==="
echo "✅ Database path: Now uses /app/data/db.sqlite3 (mounted volume)"
echo "✅ Container permissions: Added proper data directory setup"
echo "✅ Django settings: Uses production settings module"
echo "✅ Debugging: Enhanced startup script with diagnostics"
echo "✅ Static files: Configured WhiteNoise for production"
