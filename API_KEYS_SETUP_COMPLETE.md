# 🔑 NEXUS API Keys Configuration Guide

This guide helps you obtain and configure all API keys needed for full NEXUS functionality.

---

## ✅ Already Configured (Working)

### 1. Emergent LLM Key (Universal Key)
**Status**: ✓ Active  
**Used For**: OpenAI GPT-5.2, Claude Sonnet 4, Gemini Nano Banana  
**Cost**: Pay-as-you-go via your Emergent account  
**Location**: Pre-configured in `backend/.env`

### 2. Stripe (Payment Processing)
**Status**: ✓ Active (Test Mode)  
**Used For**: Product purchases, featured listing boosts  
**Cost**: Free in test mode, 2.9% + $0.30 per transaction in production  
**Location**: Pre-configured in `backend/.env`

### 3. MongoDB
**Status**: ✓ Active  
**Used For**: Database storage  
**Location**: Pre-configured via `MONGO_URL` in `backend/.env`

---

## ⚠️ Demo Mode (Need Real Keys)

### 4. Resend (Email Service)
**Status**: ⚠️ Demo Mode  
**Used For**: 
- Welcome emails on user registration
- Sale notifications to vendors
- Follower alerts
- Password reset emails

**How to Get Key**:
1. Go to [resend.com](https://resend.com)
2. Sign up for free account (100 emails/day on free tier)
3. Navigate to **API Keys** section
4. Click **Create API Key**
5. Copy the key (starts with `re_`)

**How to Configure**:
1. Open `/app/backend/.env`
2. Replace `RESEND_API_KEY=re_demo_key_placeholder` with your real key:
   ```
   RESEND_API_KEY=re_abc123xyz456...
   ```
3. Restart backend: `sudo supervisorctl restart backend`

**Pricing**: 
- Free: 100 emails/day, 3K/month
- Pro: $20/month for 50K emails
- [Full pricing](https://resend.com/pricing)

**Test Email Flow**:
After adding key, register a new user and check your inbox for welcome email.

---

### 5. Manus AI (Agent Orchestration)
**Status**: ⚠️ Demo Mode  
**Used For**:
- Investor research and outreach automation
- Marketing campaign generation
- Platform optimization suggestions
- Complex multi-step autonomous tasks

**How to Get Key**:
1. Visit [manus.im](https://manus.im) (or check official Manus AI website)
2. Sign up for API access
3. Generate API key from dashboard

**How to Configure**:
1. Open `/app/backend/.env`
2. Replace `MANUS_API_KEY=manus_demo_key_placeholder` with real key
3. Restart backend: `sudo supervisorctl restart backend`

**Note**: Manus AI is currently running in demo mode with mocked responses. The 5 Manus agents (Tool Discovery, Investor Outreach, Marketing Automation, Platform Optimizer, CI/CD Monitor) will provide simulated outputs until a real key is added.

---

### 6. GitHub API (Repository Monitoring)
**Status**: ⚠️ Demo Mode  
**Used For**:
- CI/CD monitoring
- Repository health checks
- Code quality analysis
- Automated tool discovery from trending repos

**How to Get Key**:
1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**
3. Select scopes: `repo`, `read:org`, `read:user`
4. Generate and copy token

**How to Configure**:
1. Open `/app/backend/.env`
2. Replace `GITHUB_TOKEN=github_demo_token_placeholder` with your token
3. Restart backend

**Pricing**: Free for public repos, GitHub Pro for private ($4/month)

---

### 7. GitLab API (CI/CD Integration)
**Status**: ⚠️ Demo Mode  
**Used For**:
- CI/CD pipeline monitoring
- Deployment automation
- Code quality gates

**How to Get Key**:
1. Go to [gitlab.com/-/profile/personal_access_tokens](https://gitlab.com/-/profile/personal_access_tokens)
2. Create token with `api`, `read_repository` scopes
3. Copy token

**How to Configure**:
1. Open `/app/backend/.env`
2. Replace `GITLAB_TOKEN=gitlab_demo_token_placeholder` with your token
3. Restart backend

---

## 📋 Quick Setup Checklist

Copy this checklist to track your progress:

- [x] Emergent LLM Key (pre-configured)
- [x] Stripe Test Key (pre-configured)
- [x] MongoDB (pre-configured)
- [ ] Resend API Key → [Get it](https://resend.com/api-keys)
- [ ] Manus AI Key → [Get it](https://manus.im)
- [ ] GitHub Token → [Get it](https://github.com/settings/tokens)
- [ ] GitLab Token → [Get it](https://gitlab.com/-/profile/personal_access_tokens)

---

## 🚨 Important Notes

1. **Never Commit Real Keys**: The `.env` file is gitignored for security
2. **Production Keys**: Use separate keys for development and production
3. **Key Rotation**: Regularly rotate API keys for security
4. **Rate Limits**: Be aware of API rate limits:
   - Resend: 100 emails/day (free tier)
   - GitHub: 60 requests/hour (unauthenticated), 5000/hour (authenticated)
   - Emergent LLM: Based on your account balance

---

## 🆘 Troubleshooting

### "Email not sending"
→ Check if `RESEND_API_KEY` is set correctly  
→ View backend logs: `tail -f /var/log/supervisor/backend.err.log`  
→ Look for "Email sent successfully" or error messages

### "Manus AI not responding"
→ Currently in demo mode - this is expected  
→ Add real `MANUS_API_KEY` to enable full functionality

### "GitHub tool discovery not working"
→ AIxploria discovery works without GitHub key  
→ GitHub API requires token for higher rate limits  
→ Currently using unauthenticated scraping (60 requests/hour limit)

---

## 📞 Support

For questions about:
- **API keys**: Consult each provider's documentation
- **NEXUS platform**: Contact Emergent support
- **Integration issues**: Check `/app/INTEGRATION_GUIDE.md`
- **Deployment**: See `/app/SETUP_GUIDE.md`

---

**Last Updated**: March 22, 2026  
**Version**: v4.1
