#!/bin/bash
# Cloudflare Automated Setup for www.nexussocialmarket.com
# Uses Cloudflare API to configure domain

CLOUDFLARE_TOKEN="cfat_A3gq1xqMrVXBtWQN7cqOaNuFSiFS4RBGRsqezGXEd3e6d497"
DOMAIN="nexussocialmarket.com"
SUBDOMAIN="www"
EMERGENT_URL="model-exchange-2.preview.emergentagent.com"

echo "🚀 Cloudflare Automated Setup"
echo "================================"
echo ""

# Function to make Cloudflare API calls
cf_api() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [ -n "$data" ]; then
        curl -s -X "$method" "https://api.cloudflare.com/client/v4/$endpoint" \
             -H "Authorization: Bearer $CLOUDFLARE_TOKEN" \
             -H "Content-Type: application/json" \
             -d "$data"
    else
        curl -s -X "$method" "https://api.cloudflare.com/client/v4/$endpoint" \
             -H "Authorization: Bearer $CLOUDFLARE_TOKEN" \
             -H "Content-Type: application/json"
    fi
}

echo "Step 1: Verifying Cloudflare API access..."
VERIFY=$(cf_api "GET" "user/tokens/verify")
SUCCESS=$(echo "$VERIFY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)

if [ "$SUCCESS" != "True" ]; then
    echo "⚠️  Token verification failed or has limited permissions"
    echo ""
    echo "This token may need these permissions:"
    echo "  - Zone.DNS (Edit)"
    echo "  - Zone.Zone Settings (Edit)"
    echo "  - Zone.Zone (Read)"
    echo ""
    echo "Current token: $CLOUDFLARE_TOKEN"
    echo ""
    echo "Please verify token permissions at:"
    echo "https://dash.cloudflare.com/profile/api-tokens"
    echo ""
fi

echo ""
echo "Step 2: Checking if domain exists in Cloudflare..."
ZONES=$(cf_api "GET" "zones?name=$DOMAIN")
ZONE_ID=$(echo "$ZONES" | python3 -c "import sys,json; zones=json.load(sys.stdin).get('result', []); print(zones[0]['id'] if zones else '')" 2>/dev/null)

if [ -z "$ZONE_ID" ]; then
    echo "❌ Domain '$DOMAIN' not found in Cloudflare"
    echo ""
    echo "You need to add the domain first:"
    echo "1. Go to https://dash.cloudflare.com"
    echo "2. Click 'Add site'"
    echo "3. Enter: $DOMAIN"
    echo "4. Choose Free plan"
    echo "5. Update nameservers at your domain registrar"
    echo "6. Wait for domain to become active (can take 24-48 hours)"
    echo ""
    echo "After domain is active, run this script again."
    exit 1
fi

echo "✅ Domain found! Zone ID: $ZONE_ID"
echo ""

echo "Step 3: Checking existing DNS records..."
DNS_RECORDS=$(cf_api "GET" "zones/$ZONE_ID/dns_records?name=$SUBDOMAIN.$DOMAIN")
EXISTING=$(echo "$DNS_RECORDS" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('result', [])))" 2>/dev/null)

echo "Found $EXISTING existing DNS record(s) for $SUBDOMAIN.$DOMAIN"
echo ""

echo "Step 4: Creating/Updating DNS records..."

# Create CNAME record for www pointing to Emergent
CNAME_DATA='{
  "type": "CNAME",
  "name": "'$SUBDOMAIN'",
  "content": "'$EMERGENT_URL'",
  "ttl": 1,
  "proxied": true,
  "comment": "NEXUS platform on Emergent"
}'

if [ "$EXISTING" -gt 0 ]; then
    # Update existing record
    RECORD_ID=$(echo "$DNS_RECORDS" | python3 -c "import sys,json; records=json.load(sys.stdin).get('result', []); print(records[0]['id'] if records else '')" 2>/dev/null)
    
    if [ -n "$RECORD_ID" ]; then
        echo "Updating existing DNS record..."
        UPDATE=$(cf_api "PUT" "zones/$ZONE_ID/dns_records/$RECORD_ID" "$CNAME_DATA")
        SUCCESS=$(echo "$UPDATE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)
        
        if [ "$SUCCESS" = "True" ]; then
            echo "✅ DNS record updated"
        else
            echo "⚠️  Failed to update DNS record"
            echo "$UPDATE"
        fi
    fi
else
    # Create new record
    echo "Creating new DNS record..."
    CREATE=$(cf_api "POST" "zones/$ZONE_ID/dns_records" "$CNAME_DATA")
    SUCCESS=$(echo "$CREATE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)
    
    if [ "$SUCCESS" = "True" ]; then
        echo "✅ DNS record created"
    else
        echo "⚠️  Failed to create DNS record"
        echo "$CREATE"
    fi
fi

echo ""
echo "Step 5: Configuring SSL/TLS settings..."

# Set SSL mode to Full
SSL_DATA='{"value": "full"}'
SSL_UPDATE=$(cf_api "PATCH" "zones/$ZONE_ID/settings/ssl" "$SSL_DATA")
echo "✅ SSL/TLS mode set to Full"

# Enable Always Use HTTPS
HTTPS_DATA='{"value": "on"}'
HTTPS_UPDATE=$(cf_api "PATCH" "zones/$ZONE_ID/settings/always_use_https" "$HTTPS_DATA")
echo "✅ Always Use HTTPS enabled"

# Enable Automatic HTTPS Rewrites
AUTO_HTTPS_DATA='{"value": "on"}'
AUTO_HTTPS_UPDATE=$(cf_api "PATCH" "zones/$ZONE_ID/settings/automatic_https_rewrites" "$AUTO_HTTPS_DATA")
echo "✅ Automatic HTTPS Rewrites enabled"

echo ""
echo "Step 6: Enabling performance features..."

# Enable Brotli compression
BROTLI_DATA='{"value": "on"}'
cf_api "PATCH" "zones/$ZONE_ID/settings/brotli" "$BROTLI_DATA" > /dev/null
echo "✅ Brotli compression enabled"

# Enable Auto Minify
MINIFY_DATA='{"value": {"css": "on", "html": "on", "js": "on"}}'
cf_api "PATCH" "zones/$ZONE_ID/settings/minify" "$MINIFY_DATA" > /dev/null
echo "✅ Auto-minify enabled (JS, CSS, HTML)"

echo ""
echo "================================"
echo "✅ Cloudflare Setup Complete!"
echo "================================"
echo ""
echo "Your domain configuration:"
echo "  Domain: $SUBDOMAIN.$DOMAIN"
echo "  Points to: $EMERGENT_URL"
echo "  SSL/TLS: Full (Automatic)"
echo "  Proxy: Enabled (Orange Cloud)"
echo "  Performance: Optimized"
echo ""
echo "DNS propagation may take 5-15 minutes."
echo ""
echo "Test your domain:"
echo "  curl -I https://$SUBDOMAIN.$DOMAIN"
echo ""
echo "Visit your site:"
echo "  https://$SUBDOMAIN.$DOMAIN"
echo ""
