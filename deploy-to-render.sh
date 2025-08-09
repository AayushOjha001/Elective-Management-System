#!/bin/bash

# Quick Deploy Script for Render.com
# This script helps you prepare and deploy the Django Elective Management System

set -e

echo "🚀 Django Elective Management System - Render.com Deployment"
echo "============================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if git is initialized
if [ ! -d ".git" ]; then
    print_warning "Git repository not found. Initializing..."
    git init
    print_status "Git repository initialized"
fi

# Check if we have uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    print_info "Found uncommitted changes. Adding all files..."
    git add .
    
    echo -n "Enter commit message (or press Enter for default): "
    read commit_message
    
    if [ -z "$commit_message" ]; then
        commit_message="Deploy to Render - All Docker issues fixed"
    fi
    
    git commit -m "$commit_message"
    print_status "Changes committed"
else
    print_status "No uncommitted changes found"
fi

# Check if remote origin exists
if ! git remote get-url origin >/dev/null 2>&1; then
    echo -n "Enter your GitHub repository URL (https://github.com/username/repo.git): "
    read repo_url
    
    if [ -n "$repo_url" ]; then
        git remote add origin "$repo_url"
        print_status "Remote origin added"
    else
        print_error "Repository URL is required for deployment"
        exit 1
    fi
fi

# Push to GitHub
print_info "Pushing to GitHub..."
git branch -M main
git push -u origin main
print_status "Code pushed to GitHub successfully"

echo ""
echo "🎯 Next Steps for Render.com Deployment:"
echo "========================================="
echo ""
echo "1. Go to https://render.com and sign in with your GitHub account"
echo ""
echo "2. Create PostgreSQL Database:"
echo "   - Click 'New' → 'PostgreSQL'"
echo "   - Name: elective-db"
echo "   - Database: elective_management"
echo "   - User: elective_user"
echo "   - Plan: Free"
echo ""
echo "3. Create Web Service:"
echo "   - Click 'New' → 'Web Service'"
echo "   - Connect your repository"
echo "   - Name: elective-management-system"
echo "   - Environment: Docker"
echo "   - Dockerfile Path: ./Dockerfile.prod"
echo ""
echo "4. Set Environment Variables:"
echo "   DEBUG=0"
echo "   DJANGO_SETTINGS_MODULE=PMS.settings_production"
echo "   ALLOWED_HOSTS=*.onrender.com,localhost,127.0.0.1"
echo "   SECRET_KEY=<click Generate>"
echo "   DATABASE_URL=<from your PostgreSQL database>"
echo ""
echo "5. Deploy and wait for completion (3-5 minutes)"
echo ""
echo "6. Access your app at: https://your-service-name.onrender.com"
echo ""
echo "📋 Default Admin Credentials:"
echo "   Username: admin"
echo "   Password: adminpassword123"
echo "   (Change immediately after first login!)"
echo ""
print_status "Deployment preparation complete!"
print_info "Check RENDER_DEPLOYMENT.md for detailed instructions"
