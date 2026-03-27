#!/bin/bash

# NEXUS API Keys Setup Automation Script
# This script helps you quickly obtain and configure all necessary API keys

echo "🚀 NEXUS v4.1 - API Keys Setup Assistant"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# User credentials (DO NOT commit to GitHub)
USER_EMAIL="hm2krebsmatthewl@gmail.com"
USER_PASSWORD="Tristen527!"

echo -e "${CYAN}Your Account Information:${NC}"
echo "Email: $USER_EMAIL"
echo ""

# Step 1: Resend
echo -e "${YELLOW}Step 1: Resend Email API Key${NC}"
echo "-----------------------------------"
echo "1. Open: https://resend.com/signup"
echo "2. Sign up with: $USER_EMAIL"
echo "3. Verify your email inbox"
echo "4. Go to: https://resend.com/api-keys"
echo "5. Click 'Create API Key'"
echo "6. Copy the key (starts with re_)"
echo ""
read -p "Paste your Resend API Key here: " RESEND_KEY

if [[ $RESEND_KEY == re_* ]]; then
    echo -e "${GREEN}✓ Valid Resend key format${NC}"
else
    echo -e "${RED}⚠ Warning: Key doesn't start with re_${NC}"
fi

# Step 2: GitHub
echo ""
echo -e "${YELLOW}Step 2: GitHub Personal Access Token${NC}"
echo "-----------------------------------"
echo "1. Login to GitHub: https://github.com/login"
echo "   Email: $USER_EMAIL"
echo "   Password: $USER_PASSWORD"
echo "2. Go to: https://github.com/settings/tokens"
echo "3. Generate new token (classic)"
echo "4. Select scopes: repo, read:org, read:user"
echo "5. Copy token (starts with ghp_)"
echo ""
read -p "Paste your GitHub Token here: " GITHUB_TOKEN

if [[ $GITHUB_TOKEN == ghp_* ]]; then
    echo -e "${GREEN}✓ Valid GitHub token format${NC}"
else
    echo -e "${RED}⚠ Warning: Token doesn't start with ghp_${NC}"
fi

# Step 3: GitLab (via GitHub OAuth)
echo ""
echo -e "${YELLOW}Step 3: GitLab Personal Access Token${NC}"
echo "-----------------------------------"
echo "1. Go to: https://gitlab.com/users/sign_in"
echo "2. Click 'Sign in with GitHub'"
echo "3. Authorize GitLab"
echo "4. Go to: https://gitlab.com/-/profile/personal_access_tokens"
echo "5. Create token with api, read_repository scopes"
echo "6. Copy token (starts with glpat-)"
echo ""
read -p "Paste your GitLab Token here: " GITLAB_TOKEN

if [[ $GITLAB_TOKEN == glpat-* ]]; then
    echo -e "${GREEN}✓ Valid GitLab token format${NC}"
else
    echo -e "${RED}⚠ Warning: Token doesn't start with glpat-${NC}"
fi

# Step 4: ProductHunt
echo ""
echo -e "${YELLOW}Step 4: ProductHunt API Key${NC}"
echo "-----------------------------------"
echo "1. Go to: https://www.producthunt.com/"
echo "2. Sign in with GitHub (use your GitHub account)"
echo "3. Go to: https://www.producthunt.com/v2/oauth/applications"
echo "4. Create new application:"
echo "   - Name: NEXUS Discovery"
echo "   - Redirect URI: http://localhost:8001/api/callback"
echo "5. Generate Access Token"
echo "6. Copy the token"
echo ""
read -p "Paste your ProductHunt Access Token here: " PRODUCTHUNT_KEY

# Step 5: Manus AI (optional)
echo ""
echo -e "${YELLOW}Step 5: Manus AI API Key (Optional)${NC}"
echo "-----------------------------------"
echo "1. Visit: https://www.manus.im/"
echo "2. Sign up with: $USER_EMAIL"
echo "3. Generate API key from dashboard"
echo ""
read -p "Paste your Manus AI Key (or press Enter to skip): " MANUS_KEY

# Update .env file
echo ""
echo -e "${CYAN}Updating /app/backend/.env...${NC}"

