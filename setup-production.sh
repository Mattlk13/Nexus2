#!/bin/bash
# NEXUS Production Secrets Setup Script
# This script helps you set up all required secrets and tokens

set -e

echo "🔐 NEXUS Production Secrets Setup"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Create secrets directory
mkdir -p /app/.secrets
chmod 700 /app/.secrets

echo -e "${BLUE}[1/10] MongoDB Atlas Setup${NC}"
echo "----------------------------------------"
echo "1. Go to: https://cloud.mongodb.com/v2#/org/"
echo "2. Click 'Create' → 'Shared' (Free M0)"
echo "3. Choose AWS, Region: us-east-1"
echo "4. Create Cluster (wait 3-5 min)"
echo "5. Security → Database Access → Add User"
echo "6. Username: nexus-admin"
echo "7. Password: Auto-generate (copy it!)"
echo "8. Network Access → Add IP → 0.0.0.0/0 (Allow from anywhere)"
echo "9. Connect → Connect your application → Copy connection string"
echo ""
read -p "Enter MongoDB Connection String: " MONGO_URL
echo "MONGO_URL=\"$MONGO_URL\"" > /app/.secrets/mongodb.env
echo -e "${GREEN}✓ MongoDB configured${NC}"
echo ""

echo -e "${BLUE}[2/10] Cloudflare API Token${NC}"
echo "----------------------------------------"
echo "1. Go to: https://dash.cloudflare.com/profile/api-tokens"
echo "2. Click 'Create Token'"
echo "3. Use template: 'Edit Cloudflare Workers'"
echo "4. Or create custom with permissions:"
echo "   - Account.Cloudflare Pages: Edit"
echo "   - Account.Account Settings: Read"
echo "5. Copy the token"
echo ""
read -p "Enter Cloudflare API Token: " CF_TOKEN
read -p "Enter Cloudflare Account ID (9ea3a0065894...): " CF_ACCOUNT_ID
echo "CLOUDFLARE_API_TOKEN=\"$CF_TOKEN\"" > /app/.secrets/cloudflare.env
echo "CLOUDFLARE_ACCOUNT_ID=\"$CF_ACCOUNT_ID\"" >> /app/.secrets/cloudflare.env
echo -e "${GREEN}✓ Cloudflare configured${NC}"
echo ""

echo -e "${BLUE}[3/10] Railway Setup${NC}"
echo "----------------------------------------"
echo "1. Go to: https://railway.app/"
echo "2. Sign up with GitHub"
echo "3. Click profile → Account Settings"
echo "4. Tokens → Create new token"
echo "5. Name: 'NEXUS Production'"
echo "6. Copy the token"
echo ""
read -p "Enter Railway Token: " RAILWAY_TOKEN
echo "RAILWAY_TOKEN=\"$RAILWAY_TOKEN\"" > /app/.secrets/railway.env
echo -e "${GREEN}✓ Railway configured${NC}"
echo ""

echo -e "${BLUE}[4/10] GitHub Secrets Setup${NC}"
echo "----------------------------------------"
echo "Setting up GitHub Actions secrets..."
echo ""
echo "Go to: https://github.com/Mattlk13/nexus-ai-platform/settings/secrets/actions"
echo ""
echo "Add these secrets:"
echo "-------------------"
echo "1. CLOUDFLARE_API_TOKEN = $CF_TOKEN"
echo "2. CLOUDFLARE_ACCOUNT_ID = $CF_ACCOUNT_ID"
echo "3. RAILWAY_TOKEN = $RAILWAY_TOKEN"
echo "4. MONGO_URL = $MONGO_URL"
echo "5. EMERGENT_LLM_KEY = $(grep EMERGENT_LLM_KEY /app/backend/.env | cut -d '=' -f2)"
echo ""
read -p "Press Enter after adding secrets to GitHub..."
echo -e "${GREEN}✓ GitHub secrets documented${NC}"
echo ""

echo -e "${BLUE}[5/10] Production Environment Variables${NC}"
echo "----------------------------------------"
cat > /app/.secrets/production.env << EOF
# Production Environment Variables
# Copy these to your deployment platform (Railway/Render)

# Database
MONGO_URL=$MONGO_URL
DB_NAME=nexus_production

# AI Services
EMERGENT_LLM_KEY=$(grep EMERGENT_LLM_KEY /app/backend/.env | cut -d '=' -f2)
ELEVENLABS_API_KEY=$(grep ELEVENLABS_API_KEY /app/backend/.env | cut -d '=' -f2)
FAL_KEY=$(grep FAL_KEY /app/backend/.env | cut -d '=' -f2)
RUNWAYML_API_KEY=$(grep RUNWAYML_API_KEY /app/backend/.env | cut -d '=' -f2)

# Cloudflare
CLOUDFLARE_ACCOUNT_ID=$CF_ACCOUNT_ID
R2_ENABLED=true
R2_ACCESS_KEY_ID=$(grep R2_ACCESS_KEY_ID /app/backend/.env | cut -d '=' -f2)
R2_SECRET_ACCESS_KEY=$(grep R2_SECRET_ACCESS_KEY /app/backend/.env | cut -d '=' -f2)
R2_ENDPOINT_URL=$(grep R2_ENDPOINT_URL /app/backend/.env | cut -d '=' -f2)
R2_BUCKET_NAME=$(grep R2_BUCKET_NAME /app/backend/.env | cut -d '=' -f2)

