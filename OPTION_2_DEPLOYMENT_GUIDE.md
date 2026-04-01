# 🚀 NEXUS PRODUCTION DEPLOYMENT - OPTION 2 GUIDE
**Interactive Step-by-Step Deployment**  
**Target:** Production-ready ($20/month)  
**Time Required:** 60-90 minutes

---

## 📋 OVERVIEW - OPTION 2 COMPONENTS

### Monthly Costs:
- ✅ Cloudflare Pages Pro: **$5/month**
- ✅ Railway Starter: **$5/month**
- ✅ MongoDB Atlas M10: **$9/month**
- ✅ Custom Domain: **~$1/month** ($12/year)
- **Total: $20/month**

### Benefits Over Free Tier:
- ⚡ Better performance & reliability
- 📈 Handles 10K+ concurrent users
- 💾 Production-grade database (10GB)
- 🔒 24/7 uptime guarantees
- 📊 Advanced monitoring & analytics
- 🌐 Custom domain with SSL

---

## 🎯 DEPLOYMENT STEPS

I'll guide you through each step with detailed instructions and wait for your confirmation before proceeding.

---

## STEP 1: MongoDB Atlas M10 Setup (15-20 minutes)

### 1.1 Create Account & Cluster

**Action Required:** Open your browser and follow these steps:

1. **Go to:** https://cloud.mongodb.com/
2. **Sign up** or **Log in**
3. Click **"Build a Database"**
4. Choose **"Dedicated"** (not Shared)
5. Select **M10** cluster:
   - Provider: **AWS**
   - Region: **us-east-1** (or closest to your users)
   - Cluster Name: **nexus-production**
6. Click **"Create"** (will take 5-7 minutes to provision)

**Cost:** $9/month (includes 10GB storage, 2GB RAM)

### 1.2 Configure Security

**While cluster is provisioning:**

1. Click **"Database Access"** (left sidebar)
2. Click **"Add New Database User"**
   - Username: `nexus-admin`
   - Password: Click **"Autogenerate Secure Password"**
   - ⚠️ **COPY AND SAVE THIS PASSWORD IMMEDIATELY!**
   - Database User Privileges: **Atlas admin**
3. Click **"Add User"**

4. Click **"Network Access"** (left sidebar)
5. Click **"Add IP Address"**
6. Click **"Allow Access from Anywhere"** (0.0.0.0/0)
   - Description: "NEXUS Production"
7. Click **"Confirm"**

### 1.3 Get Connection String

**After cluster finishes provisioning:**

