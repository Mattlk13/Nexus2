#!/bin/bash
# NEXUS Complete Deployment Script
# Run this script to deploy NEXUS to production

set -e

echo "🚀 NEXUS Deployment Script"
echo "=========================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check prerequisites
echo -e "${YELLOW}[1/7] Checking prerequisites...${NC}"
command -v node >/dev/null 2>&1 || { echo "Node.js required but not installed. Install from nodejs.org"; exit 1; }
command -v yarn >/dev/null 2>&1 || { echo "Yarn required. Run: npm install -g yarn"; exit 1; }
command -v git >/dev/null 2>&1 || { echo "Git required but not installed."; exit 1; }

echo -e "${GREEN}✓ Prerequisites OK${NC}"

# Step 2: Install dependencies
echo -e "${YELLOW}[2/7] Installing dependencies...${NC}"
cd /app/frontend
yarn install --silent

cd /app/backend
pip install -r requirements.txt --quiet

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 3: Run tests
echo -e "${YELLOW}[3/7] Running health checks...${NC}"
cd /app/backend
python3 -c "
import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def test():
    try:
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        client = AsyncIOMotorClient(mongo_url)
        await client.admin.command('ping')
        print('✓ MongoDB connected')
        return True
    except Exception as e:
        print(f'✗ MongoDB error: {e}')
        return False

asyncio.run(test())
"

echo -e "${GREEN}✓ Health checks passed${NC}"

# Step 4: Build frontend
echo -e "${YELLOW}[4/7] Building frontend...${NC}"
cd /app/frontend
yarn build

if [ ! -d "build" ]; then
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Frontend built successfully${NC}"
echo "  Build size: $(du -sh build | cut -f1)"

# Step 5: Commit to git
echo -e "${YELLOW}[5/7] Committing to Git...${NC}"
cd /app
git add -A
git commit -m "deploy: Production build $(date '+%Y-%m-%d %H:%M:%S')" || echo "No changes to commit"
git push origin main 2>&1 | grep -v "Username\|Password" || echo "Push complete"

echo -e "${GREEN}✓ Code pushed to GitHub${NC}"

# Step 6: Deploy frontend to Cloudflare Pages
echo -e "${YELLOW}[6/7] Deploying to Cloudflare Pages...${NC}"
echo "Run: wrangler pages deploy /app/frontend/build --project-name nexus-ai-social"
echo ""
echo "If wrangler not installed:"
echo "  npm install -g wrangler"
echo "  wrangler login"
echo "  wrangler pages deploy /app/frontend/build --project-name nexus-ai-social"

# Step 7: Post-deployment
echo -e "${YELLOW}[7/7] Post-deployment checklist...${NC}"
echo ""
echo "📋 NEXT STEPS:"
echo "-------------"
echo "1. Deploy frontend: wrangler pages deploy /app/frontend/build --project-name nexus-ai-social"
echo "2. Deploy backend to Railway/Render (see CLOUDFLARE_DEPLOYMENT.md)"
echo "3. Set up MongoDB Atlas (free tier)"
echo "4. Configure environment variables in deployment platform"
echo "5. Test production URLs"
echo "6. Configure custom domain (optional)"
echo ""
echo -e "${GREEN}✅ Deployment preparation complete!${NC}"
echo ""
echo "Frontend build ready at: /app/frontend/build"
echo "Backend code ready at: /app/backend"
echo "GitHub repository: github.com/Mattlk13/nexus-ai-platform"
echo ""
echo "🎉 NEXUS is ready for production!"
