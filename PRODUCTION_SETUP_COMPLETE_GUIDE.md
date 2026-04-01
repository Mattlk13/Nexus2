# NEXUS Production Setup Guide
# Complete step-by-step guide for recommended production deployment

## 🎯 Recommended Production Stack

**Monthly Cost: ~$20**

1. **Cloudflare Pages** - Frontend hosting ($5/month Pro or FREE)
2. **Railway** - Backend hosting ($5/month Starter)
3. **MongoDB Atlas** - Database ($9/month M10 or FREE M0)
4. **Custom Domain** - Optional ($12/year)

---

## 📋 Prerequisites

- [x] Code pushed to GitHub
- [x] Production build created (`/app/frontend/build`)
- [ ] Cloudflare account
- [ ] Railway account
- [ ] MongoDB Atlas account
- [ ] Domain (optional)

---

## 🚀 Quick Setup (Automated)

### Option 1: Fully Automated (Recommended)

```bash
# Step 1: Set up secrets and tokens
./setup-production.sh

# Step 2: Deploy everything
./deploy-production.sh

# Done! Your site is live in ~10 minutes
```

### Option 2: Manual Setup (Step-by-Step)

Follow the detailed guide below.

---

## 📖 Detailed Setup Guide

### STEP 1: MongoDB Atlas (Database) - 15 minutes

**Create Free Cluster (M0) or Paid (M10 - $9/month)**

1. Go to https://cloud.mongodb.com/
2. Sign up / Log in
3. Click **"Build a Database"**
4. Choose **"Shared"** (Free M0) or **"Dedicated"** (M10 - $9/month)
5. Select:
   - Provider: **AWS**
   - Region: **us-east-1**
   - Cluster Name: **nexus-production**
6. Click **"Create"** (wait 3-5 minutes)

**Configure Security:**

7. **Database Access:**
   - Click **"Database Access"** → **"Add New Database User"**
   - Username: `nexus-admin`
   - Password: **Auto-generate** (save it!)
   - Database User Privileges: **Atlas admin**
   - Click **"Add User"**

8. **Network Access:**
   - Click **"Network Access"** → **"Add IP Address"**
   - Click **"Allow Access from Anywhere"** (0.0.0.0/0)
   - Click **"Confirm"**

9. **Get Connection String:**
   - Click **"Database"** → **"Connect"**
   - Choose **"Connect your application"**
   - Copy the connection string:
   ```
   mongodb+srv://nexus-admin:<password>@nexus-production.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
   - Replace `<password>` with your generated password
   - Save this connection string!

---

### STEP 2: Cloudflare Pages (Frontend) - 10 minutes

**Deploy Frontend**

1. Install Wrangler CLI:
   ```bash
   npm install -g wrangler
   ```

2. Login to Cloudflare:
   ```bash
   wrangler login
   ```
   - Opens browser → Log in with your account

3. Deploy:
   ```bash
   cd /app/frontend/build
   wrangler pages deploy . --project-name nexus-ai-social
   ```

4. **Your frontend is live!**
   - URL: `https://nexus-ai-social.pages.dev`

**Get API Token (for CI/CD):**

5. Go to https://dash.cloudflare.com/profile/api-tokens
6. Click **"Create Token"**
7. Use template: **"Edit Cloudflare Workers"**
8. Click **"Continue to summary"** → **"Create Token"**
9. **Save the token** (shown only once!)

**Get Account ID:**

10. Go to https://dash.cloudflare.com/
11. Select any domain or click profile
12. Copy **Account ID** (looks like: `9ea3a0065894...`)

---

### STEP 3: Railway (Backend) - 10 minutes

**Create Account & Deploy**

1. Go to https://railway.app/
2. Click **"Start a New Project"**
3. Sign up with GitHub (recommended)

**Option A: Deploy from GitHub (Recommended)**

4. Click **"Deploy from GitHub repo"**
5. Select repository: **`Mattlk13/nexus-ai-platform`**
6. Select root directory: **`/backend`**
7. Railway auto-detects `railway.toml` ✅

**Option B: Deploy via CLI**

4. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

5. Login:
   ```bash
   railway login
   ```

