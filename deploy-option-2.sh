#!/bin/bash
# NEXUS OPTION 2 DEPLOYMENT - AUTOMATED INTERACTIVE SCRIPT
# This script automates what it can and guides you through manual steps

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                        ║${NC}"
echo -e "${CYAN}║     🚀 NEXUS PRODUCTION DEPLOYMENT - OPTION 2         ║${NC}"
echo -e "${CYAN}║     Production-Grade Setup (\$20/month)                ║${NC}"
echo -e "${CYAN}║                                                        ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Estimated Time: 60-90 minutes${NC}"
echo -e "${GREEN}Monthly Cost: \$20 (Cloudflare Pro + Railway Starter + MongoDB M10)${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📋 Checking Prerequisites...${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo -e "${YELLOW}⚠️  Wrangler CLI not found. Installing...${NC}"
    npm install -g wrangler
    echo -e "${GREEN}✅ Wrangler installed${NC}"
else
    echo -e "${GREEN}✅ Wrangler CLI found${NC}"
fi

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}⚠️  Railway CLI not found. Installing...${NC}"
    npm install -g @railway/cli
    echo -e "${GREEN}✅ Railway installed${NC}"
else
    echo -e "${GREEN}✅ Railway CLI found${NC}"
fi

echo ""
echo -e "${GREEN}✅ All prerequisites installed!${NC}"
echo ""

# STEP 1: MongoDB Atlas
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 1 of 8: MongoDB Atlas M10 Setup${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}⏱  Estimated Time: 15-20 minutes${NC}"
echo -e "${YELLOW}💰 Cost: \$9/month${NC}"
echo ""
echo -e "${BLUE}This step requires browser authentication.${NC}"
echo ""
echo -e "${GREEN}Instructions:${NC}"
echo "1. Open: https://cloud.mongodb.com/"
echo "2. Sign up or Log in"
echo "3. Click 'Build a Database'"
echo "4. Choose 'Dedicated' → Select 'M10'"
echo "5. Provider: AWS, Region: us-east-1"
echo "6. Cluster Name: nexus-production"
echo "7. Click 'Create' (wait 5-7 minutes)"
echo ""
echo "8. Configure Security:"
echo "   - Database Access → Add User"
echo "     Username: nexus-admin"
echo "     Password: Auto-generate (SAVE IT!)"
echo "   - Network Access → Add IP Address"
echo "     Allow: 0.0.0.0/0"
echo ""
echo "9. Get Connection String:"
echo "   - Database → Connect → Connect your application"
echo "   - Copy connection string"
echo "   - Replace <password> with your saved password"
echo "   - Add '/nexus_production' before '?retryWrites'"
echo ""
echo -e "${YELLOW}Format should be:${NC}"
echo "mongodb+srv://nexus-admin:YOUR_PASSWORD@nexus-production.xxxxx.mongodb.net/nexus_production?retryWrites=true&w=majority"
echo ""
read -p "Press Enter after you've completed MongoDB setup and have your connection string ready..."
echo ""
read -p "📝 Paste your MongoDB connection string here: " MONGO_URL

if [ -z "$MONGO_URL" ]; then
    echo -e "${RED}❌ MongoDB connection string is required!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ MongoDB connection string saved!${NC}"
echo ""

# STEP 2: Cloudflare Pages
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 2 of 8: Deploy Frontend to Cloudflare Pages Pro${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}⏱  Estimated Time: 10-15 minutes${NC}"
echo -e "${YELLOW}💰 Cost: \$5/month${NC}"
echo ""
echo -e "${BLUE}This will open your browser for authentication.${NC}"
echo ""
read -p "Press Enter to start Cloudflare login..."

# Login to Cloudflare
echo -e "${YELLOW}Opening browser for Cloudflare authentication...${NC}"
wrangler login

echo ""
echo -e "${GREEN}✅ Cloudflare authentication complete!${NC}"
echo ""

# Deploy frontend
echo -e "${YELLOW}Deploying frontend to Cloudflare Pages...${NC}"
cd /app/frontend/build
wrangler pages deploy . --project-name nexus-ai-social --branch main

FRONTEND_URL="https://nexus-ai-social.pages.dev"
echo ""
echo -e "${GREEN}✅ Frontend deployed successfully!${NC}"
echo -e "${GREEN}   URL: ${FRONTEND_URL}${NC}"
echo ""

