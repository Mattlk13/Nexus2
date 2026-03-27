# NEXUS AI - CI/CD Workflow Setup Guide

## 🎯 Overview
Your NEXUS platform now has a fully automated CI/CD workflow system that runs continuously to:
- **Test automatically** every 30 minutes
- **Monitor health** every 15 minutes  
- **Process tasks** every hour
- **Send Slack notifications** for all events
- **Create GitHub PRs** for completed work

---

## 🔐 Step 1: Add Your Real Credentials

The placeholders have been added to `/app/backend/.env`. Replace them with your real values:

```bash
# Edit the .env file
nano /app/backend/.env

# Then update these values:
GITHUB_TOKEN=your_actual_github_token
GITHUB_REPO_OWNER=your_github_username  
GITHUB_REPO_NAME=your_repo_name

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/ACTUAL/WEBHOOK

POSTHOG_API_KEY=your_actual_posthog_key
POSTHOG_PROJECT_ID=your_project_id

# Restart backend to load new values
sudo supervisorctl restart backend
```

---

## 🚀 Step 2: Start the CI/CD Workflow

### Method 1: Via API (Recommended)
```bash
# Login and get token
TOKEN=$(curl -s -X POST "YOUR_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@nexus.ai","password":"admin123"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")

# Start the CI/CD scheduler
curl -X POST "YOUR_URL/api/autonomous-systems/scheduler/start" \
  -H "Authorization: Bearer $TOKEN"

# Check status
curl -X GET "YOUR_URL/api/autonomous-systems/scheduler/status" \
  -H "Authorization: Bearer $TOKEN"
```

### Method 2: Via Frontend Dashboard
1. Login to NEXUS (admin@nexus.ai / admin123)
2. Navigate to `/admin/autonomous-systems`
3. Click "Start All Systems" button
4. The CI/CD scheduler will start automatically

---

## 📊 What the CI/CD Workflow Does

### Automated Testing Loop (Every 30 minutes)
- Runs backend tests
- Runs integration tests (API endpoints)
- Runs performance tests
- Calculates code coverage
- **Sends Slack notification** with results
- Auto-fixes failing tests if possible

### Health Monitoring Loop (Every 15 minutes)
- Checks backend, frontend, database status
- **Sends Slack alert** if services are unhealthy
- Attempts auto-healing (restarts failed services)
- Tracks health history

### Task Processing Loop (Every 60 minutes)
- Processes queued development tasks
- Uses LLM to generate code
- Runs tests on generated code
- **Creates GitHub PR** if code quality passes
- **Sends Slack notification** on completion/failure

---

## 📱 Slack Notifications

You'll receive notifications for:
- ✅ Test results (pass/fail with details)
- ⚠️ Health check alerts
- 🔧 Task processing updates
- ❌ Errors and failures
- 🚀 System startup/shutdown

Example notification:
```
🚀 CI/CD Workflow Started
Autonomous testing, health monitoring, and task processing are now active.
```

---

## 🐙 GitHub Integration

When tasks complete successfully, the system will:
1. Create a new branch (`auto-task-{number}`)
2. Commit the generated code
3. Open a Pull Request
4. Add description with task details
5. Notify you via Slack

---

## 🎛️ Control Endpoints

### Scheduler Control
- `POST /api/autonomous-systems/scheduler/start` - Start workflow
- `POST /api/autonomous-systems/scheduler/stop` - Stop workflow
- `GET /api/autonomous-systems/scheduler/status` - Get status

### System Control
- `POST /api/autonomous-systems/start-all` - Start all systems + scheduler
- `GET /api/autonomous-systems/status` - Get all systems status
- `POST /api/autonomous-systems/testing/run` - Run tests now
- `POST /api/autonomous-systems/cicd/audit` - Run code audit now
- `GET /api/autonomous-systems/cicd/health` - Check health now

---

## 🔧 Customizing Intervals

Edit `/app/backend/services/cicd_workflow_scheduler.py`:

```python
self.test_interval = 1800  # 30 minutes (in seconds)
self.health_interval = 900  # 15 minutes
self.task_interval = 3600  # 1 hour
```

Then restart: `sudo supervisorctl restart backend`

---

## 📈 Monitoring Your Workflow

### Check Scheduler Status
```bash
curl -X GET "YOUR_URL/api/autonomous-systems/scheduler/status" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### View Backend Logs
```bash
tail -f /var/log/supervisor/backend.*.log | grep -E "CI/CD|Test|Health|Task"
```

### Check Slack Channel
All events will be posted to your configured Slack webhook.

---

## 🐛 Troubleshooting

### Scheduler Not Running
```bash
# Check backend logs
tail -n 100 /var/log/supervisor/backend.err.log

# Verify credentials are set
grep -E "SLACK_WEBHOOK|GITHUB_TOKEN|POSTHOG" /app/backend/.env

# Restart backend
sudo supervisorctl restart backend
```

### Slack Notifications Not Arriving
- Verify `SLACK_WEBHOOK_URL` is correct
- Test webhook manually:
```bash
curl -X POST YOUR_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{"text":"Test from NEXUS"}'
```

### GitHub PRs Not Creating
- Verify `GITHUB_TOKEN` has `repo` scope
- Verify `GITHUB_REPO_OWNER` and `GITHUB_REPO_NAME` are correct
- Check backend logs for GitHub API errors

---

## ✅ Success Indicators

You'll know it's working when:
- ✓ Scheduler status shows `"running": true`
- ✓ `last_test_run`, `last_health_check`, `last_task_process` have timestamps
- ✓ You receive Slack notifications every 15-30-60 minutes
- ✓ Backend logs show "Running automated test suite...", "Running health check...", etc.

---

## 🎉 What's Next?

1. **Add tasks** to the development queue via API or dashboard
2. **Monitor** via Slack notifications
3. **Review** GitHub PRs created by the system
4. **Adjust** intervals based on your needs
5. **Extend** with custom workflows

The system is now fully autonomous - it will test, monitor, fix, and deploy continuously!

---

## 📞 Support

- View scheduler code: `/app/backend/services/cicd_workflow_scheduler.py`
- View routes: `/app/backend/routes/autonomous_systems.py`
- Check integration services:
  - Slack: `/app/backend/services/slack_notification_service.py`
  - GitHub: `/app/backend/services/github_integration_service.py`
  - Testing: `/app/backend/services/autonomous_testing_system.py`
