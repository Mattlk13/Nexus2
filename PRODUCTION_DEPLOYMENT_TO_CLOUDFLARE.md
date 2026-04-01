# Cloudflare Pages Deployment Guide
# Domain: www.nexussocialmarket.com

## Prerequisites

You'll need:
1. ✅ Cloudflare account (free tier works)
2. ✅ Domain ownership of nexussocialmarket.com
3. ⚠️ Backend hosting (Cloudflare Workers OR Railway/Render recommended)
4. ⚠️ MongoDB Atlas (free tier available)

## Step 1: Domain Setup (Cloudflare Dashboard)

### Add Domain to Cloudflare
1. Go to: https://dash.cloudflare.com/
2. Click "Add a Site"
3. Enter: `nexussocialmarket.com`
4. Select Free plan → Continue
5. Cloudflare will scan DNS records
6. Click "Continue"
7. **Update nameservers at your domain registrar**:
   - Copy the 2 Cloudflare nameservers shown
   - Go to your domain registrar (GoDaddy/Namecheap/Google Domains/etc.)
   - Replace existing nameservers with Cloudflare's
   - Save changes (DNS propagation takes 5-60 minutes)

8. Return to Cloudflare dashboard → Click "Check nameservers"
9. Wait for "Active" status

## Step 2: Deploy Frontend to Cloudflare Pages

### Option A: Via Dashboard (Recommended)

1. **Connect to Git** (if you have repo):
   - Go to: https://dash.cloudflare.com/ → Pages → Create project
   - Connect GitHub/GitLab account
   - Select NEXUS repository
   - Configure build:
     ```
     Framework preset: Create React App
     Build command: cd frontend && yarn install && yarn build
     Build output directory: frontend/build
     Root directory: /
     ```

2. **Direct Upload** (if no git repo):
   - Build locally first:
     ```bash
     cd /app/frontend
     yarn build
     ```
   - Go to Cloudflare Pages → Create → Upload assets
   - Drag `/app/frontend/build` folder
   - Name: nexus-frontend
   - Deploy

### Option B: Via Wrangler CLI

```bash
# Install Wrangler
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Build frontend
cd /app/frontend
yarn build

# Deploy to Pages
wrangler pages deploy build --project-name=nexus-frontend
```

### Environment Variables for Frontend

In Cloudflare Pages settings → Environment variables:
```
REACT_APP_BACKEND_URL=https://api.nexussocialmarket.com/api
```

## Step 3: Deploy Backend

### ⚠️ IMPORTANT: Cloudflare Workers Limitations

Cloudflare Workers **DO NOT** support Python/FastAPI directly. Choose one:

### Option A: Railway (Recommended for FastAPI)

1. **Sign up**: https://railway.app/
2. **New Project** → Deploy from GitHub
3. **Or** use CLI:
   ```bash
   npm i -g @railway/cli
   railway login
   railway init
   railway up
   ```

4. **Environment Variables** (Railway dashboard):
   ```
   MONGO_URL=mongodb+srv://...
   DB_NAME=nexus_production
   EMERGENT_LLM_KEY=sk-emergent-...
   FRONTEND_URL=https://www.nexussocialmarket.com
   CORS_ORIGINS=https://www.nexussocialmarket.com
   ```

5. **Custom Domain**: Railway settings → Domains → Add `api.nexussocialmarket.com`

### Option B: Render

1. **Sign up**: https://render.com/
2. **New Web Service** → Connect repository
3. **Configure**:
   ```
   Name: nexus-backend
   Environment: Python 3.11
   Build Command: pip install -r backend/requirements.txt
   Start Command: cd backend && uvicorn server:app --host 0.0.0.0 --port 10000
   ```

4. **Environment Variables** (same as Railway above)
5. **Custom Domain**: Add `api.nexussocialmarket.com`

