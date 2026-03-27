# NEXUS v4.0 - Advanced Integration Guide

## 🎯 Overview
NEXUS now operates with **10 autonomous AI agents** orchestrated across two layers:
- **5 Core Agents** (GPT-5.2, Claude Sonnet 4, Gemini 2.5): Handle daily operations
- **5 Manus AI Agents**: Handle complex automation, discovery, and strategic tasks

---

## 🤖 Agent System Architecture

### Layer 1: Core Operational Agents (Always Active)
These run on **Emergent LLM Key** with scheduled tasks:

1. **CEO Agent** (8PM Daily)
   - Reviews platform KPIs
   - Generates profit reports
   - Strategic oversight

2. **Product Manager Agent** (6AM Daily)
   - Imports trending products
   - Optimizes product catalog
   - Quality control

3. **Marketing Agent** (12PM Daily)
   - Posts to social platforms
   - Creates campaigns
   - Engagement tracking

4. **Vendor Manager Agent** (9AM Daily)
   - Approves new vendors
   - Moderates listings
   - Vendor support

5. **Finance Agent** (8:30PM Daily)
   - Tracks revenue
   - Processes payouts
   - Financial reporting

### Layer 2: Manus AI Orchestration Layer (Autonomous)
These run on **Manus AI API** for complex, multi-step tasks:

6. **Tool Discovery Agent** (3AM Daily)
   - Searches GitHub/GitLab for beneficial tools
   - Evaluates integration ROI
   - Auto-recommends high-priority tools
   - **API**: `/api/automation/discover-tools`

7. **Investor Outreach Agent** (10AM Daily)
   - Researches VCs and angel investors
   - Creates pitch materials
   - Tracks outreach campaigns
   - **API**: `/api/agents/agent-investor/run`

8. **Marketing Automation Agent** (2PM Daily)
   - Auto-generates campaigns
   - Schedules social posts
   - A/B testing
   - **API**: `/api/agents/agent-marketing-auto/run`

9. **Platform Optimizer Agent** (11PM Daily)
   - Analyzes user behavior
   - Suggests UX improvements
   - Performance optimization
   - **API**: `/api/agents/agent-optimizer/run`

10. **CI/CD Monitor Agent** (4AM Daily)
    - Monitors deployments
    - Runs automated tests
    - Health checks
    - **API**: `/api/cicd/status`

---

## 📧 Email Automation (Resend Integration)

### Automated Email Triggers

1. **Welcome Email** - Sent on user registration
   - Platform tour
   - Getting started guide
   - First action prompts

2. **Sale Notification** - Sent when vendor makes a sale
   - Sale amount (after platform fee)
   - Product details
   - Link to analytics dashboard

3. **New Follower** - Sent when someone follows you
   - Follower name
   - Engagement encouragement

### Email Service API
```python
from services.email_service import email_service

# Send custom email
await email_service.send_email(
    to="user@example.com",
    subject="Your Subject",
    html="<html>...</html>"
)

# Pre-built templates
await email_service.send_sale_notification(seller_email, name, product, amount)
await email_service.send_welcome_email(email, username)
await email_service.send_follower_notification(email, follower_name)
```

**Setup**: Add `RESEND_API_KEY` to `/app/backend/.env` (get from resend.com)

---

## 🔮 Manus AI Integration

### What is Manus AI?
Autonomous agent platform for complex, multi-step tasks requiring research, planning, and execution.

### Use Cases in NEXUS
- **Investor Research**: Finds 20+ VCs with contact info and fit analysis
- **Tool Discovery**: Searches GitHub for integration opportunities
- **Marketing Campaigns**: Creates full campaign strategies
- **Platform Analytics**: Deep-dive analysis with actionable insights

### API Endpoints

**Create Task**
```bash
POST /api/manus/task
Authorization: Bearer <admin_token>
{
  "description": "Research top 10 payment gateways for crypto",
  "context": {"category": "payments", "focus": "crypto"}
}
```

**Get Task Status**
```bash
GET /api/manus/task/{task_id}
Authorization: Bearer <admin_token>
```

**Setup**: Add `MANUS_API_KEY` to `/app/backend/.env` (get from manus.im)

---

## 🔧 CI/CD & Automation Services

### GitHub/GitLab Integration
Automated monitoring and discovery across repositories.

**Endpoints**:
- `GET /api/cicd/status` - Repository health, code quality
- `POST /api/cicd/deploy` - Trigger deployment
- `POST /api/cicd/test` - Run automated tests

**Setup**: Add `GITHUB_TOKEN` and `GITLAB_TOKEN` to `.env`

### Tool Discovery System
Automatically searches GitHub/GitLab every day at 3AM for tools that would benefit NEXUS.

**Categories Monitored**:
- Marketing automation
- Investor tools
- Admin dashboard enhancements
- Payment solutions
- AI tools
- Workflow automation

**Manual Trigger**:
```bash
POST /api/automation/discover-tools
Authorization: Bearer <admin_token>
["marketing", "ai_tools", "payments"]
```

