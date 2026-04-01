# Cloudflare Deployment Guide for www.nexussocialmarket.com

## Overview
This guide walks you through deploying the NEXUS AI Social Marketplace platform to Cloudflare and configuring your custom domain `www.nexussocialmarket.com`.

---

## Prerequisites

### Required Cloudflare Account Setup
1. **Cloudflare Account** - Sign up at https://dash.cloudflare.com/sign-up
2. **Domain in Cloudflare** - Add `nexussocialmarket.com` to your Cloudflare account
3. **Cloudflare API Token** - Create one with the following permissions:
   - Zone.DNS (Edit)
   - Zone.Zone Settings (Edit)
   - Zone.Zone (Read)
   - Workers Scripts (Edit)
   - Pages (Edit)

### Required Cloudflare Products
You'll need access to:
- **Cloudflare Pages** (for frontend hosting) - FREE tier available
- **Cloudflare Workers** (for backend API) - FREE tier: 100k requests/day
- **Cloudflare D1** or **MongoDB Atlas** (for database) - FREE tier available
- **Cloudflare KV** (for sessions/cache) - FREE tier: 100k reads/day

---

## Deployment Options

### Option 1: Cloudflare Pages + Workers (Recommended for Static Sites)

**Best for:** React/Vue/Next.js frontend with serverless backend

#### Step 1: Deploy Frontend to Cloudflare Pages

1. **Install Wrangler CLI:**
```bash
npm install -g wrangler
wrangler login
```

2. **Build Frontend:**
```bash
cd /app/frontend
yarn build
```

3. **Deploy to Pages:**
```bash
wrangler pages project create nexus-marketplace
wrangler pages deploy build --project-name=nexus-marketplace
```

4. **Configure Custom Domain:**
```bash
# In Cloudflare Dashboard:
# Pages > nexus-marketplace > Custom domains > Add domain
# Enter: www.nexussocialmarket.com
# Cloudflare will auto-configure DNS
```

#### Step 2: Deploy Backend as Cloudflare Worker

1. **Create Worker Directory:**
```bash
mkdir -p /app/cloudflare-worker
cd /app/cloudflare-worker
```

2. **Initialize Worker:**
```bash
wrangler init nexus-backend
# Choose: "Hello World" Worker
# Language: JavaScript
```

3. **Convert FastAPI to Worker:**
Your backend needs to be adapted to Worker format. Create `worker.js`:

```javascript
// Example Worker for NEXUS Backend
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // Health check
    if (url.pathname === '/api/health') {
      return Response.json({ status: 'healthy' });
    }
    
    // Hybrid services routing
    if (url.pathname.startsWith('/api/v2/hybrid/')) {
      // Route to appropriate hybrid service
      // Connect to D1 database or MongoDB Atlas
      const db = env.DB; // D1 binding
      // ... your API logic
    }
    
    return new Response('NEXUS API', { status: 200 });
  }
};
```

4. **Deploy Worker:**
```bash
wrangler deploy
```

5. **Add Custom Route:**
```bash
# In Cloudflare Dashboard:
# Workers & Pages > nexus-backend > Settings > Triggers
# Add route: api.nexussocialmarket.com/*
```

---

### Option 2: Full Server Deployment (Best for Your Current Stack)

**Best for:** Keeping FastAPI backend as-is

#### Use Cloudflare as CDN/Proxy Only

1. **Deploy Backend to a Server:**
   - **Recommended**: Use Railway, Render, DigitalOcean, or keep on Emergent
   - Get a server URL, e.g., `https://nexus-backend.railway.app`

2. **Deploy Frontend to Cloudflare Pages:**
   - Follow steps from Option 1, Step 1
   - Update `REACT_APP_BACKEND_URL` to point to your backend server

3. **Configure Cloudflare DNS:**

In Cloudflare Dashboard > DNS:

```
Type  Name                    Content                          Proxy Status
A     nexussocialmarket.com   <your-server-ip>                 Proxied (Orange Cloud)
CNAME www                     nexussocialmarket.com            Proxied (Orange Cloud)
CNAME api                     nexus-backend.railway.app        Proxied (Orange Cloud)
```

4. **SSL/TLS Settings:**
   - Go to SSL/TLS > Overview
   - Set encryption mode: **Full (strict)**
   - Enable **Always Use HTTPS**

---

## Current Deployment on Emergent

### What You Have Now
- **Current URL**: `https://{your-app}.emergent.host` (provided by Emergent)
- **Backend**: Running on Emergent's Kubernetes cluster
- **Frontend**: Running on Emergent
- **Database**: MongoDB managed by Emergent

### URL Forwarding Options

#### Option A: Cloudflare Redirect Rule (Simplest)

This keeps your app on Emergent but forwards traffic from www.nexussocialmarket.com to it:

1. **Add Domain to Cloudflare:**
   - Add `nexussocialmarket.com` to Cloudflare
   - Update nameservers at your domain registrar to Cloudflare's

2. **Create DNS Record:**
```
Type  Name  Content                           Proxy
A     @     192.0.2.1 (dummy IP)              Proxied
CNAME www   nexussocialmarket.com             Proxied
```

3. **Create Redirect Rule:**
   - Go to: Rules > Redirect Rules > Create rule
   - Name: "Forward to Emergent"
   - When incoming requests match: `http.host eq "www.nexussocialmarket.com"`
   - Then: Dynamic redirect
   - Expression: `concat("https://your-app.emergent.host", http.request.uri.path)`
   - Status code: 301 (Permanent)

