# NEXUS Platform - Autonomous Agent Configuration

## 📋 Environment Setup Checklist

### Required for Full Functionality

```bash
# Copy to /app/backend/.env

# ✅ Already Configured (DO NOT CHANGE)
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
JWT_SECRET="nexus-marketplace-jwt-secret-2025"
EMERGENT_LLM_KEY=sk-emergent-a79Ba891bC89777B1C
STRIPE_API_KEY=sk_test_emergent

# ⚠️ ADD THESE FOR FULL AUTOMATION

# Email Service (Resend.com)
RESEND_API_KEY=re_your_key_here
SENDER_EMAIL=hello@yourdomain.com

# Manus AI Orchestration (manus.im)
MANUS_API_KEY=manus_your_key_here

# Optional: Tool Discovery & CI/CD
GITHUB_TOKEN=ghp_your_token_here
GITLAB_TOKEN=glpat_your_token_here
```

---

## 🔑 How to Get API Keys

### 1. Resend Email Service
**What it does**: Sends automated emails (sales, followers, welcome)
**Where to get**:
1. Go to https://resend.com
2. Sign up (free tier: 3000 emails/month)
3. Navigate to "API Keys" section
4. Create new key → Copy to `RESEND_API_KEY`
5. Verify sender domain or use default `onboarding@resend.dev` for testing

### 2. Manus AI
**What it does**: Orchestrates complex autonomous tasks (investor research, tool discovery, strategic analysis)
**Where to get**:
1. Visit https://manus.im or https://open.manus.im
2. Create account
3. Go to API settings → Generate key
4. Copy to `MANUS_API_KEY`
5. **Note**: As of March 2026, Manus is in beta - may require waitlist

### 3. GitHub Personal Access Token (Optional)
**What it does**: Enables tool discovery across GitHub repositories
**Where to get**:
1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Scopes needed: `repo`, `read:org`
4. Copy token → Add to `GITHUB_TOKEN`

### 4. GitLab Personal Access Token (Optional)
**What it does**: CI/CD monitoring and repository management
**Where to get**:
1. Go to https://gitlab.com/-/profile/personal_access_tokens
2. Create token with `api` and `read_repository` scopes
3. Copy → Add to `GITLAB_TOKEN`

---

## 🔄 After Adding Keys

```bash
# Restart backend to load new environment variables
sudo supervisorctl restart backend

# Verify integration status
curl https://your-domain.com/api/cicd/status -H "Authorization: Bearer <admin_token>"
```

---

## 🚦 Service Status Indicators

### Check Current Status
Navigate to `/admin` → **Automation Tab**

**Integration Status Card** shows:
- ✅ **Green "Active"**: API key configured and working
- ⚠️ **Yellow "Demo"**: Running in mock mode (no API key)
- ⚪ **Gray "Pending"**: Not yet configured

### Services Currently in Demo Mode
Without API keys, these services return mock data:
- Manus AI tasks (returns placeholder task IDs)
- GitHub tool discovery (returns sample tools)
- Email sending (logs to console, doesn't send)

**Everything works end-to-end**, but with simulated data.

---

## 🎯 Quick Start (Without External Keys)

The platform is **fully functional** even without external API keys:

1. ✅ **Marketplace** - Buy/sell products (Stripe test mode)
2. ✅ **Creator Studio** - Generate content (Emergent LLM Key)
3. ✅ **Social Feed** - Post and engage
4. ✅ **AI Agents** - All 10 agents run (mock mode for Manus)
5. ✅ **Real-time Notifications** - WebSocket powered
6. ✅ **Vendor Analytics** - Full dashboard with metrics

**To unlock**:
- **Real emails**: Add Resend key
- **Advanced AI tasks**: Add Manus key
- **Tool auto-discovery**: Add GitHub token

---

## 🧪 Testing Agent Functionality

### Test Core Agent
```bash
curl -X POST "https://your-domain.com/api/agents/agent-ceo/run" \
  -H "Authorization: Bearer <admin_token>"
```

### Test Manus Agent
```bash
curl -X POST "https://your-domain.com/api/agents/agent-tool-discovery/run" \
  -H "Authorization: Bearer <admin_token>"
```

### Test Email (if Resend configured)
Register a new account with your real email - you'll receive welcome email instantly.

### Test Notifications
1. Login as User A
2. In another browser, login as User B
3. User B follows User A
4. User A sees real-time notification bell update

---

## 📊 Monitoring & Logs

### Agent Activity Logs
```bash
tail -f /var/log/supervisor/backend.out.log | grep "Agent running"
```

### Email Send Logs
```bash
tail -f /var/log/supervisor/backend.out.log | grep "Email sent"
```

### Manus Task Status
Check admin dashboard → Automation tab → Manus AI Status card

---

## 🚨 Troubleshooting

### Emails Not Sending
- Check `RESEND_API_KEY` is set correctly
- Verify sender domain or use `onboarding@resend.dev`
- Check backend logs: `tail /var/log/supervisor/backend.err.log`

### Manus Agents Showing "Mocked"
- Normal behavior without API key
- Add `MANUS_API_KEY` to enable real autonomous tasks
- Restart backend after adding key

### Tool Discovery Returns Empty
- Requires `GITHUB_TOKEN`
- Check GitHub API rate limits
- Verify token has `repo` scope

### CI/CD Status Shows Error
- Requires `GITHUB_TOKEN` or `GITLAB_TOKEN`
- Works in mock mode without tokens

---

## 💰 Cost Breakdown

### With Current Setup (Emergent LLM Key Only)
- **Emergent LLM Key**: Pay-as-you-go (covers OpenAI, Claude, Gemini)
- **Stripe**: Free (2.9% + $0.30 per transaction)
- **MongoDB**: Free (local hosting)
- **Resend**: Free tier available
- **Estimated**: $50-200/month at 1000 active users

### Adding Manus AI
- **Manus**: Pricing TBD (beta phase)
- **Benefit**: Handles complex tasks that would cost 10x more in manual LLM calls

### Production Scaling (Future)
- **Aiven MongoDB**: $50-500/month (managed hosting)
- **CloudFlare**: $20/month (CDN + DDoS protection)
- **Estimated**: $500-1000/month at 50K users

---

## 🎓 Architecture Notes

### Why Manus AI Layer?
Instead of making dozens of individual API calls for complex tasks, Manus AI:
- Plans multi-step workflows autonomously
- Handles research that requires browsing/searching
- Synthesizes information from multiple sources
- Reduces token costs by 70%+ for complex operations

### Example: Investor Research
**Without Manus** (Manual approach):
1. LLM call: "List VCs in AI space" → 20 names
2. 20x LLM calls: "Research [VC name]"
3. Manual compilation and scoring
4. **Cost**: ~50K tokens = $0.50-1.00

**With Manus**:
1. Single task: "Find 20 VCs for AI marketplace, include contact info and fit analysis"
2. Manus autonomously searches, compiles, and analyzes
3. **Cost**: Single flat rate task = ~$0.10-0.30

---

## 📞 Support

### Agent Not Running?
- Check agent schedule in `/app/backend/server.py` → `agent_schedule`
- Agents run at specific times daily (UTC timezone)
- Use "Run Now" button in admin dashboard for manual trigger

### Need Custom Agent?
The agent system is modular. Add new agents in:
1. `/app/backend/services/advanced_agents.py`
2. Update `agent_schedule`
3. Add to `advanced_agent_map` in `/api/agents/{id}/run` endpoint

---

**Questions?** Check the main integration guide at `/app/INTEGRATION_GUIDE.md`
