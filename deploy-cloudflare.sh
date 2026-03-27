#!/bin/bash

# NEXUS Cloudflare Deployment Script
# Deploys frontend to Cloudflare Pages

set -e

echo "🚀 Deploying NEXUS to Cloudflare Pages..."

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "📦 Installing Wrangler CLI..."
    npm install -g wrangler
fi

# Login to Cloudflare (if not already logged in)
echo "🔐 Checking Cloudflare authentication..."
wrangler whoami || wrangler login

# Build frontend
echo "🏗️  Building frontend..."
cd frontend
yarn install
yarn build
cd ..

# Deploy to Cloudflare Pages
echo "☁️  Deploying to Cloudflare Pages..."
wrangler pages deploy frontend/build --project-name=nexus --branch=main

echo "✅ Deployment complete!"
echo "📍 Your site: https://nexus.pages.dev"
echo ""
echo "Next steps:"
echo "1. Add custom domain in Cloudflare dashboard"
echo "2. Configure R2 storage (see CLOUDFLARE_COMPLETE_GUIDE.md)"
echo "3. Set up Cloudflare Images"