1. Go back to **"Database"** (left sidebar)
2. Click **"Connect"** button on your cluster
3. Choose **"Connect your application"**
4. Driver: **Python**, Version: **3.11 or later**
5. Copy the connection string (looks like):
   ```
   mongodb+srv://nexus-admin:<password>@nexus-production.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. **Replace `<password>`** with the password you saved earlier
7. Add database name at the end:
   ```
   mongodb+srv://nexus-admin:YOUR_PASSWORD@nexus-production.xxxxx.mongodb.net/nexus_production?retryWrites=true&w=majority
   ```

**⚠️ SAVE THIS COMPLETE CONNECTION STRING!**

---

## STEP 2: Deploy Frontend to Cloudflare Pages Pro (10-15 minutes)

### 2.1 Install Wrangler CLI

**Run in your terminal:**
```bash
npm install -g wrangler
```

### 2.2 Login to Cloudflare

**Run this command - it will open your browser:**
```bash
wrangler login
```

**In the browser:**
1. Sign in to your Cloudflare account (or create one)
2. Authorize the login
3. Return to terminal

### 2.3 Deploy Frontend

**Run:**
```bash
cd /app/frontend/build
wrangler pages deploy . --project-name nexus-ai-social --branch main
```

**You'll see output like:**
```
✨ Success! Uploaded 45 files
✨ Deployment complete!
https://nexus-ai-social.pages.dev
```

**⚠️ SAVE THIS URL!** (Your frontend URL)

### 2.4 Upgrade to Pages Pro

**In Cloudflare Dashboard:**
1. Go to: https://dash.cloudflare.com/
2. Select **Pages** → **nexus-ai-social**
3. Click **"Upgrade"** or **"Plans"**
4. Select **"Pages Pro"** - $5/month
5. Add payment method
6. Confirm upgrade

**Pro Features Unlocked:**
- Unlimited bandwidth
- Unlimited builds
- Advanced analytics
- Better performance

### 2.5 Get API Credentials (for CI/CD later)

1. Go to: https://dash.cloudflare.com/profile/api-tokens
2. Click **"Create Token"**
3. Use template: **"Edit Cloudflare Workers"**
4. Click **"Continue to summary"** → **"Create Token"**
5. **⚠️ COPY THE TOKEN** (shown only once!)
6. Save as: `CLOUDFLARE_API_TOKEN`

7. Get your Account ID:
   - Go to dashboard home
   - Copy **Account ID**
   - Save as: `CLOUDFLARE_ACCOUNT_ID`

---

## STEP 3: Deploy Backend to Railway Starter (15-20 minutes)

### 3.1 Create Railway Account

**Action Required:**
1. Go to: https://railway.app/
2. Click **"Start a New Project"**
3. Sign up with GitHub (recommended)

### 3.2 Deploy Backend

**Option A: Deploy from GitHub (Recommended)**

1. In Railway dashboard, click **"Deploy from GitHub repo"**
2. Authorize GitHub access
3. Select repository: **`Mattlk13/nexus-ai-platform`**
4. Railway will ask for root directory
5. Set root directory: `/backend`
6. Railway auto-detects `requirements.txt` ✅
7. Click **"Deploy"**

**Option B: Deploy via CLI**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login (opens browser)
railway login

# Deploy
cd /app/backend
railway init
railway up
```

### 3.3 Upgrade to Starter Plan

**In Railway dashboard:**
1. Click **"Upgrade"** or project settings
2. Select **"Starter"** plan - $5/month
3. Add payment method
4. Confirm upgrade

**Starter Features:**
- $5/month + usage
- 500 hours execution time
- 8GB RAM, 8vCPU
- Custom domains
- Priority support

### 3.4 Set Environment Variables

**In Railway dashboard:**
1. Click your service → **"Variables"** tab
2. Click **"RAW Editor"**
3. Paste the following (update with YOUR values):

```env
# DATABASE (USE YOUR MONGODB ATLAS CONNECTION STRING FROM STEP 1)
MONGO_URL=mongodb+srv://nexus-admin:YOUR_PASSWORD@nexus-production.xxxxx.mongodb.net/nexus_production?retryWrites=true&w=majority
DB_NAME=nexus_production

# AI SERVICES (FROM /app/backend/.env)
EMERGENT_LLM_KEY=sk-emergent-a79Ba891bC89777B1C
ELEVENLABS_API_KEY=sk_184639adad6c751f8fc5d04facf2e9c83d0e91f2c78d569d
FAL_KEY=cc0e11e3-b7bb-45af-8c54-af8a9df74c2a:1b60a6e1d4e85a3c4ed2756681c3a1fa

# CLOUDFLARE (FROM /app/backend/.env)
CLOUDFLARE_ACCOUNT_ID=9ea3a006589428efed0480da5c037163
R2_ENABLED=true

# SECURITY (GENERATE NEW SECRET!)
JWT_SECRET=RUN_THIS_COMMAND_TO_GENERATE: openssl rand -hex 32
CORS_ORIGINS=https://nexus-ai-social.pages.dev

# APPLICATION
ENVIRONMENT=production
LOG_LEVEL=info
PORT=8001
```

4. Click **"Save"**
5. Railway will automatically redeploy

### 3.5 Get Backend URL

**After deployment completes:**
1. Railway assigns a URL like: `nexus-backend-production-xxxx.up.railway.app`
2. Find it in: **Settings** → **Networking** → **Public URL**
3. **⚠️ SAVE THIS URL!** (Your backend URL)