#### Option B: Cloudflare Reverse Proxy

Keep backend on Emergent, use Cloudflare as reverse proxy:

1. **DNS Configuration:**
```
Type  Name  Content                           Proxy
CNAME www   your-app.emergent.host            Proxied
```

2. **Transform Rules (Optional):**
   - Go to: Rules > Transform Rules
   - Modify Request Header to preserve original host

---

## Step-by-Step: Deploy to www.nexussocialmarket.com

### Quick Start (Recommended Path)

**I cannot automatically configure Cloudflare for you because it requires:**
- Your Cloudflare account credentials
- API key generation
- Domain ownership verification
- DNS propagation (24-48 hours)

### What You Need to Do:

1. **Get Cloudflare Account:**
   - Sign up: https://dash.cloudflare.com/sign-up
   - Verify email

2. **Add Your Domain:**
   - Dashboard > Add site
   - Enter: `nexussocialmarket.com`
   - Choose FREE plan
   - Copy the nameservers Cloudflare provides

3. **Update Domain Registrar:**
   - Go to where you bought `nexussocialmarket.com` (e.g., GoDaddy, Namecheap)
   - Update nameservers to Cloudflare's
   - Wait for DNS propagation (usually 1-24 hours)

4. **Configure DNS in Cloudflare:**
   ```
   Type  Name  Content                      Proxy
   A     @     192.0.2.1                    Proxied
   CNAME www   nexussocialmarket.com        Proxied
   ```

5. **Set Up Page Rule or Redirect:**
   - Rules > Page Rules > Create Page Rule
   - URL: `www.nexussocialmarket.com/*`
   - Setting: Forwarding URL
   - Status: 301 (Permanent Redirect)
   - Destination: `https://your-app.emergent.host/$1`

6. **SSL/TLS Settings:**
   - SSL/TLS > Overview: Set to "Full" or "Full (strict)"
   - Edge Certificates: Enable "Always Use HTTPS"

---

## Testing Your Deployment

After DNS propagates (24-48 hours):

1. **Test Domain:**
```bash
curl -I https://www.nexussocialmarket.com
# Should show: HTTP/2 200
```

2. **Test API:**
```bash
curl https://www.nexussocialmarket.com/api/health
# Should return: {"status":"healthy"}
```

3. **Test in Browser:**
   - Visit: https://www.nexussocialmarket.com
   - Should load your NEXUS platform

---

## Troubleshooting

### DNS Not Resolving
- **Check**: Use `nslookup www.nexussocialmarket.com`
- **Wait**: DNS can take 24-48 hours to propagate
- **Verify**: Nameservers are correctly set at registrar

### SSL Errors
- **Issue**: "Your connection is not private"
- **Fix**: SSL/TLS > Overview > Change to "Full (strict)"
- **Wait**: SSL certificate generation can take 15 minutes

### 502 Bad Gateway
- **Issue**: Cloudflare can't reach your origin server
- **Check**: Origin server is running
- **Verify**: DNS record points to correct IP/CNAME

### Mixed Content Warnings
- **Issue**: HTTP content on HTTPS page
- **Fix**: Update all `http://` URLs to `https://` in your code
- **Enable**: Always Use HTTPS in Cloudflare

---

## Cost Estimate

### Cloudflare FREE Plan Includes:
- Unlimited bandwidth (Cloudflare proxy)
- Unlimited DNS queries
- SSL certificates
- Basic DDoS protection
- 3 Page Rules
- Cloudflare Workers: 100k requests/day
- Pages: Unlimited sites

### If You Need More:
- **Pro Plan**: $20/month (faster caching, 20 Page Rules, image optimization)
- **Business Plan**: $200/month (custom SSL, advanced DDoS)
- **Workers Paid**: $5/month (10M requests, more CPU time)

---

## Next Steps

1. **Complete Cloudflare Setup:**
   - Create account
   - Add domain
   - Configure DNS
   - Set up redirect/proxy

2. **Update Environment Variables:**
   ```bash
   # Frontend .env
   REACT_APP_BACKEND_URL=https://www.nexussocialmarket.com/api
   ```

3. **Monitor Performance:**
   - Cloudflare Analytics
   - Set up alerts for downtime
   - Monitor bandwidth usage

4. **Optional Enhancements:**
   - Enable Cloudflare Workers for edge computing
   - Use Cloudflare R2 for file storage
   - Integrate Cloudflare Stream for videos
   - Set up Cloudflare Access for team authentication

---

## Support Resources

- **Cloudflare Docs**: https://developers.cloudflare.com
- **Community Forum**: https://community.cloudflare.com
- **Status Page**: https://www.cloudflarestatus.com
- **Support**: https://support.cloudflare.com

---

## Important Notes

⚠️ **I Cannot Automate This Because:**
- Requires your Cloudflare account login
- Needs 2FA verification
- Requires domain ownership verification
- DNS changes need to be done at your domain registrar
- API tokens are tied to your account

✅ **What's Already Done:**
- NEXUS platform is fully deployment-ready
- All environment variables properly configured
- No hardcoded URLs (all in .env)
- CORS configured for production
- SSL/TLS compatible
- Kubernetes-ready

🎯 **Recommended Approach:**
Keep NEXUS running on Emergent (stable, managed) and use Cloudflare as:
1. DNS provider
2. CDN/proxy (faster global access)
3. SSL/TLS termination
4. DDoS protection
5. URL forwarding to your Emergent URL

This gives you the best of both worlds: Emergent's managed infrastructure + Cloudflare's global network.