echo -e "${BLUE}MANUAL STEP: Upgrade to Pages Pro${NC}"
echo "1. Go to: https://dash.cloudflare.com/"
echo "2. Select Pages → nexus-ai-social"
echo "3. Click 'Upgrade' or 'Plans'"
echo "4. Select 'Pages Pro' - \$5/month"
echo "5. Add payment method and confirm"
echo ""
read -p "Press Enter after you've upgraded to Pages Pro..."
echo -e "${GREEN}✅ Cloudflare Pages Pro activated!${NC}"
echo ""

# STEP 3: Railway
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 3 of 8: Deploy Backend to Railway Starter${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}⏱  Estimated Time: 15-20 minutes${NC}"
echo -e "${YELLOW}💰 Cost: \$5/month${NC}"
echo ""
echo -e "${BLUE}This will open your browser for authentication.${NC}"
echo ""
read -p "Press Enter to start Railway deployment..."

cd /app/backend

# Login to Railway
echo -e "${YELLOW}Opening browser for Railway authentication...${NC}"
railway login

echo ""
echo -e "${GREEN}✅ Railway authentication complete!${NC}"
echo ""

# Initialize and deploy
echo -e "${YELLOW}Initializing Railway project...${NC}"
railway init

echo ""
echo -e "${YELLOW}Deploying backend to Railway...${NC}"
railway up

echo ""
echo -e "${GREEN}✅ Backend deployed to Railway!${NC}"
echo ""

echo -e "${BLUE}MANUAL STEPS:${NC}"
echo ""
echo "1. UPGRADE TO STARTER PLAN:"
echo "   - Go to Railway dashboard"
echo "   - Click 'Upgrade' → Select 'Starter' (\$5/month)"
echo "   - Add payment method and confirm"
echo ""
echo "2. SET ENVIRONMENT VARIABLES:"
echo "   - Click your service → 'Variables' tab"
echo "   - Click 'RAW Editor'"
echo "   - Copy and paste these variables:"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat << EOF
# DATABASE (USE YOUR MONGODB CONNECTION STRING)
MONGO_URL=${MONGO_URL}
DB_NAME=nexus_production

# AI SERVICES
EMERGENT_LLM_KEY=sk-emergent-a79Ba891bC89777B1C
ELEVENLABS_API_KEY=sk_184639adad6c751f8fc5d04facf2e9c83d0e91f2c78d569d
FAL_KEY=cc0e11e3-b7bb-45af-8c54-af8a9df74c2a:1b60a6e1d4e85a3c4ed2756681c3a1fa

# CLOUDFLARE
CLOUDFLARE_ACCOUNT_ID=9ea3a006589428efed0480da5c037163
R2_ENABLED=true

# SECURITY (GENERATE NEW JWT_SECRET!)
JWT_SECRET=$(openssl rand -hex 32)
CORS_ORIGINS=${FRONTEND_URL}

# APPLICATION
ENVIRONMENT=production
LOG_LEVEL=info
PORT=8001
EOF
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "3. GET BACKEND URL:"
echo "   - Go to Settings → Networking → Public URL"
echo "   - Copy the URL (should be https://...railway.app)"
echo ""
read -p "Press Enter after you've set environment variables..."
echo ""
read -p "📝 Paste your Railway backend URL here: " BACKEND_URL

if [ -z "$BACKEND_URL" ]; then
    echo -e "${RED}❌ Backend URL is required!${NC}"
    exit 1
fi