**Add https:// if not present:**
```
https://nexus-backend-production-xxxx.up.railway.app
```

---

## STEP 4: Connect Frontend ↔ Backend (5-10 minutes)

### 4.1 Update Frontend Environment in Cloudflare

**In Cloudflare Pages dashboard:**
1. Go to: https://dash.cloudflare.com/
2. Select **Pages** → **nexus-ai-social**
3. Click **"Settings"** → **"Environment variables"**
4. Click **"Add variable"**
5. Add:
   - **Name:** `REACT_APP_BACKEND_URL`
   - **Value:** `https://nexus-backend-production-xxxx.up.railway.app` (YOUR Railway URL)
6. Click **"Save"**

### 4.2 Redeploy Frontend

**Redeploy to apply new environment variable:**
```bash
cd /app/frontend/build
wrangler pages deploy . --project-name nexus-ai-social --branch main
```

### 4.3 Update Backend CORS

**In Railway dashboard:**
1. Go to **Variables** tab
2. Update `CORS_ORIGINS` to:
   ```
   https://nexus-ai-social.pages.dev
   ```
3. Click **"Save"** (Railway auto-redeploys)

---

## STEP 5: Custom Domain Setup (15-20 minutes)

### 5.1 Purchase Domain

**Choose a registrar:**
- **Namecheap:** https://www.namecheap.com/ (Recommended)
- **Google Domains:** https://domains.google/
- **Cloudflare Registrar:** https://www.cloudflare.com/products/registrar/

**Search for domain:**
- Suggestions: `nexus-ai.social`, `nexusmarket.ai`, `nexus.app`
- Cost: $10-15/year (~$1/month)

**Purchase the domain**

### 5.2 Add Domain to Cloudflare

**In Cloudflare dashboard:**
1. Click **"Add a Site"**
2. Enter your domain
3. Choose **Free** plan (you already have Pages Pro)
4. Follow the nameserver update instructions
5. Update nameservers at your registrar

**Wait 5-30 minutes for DNS propagation**

### 5.3 Configure Custom Domain in Pages

**After DNS is active:**
1. Go to **Pages** → **nexus-ai-social**
2. Click **"Custom domains"**
3. Click **"Set up a custom domain"**
4. Enter: `yourdomain.com` (or `www.yourdomain.com`)
5. Cloudflare auto-configures DNS
6. SSL certificate auto-generated (10-30 min)

### 5.4 Update CORS for Custom Domain

**In Railway:**
1. Update `CORS_ORIGINS` to:
   ```
   https://yourdomain.com
   ```
2. Save and redeploy

**In Cloudflare Pages:**
1. Update `REACT_APP_BACKEND_URL` if needed
2. Redeploy

---

## STEP 6: Security & Final Configuration (10-15 minutes)

### 6.1 Generate New JWT Secret

**Run locally:**
```bash
openssl rand -hex 32
```

**Copy the output and update in Railway:**
- Variable: `JWT_SECRET`
- Value: (the generated secret)

### 6.2 Change Critical Passwords

**⚠️ CRITICAL SECURITY:**
1. **Change GitHub password:** https://github.com/settings/security
   - Account: Mattlk13
   - Enable 2FA
2. **Change Gmail password:** https://myaccount.google.com/security
   - Email: Hm2krebsmatthewl@gmail.com
   - Enable 2FA

### 6.3 Enable 2FA Everywhere

- ✅ GitHub: https://github.com/settings/security
- ✅ Cloudflare: Dashboard → Account → Security
- ✅ Railway: Dashboard → Account → Security
- ✅ MongoDB Atlas: Account → Security

### 6.4 Restrict CORS (Final)

**In Railway backend variables:**
- Remove wildcards `*`
- Set exact domain: `https://yourdomain.com`
- Multiple domains: `https://yourdomain.com,https://www.yourdomain.com`

---

## STEP 7: Verification & Testing (10-15 minutes)

### 7.1 Health Checks

