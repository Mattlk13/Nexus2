# 🚀 NEXUS API Keys - Quick Setup (5 Minutes)

## ⚡ Speed Run Instructions

You provided credentials: `hm2krebsmatthewl@gmail.com` / `Tristen527!`

### 1️⃣ Resend (Email) - 2 minutes
1. Open: https://resend.com/signup
2. Sign up with your email → Verify email inbox
3. Dashboard → **API Keys** → **Create API Key**
4. Copy the key (starts with `re_`)

### 2️⃣ ProductHunt (AI Discovery) - 2 minutes
**Simplified approach - Developer Token:**
1. Open: https://www.producthunt.com/
2. **Sign in with GitHub** (easier than email)
   - First login to GitHub with your credentials if needed
3. Go to: https://www.producthunt.com/v2/oauth/applications
4. **Create New Application**:
   - Name: `NEXUS Discovery`
   - Redirect URI: `http://localhost:8001/api/callback`
5. Click **Create Token** in Developer Token section
6. Copy the token

### 3️⃣ GitHub (Code Discovery) - 1 minute
1. Login: https://github.com/login
2. Go to: https://github.com/settings/tokens
3. **Generate new token (classic)**
4. Name: `NEXUS Platform`
5. Scopes: ✓ `repo`, ✓ `read:org`, ✓ `read:user`
6. Click Generate → Copy token (starts with `ghp_`)

### 4️⃣ GitLab (CI/CD) - 1 minute
1. Open: https://gitlab.com/users/sign_in
2. Click **Sign in with GitHub** (uses your GitHub account)
3. Go to: https://gitlab.com/-/user_settings/personal_access_tokens
4. **Add new token**:
   - Name: `NEXUS CICD`
   - Scopes: ✓ `api`, ✓ `read_repository`
5. Create → Copy token (starts with `glpat-`)

---

## 📋 Quick Copy-Paste Template

After getting all keys, run this in terminal:

```bash
# Backup current .env
cp /app/backend/.env /app/backend/.env.backup

# Create updated .env with your keys
cat > /app/backend/.env << 'EOF'
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
CORS_ORIGINS="*"
JWT_SECRET="nexus-marketplace-jwt-secret-2025"
EMERGENT_LLM_KEY=sk-emergent-a79Ba891bC89777B1C
STRIPE_API_KEY=sk_test_emergent
RESEND_API_KEY=re_YOUR_RESEND_KEY_HERE
SENDER_EMAIL=hm2krebsmatthewl@gmail.com
MANUS_API_KEY=manus_demo_key_placeholder
GITHUB_TOKEN=ghp_YOUR_GITHUB_TOKEN_HERE
GITLAB_TOKEN=glpat-YOUR_GITLAB_TOKEN_HERE
PRODUCTHUNT_API_KEY=YOUR_PRODUCTHUNT_TOKEN_HERE
EOF

# Restart backend
sudo supervisorctl restart backend

# Check status
sudo supervisorctl status backend
```

**Then replace**:
- `re_YOUR_RESEND_KEY_HERE` with your Resend key
- `ghp_YOUR_GITHUB_TOKEN_HERE` with your GitHub token
- `glpat-YOUR_GITLAB_TOKEN_HERE` with your GitLab token
- `YOUR_PRODUCTHUNT_TOKEN_HERE` with your ProductHunt token

---

## ✅ Verification (After Keys Added)

Test each integration:

```bash
# Get API URL
API_URL=$(grep REACT_APP_BACKEND_URL /app/frontend/.env | cut -d '=' -f2 | tr -d '"')

# 1. Test Email (Resend)
curl -X POST "$API_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser123","email":"your_real_email@gmail.com","password":"Test1234!"}'
# ✓ Check your email for welcome message

# 2. Test ProductHunt + GitHub (Discovery)
# First get admin token
TOKEN=$(curl -s -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@nexus.ai","password":"admin123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")

# Trigger comprehensive scan
curl -X POST "$API_URL/api/admin/aixploria/scan?comprehensive=true" \
  -H "Authorization: Bearer $TOKEN"

# Wait 60 seconds, then check stats
sleep 60 && curl -X GET "$API_URL/api/admin/aixploria/stats" \
  -H "Authorization: Bearer $TOKEN"
# ✓ Should show tools from: aixploria_top100, aixploria_latest, github_trending, producthunt_api, priority_list
```

---

## 🎯 What Activates After Setup

| Service | Before | After |
|---------|--------|-------|
| **Resend** | Console logs only | Real emails to users |
| **ProductHunt** | Skipped (403 error) | ~20 AI tools per scan |
| **GitHub** | 60 requests/hour | 5,000 requests/hour |
| **GitLab** | Mock data | Real repo monitoring |

---

**Need Help?** Each platform has "Forgot Password" if you need to reset before using provided credentials.

**Estimated Total Time**: 5-7 minutes for all 4 services
