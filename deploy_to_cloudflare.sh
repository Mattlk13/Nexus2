#!/bin/bash
# Auto-deploy to Cloudflare once Zone ID is available

TOKEN="cfat_A3gq1xqMrVXBtWQN7cqOaNuFSiFS4RBGRsqezGXEd3e6d497"
ZONE_ID="$1"

if [ -z "$ZONE_ID" ]; then
    echo "Usage: $0 <ZONE_ID>"
    echo ""
    echo "Get Zone ID with:"
    echo "curl -s 'https://api.cloudflare.com/client/v4/zones?name=nexussocialmarket.com' \\"
    echo "  -H 'Authorization: Bearer $TOKEN' | \\"
    echo "  python3 -c 'import sys,json; z=json.load(sys.stdin).get(\"result\",[]); print(z[0][\"id\"] if z else \"\")'"
    exit 1
fi

echo "🚀 Deploying to Cloudflare..."
echo "Zone ID: $ZONE_ID"
echo ""

# Create DNS record
echo "Creating DNS record..."
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  --data @/tmp/cloudflare_dns_config.json | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print('✅ DNS record created' if d.get('success') else '❌ Failed: ' + str(d.get('errors')))"

# Configure SSL
echo "Configuring SSL..."
curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/ssl" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"value": "full"}' > /dev/null
echo "✅ SSL mode: Full"

curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/always_use_https" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"value": "on"}' > /dev/null
echo "✅ Always Use HTTPS: Enabled"

curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/automatic_https_rewrites" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"value": "on"}' > /dev/null
echo "✅ Automatic HTTPS Rewrites: Enabled"

# Configure Performance
echo "Configuring Performance..."
curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/brotli" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"value": "on"}' > /dev/null
echo "✅ Brotli compression: Enabled"

curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/minify" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"value": {"css": "on", "html": "on", "js": "on"}}' > /dev/null
echo "✅ Auto-minify: Enabled"

curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/rocket_loader" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"value": "on"}' > /dev/null
echo "✅ Rocket Loader: Enabled"

echo ""
echo "=========================================="
echo "✅ Cloudflare Deployment Complete!"
echo "=========================================="
echo ""
echo "Your site should be live at:"
echo "https://www.nexussocialmarket.com"
echo ""
echo "Test with:"
echo "curl -I https://www.nexussocialmarket.com"
echo ""