**Test Frontend:**
```bash
curl https://yourdomain.com
# OR
curl https://nexus-ai-social.pages.dev
```

**Test Backend Health:**
```bash
curl https://your-backend.railway.app/api/health
# Should return: {"status":"healthy",...}
```

**Test AI Service:**
```bash
curl https://your-backend.railway.app/api/v2/hybrid/groq/capabilities
# Should return: {"status":"active",...}
```

### 7.2 Browser Testing

**Open in browser:**
1. Visit: `https://yourdomain.com` (or Cloudflare Pages URL)
2. Check homepage loads ✅
3. Test navigation
4. Test new pages:
   - `/messages` ✅
   - `/profile-new` ✅
   - `/admin-dashboard` ✅
5. Open browser console - check for errors
6. Test user registration/login
7. Test AI services (Creation Studio)

### 7.3 Monitor Deployment

**Railway Logs:**
1. Go to Railway → Your service → **Logs**
2. Check for errors
3. Verify successful startup

**Cloudflare Analytics:**
1. Pages → Analytics
2. Monitor traffic and performance

---

## STEP 8: Optional Enhancements (15-30 minutes)

### 8.1 Email Domain Setup (Optional)

**Option A: Zoho Mail (Free)**
1. Go to: https://www.zoho.com/mail/
2. Add your custom domain
3. Create mailbox: `admin@yourdomain.com`

**Option B: Resend API (Already Integrated)**
1. Sign up: https://resend.com/
2. Add and verify your domain
3. Get API key
4. Add to Railway: `RESEND_API_KEY=re_...`

### 8.2 Monitoring Setup (Recommended)

**Sentry (Error Tracking):**
1. Sign up: https://sentry.io/
2. Create projects for frontend & backend
3. Get DSN keys
4. Add to environment variables

**UptimeRobot (Uptime Monitoring):**
1. Sign up: https://uptimerobot.com/
2. Add monitors:
   - Frontend URL
   - Backend `/api/health` endpoint
3. Configure email alerts

### 8.3 Analytics (Recommended)

**Google Analytics:**
1. Create property: https://analytics.google.com/
2. Get Measurement ID
3. Add to Cloudflare Pages env vars

---

## ✅ DEPLOYMENT COMPLETE CHECKLIST

### Infrastructure ✅
- [ ] MongoDB Atlas M10 cluster created
- [ ] Frontend deployed to Cloudflare Pages Pro
- [ ] Backend deployed to Railway Starter
- [ ] Custom domain configured
- [ ] SSL certificate active

### Configuration ✅
- [ ] Environment variables set (frontend & backend)
- [ ] CORS configured correctly
- [ ] JWT_SECRET generated
- [ ] MongoDB connection string updated
- [ ] API keys configured

### Security ✅
- [ ] GitHub password changed
- [ ] Gmail password changed
- [ ] 2FA enabled on all accounts
- [ ] API keys rotated
- [ ] CORS restricted to domain only

### Testing ✅
- [ ] Frontend loads correctly
- [ ] Backend health check passing
- [ ] All new pages accessible
- [ ] API calls working
- [ ] WebSocket connections working
- [ ] No console errors

### Optional ✅
- [ ] Email domain configured
- [ ] Monitoring set up (Sentry, UptimeRobot)
- [ ] Analytics configured
- [ ] Backup strategy implemented

---

## 🎉 SUCCESS!

**Your NEXUS platform is now LIVE on production infrastructure!**

**URLs:**
- Frontend: `https://yourdomain.com`
- Backend: `https://your-backend.railway.app`
- Admin: `https://yourdomain.com/admin-dashboard`

**Monthly Cost:** $20/month
- Cloudflare Pages Pro: $5
- Railway Starter: $5
- MongoDB Atlas M10: $9
- Domain: ~$1

**Next Steps:**
- Monitor logs for first 24 hours
- Gather user feedback
- Plan next features
- Regular security audits

---

**🚀 Congratulations on your launch!**

*Generated: April 1, 2026*
