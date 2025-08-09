#!/bin/bash

echo "🔧 Fixing Render.com Deployment Configuration"
echo "============================================="

echo "📋 Current render.yaml configuration:"
echo "- DJANGO_SETTINGS_MODULE: PMS.settings_production"
echo "- ALLOWED_HOSTS: *.onrender.com,localhost,127.0.0.1"
echo "- PostgreSQL database configured"
echo ""

echo "🚨 ISSUE IDENTIFIED:"
echo "The application is using DJANGO_SETTINGS_MODULE='PMS.settings' instead of 'PMS.settings_production'"
echo "This causes ALLOWED_HOSTS=[] (empty) instead of the production configuration."
echo ""

echo "✅ SOLUTION:"
echo "1. Go to your Render dashboard: https://dashboard.render.com/"
echo "2. Find your 'elective-management-system' service"
echo "3. Go to Environment tab"
echo "4. Update DJANGO_SETTINGS_MODULE from 'PMS.settings' to 'PMS.settings_production'"
echo "5. Click 'Save Changes' to trigger a new deployment"
echo ""

echo "🔄 ALTERNATIVE: Re-deploy using render.yaml (Infrastructure as Code)"
echo "This will ensure all environment variables are set correctly:"
echo ""
echo "Steps:"
echo "1. Go to https://dashboard.render.com/create?type=blueprint"
echo "2. Connect your GitHub repository"
echo "3. Upload the render.yaml file (it will override existing config)"
echo "4. Deploy - this will use the correct settings module"
echo ""

echo "📊 After fixing, verify at:"
echo "🌐 https://elective-management-system.onrender.com/"
echo "🔧 https://elective-management-system.onrender.com/admin/"
echo ""

echo "✨ The render.yaml file is already correctly configured!"
echo "The deployment just needs the environment variable updated."

# Check if git is available and show current status
if command -v git &> /dev/null; then
    echo ""
    echo "📁 Current repository status:"
    git status --porcelain
    echo ""
    echo "🏷️  Latest commit:"
    git log --oneline -1
fi

echo ""
echo "🎯 QUICK FIX: Update environment variable in Render dashboard"
echo "   DJANGO_SETTINGS_MODULE = 'PMS.settings_production'"
echo ""
echo "Done! 🚀"
