# 🔐 API Keys Acquisition Guide

## Your Account Information
- **Email**: hm2krebsmatthewl@gmail.com
- **Password**: Tristen527!

⚠️ **SECURITY NOTE**: For your protection, I haven't logged into external services with your credentials. Follow the steps below to obtain API keys manually.

---

## 🚀 Quick Setup (Required API Keys)

### 1. Resend Email API Key

**Why**: Send transactional emails (welcome, notifications, password resets)

**Steps**:
1. Go to [resend.com/signup](https://resend.com/signup)
2. Sign up with: `hm2krebsmatthewl@gmail.com`
3. Verify your email
4. Go to **API Keys** → **Create API Key**
5. Name it: "NEXUS Marketplace"
6. Copy the key (starts with `re_`)

**Add to NEXUS**:
```bash
# Edit /app/backend/.env
RESEND_API_KEY=re_YOUR_KEY_HERE
```

**Restart backend**:
```bash
sudo supervisorctl restart backend
```

**Free Tier**: 100 emails/day, 3,000/month

---

### 2. ProductHunt API Key

**Why**: Discover AI tools from ProductHunt (currently blocked with scraping)

**Steps**:
1. Go to [producthunt.com](https://www.producthunt.com/)
2. **Sign in with GitHub**:
   - First, go to [github.com](https://github.com/)
   - Sign up/login with: `hm2krebsmatthewl@gmail.com` / `Tristen527!`
   - Return to ProductHunt and click "Continue with GitHub"
3. Once logged in, go to [ProductHunt API Dashboard](https://www.producthunt.com/v2/oauth/applications)
4. Create new application:
   - Name: "NEXUS Discovery"
   - Redirect URI: `http://localhost:8001/api/callback`
5. Copy **API Key** and **API Secret**
6. Generate **Access Token** from dashboard

**Add to NEXUS**:
```bash
# Edit /app/backend/.env
PRODUCTHUNT_API_KEY=YOUR_ACCESS_TOKEN_HERE
```

**Restart backend**:
```bash
sudo supervisorctl restart backend
```

---

### 3. GitHub Personal Access Token

**Why**: Monitor repositories, track code quality, access trending AI repos

**Steps**:
1. Go to [github.com](https://github.com/)
2. Login with: `hm2krebsmatthewl@gmail.com` / `Tristen527!`
3. Navigate to **Settings** (top-right profile dropdown)
4. Scroll down to **Developer settings** (bottom left)
5. Click **Personal access tokens** → **Tokens (classic)**
6. **Generate new token**
7. Name: "NEXUS Platform Access"
8. Expiration: 90 days (or No expiration)
9. Select scopes:
   - ✓ `repo` (Full repository access)
   - ✓ `read:org` (Read organization data)
   - ✓ `read:user` (Read user profile)
10. Generate token and copy it (starts with `ghp_`)

**Add to NEXUS**:
```bash
# Edit /app/backend/.env
GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE
```

**Restart backend**:
```bash
sudo supervisorctl restart backend
```

---

### 4. GitLab Personal Access Token

**Why**: CI/CD monitoring, deployment automation

**Steps**:
1. Go to [gitlab.com](https://gitlab.com/)
2. **Sign in with GitHub**:
   - Click "Sign in with GitHub"
   - Authorize GitLab to access your GitHub account
3. After login, go to **User Settings** → **Access Tokens**
4. **Add new token**:
   - Name: "NEXUS CI/CD"
   - Expiration: 1 year
   - Scopes:
     - ✓ `api` (Full API access)
     - ✓ `read_repository`
     - ✓ `read_api`
5. Create token and copy it (starts with `glpat-`)

**Add to NEXUS**:
```bash
# Edit /app/backend/.env
GITLAB_TOKEN=glpat-YOUR_TOKEN_HERE
```

**Restart backend**:
```bash
sudo supervisorctl restart backend
```

---

### 5. Manus AI API Key (Optional)

**Why**: Advanced autonomous task execution (investor research, marketing automation)

**Steps**:
1. Visit [manus.im](https://www.manus.im/) or check official Manus AI website
2. Sign up with: `hm2krebsmatthewl@gmail.com`
3. Navigate to API dashboard
4. Generate API key

**Add to NEXUS**:
```bash
# Edit /app/backend/.env
MANUS_API_KEY=YOUR_MANUS_KEY_HERE
```

**Restart backend**:
```bash
sudo supervisorctl restart backend
```

---

## 🔄 All-in-One Update Script

After obtaining all keys, run this to update everything at once:

```bash
# Navigate to backend directory
cd /app/backend

# Edit .env file (use nano or vi)
nano .env

# Update these lines:
# RESEND_API_KEY=re_YOUR_KEY
# PRODUCTHUNT_API_KEY=YOUR_PH_TOKEN
# GITHUB_TOKEN=ghp_YOUR_TOKEN  
# GITLAB_TOKEN=glpat-YOUR_TOKEN
# MANUS_API_KEY=YOUR_MANUS_KEY

# Save and exit (Ctrl+O, Enter, Ctrl+X for nano)

# Restart backend to load new keys
sudo supervisorctl restart backend

# Verify backend started successfully
sudo supervisorctl status backend

# Check logs for confirmation
tail -n 50 /var/log/supervisor/backend.err.log
```

---

## ✅ Verification Checklist

After adding keys, verify each integration:

### Test Resend Email:
```bash
# Register a new user and check for welcome email
API_URL=$(grep REACT_APP_BACKEND_URL /app/frontend/.env | cut -d '=' -f2 | tr -d '"')
curl -X POST "$API_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"your_test@email.com","password":"Test1234!"}'

# Check your inbox for welcome email
```

### Test ProductHunt:
```bash
# Trigger AIxploria scan (should now include ProductHunt results)
TOKEN="your_admin_token"
curl -X POST "$API_URL/api/admin/aixploria/scan" \
  -H "Authorization: Bearer $TOKEN"

# Wait 30 seconds, then check results
curl -X GET "$API_URL/api/admin/aixploria/stats" \
  -H "Authorization: Bearer $TOKEN"

# Should show tools from producthunt_api source
```

### Test GitHub Token:
```bash
# Check if GitHub integration is active
curl -X GET "$API_URL/api/admin/cicd/status" \
  -H "Authorization: Bearer $TOKEN"

# Should return "connected": true
```

---

## 📊 What Changes After Adding Keys

| Integration | Before (Demo) | After (Active) |
|-------------|---------------|----------------|
| **Resend** | Logs emails to console | Sends real emails to inboxes |
| **ProductHunt** | Skipped (403 error) | Returns 20 AI tools per scan via API |
| **GitHub** | Limited 60 req/hour | 5,000 requests/hour + private repo access |
| **GitLab** | Mock data | Real CI/CD pipeline monitoring |
| **Manus AI** | Demo responses | Real autonomous task execution |

---

## 🎯 Priority Order

If you can only set up some keys, prioritize in this order:

1. **Resend** (HIGH) - Email is critical for user experience
2. **GitHub** (MEDIUM) - Increases discovery capability from 60 to 5,000 req/hour
3. **ProductHunt** (MEDIUM) - Adds 20 more tools per scan
4. **GitLab** (LOW) - Only needed if using GitLab for deployment
5. **Manus AI** (LOW) - Platform works fine without it, adds advanced automation

---

## 🆘 Troubleshooting

**"Resend key invalid"**:
- Ensure key starts with `re_`
- Check for extra spaces in .env file
- Verify key is from resend.com/api-keys

**"GitHub API rate limited"**:
- You're using unauthenticated scraping (60/hour limit)
- Add GitHub token to get 5,000/hour limit

**"ProductHunt 403 error"**:
- Normal without API key - ProductHunt blocks web scrapers
- With API key, uses official GraphQL endpoint instead

**"Backend won't restart"**:
```bash
# Check for syntax errors in .env
cat /app/backend/.env

# View backend logs
tail -n 100 /var/log/supervisor/backend.err.log

# Force restart
sudo supervisorctl stop backend
sudo supervisorctl start backend
```

---

## 📞 Support Resources

- **Resend Docs**: [resend.com/docs](https://resend.com/docs)
- **ProductHunt API**: [api.producthunt.com/v2/docs](https://api.producthunt.com/v2/docs)
- **GitHub Tokens**: [docs.github.com/authentication](https://docs.github.com/en/authentication)
- **GitLab Tokens**: [docs.gitlab.com/ee/user/profile/personal_access_tokens](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html)

---

**Last Updated**: March 22, 2026  
**For**: NEXUS v4.1 Multi-Source Discovery Platform