6. Deploy:
   ```bash
   cd /app/backend
   railway init
   railway up
   ```

**Set Environment Variables:**

7. In Railway dashboard, go to **Variables** tab
8. Click **"Raw Editor"**
9. Paste (update with your values):
   ```env
   # Database
   MONGO_URL=mongodb+srv://nexus-admin:YOUR_PASSWORD@nexus-production.xxxxx.mongodb.net/nexus?retryWrites=true&w=majority
   DB_NAME=nexus_production

   # AI Services (from /app/backend/.env)
   EMERGENT_LLM_KEY=sk-emergent-...
   ELEVENLABS_API_KEY=sk_...
   FAL_KEY=...
   RUNWAYML_API_KEY=...

   # Cloudflare
   CLOUDFLARE_ACCOUNT_ID=9ea3a0065894...
   R2_ENABLED=true
   R2_ACCESS_KEY_ID=...
   R2_SECRET_ACCESS_KEY=...
   R2_ENDPOINT_URL=...
   R2_BUCKET_NAME=nexus-storage

   # Security
   JWT_SECRET=<generate with: openssl rand -hex 32>
   CORS_ORIGINS=https://nexus-ai-social.pages.dev

   # Application
   ENVIRONMENT=production
   LOG_LEVEL=info
   ```

10. Click **"Deploy"**

**Get Backend URL:**

11. Railway assigns a URL like: `nexus-backend-production-xxxx.up.railway.app`
12. **Save this URL!**

---

### STEP 4: Connect Frontend to Backend - 5 minutes

**Update Frontend Environment**

1. In Cloudflare Pages dashboard:
   - Go to your project **"nexus-ai-social"**
   - Click **"Settings"** → **"Environment variables"**
   - Add variable:
     - Name: `REACT_APP_BACKEND_URL`
     - Value: `https://nexus-backend-production-xxxx.up.railway.app`
   - Click **"Save"**

2. Redeploy frontend (changes take effect):
   ```bash
   cd /app/frontend/build
   wrangler pages deploy . --project-name nexus-ai-social
   ```

**Update Backend CORS**

3. In Railway dashboard:
   - Go to **Variables**
   - Update `CORS_ORIGINS` to: `https://nexus-ai-social.pages.dev`
   - Railway auto-redeploys

---

### STEP 5: GitHub Secrets (for CI/CD) - 5 minutes

**Enable Automated Deployments**

1. Go to: `https://github.com/Mattlk13/nexus-ai-platform/settings/secrets/actions`

2. Click **"New repository secret"** for each:

   | Name | Value |
   |------|-------|
   | `CLOUDFLARE_API_TOKEN` | Your Cloudflare API token |
   | `CLOUDFLARE_ACCOUNT_ID` | Your Cloudflare account ID |
   | `RAILWAY_TOKEN` | Get from Railway → Settings → Tokens |
   | `BACKEND_URL` | Your Railway backend URL |
   | `MONGO_URL` | Your MongoDB Atlas connection string |
   | `EMERGENT_LLM_KEY` | From `/app/backend/.env` |

3. **Automated deployments now work!**
   - Every push to `main` branch auto-deploys
   - GitHub Actions workflow: `.github/workflows/deploy.yml`

---

### STEP 6: Custom Domain (Optional) - 15 minutes

**Purchase Domain**

