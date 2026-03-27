#!/bin/bash
# NEXUS API Keys Configuration Script
# Usage: ./configure_api_keys.sh

set -e

echo "🔑 NEXUS API Keys Configuration Wizard"
echo "======================================="
echo ""
echo "This script will help you configure all API keys for NEXUS v4.3"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Backup current .env
cp /app/backend/.env /app/backend/.env.backup
echo "✓ Backed up current .env to .env.backup"
echo ""

# Function to update .env key
update_env_key() {
    local key=$1
    local value=$2
    local file="/app/backend/.env"
    
    if grep -q "^${key}=" "$file"; then
        # Key exists, update it
        sed -i "s|^${key}=.*|${key}=${value}|" "$file"
        echo -e "${GREEN}✓${NC} Updated $key"
    else
        # Key doesn't exist, append it
        echo "${key}=${value}" >> "$file"
        echo -e "${GREEN}✓${NC} Added $key"
    fi
}

# Check if running interactively
if [ -t 0 ]; then
    INTERACTIVE=true
else
    INTERACTIVE=false
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  ProductHunt API Key"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Get key from: https://www.producthunt.com"
echo "Login: hm2krebsmatthewl@gmail.com"
echo "Navigate: Profile → API Dashboard → Create Application → Create Token"
echo ""

if [ "$INTERACTIVE" = true ]; then
    read -p "Enter ProductHunt API Key (or press Enter to skip): " PH_KEY
    if [ ! -z "$PH_KEY" ]; then
        update_env_key "PRODUCTHUNT_API_KEY" "$PH_KEY"
    else
        echo -e "${YELLOW}⊘${NC} Skipped ProductHunt"
    fi
else
    echo -e "${YELLOW}⊘${NC} Non-interactive mode - skipped"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  Resend Email API Key"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Get key from: https://resend.com"
echo "Signup with: hm2krebsmatthewl@gmail.com"
echo "Navigate: Dashboard → API Keys → Create Key"
echo ""

if [ "$INTERACTIVE" = true ]; then
    read -p "Enter Resend API Key (starts with 're_'): " RESEND_KEY
    if [ ! -z "$RESEND_KEY" ]; then
        update_env_key "RESEND_API_KEY" "$RESEND_KEY"
    else
        echo -e "${YELLOW}⊘${NC} Skipped Resend"
    fi
else
    echo -e "${YELLOW}⊘${NC} Non-interactive mode - skipped"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  ElevenLabs Voice API Key"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Get key from: https://elevenlabs.io"
echo "Navigate: Settings → API Keys → Create Key"
echo ""

if [ "$INTERACTIVE" = true ]; then
    read -p "Enter ElevenLabs API Key: " ELEVEN_KEY
    if [ ! -z "$ELEVEN_KEY" ]; then
        update_env_key "ELEVENLABS_API_KEY" "$ELEVEN_KEY"
    else
        echo -e "${YELLOW}⊘${NC} Skipped ElevenLabs"
    fi
else
    echo -e "${YELLOW}⊘${NC} Non-interactive mode - skipped"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Fal.ai Image Generation Key"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Get key from: https://fal.ai/dashboard/keys"
echo "Create Key → Add credits (minimum $10)"
echo ""

if [ "$INTERACTIVE" = true ]; then
    read -p "Enter Fal.ai API Key: " FAL_KEY
    if [ ! -z "$FAL_KEY" ]; then
        update_env_key "FAL_KEY" "$FAL_KEY"
    else
        echo -e "${YELLOW}⊘${NC} Skipped Fal.ai"
    fi
else
    echo -e "${YELLOW}⊘${NC} Non-interactive mode - skipped"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  GitHub Token (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Get token from: https://github.com/settings/tokens"
echo "Create: Personal Access Token (Classic)"
echo "Scopes: repo, read:org"
echo ""

if [ "$INTERACTIVE" = true ]; then
    read -p "Enter GitHub Token (or press Enter to skip): " GH_TOKEN
    if [ ! -z "$GH_TOKEN" ]; then
        update_env_key "GITHUB_TOKEN" "$GH_TOKEN"
    else
        echo -e "${YELLOW}⊘${NC} Skipped GitHub"
    fi
else
    echo -e "${YELLOW}⊘${NC} Non-interactive mode - skipped"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  Anthropic API Key (for OpenClaw)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Get key from: https://console.anthropic.com"
echo "Navigate: API Keys → Create Key"
echo ""

if [ "$INTERACTIVE" = true ]; then
    read -p "Enter Anthropic API Key (starts with 'sk-ant-'): " ANT_KEY
    if [ ! -z "$ANT_KEY" ]; then
        # Save to OpenClaw config
        mkdir -p /app/openclaw_agent
        echo "ANTHROPIC_API_KEY=${ANT_KEY}" > /app/openclaw_agent/.env
        echo -e "${GREEN}✓${NC} Configured OpenClaw"
    else
        echo -e "${YELLOW}⊘${NC} Skipped Anthropic/OpenClaw"
    fi
else
    echo -e "${YELLOW}⊘${NC} Non-interactive mode - skipped"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Configuration Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "1. Restart backend: sudo supervisorctl restart backend"
echo "2. Check health: curl http://localhost:3000/api/integrations/status"
echo "3. View dashboard: Visit Admin → Automation → Integrations"
echo ""
echo "Expected health improvement:"
echo "  Before: 18.2% (2/11 active)"
echo "  After:  64-100% (7-11/11 active)"
echo ""

# Ask if should restart now
if [ "$INTERACTIVE" = true ]; then
    read -p "Restart backend now? (y/n): " RESTART
    if [ "$RESTART" = "y" ] || [ "$RESTART" = "Y" ]; then
        echo "Restarting backend..."
        sudo supervisorctl restart backend
        sleep 3
        echo -e "${GREEN}✓${NC} Backend restarted"
        
        # Test health
        API_URL=$(grep REACT_APP_BACKEND_URL /app/frontend/.env | cut -d '=' -f2)
        HEALTH=$(curl -s "$API_URL/api/integrations/status" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"{d['summary']['active']}/{d['summary']['total']} active ({d['summary']['health_score']:.1f}% health)\")")
        echo ""
        echo "🏥 New Health Status: $HEALTH"
    fi
fi

echo ""
echo "🎉 Configuration wizard complete!"