### Option C: Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Deploy
cd /app
flyctl launch
```

## Step 4: MongoDB Atlas Setup

1. **Create Account**: https://www.mongodb.com/cloud/atlas/register
2. **Create Cluster**:
   - Choose FREE tier (M0)
   - Region: Choose closest to your backend host
   - Cluster Name: nexus-production

3. **Database Access**:
   - Create database user
   - Username: nexus_admin
   - Password: (generate strong password)
   - Copy connection string

4. **Network Access**:
   - Add IP: 0.0.0.0/0 (allow from anywhere)
   - OR add specific IPs from Railway/Render

5. **Get Connection String**:
   ```
   mongodb+srv://nexus_admin:<password>@cluster0.xxxxx.mongodb.net/
   ```

6. **Add to Backend Environment**:
   ```
   MONGO_URL=mongodb+srv://nexus_admin:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/nexus_production?retryWrites=true&w=majority
   DB_NAME=nexus_production
   ```

## Step 5: Configure DNS (Cloudflare Dashboard)

1. Go to: DNS → Records
2. Add records:

```
Type  Name  Content                              Proxy  TTL
----  ----  -------                              -----  ---
A     @     [Railway/Render IP]                  ON     Auto
CNAME www   nexussocialmarket.com                ON     Auto
CNAME api   [your-backend].railway.app           ON     Auto
```

**OR** if using Cloudflare Pages for frontend:
```
CNAME www   nexus-frontend.pages.dev             ON     Auto
CNAME @     nexus-frontend.pages.dev             ON     Auto
CNAME api   [your-backend].railway.app           ON     Auto
```

## Step 6: SSL/HTTPS

Cloudflare provides FREE SSL automatically:
1. Go to: SSL/TLS → Overview
2. Set mode: **Full (strict)**
3. Edge Certificates: Enable "Always Use HTTPS"
4. Done! ✅

## Step 7: Update Environment Variables

### Backend `.env` (Railway/Render)
```bash
# Database
MONGO_URL=mongodb+srv://nexus_admin:PASSWORD@cluster0.xxxxx.mongodb.net/nexus_production?retryWrites=true&w=majority
DB_NAME=nexus_production

# CORS & Frontend
FRONTEND_URL=https://www.nexussocialmarket.com
CORS_ORIGINS=https://www.nexussocialmarket.com
REACT_APP_BACKEND_URL=https://api.nexussocialmarket.com/api

# Keys (already have these)
EMERGENT_LLM_KEY=sk-emergent-a79Ba891bC89777B1C
STRIPE_SECRET_KEY=...
# Add optional keys from API_KEY_ACQUISITION_GUIDE.md
```

### Frontend Environment (Cloudflare Pages)
```bash
REACT_APP_BACKEND_URL=https://api.nexussocialmarket.com/api
```

## Step 8: Deploy & Test

### Deploy Sequence
1. ✅ Set up MongoDB Atlas (get connection string)
2. ✅ Deploy backend to Railway/Render with env vars
3. ✅ Get backend URL (e.g., `nexus-backend.railway.app`)
4. ✅ Add DNS record for `api.nexussocialmarket.com` → backend
5. ✅ Build frontend with updated API URL
6. ✅ Deploy frontend to Cloudflare Pages
7. ✅ Add DNS records for www and root domain
8. ✅ Wait for DNS propagation (5-60 minutes)

### Test Deployment
```bash
# Test frontend
curl https://www.nexussocialmarket.com

# Test backend health
curl https://api.nexussocialmarket.com/api/health

# Test Universal AI
curl -X POST https://api.nexussocialmarket.com/api/universal/status
```

## Estimated Costs

| Service | Plan | Cost |
|---------|------|------|
| Cloudflare (DNS, Pages, SSL) | Free | $0 |
| Railway (Backend hosting) | Hobby | $5/month |
| MongoDB Atlas | M0 Free Tier | $0 |
| **TOTAL** | | **$5/month** |

Alternative: Render free tier = $0/month total!

## Timeline

- Domain transfer to Cloudflare: 5-60 minutes
- Backend deployment: 5-10 minutes
- Frontend deployment: 2-5 minutes
- DNS propagation: 5-60 minutes
- **Total: 30 minutes - 2 hours**

## Troubleshooting

### Frontend 404 Errors
- Check build output directory is correct
- Verify DNS records point to Pages deployment
- Check Cloudflare proxy is ON (orange cloud)

### Backend Connection Errors
- Verify CORS_ORIGINS includes frontend URL
- Check MongoDB Atlas IP whitelist
- Test backend URL directly (bypass DNS)
- Check Railway/Render logs for errors

### OAuth Not Working
- Ensure FRONTEND_URL is set correctly in backend
- Update OAuth app redirect URLs to production domain
- Test with hardcoded redirect URL first

## Next Steps After Deployment

1. ✅ Test all 34 hybrid services
2. ✅ Set up monitoring (Cloudflare Analytics, Railway metrics)
3. ✅ Configure caching (Cloudflare Cache Rules)
4. ✅ Add optional API keys (see API_KEY_ACQUISITION_GUIDE.md)
5. ✅ Set up backups (MongoDB Atlas automated backups)
6. ✅ Configure email notifications (alerts)

## Support

- Cloudflare: https://dash.cloudflare.com/
- Railway: https://railway.app/
- MongoDB: https://cloud.mongodb.com/
- NEXUS Docs: See `/app/COMPREHENSIVE_AUDIT_REPORT.md`

---

**Ready to deploy!** Follow steps 1-8 in order. Feel free to ask for help at any step.
