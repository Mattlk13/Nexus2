#!/bin/bash

# NEXUS API Keys Setup Script
# This script helps you quickly add API keys to NEXUS

echo "🚀 NEXUS API Keys Setup Wizard"
echo "================================"
echo ""
echo "You'll need to obtain API keys from the following services:"
echo "1. Resend (Email) - https://resend.com/signup"
echo "2. ProductHunt (AI Discovery) - https://www.producthunt.com/v2/oauth/applications"
echo "3. GitHub (Code Discovery) - https://github.com/settings/tokens"
echo "4. GitLab (CI/CD) - https://gitlab.com/-/user_settings/personal_access_tokens"
echo ""
echo "📋 Your account credentials: hm2krebsmatthewl@gmail.com / Tristen527!"
echo ""

# Backup current .env
echo "📦 Backing up current .env..."
cp /app/backend/.env /app/backend/.env.backup.$(date +%s)

# Function to update env variable
update_env() {
    local key=$1
    local value=$2
    local file="/app/backend/.env"
    
    if grep -q "^${key}=" "$file"; then
        # Update existing key
        sed -i "s|^${key}=.*|${key}=${value}|" "$file"
    else
        # Add new key
        echo "${key}=${value}" >> "$file"
    fi
}

echo ""
echo "Let's add your API keys one by one (press Enter to skip):"
echo ""

# Resend
read -p "1. Resend API Key (re_...): " RESEND_KEY
if [ ! -z "$RESEND_KEY" ]; then
    update_env "RESEND_API_KEY" "$RESEND_KEY"
    echo "   ✓ Resend key updated"
fi

# ProductHunt
read -p "2. ProductHunt API Token: " PH_KEY
if [ ! -z "$PH_KEY" ]; then
    update_env "PRODUCTHUNT_API_KEY" "$PH_KEY"
    echo "   ✓ ProductHunt key updated"
fi

# GitHub
read -p "3. GitHub Personal Access Token (ghp_...): " GITHUB_KEY
if [ ! -z "$GITHUB_KEY" ]; then
    update_env "GITHUB_TOKEN" "$GITHUB_KEY"
    echo "   ✓ GitHub token updated"
fi

# GitLab
read -p "4. GitLab Personal Access Token (glpat-...): " GITLAB_KEY
if [ ! -z "$GITLAB_KEY" ]; then
    update_env "GITLAB_TOKEN" "$GITLAB_KEY"
    echo "   ✓ GitLab token updated"
fi

# Softr (optional)
read -p "5. Softr API Key (optional): " SOFTR_KEY
if [ ! -z "$SOFTR_KEY" ]; then
    update_env "SOFTR_API_KEY" "$SOFTR_KEY"
    echo "   ✓ Softr key updated"
fi

# Manus AI (optional)
read -p "6. Manus AI API Key (optional): " MANUS_KEY
if [ ! -z "$MANUS_KEY" ]; then
    update_env "MANUS_API_KEY" "$MANUS_KEY"
    echo "   ✓ Manus key updated"
fi

echo ""
echo "✅ Configuration complete!"
echo ""
echo "🔄 Restarting backend to apply changes..."
sudo supervisorctl restart backend
sleep 3

echo ""
echo "📊 Checking backend status..."
sudo supervisorctl status backend

echo ""
echo "🎉 Setup complete! Your integrations are now active."
echo ""
echo "📝 Next steps:"
echo "  1. Visit http://localhost:3000/admin to see the automation panel"
echo "  2. Trigger a comprehensive scan to test all integrations"
echo "  3. Check backend logs: tail -f /var/log/supervisor/backend.err.log"
echo ""
echo "💡 To verify integrations:"
echo "  curl -X GET \"$(grep REACT_APP_BACKEND_URL /app/frontend/.env | cut -d '=' -f2 | tr -d '\"')/api/integrations/status\" | python3 -m json.tool"
