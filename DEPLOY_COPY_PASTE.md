# 🚀 NEXUS DEPLOYMENT - COPY/PASTE GUIDE
**Simplified: No broken CLIs, just working commands**

═══════════════════════════════════════════════════════════

## STEP 1: MongoDB Atlas (10 minutes)

**Do this in your browser:**

1. Go to: https://cloud.mongodb.com/
2. Sign up / Log in
3. Click "Build a Database"
4. Choose **M0 FREE** (or M10 for $9/month)
5. Provider: AWS, Region: us-east-1
6. Cluster Name: `nexus-production`
7. Click "Create" (wait 5 min)

**Configure Security:**
- Database Access → Add User
  - Username: `nexus-admin`  
  - Password: Auto-generate (SAVE IT!)
- Network Access → Add IP: `0.0.0.0/0`

**Get Connection String:**
- Database → Connect → Connect your application
- Copy the string, replace `<password>`, add database name:

```
mongodb+srv://nexus-admin:YOUR_PASSWORD@nexus-production.xxxxx.mongodb.net/nexus_production?retryWrites=true&w=majority
```

**SAVE THIS STRING!** You'll need it in Step 3.

═══════════════════════════════════════════════════════════

## STEP 2: Deploy Frontend to Cloudflare (5 minutes)

**Run these commands in terminal:**

```bash
# Install Wrangler (if not installed)
npm install -g wrangler

# Login to Cloudflare (opens browser)
wrangler login

# Deploy frontend
cd /app/frontend/build
wrangler pages deploy . --project-name nexus-ai-social --branch main
```

**Your frontend is now live at:**
`https://nexus-ai-social.pages.dev`

═══════════════════════════════════════════════════════════

## STEP 3: Deploy Backend to Railway (10 minutes)

**Railway CLI doesn't work on this system, so use the web UI:**

1. Go to: https://railway.app/
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select repository: `Mattlk13/nexus-ai-platform`
5. Railway will ask for root directory: enter `/backend`
6. Click "Deploy"

**After deployment starts, set environment variables:**

7. Click your service → "Variables" tab → "Raw Editor"
8. Paste these variables (UPDATE MONGO_URL with YOUR connection string):

```env
MONGO_URL=mongodb+srv://nexus-admin:YOUR_PASSWORD@nexus-production.xxxxx.mongodb.net/nexus_production?retryWrites=true&w=majority
DB_NAME=nexus_production
EMERGENT_LLM_KEY=sk-emergent-a79Ba891bC89777B1C
ELEVENLABS_API_KEY=sk_184639adad6c751f8fc5d04facf2e9c83d0e91f2c78d569d
FAL_KEY=cc0e11e3-b7bb-45af-8c54-af8a9df74c2a:1b60a6e1d4e85a3c4ed2756681c3a1fa
CLOUDFLARE_ACCOUNT_ID=9ea3a006589428efed0480da5c037163
R2_ENABLED=true
JWT_SECRET=REPLACE_WITH_RANDOM_STRING_32_CHARS
CORS_ORIGINS=https://nexus-ai-social.pages.dev
ENVIRONMENT=production
LOG_LEVEL=info
PORT=8001
```

**Generate JWT_SECRET:**
Run in terminal: `openssl rand -hex 32`
Replace `REPLACE_WITH_RANDOM_STRING_32_CHARS` with the output.

9. Click "Save" (Railway redeploys automatically)

**Get your backend URL:**
- Go to Settings → Networking → Copy the Public URL
- Should look like: `https://nexus-backend-production-xxxx.up.railway.app`

═══════════════════════════════════════════════════════════

## STEP 4: Connect Frontend & Backend (5 minutes)

**In Cloudflare Pages:**
1. Go to: https://dash.cloudflare.com/
2. Pages → `nexus-ai-social` → Settings → Environment variables
3. Add variable:
   - Name: `REACT_APP_BACKEND_URL`
   - Value: `https://your-railway-url.railway.app` (YOUR actual URL)
4. Click "Save"

**In Railway:**
1. Go to Variables
2. Update `CORS_ORIGINS` to: `https://nexus-ai-social.pages.dev`
3. Click "Save" (auto-redeploys)

**Redeploy Frontend:**
```bash
cd /app/frontend/build
wrangler pages deploy . --project-name nexus-ai-social --branch main
```

═══════════════════════════════════════════════════════════

## ✅ DONE! Test Your Site

**Frontend:** https://nexus-ai-social.pages.dev
**Backend Health:** https://your-railway-url.railway.app/api/health

Open the frontend URL in your browser!

═══════════════════════════════════════════════════════════

## 💰 CURRENT COST: FREE ($0/month)

To upgrade to production ($20/month):
- Cloudflare: Upgrade to Pages Pro ($5)
- Railway: Upgrade to Starter ($5)
- MongoDB: Change to M10 cluster ($9)

═══════════════════════════════════════════════════════════

## 🆘 TROUBLESHOOTING

**Frontend blank?**
→ Check REACT_APP_BACKEND_URL is set in Cloudflare

**Backend 500 errors?**
→ Check Railway logs, verify MONGO_URL is correct

**CORS errors?**
→ Update CORS_ORIGINS in Railway to match frontend URL

═══════════════════════════════════════════════════════════
