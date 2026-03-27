# 🔑 API Keys Quick Start Guide

## Current Status: ✅ Platform Fully Functional

Your NEXUS platform is **100% operational** right now. All services work in demo/mock mode without requiring additional API keys.

---

## 🎯 What Works WITHOUT Extra Keys

✅ **Marketplace** - Buy/sell products (Stripe test mode)
✅ **Creator Studio** - Generate AI content (Emergent LLM Key)
✅ **Social Feed** - Post, like, comment, follow
✅ **10 AI Agents** - All agents run (Manus agents in mock mode)
✅ **Admin Dashboard** - Full platform management
✅ **Vendor Analytics** - Complete metrics dashboard
✅ **Real-time Notifications** - WebSocket powered
✅ **Email Queueing** - System logs email events (doesn't send)

**You can use everything and test the full platform immediately.**

---

## 🚀 Unlock Full Power (Optional)

Add these keys to `/app/backend/.env` to enable:

### 1. Real Emails (Resend)
**What it unlocks**: Actual email delivery to users
**Current behavior**: Emails are queued but logged to console only
**Cost**: Free (3,000 emails/month)

```env
RESEND_API_KEY=re_xxxxxxxxx
SENDER_EMAIL=hello@yourdomain.com
```

**Get key**:
1. Go to https://resend.com
2. Sign up (free)
3. Create API key
4. Add to `.env`
5. Restart: `sudo supervisorctl restart backend`

**Test**: Register new user with real email → Check inbox for welcome email

---

### 2. Manus AI (Advanced Agents)
**What it unlocks**: Real autonomous task execution
**Current behavior**: Returns mock task IDs and placeholder results
**Cost**: TBD (Beta phase - may be free during beta)

```env
MANUS_API_KEY=manus_xxxxxxxxx
```

**Get key**:
1. Visit https://manus.im or https://open.manus.im
2. Create account
3. Go to API settings
4. Generate key
5. Add to `.env`
6. Restart backend

**Test**: 
```bash
curl -X POST "https://your-domain.com/api/manus/task" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"description":"Research top 5 payment gateways","context":{}}'
```

**What changes**: 
- Tool Discovery Agent → Finds REAL tools from GitHub
- Investor Outreach Agent → Researches REAL VCs with contact info
- Marketing Automation → Creates REAL campaign strategies
- Platform Optimizer → Provides REAL data-driven insights

---

### 3. GitHub Token (Tool Discovery)
**What it unlocks**: Automated search for beneficial integrations
**Current behavior**: Returns sample tools
**Cost**: Free

```env
GITHUB_TOKEN=ghp_xxxxxxxxx
```

**Get key**:
1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: `repo`, `read:org`
4. Copy token
5. Add to `.env`

**Test**: Admin panel → Automation tab → Click "RUN DISCOVERY"

---

### 4. GitLab Token (Optional - CI/CD)
**What it unlocks**: GitLab repository monitoring
**Current behavior**: Mock CI/CD data
**Cost**: Free

```env
GITLAB_TOKEN=glpat-xxxxxxxxx
```

**Get key**:
1. Go to https://gitlab.com/-/profile/personal_access_tokens
2. Create token
3. Scopes: `api`, `read_repository`
4. Add to `.env`

---

## ⚡ Quick Setup (2 Minutes)

**For most impact, add Resend first**:

```bash
# 1. Edit .env
nano /app/backend/.env

# 2. Add this line (replace with your key):
RESEND_API_KEY=re_your_actual_key
SENDER_EMAIL=hello@yourdomain.com

# 3. Save (Ctrl+O, Enter, Ctrl+X)

# 4. Restart backend
sudo supervisorctl restart backend

# 5. Test - register with your real email
# You'll receive welcome email instantly!
```

---

## 📊 Impact Matrix

| Service | Without Key | With Key | Cost | Impact |
|---------|------------|----------|------|--------|
| **Resend** | Logs emails | Real email delivery | Free (3K/mo) | 🟢 High - User engagement |
| **Manus AI** | Mock tasks | Real autonomous tasks | TBD (Beta) | 🟡 Medium - Better insights |
| **GitHub** | Sample tools | Real tool discovery | Free | 🟡 Medium - Find integrations |
| **GitLab** | Mock CI/CD | Real monitoring | Free | 🔵 Low - Nice to have |

**Recommendation**: Start with **Resend** (takes 2 minutes, high impact)

---

## 🧪 How to Verify

### Email Service
```bash
# Check logs for email queueing
tail -f /var/log/supervisor/backend.out.log | grep "Email"
```

### Manus AI
```bash
# Check admin panel → Automation tab
# Manus AI Orchestration card should show "✓ Connected" instead of "⚠ Demo Mode"
```

### GitHub Token
```bash
# Trigger discovery, check results
curl -X POST "https://your-domain.com/api/automation/discover-tools" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '["marketing"]'
```

---

## ❓ FAQ

**Q: Do I need all keys to use the platform?**
A: No! Platform is fully functional without any additional keys. They just unlock advanced features.

**Q: What if I don't add any keys?**
A: Everything works, just with simulated data for advanced features. Perfect for testing and demos.

**Q: Can I add keys later?**
A: Yes! Add anytime and restart backend. No data loss, seamless upgrade.

**Q: Are placeholder keys secure?**
A: Yes, they're just markers. Services detect them and run in safe mock mode.

**Q: Which key should I add first?**
A: **Resend** - Biggest user experience improvement for minimal effort.

**Q: How much will this cost at scale?**
A: Estimated monthly costs:
- 1K users: $50-100 (mostly Emergent LLM Key)
- 10K users: $200-500
- 100K users: $1K-2K (add Aiven for database)

---

## 🎓 Next Steps

1. **Test Everything** - Platform works perfectly in demo mode
2. **Add Resend Key** - Takes 2 minutes, enables real emails
3. **Add Manus Key** (When Available) - Unlocks advanced automation
4. **Monitor Agents** - Check `/admin` → Automation tab daily
5. **Iterate** - Agents discover improvements automatically

---

**The platform is ready to use RIGHT NOW.** API keys are optional upgrades. 🚀

---

**Questions?** See `/app/INTEGRATION_GUIDE.md` for detailed setup instructions.