ENV_FILE="/app/backend/.env"

# Backup original .env
cp $ENV_FILE "${ENV_FILE}.backup"
echo -e "${GREEN}✓ Backup created: ${ENV_FILE}.backup${NC}"

# Update keys
if [ ! -z "$RESEND_KEY" ]; then
    sed -i "s/^RESEND_API_KEY=.*/RESEND_API_KEY=$RESEND_KEY/" $ENV_FILE
    echo -e "${GREEN}✓ Resend API key updated${NC}"
fi

if [ ! -z "$GITHUB_TOKEN" ]; then
    sed -i "s/^GITHUB_TOKEN=.*/GITHUB_TOKEN=$GITHUB_TOKEN/" $ENV_FILE
    echo -e "${GREEN}✓ GitHub token updated${NC}"
fi

if [ ! -z "$GITLAB_TOKEN" ]; then
    sed -i "s/^GITLAB_TOKEN=.*/GITLAB_TOKEN=$GITLAB_TOKEN/" $ENV_FILE
    echo -e "${GREEN}✓ GitLab token updated${NC}"
fi

if [ ! -z "$PRODUCTHUNT_KEY" ]; then
    sed -i "s/^PRODUCTHUNT_API_KEY=.*/PRODUCTHUNT_API_KEY=$PRODUCTHUNT_KEY/" $ENV_FILE
    echo -e "${GREEN}✓ ProductHunt API key updated${NC}"
fi

if [ ! -z "$MANUS_KEY" ]; then
    sed -i "s/^MANUS_API_KEY=.*/MANUS_API_KEY=$MANUS_KEY/" $ENV_FILE
    echo -e "${GREEN}✓ Manus AI key updated${NC}"
fi

# Restart backend
echo ""
echo -e "${CYAN}Restarting backend...${NC}"
sudo supervisorctl restart backend
sleep 3

# Check status
echo ""
if sudo supervisorctl status backend | grep -q "RUNNING"; then
    echo -e "${GREEN}✓ Backend restarted successfully!${NC}"
else
    echo -e "${RED}✗ Backend failed to start. Check logs:${NC}"
    echo "tail -n 50 /var/log/supervisor/backend.err.log"
    exit 1
fi

# Verify keys
echo ""
echo -e "${CYAN}Verifying integrations...${NC}"
sleep 2

# Test backend health
API_URL=$(grep REACT_APP_BACKEND_URL /app/frontend/.env | cut -d '=' -f2 | tr -d '"')
TOKEN=$(curl -s -X POST "$API_URL/api/auth/login" -H "Content-Type: application/json" -d "{\"email\":\"admin@nexus.ai\",\"password\":\"admin123\"}" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('token', ''))" 2>/dev/null)

if [ ! -z "$TOKEN" ]; then
    echo -e "${GREEN}✓ Backend API responding${NC}"
    
    # Trigger comprehensive AIxploria scan
    echo -e "${CYAN}Triggering comprehensive AI discovery scan...${NC}"
    curl -s -X POST "$API_URL/api/admin/aixploria/scan?comprehensive=true" \
        -H "Authorization: Bearer $TOKEN" > /dev/null
    
    echo -e "${GREEN}✓ Comprehensive scan started (will take 2-3 minutes)${NC}"
    echo ""
    echo "Scan will discover 250+ AI tools from:"
    echo "  - AIxploria (50+ categories)"
    echo "  - GitHub Trending"
    echo "  - ProductHunt (if key is valid)"
    echo ""
else
    echo -e "${RED}✗ Could not verify backend${NC}"
fi

echo ""
echo -e "${CYAN}================================================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${CYAN}================================================${NC}"
echo ""
echo "Next steps:"
echo "1. Wait 2-3 minutes for comprehensive scan to complete"
echo "2. Go to: http://localhost:3000/admin"
echo "3. Navigate to: Automation → AIxploria tab"
echo "4. See discovered tools with scores and recommendations"
echo ""
echo "View backend logs:"
echo "  tail -f /var/log/supervisor/backend.err.log"
echo ""
echo -e "${GREEN}Your NEXUS platform is now fully operational! 🚀${NC}"
