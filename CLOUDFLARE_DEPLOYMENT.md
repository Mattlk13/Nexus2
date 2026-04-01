# CLOUDFLARE DEPLOYMENT GUIDE

## Quick Deploy Commands

### Frontend (Cloudflare Pages)
```bash
# Login to Cloudflare
wrangler login

# Deploy frontend
cd /app/frontend/build
wrangler pages deploy . --project-name nexus-ai-social --branch main

# Your site will be live at: nexus-ai-social.pages.dev
```

### Backend (Cloudflare Workers - Requires Adapter)
Backend deployment to Cloudflare Workers requires a FastAPI adapter.

**Alternative: Deploy Backend to Railway/Render**

#### Railway:
```bash
npm install -g @railway/cli
railway login
cd /app/backend
railway init
railway up
```

#### Render:
1. Go to render.com
2. Connect GitHub repository
3. Create new Web Service
4. Point to /app/backend
5. Set environment variables from backend/.env
6. Deploy

### Environment Variables for Production

**Frontend (.env):**
```
REACT_APP_BACKEND_URL=https://your-backend-url.com
```

**Backend (.env):**
- Copy all variables from /app/backend/.env
- Update MONGO_URL to MongoDB Atlas connection string
- Update CLOUDFLARE_* variables if needed

### MongoDB Atlas Setup
1. Go to mongodb.com/cloud/atlas
2. Create free cluster (M0)
3. Create database user
4. Whitelist IP: 0.0.0.0/0 (all IPs)
5. Get connection string
6. Update MONGO_URL in backend .env

### DNS Configuration
1. Purchase domain (e.g., nexus.aisocialmarket)
2. Add CNAME record:
   - Name: @ or www
   - Target: nexus-ai-social.pages.dev
3. Wait for DNS propagation (5-30 min)

### SSL/TLS
- ✅ Automatic with Cloudflare Pages
- ✅ Automatic with Railway/Render
- Certificate issued within minutes

## Post-Deployment

1. Test frontend: https://nexus-ai-social.pages.dev
2. Test backend health: https://your-backend/api/health
3. Configure CORS to allow frontend domain
4. Set up monitoring (optional)

## Credentials Needed

**Cloudflare:**
- Email: Hm2krebsmatthewl@gmail.com
- Account ID: 9ea3a0065894
- API Token: (from Cloudflare dashboard)

**Note:** For security, create NEW API tokens in Cloudflare dashboard rather than using existing ones.
