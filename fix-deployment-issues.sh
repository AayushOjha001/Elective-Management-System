#!/bin/bash

echo "=== Fixing Critical Deployment Issues ==="

# Make sure we're in the right directory
cd /home/abhiyan/Elective-Management-System-1

# Add all files
echo "Adding updated files to git..."
git add .

# Commit changes
echo "Committing critical deployment fixes..."
git commit -m "CRITICAL FIX: Resolve database permissions and user switching issues

Key fixes:
- Updated Dockerfile.prod to run as root initially for proper permissions
- Enhanced startup script with intelligent user switching (root->django)
- Added robust database directory creation with permission testing
- Fixed all Django management commands to run as correct user
- Added fallback database path handling
- Improved error handling and debugging output

This should resolve the 'unable to open database file' error." || echo "No changes to commit"

echo ""
echo "=== Ready for Deployment ==="
echo "✅ Database permission fixes applied"
echo "✅ User switching logic improved"  
echo "✅ Startup script enhanced"
echo "✅ Error handling added"
echo ""
echo "To deploy to Render:"
echo "1. Push to your git repository:"
echo "   git push origin main"
echo "2. Go to Render dashboard and trigger a manual deploy"
echo "3. Monitor the build and runtime logs"
echo ""
echo "Expected fixes:"
echo "- Database file will be created with correct permissions"
echo "- Application will start as root, fix permissions, then run as django user"
echo "- Better error messages for debugging"