# Security
JWT_SECRET=$(openssl rand -hex 32)
CORS_ORIGINS=https://nexus-ai-social.pages.dev

# Application
ENVIRONMENT=production
LOG_LEVEL=info
EOF

echo -e "${GREEN}✓ Production env file created: /app/.secrets/production.env${NC}"
echo ""

echo -e "${BLUE}[6/10] Groq API Key (Optional)${NC}"
echo "----------------------------------------"
echo "For ultra-fast LLM inference:"
echo "1. Go to: https://console.groq.com/"
echo "2. Sign up (free tier available)"
echo "3. API Keys → Create API Key"
echo "4. Copy the key"
echo ""
read -p "Enter Groq API Key (or press Enter to skip): " GROQ_KEY
if [ ! -z "$GROQ_KEY" ]; then
    echo "GROQ_API_KEY=$GROQ_KEY" >> /app/.secrets/production.env
    echo -e "${GREEN}✓ Groq configured${NC}"
else
    echo -e "${YELLOW}⊘ Groq skipped${NC}"
fi
echo ""

echo -e "${BLUE}[7/10] Domain Setup${NC}"
echo "----------------------------------------"
echo "Recommended domain registrars:"
echo "- Namecheap: https://www.namecheap.com/"
echo "- Google Domains: https://domains.google/"
echo "- Cloudflare Registrar: https://www.cloudflare.com/products/registrar/"
echo ""
echo "Suggested domains:"
echo "- nexus-ai.social"
echo "- nexusaimarket.com"
echo "- nexus.ai (premium)"
echo ""
read -p "Enter your domain (or press Enter to skip): " DOMAIN
if [ ! -z "$DOMAIN" ]; then
    echo "DOMAIN=$DOMAIN" >> /app/.secrets/production.env
    echo "REACT_APP_BACKEND_URL=https://api.$DOMAIN" >> /app/.secrets/production.env
    echo -e "${GREEN}✓ Domain configured: $DOMAIN${NC}"
else
    echo "DOMAIN=nexus-ai-social.pages.dev" >> /app/.secrets/production.env
    echo -e "${YELLOW}⊘ Using default Cloudflare domain${NC}"
fi
echo ""

echo -e "${BLUE}[8/10] Email Setup${NC}"
echo "----------------------------------------"
echo "For admin@nexus email:"
echo ""
echo "Option 1: Zoho Mail (Recommended - Free for 5 users)"
echo "  1. Go to: https://www.zoho.com/mail/"
echo "  2. Sign up for free"
echo "  3. Add domain: $DOMAIN"
echo "  4. Verify domain with DNS records"
echo "  5. Create mailbox: admin@$DOMAIN"
echo ""
echo "Option 2: Resend (Already integrated in code)"
echo "  1. Go to: https://resend.com/"
echo "  2. Sign up"
echo "  3. Add domain"
echo "  4. Get API key"
echo ""
read -p "Enter email service (zoho/resend/skip): " EMAIL_SERVICE
if [ "$EMAIL_SERVICE" = "resend" ]; then
    read -p "Enter Resend API Key: " RESEND_KEY
    echo "RESEND_API_KEY=$RESEND_KEY" >> /app/.secrets/production.env
    echo -e "${GREEN}✓ Resend configured${NC}"
else
    echo -e "${YELLOW}⊘ Email setup deferred${NC}"
fi
echo ""

echo -e "${BLUE}[9/10] Security Configuration${NC}"
echo "----------------------------------------"
echo "Generating secure tokens..."

# Generate JWT secret
JWT_SECRET=$(openssl rand -hex 32)
echo "JWT_SECRET=$JWT_SECRET" >> /app/.secrets/production.env

# Generate webhook secret
WEBHOOK_SECRET=$(openssl rand -hex 32)
echo "WEBHOOK_SECRET=$WEBHOOK_SECRET" >> /app/.secrets/production.env

echo -e "${GREEN}✓ Security tokens generated${NC}"
echo ""

echo -e "${BLUE}[10/10] Summary & Next Steps${NC}"
echo "----------------------------------------"
echo ""
echo "✅ Configuration Complete!"
echo ""
echo "Files created:"
echo "  - /app/.secrets/mongodb.env"
echo "  - /app/.secrets/cloudflare.env"
echo "  - /app/.secrets/railway.env"
echo "  - /app/.secrets/production.env (MASTER FILE)"
echo ""
echo "🚀 DEPLOYMENT COMMANDS:"
echo "======================="
echo ""
echo "1. Deploy Frontend to Cloudflare:"
echo "   cd /app/frontend/build"
echo "   wrangler pages deploy . --project-name nexus-ai-social"
echo ""
echo "2. Deploy Backend to Railway:"
echo "   cd /app/backend"
echo "   railway login"
echo "   railway init"
echo "   railway up"
echo "   railway variables set < /app/.secrets/production.env"
echo ""
echo "3. Configure GitHub Secrets (for CI/CD):"
echo "   See: /app/.secrets/github-secrets.txt"
echo ""
echo "📝 IMPORTANT: Keep /app/.secrets/ directory secure!"
echo "    Add to .gitignore: ✓ Already done"
echo ""
echo -e "${GREEN}🎉 Production setup complete!${NC}"
echo ""