1. Go to:
   - [Namecheap](https://www.namecheap.com/)
   - [Google Domains](https://domains.google/)
   - [Cloudflare Registrar](https://www.cloudflare.com/products/registrar/)

2. Search for domain (suggestions):
   - `nexus-ai.social`
   - `nexusaimarket.com`
   - `nexus.market`

3. Purchase (~$12/year)

**Configure DNS (Cloudflare)**

4. Add domain to Cloudflare:
   - Dashboard → **"Add a Site"**
   - Enter your domain
   - Choose **Free** plan
   - Update nameservers at registrar

5. Add DNS record:
   - Type: **CNAME**
   - Name: **@** (or **www**)
   - Target: **nexus-ai-social.pages.dev**
   - Proxy: ✅ **Proxied**
   - Click **"Save"**

6. Configure in Cloudflare Pages:
   - Project → **"Custom domains"**
   - Click **"Set up a custom domain"**
   - Enter: `yourdomain.com`
   - Cloudflare auto-configures

7. **SSL Certificate**:
   - ✅ Automatic! (Cloudflare handles it)
   - Active within 10-30 minutes

**Update Backend URL**

8. Update Railway environment variable:
   ```
   CORS_ORIGINS=https://yourdomain.com
   ```

---

### STEP 7: Email Domain (Optional) - 20 minutes

**Set Up admin@nexus Email**

**Option 1: Zoho Mail (Free for 5 users)**

1. Go to https://www.zoho.com/mail/
2. Sign up for **Free** plan
3. Add your domain
4. Verify domain (add DNS records)
5. Create mailbox: `admin@yourdomain.com`

**Option 2: Use Resend API (Already integrated)**

1. Go to https://resend.com/
2. Sign up
3. Add domain
4. Get API key
5. Add to Railway variables:
   ```
   RESEND_API_KEY=re_...
   ```

---

### STEP 8: Monitoring & Analytics (Optional) - 10 minutes

**Sentry (Error Monitoring)**

1. Go to https://sentry.io/
2. Create project → Choose **"FastAPI"** and **"React"**
3. Get DSN keys
4. Add to environment variables

**Google Analytics**

1. Go to https://analytics.google.com/
2. Create property
3. Get Measurement ID
4. Add to frontend environment

---

## ✅ Production Checklist

### Critical
- [ ] MongoDB Atlas cluster created
- [ ] Frontend deployed to Cloudflare Pages
- [ ] Backend deployed to Railway
- [ ] Environment variables configured
- [ ] Frontend connected to backend
- [ ] CORS configured
- [ ] Health checks passing

### Security
- [ ] Change GitHub password (Mattlk13)
- [ ] Change Gmail password
- [ ] Enable 2FA on GitHub
- [ ] Enable 2FA on Cloudflare
- [ ] Enable 2FA on Railway
- [ ] Enable 2FA on MongoDB Atlas
- [ ] Rotate API keys

### Optional
- [ ] Custom domain configured
- [ ] Email domain set up
- [ ] Monitoring (Sentry)
- [ ] Analytics (Google Analytics)
- [ ] CDN optimization
- [ ] Backup strategy

---

## 🧪 Testing Production

**Health Checks:**

```bash
# Frontend
curl https://nexus-ai-social.pages.dev

# Backend health
curl https://your-backend.railway.app/api/health

# API docs
curl https://your-backend.railway.app/docs

# Test AI service
curl https://your-backend.railway.app/api/v2/hybrid/groq/capabilities
```

---

## 💰 Final Costs

### Free Tier (MVP)
- Cloudflare Pages: **FREE**
- Railway: **FREE** (500 hours/month)
- MongoDB Atlas: **FREE** (M0 - 512MB)
- **Total: $0/month** ✅

### Recommended (Production)
- Cloudflare Pages Pro: **$5/month**
- Railway Starter: **$5/month**
- MongoDB Atlas M10: **$9/month**
- Domain: **$12/year** (~$1/month)
- **Total: ~$20/month**

---

## 🚨 Troubleshooting

**Frontend not loading?**
- Check Cloudflare Pages deploy logs
- Verify `REACT_APP_BACKEND_URL` is set

**Backend not responding?**
- Check Railway logs
- Verify MongoDB connection string
- Check environment variables

**CORS errors?**
- Update `CORS_ORIGINS` in Railway
- Include https:// in URL

**MongoDB connection failed?**
- Verify IP whitelist (0.0.0.0/0)
- Check connection string format
- Confirm password is URL-encoded

---

## 🎉 Success!

Your NEXUS platform is live!

- **Frontend:** https://nexus-ai-social.pages.dev (or your domain)
- **Backend:** https://your-backend.railway.app
- **Status:** Production-ready
- **Users:** Ready to onboard
- **AI Services:** 41 active hybrids

**Share with the world!** 🌍🚀

---

**Need Help?**
- Check logs in Railway dashboard
- View Cloudflare Pages deployment logs
- Review `/app/DEPLOYMENT_READINESS_REPORT.md`
- Check `/app/POST_DEPLOYMENT_CHECKLIST_STATUS.md`
