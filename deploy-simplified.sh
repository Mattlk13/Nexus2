#!/bin/bash
# Simplified Deployment - Manual Railway Setup

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

clear
echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     🚀 NEXUS DEPLOYMENT - SIMPLIFIED VERSION           ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Install Wrangler only
if ! command -v wrangler &> /dev/null; then
    echo -e "${YELLOW}Installing Wrangler...${NC}"
    npm install -g wrangler
fi
echo -e "${GREEN}✅ Wrangler ready${NC}"
echo ""

# STEP 1: MongoDB
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}STEP 1 of 4: MongoDB Atlas Setup${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "1. Open: https://cloud.mongodb.com/"
echo "2. Sign up/Login"
echo "3. Create Database:"
echo "   - Choose: FREE M0 or M10 ($9/month)"
echo "   - Provider: AWS, Region: us-east-1"
echo "   - Name: nexus-production"
echo ""
echo "4. Security:"
echo "   - Add User: nexus-admin (save password!)"
echo "   - Add IP: 0.0.0.0/0"
echo ""
echo "5. Get connection string:"
echo "   Format: mongodb+srv://nexus-admin:PASSWORD@cluster.mongodb.net/nexus_production?retryWrites=true"
echo ""
read -p "Press ENTER when ready, then paste connection string: " MONGO_URL
echo ""

# STEP 2: Cloudflare
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}STEP 2 of 4: Cloudflare Pages${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Logging in to Cloudflare (browser will open)...${NC}"
wrangler login

echo ""
echo -e "${YELLOW}Deploying frontend...${NC}"
cd /app/frontend/build
wrangler pages deploy . --project-name nexus-ai-social --branch main

FRONTEND_URL="https://nexus-ai-social.pages.dev"
echo ""
echo -e "${GREEN}✅ Frontend live at: ${FRONTEND_URL}${NC}"
echo ""

# STEP 3: Railway (Manual)
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}STEP 3 of 4: Railway Backend (Manual)${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "Railway CLI has issues on this system. Deploy via GitHub instead:"
echo ""
echo "1. Go to: https://railway.app/"
echo "2. Sign in with GitHub"
echo "3. New Project → Deploy from GitHub repo"
echo "4. Select: Mattlk13/nexus-ai-platform"
echo "5. Root directory: /backend"
echo "6. Click Deploy"
echo ""
echo "7. After deployment, go to Variables → Raw Editor"
echo "8. Copy and paste these:"
echo ""
echo "─────────────────────────────────────────────────"
cat << ENVEOF
MONGO_URL=${MONGO_URL}
DB_NAME=nexus_production
EMERGENT_LLM_KEY=sk-emergent-a79Ba891bC89777B1C
ELEVENLABS_API_KEY=sk_184639adad6c751f8fc5d04facf2e9c83d0e91f2c78d569d
FAL_KEY=cc0e11e3-b7bb-45af-8c54-af8a9df74c2a:1b60a6e1d4e85a3c4ed2756681c3a1fa
CLOUDFLARE_ACCOUNT_ID=9ea3a006589428efed0480da5c037163
R2_ENABLED=true
JWT_SECRET=$(openssl rand -hex 32)
CORS_ORIGINS=${FRONTEND_URL}
ENVIRONMENT=production
LOG_LEVEL=info
PORT=8001
ENVEOF
echo "─────────────────────────────────────────────────"
echo ""
echo "9. Get your Railway URL from: Settings → Networking"
echo ""
read -p "Paste your Railway backend URL: " BACKEND_URL

if [[ ! "$BACKEND_URL" =~ ^https?:// ]]; then
    BACKEND_URL="https://$BACKEND_URL"
fi

echo -e "${GREEN}✅ Backend URL: ${BACKEND_URL}${NC}"
echo ""

# STEP 4: Connect
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}STEP 4 of 4: Connect Services${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "1. In Cloudflare Pages:"
echo "   https://dash.cloudflare.com/"
echo "   → Pages → nexus-ai-social → Settings → Environment variables"
echo "   → Add: REACT_APP_BACKEND_URL = ${BACKEND_URL}"
echo ""
echo "2. In Railway:"
echo "   → Variables → Update: CORS_ORIGINS = ${FRONTEND_URL}"
echo ""
read -p "Press ENTER after updating both..."

echo ""
echo -e "${YELLOW}Redeploying frontend...${NC}"
cd /app/frontend/build
wrangler pages deploy . --project-name nexus-ai-social --branch main

echo ""
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo ""
echo -e "Frontend: ${CYAN}${FRONTEND_URL}${NC}"
echo -e "Backend:  ${CYAN}${BACKEND_URL}${NC}"
echo ""
echo "Test your site now!"
echo ""
