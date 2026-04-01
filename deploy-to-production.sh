#!/bin/bash
# NEXUS Quick Deployment Script
# This script automates the deployment to Cloudflare Pages and Railway

set -e

echo "🚀 NEXUS Production Deployment"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check Prerequisites
echo -e "${YELLOW}Step 1: Checking Prerequisites...${NC}"

if ! command -v wrangler &> /dev/null; then
    echo -e "${RED}❌ Wrangler CLI not found${NC}"
    echo "Installing wrangler..."
    npm install -g wrangler
fi

if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}⚠️  Railway CLI not found${NC}"
    echo "Installing railway..."
    npm install -g @railway/cli
fi

echo -e "${GREEN}✅ Prerequisites check complete${NC}"
echo ""

# Step 2: Deploy Frontend to Cloudflare Pages
echo -e "${YELLOW}Step 2: Deploying Frontend to Cloudflare Pages...${NC}"
echo "This will open a browser for authentication."
echo "Please login to your Cloudflare account."
read -p "Press Enter to continue..."

cd /app/frontend/build

echo "Deploying to Cloudflare Pages..."
wrangler pages deploy . --project-name nexus-ai-social --branch main

FRONTEND_URL="https://nexus-ai-social.pages.dev"
echo -e "${GREEN}✅ Frontend deployed!${NC}"
echo -e "   URL: ${GREEN}${FRONTEND_URL}${NC}"
echo ""

# Step 3: Deploy Backend to Railway
echo -e "${YELLOW}Step 3: Deploying Backend to Railway...${NC}"
echo "This will open a browser for authentication."
echo "Please login to your Railway account."
read -p "Press Enter to continue..."

cd /app/backend

echo "Initializing Railway project..."
railway init

echo "Deploying backend..."
railway up

echo -e "${YELLOW}⚠️  IMPORTANT: Set environment variables in Railway dashboard${NC}"
echo "1. Go to Railway dashboard"
echo "2. Click 'Variables' tab"
echo "3. Copy and paste variables from: /app/backend/.env"
echo "4. Add these required variables:"
echo "   - MONGO_URL (from MongoDB Atlas)"
echo "   - CORS_ORIGINS=${FRONTEND_URL}"
echo "   - ENVIRONMENT=production"
echo ""

# Step 4: Get Backend URL
echo -e "${YELLOW}Step 4: Configure Backend URL...${NC}"
echo "After Railway deploys, you'll get a URL like:"
echo "  nexus-backend-production-xxxx.up.railway.app"
echo ""
read -p "Enter your Railway backend URL: " BACKEND_URL

if [ -z "$BACKEND_URL" ]; then
    echo -e "${RED}❌ Backend URL is required${NC}"
    exit 1
fi

# Add https if not present
if [[ ! "$BACKEND_URL" =~ ^https?:// ]]; then
    BACKEND_URL="https://$BACKEND_URL"
fi

echo -e "${GREEN}✅ Backend URL set: ${BACKEND_URL}${NC}"
echo ""

# Step 5: Update Frontend Environment
echo -e "${YELLOW}Step 5: Updating Frontend Environment Variable...${NC}"
echo "Setting REACT_APP_BACKEND_URL in Cloudflare Pages..."
echo ""
echo -e "${YELLOW}⚠️  MANUAL STEP REQUIRED:${NC}"
echo "1. Go to: https://dash.cloudflare.com/"
echo "2. Select project: nexus-ai-social"
echo "3. Go to Settings → Environment variables"
echo "4. Add variable:"
echo "   Name: REACT_APP_BACKEND_URL"
echo "   Value: ${BACKEND_URL}"
echo "5. Save and redeploy"
echo ""
read -p "Press Enter after you've set the environment variable..."

# Redeploy frontend with new env
cd /app/frontend/build
wrangler pages deploy . --project-name nexus-ai-social --branch main

echo ""
echo -e "${GREEN}✅ Frontend redeployed with backend URL${NC}"
echo ""

# Step 6: Summary
echo "================================"
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "================================"
echo ""
echo "Your NEXUS platform is now live:"
echo ""
echo -e "Frontend: ${GREEN}${FRONTEND_URL}${NC}"
echo -e "Backend:  ${GREEN}${BACKEND_URL}${NC}"
echo ""
echo "Next steps:"
echo "1. Test frontend: Open ${FRONTEND_URL} in browser"
echo "2. Test backend: curl ${BACKEND_URL}/api/health"
echo "3. Verify all pages load correctly"
echo "4. Test AI services"
echo "5. Configure monitoring (optional)"
echo ""
echo -e "${YELLOW}⚠️  SECURITY REMINDERS:${NC}"
echo "- Change passwords for GitHub, Gmail"
echo "- Enable 2FA on all accounts"
echo "- Rotate API keys"
echo "- Update CORS_ORIGINS in Railway to production domain only"
echo ""
echo -e "${GREEN}Deployment guide: /app/PRODUCTION_DEPLOYMENT_PACKAGE.md${NC}"
