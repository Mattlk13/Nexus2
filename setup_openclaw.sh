#!/bin/bash
# OpenClaw Setup Script for NEXUS
# This script installs and configures OpenClaw autonomous agent framework

set -e

echo "🤖 OpenClaw Setup for NEXUS"
echo "================================"

# Check if directory exists
if [ ! -d "/app/openclaw_agent" ]; then
    echo "❌ OpenClaw directory not found. Cloning repository..."
    cd /app
    git clone https://github.com/openclaw/openclaw.git openclaw_agent
fi

cd /app/openclaw_agent

# Install pnpm if not available
if ! command -v pnpm &> /dev/null; then
    echo "📦 Installing pnpm..."
    npm install -g pnpm
fi

echo "📦 Installing OpenClaw dependencies (this may take 2-3 minutes)..."
pnpm install --prod

echo "🔨 Building OpenClaw..."
pnpm build

echo "✅ OpenClaw installed successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Get an Anthropic API key from: https://console.anthropic.com"
echo "2. Configure: POST /api/admin/openclaw/configure with {\"ANTHROPIC_API_KEY\": \"your_key\"}"
echo "3. Check status: GET /api/admin/openclaw/status"
echo "4. View suggestions: GET /api/admin/openclaw/analysis"
echo ""
echo "🎯 OpenClaw can autonomously:"
echo "   - Analyze code quality"
echo "   - Suggest performance improvements"
echo "   - Detect potential bugs"
echo "   - Recommend new integrations"
echo "   - Optimize database queries"