**View Results**:
```bash
GET /api/automation/discovered-tools
Authorization: Bearer <admin_token>
```

Each tool is scored on:
- GitHub stars (popularity)
- Language compatibility
- Category relevance
- Recent maintenance
- **Auto-recommendation** for tools scoring 60+

---

## 🎨 Real-Time Features

### WebSocket Notifications
- Connection: `wss://your-domain.com/api/socket.io`
- Events: `new_notification`, `sale_alert`, `follow_alert`
- Auto-reconnects on disconnect

### Notification Bell Component
Displays real-time notifications in navbar with unread count badge.

**Frontend Hook**:
```javascript
import { useSocket } from './pages/VendorPages';

const { connected } = useSocket();
```

---

## 📊 Vendor Analytics Dashboard

**Route**: `/vendor/analytics`

**Metrics**:
- Total sales & revenue
- Top-performing products
- Recent transactions
- Follower growth
- Revenue trends

**API**: `GET /api/vendor/analytics`

---

## 🛠 Admin Automation Panel

**Route**: `/admin` (Automation tab)

**Features**:
1. **Manus AI Status** - Connection health, active agents
2. **Tool Discovery** - View discovered tools, trigger manual scans
3. **Integration Status** - See all active integrations (Stripe, OpenAI, Claude, Resend, Manus, etc.)
4. **Manual Agent Triggers** - Run any agent on-demand

---

## 🔐 Environment Variables Reference

```env
# Database
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"

# Authentication
JWT_SECRET="nexus-marketplace-jwt-secret-2025"

# AI Services (Emergent LLM Key works for all 3)
EMERGENT_LLM_KEY=sk-emergent-xxx  # OpenAI, Claude, Gemini

# Payments
STRIPE_API_KEY=sk_test_xxx

# Email Automation
RESEND_API_KEY=re_xxx
SENDER_EMAIL=hello@yourdomain.com

# Advanced Agents
MANUS_API_KEY=manus_xxx  # From manus.im

# CI/CD (Optional)
GITHUB_TOKEN=ghp_xxx  # For tool discovery
GITLAB_TOKEN=glpat-xxx  # For CI/CD monitoring
```

---

## 🚀 Deployment Status

### ✅ Fully Integrated
- Stripe (Payments)
- OpenAI GPT-5.2 (Content generation)
- Claude Sonnet 4 (Content moderation)
- Gemini Nano Banana (Image generation)
- Resend (Email automation)
- WebSockets (Real-time notifications)

### 🟡 Configured (Requires API Keys)
- Manus AI (Task orchestration) - Add `MANUS_API_KEY`
- GitHub API (Tool discovery) - Add `GITHUB_TOKEN`
- GitLab API (CI/CD) - Add `GITLAB_TOKEN`

### ⚪ Future Integrations
- Ollama (Local LLM for cost savings)
- Aiven (Production database hosting)
- SendGrid (Alternative email service)
- Twilio (SMS notifications)

---

## 📈 Business Impact

### Revenue Streams
1. **15% Platform Fee** on all product sales
2. **Featured Boost** ($99/7 days) for prominent product placement
3. **Future**: Premium agent features, white-label licensing

### Automation Benefits
- **$0 operational cost** - All agents run autonomously
- **24/7 operation** - No human intervention needed
- **Scalability** - Handles 10K+ users with same agent count
- **Data-driven decisions** - Agents analyze metrics daily

---

## 🧪 Testing Endpoints

### Health Check
```bash
curl https://your-domain.com/api/health
```

### Get All Agents
```bash
curl https://your-domain.com/api/agents
```

### Trigger Agent Manually (Admin only)
```bash
curl -X POST https://your-domain.com/api/agents/agent-tool-discovery/run \
  -H "Authorization: Bearer <admin_token>"
```

### Check Tool Discovery Results
```bash
curl https://your-domain.com/api/automation/discovered-tools \
  -H "Authorization: Bearer <admin_token>"
```

---

## 🎓 Next Steps

1. **Add API Keys**: Update `.env` with Manus, GitHub, GitLab tokens for full functionality
2. **Monitor Agents**: Check `/admin` → Automation tab for tool discoveries
3. **Review Reports**: Agents generate daily reports accessible in admin dashboard
4. **Scale**: When ready, migrate to Aiven for production database
5. **Customize**: Adjust agent schedules in `server.py` → `agent_schedule`

---

## 💡 Pro Tips

- **Agent Reports**: All agent activities are logged to `agent_reports` collection
- **Demo Mode**: Most services work in demo mode without API keys (mock data)
- **Email Testing**: Resend provides test mode at onboarding@resend.dev
- **Cost Optimization**: Emergent LLM Key covers 3 major LLM providers
- **Monitoring**: CI/CD agent tracks code quality and deployment health

---

**Last Updated**: March 22, 2026
**Version**: 4.0.0 (Autonomous Edition)
**Status**: Production Ready ✅