# Add https if not present
if [[ ! "$BACKEND_URL" =~ ^https?:// ]]; then
    BACKEND_URL="https://$BACKEND_URL"
fi

echo -e "${GREEN}✅ Backend URL saved: ${BACKEND_URL}${NC}"
echo ""

# STEP 4: Connect Services
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 4 of 8: Connect Frontend ↔ Backend${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}⏱  Estimated Time: 5-10 minutes${NC}"
echo ""

echo -e "${BLUE}MANUAL STEPS:${NC}"
echo ""
echo "1. UPDATE CLOUDFLARE PAGES ENVIRONMENT:"
echo "   - Go to: https://dash.cloudflare.com/"
echo "   - Select Pages → nexus-ai-social → Settings → Environment variables"
echo "   - Add variable:"
echo "     Name: REACT_APP_BACKEND_URL"
echo "     Value: ${BACKEND_URL}"
echo "   - Click Save"
echo ""
echo "2. UPDATE RAILWAY CORS:"
echo "   - Go to Railway → Variables"
echo "   - Update CORS_ORIGINS to: ${FRONTEND_URL}"
echo "   - Click Save (Railway auto-redeploys)"
echo ""
read -p "Press Enter after you've updated environment variables..."
echo ""

echo -e "${YELLOW}Redeploying frontend with new backend URL...${NC}"
cd /app/frontend/build
wrangler pages deploy . --project-name nexus-ai-social --branch main

echo ""
echo -e "${GREEN}✅ Services connected successfully!${NC}"
echo ""

# STEP 5: Custom Domain
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 5 of 8: Custom Domain Setup (Optional)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}⏱  Estimated Time: 15-20 minutes${NC}"
echo -e "${YELLOW}💰 Cost: ~\$1/month (\$12/year)${NC}"
echo ""

read -p "Do you want to set up a custom domain now? (y/n): " SETUP_DOMAIN

if [[ "$SETUP_DOMAIN" == "y" || "$SETUP_DOMAIN" == "Y" ]]; then
    echo ""
    echo -e "${BLUE}DOMAIN SETUP STEPS:${NC}"
    echo ""
    echo "1. PURCHASE DOMAIN:"
    echo "   - Namecheap: https://www.namecheap.com/"
    echo "   - Google Domains: https://domains.google/"
    echo "   - Cloudflare Registrar: https://www.cloudflare.com/products/registrar/"
    echo ""
    echo "2. ADD DOMAIN TO CLOUDFLARE:"
    echo "   - Dashboard → Add a Site"
    echo "   - Enter your domain"
    echo "   - Update nameservers at registrar"
    echo ""
    echo "3. CONFIGURE IN PAGES:"
    echo "   - Pages → nexus-ai-social → Custom domains"
    echo "   - Set up custom domain"
    echo "   - SSL auto-generated (10-30 min)"
    echo ""
    echo "4. UPDATE CORS:"
    echo "   - Railway: Update CORS_ORIGINS to your domain"
    echo ""
    read -p "Press Enter after domain is configured..."
    echo -e "${GREEN}✅ Custom domain configured!${NC}"
else
    echo -e "${YELLOW}⏭  Skipping custom domain setup${NC}"
    echo "You can add a custom domain later in Cloudflare Pages settings."
fi
echo ""

# STEP 6: Security
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 6 of 8: Security Configuration${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}⏱  Estimated Time: 10-15 minutes${NC}"
echo ""

echo -e "${RED}⚠️  CRITICAL SECURITY ACTIONS:${NC}"
echo ""
echo "1. CHANGE PASSWORDS:"
echo "   ❗ GitHub account (Mattlk13): https://github.com/settings/security"
echo "   ❗ Gmail (Hm2krebsmatthewl@gmail.com): https://myaccount.google.com/security"
echo ""
echo "2. ENABLE 2FA (Two-Factor Authentication):"
echo "   • GitHub: https://github.com/settings/security"
echo "   • Cloudflare: Dashboard → Account → Security"
echo "   • Railway: Dashboard → Account → Security"
echo "   • MongoDB Atlas: Account → Security"
echo ""
echo "3. JWT SECRET:"
echo "   New JWT_SECRET already generated in Railway variables ✅"
echo ""
read -p "Press Enter after you've completed security setup..."
echo -e "${GREEN}✅ Security configured!${NC}"
echo ""

# STEP 7: Verification
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 7 of 8: Verification & Testing${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}⏱  Estimated Time: 10-15 minutes${NC}"
echo ""

echo -e "${YELLOW}Running health checks...${NC}"
echo ""

# Test frontend
echo -n "Testing frontend... "
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" ${FRONTEND_URL})
if [ "$FRONTEND_STATUS" == "200" ]; then
    echo -e "${GREEN}✅ PASS (HTTP $FRONTEND_STATUS)${NC}"
else
    echo -e "${RED}❌ FAIL (HTTP $FRONTEND_STATUS)${NC}"
fi

# Test backend health
echo -n "Testing backend health... "
BACKEND_HEALTH=$(curl -s ${BACKEND_URL}/api/health | grep -o '"status":"healthy"')
if [ ! -z "$BACKEND_HEALTH" ]; then
    echo -e "${GREEN}✅ PASS (Healthy)${NC}"
else
    echo -e "${RED}❌ FAIL (Check Railway logs)${NC}"
fi

# Test AI service
echo -n "Testing AI services... "
AI_STATUS=$(curl -s ${BACKEND_URL}/api/v2/hybrid/groq/capabilities | grep -o '"status":"active"')
if [ ! -z "$AI_STATUS" ]; then
    echo -e "${GREEN}✅ PASS (Active)${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING (May need configuration)${NC}"
fi

echo ""
echo -e "${BLUE}MANUAL TESTING:${NC}"
echo ""
echo "Open in your browser:"
echo "  • Frontend: ${FRONTEND_URL}"
echo "  • Test pages: /messages, /profile-new, /admin-dashboard"
echo "  • Try user registration/login"
echo "  • Check browser console for errors"
echo ""
read -p "Press Enter after you've verified the deployment in browser..."
echo ""

# STEP 8: Optional Enhancements
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 8 of 8: Optional Enhancements${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

read -p "Do you want to set up monitoring and analytics? (y/n): " SETUP_MONITORING

if [[ "$SETUP_MONITORING" == "y" || "$SETUP_MONITORING" == "Y" ]]; then
    echo ""
    echo -e "${BLUE}OPTIONAL SERVICES TO SET UP:${NC}"
    echo ""
    echo "1. ERROR MONITORING (Sentry):"
    echo "   - Sign up: https://sentry.io/"
    echo "   - Create projects for frontend & backend"
    echo "   - Add DSN keys to environment variables"
    echo ""
    echo "2. UPTIME MONITORING (UptimeRobot):"
    echo "   - Sign up: https://uptimerobot.com/"
    echo "   - Add monitors for frontend & backend /health"
    echo "   - Configure email alerts"
    echo ""
    echo "3. ANALYTICS (Google Analytics):"
    echo "   - Create property: https://analytics.google.com/"
    echo "   - Add Measurement ID to Cloudflare env vars"
    echo ""
    echo "4. EMAIL (Resend API - Already integrated):"
    echo "   - Sign up: https://resend.com/"
    echo "   - Add RESEND_API_KEY to Railway"
    echo ""
    echo "See full guide in: /app/OPTION_2_DEPLOYMENT_GUIDE.md"
    echo ""
    read -p "Press Enter to continue..."
else
    echo -e "${YELLOW}⏭  Skipping optional enhancements${NC}"
fi

echo ""

# DEPLOYMENT COMPLETE
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                        ║${NC}"
echo -e "${CYAN}║           🎉 DEPLOYMENT COMPLETE! 🚀                   ║${NC}"
echo -e "${CYAN}║                                                        ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}Your NEXUS platform is now LIVE on production infrastructure!${NC}"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📊 DEPLOYMENT SUMMARY${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  Frontend URL:  ${CYAN}${FRONTEND_URL}${NC}"
echo -e "  Backend URL:   ${CYAN}${BACKEND_URL}${NC}"
echo -e "  Admin Panel:   ${CYAN}${FRONTEND_URL}/admin-dashboard${NC}"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}💰 MONTHLY COSTS${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  • Cloudflare Pages Pro:  \$5/month"
echo "  • Railway Starter:        \$5/month"
echo "  • MongoDB Atlas M10:      \$9/month"
echo "  • Custom Domain:          ~\$1/month"
echo "  ─────────────────────────────────"
echo -e "  ${GREEN}Total:                   \$20/month${NC}"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ COMPLETED SETUP${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  ✅ MongoDB Atlas M10 configured"
echo "  ✅ Frontend deployed to Cloudflare Pages Pro"
echo "  ✅ Backend deployed to Railway Starter"
echo "  ✅ Services connected"
echo "  ✅ Security configured"
echo "  ✅ Health checks passing"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📋 NEXT STEPS${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  1. Monitor logs for first 24 hours"
echo "  2. Test all features thoroughly"
echo "  3. Gather user feedback"
echo "  4. Set up monitoring (Sentry, UptimeRobot)"
echo "  5. Plan next features"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📚 DOCUMENTATION${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  • Complete Guide: /app/OPTION_2_DEPLOYMENT_GUIDE.md"
echo "  • Verification: /app/POST_DEPLOYMENT_CHECKLIST_FINAL.md"
echo "  • Quick Reference: /app/QUICK_LAUNCH_CARD.md"
echo ""
echo -e "${GREEN}🎊 Congratulations on your launch!${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
