#!/bin/bash
# NEXUS 24/7 Autonomous Mode Startup Script
# Launches all autonomous agents and monitoring systems

echo "🤖 Starting NEXUS Autonomous Mode 24/7..."

# Start backend in background if not running
if ! sudo supervisorctl status backend | grep -q "RUNNING"; then
    echo "🚀 Starting backend..."
    sudo supervisorctl start backend
    sleep 5
fi

# Start frontend in background if not running
if ! sudo supervisorctl status frontend | grep -q "RUNNING"; then
    echo "🎨 Starting frontend..."
    sudo supervisorctl start frontend
    sleep 3
fi

# Wait for services to be ready
echo "⏳ Waiting for services to initialize..."
sleep 10

# Get backend URL
BACKEND_URL=$(grep REACT_APP_BACKEND_URL /app/frontend/.env | cut -d '=' -f2)

echo "🤖 Activating Autonomous Platform Manager..."
curl -X POST "$BACKEND_URL/api/v2/hybrid/autonomous/start" \
    -H "Content-Type: application/json"

echo ""
echo "⚕️ Activating Self-Healing Infrastructure..."
curl -X POST "$BACKEND_URL/api/v2/hybrid/selfhealing/start" \
    -H "Content-Type: application/json"

echo ""
echo "🔍 Activating Autonomous Auditor..."
curl -X POST "$BACKEND_URL/api/v2/hybrid/auditor/start" \
    -H "Content-Type: application/json"

echo ""
echo "🔧 Activating Maintenance Automation..."
curl -X POST "$BACKEND_URL/api/v2/hybrid/maintenance/start" \
    -H "Content-Type: application/json"

echo ""
echo "✅ All autonomous systems activated!"
echo ""
echo "📊 Dashboard: http://localhost:3000/autonomous"
echo "🤖 8 AI Agents: Running 24/7"
echo "⚕️ Self-Healing: Active"
echo "🔍 Auditing: Continuous"
echo "🔧 Maintenance: Automated"
echo ""
echo "🎉 NEXUS is now fully autonomous!"
echo "💤 The platform will manage itself 24/7"
echo ""

# Create systemd service for persistence
echo "📝 Creating systemd service for 24/7 operation..."

sudo tee /etc/systemd/system/nexus-autonomous.service > /dev/null << 'EOF'
[Unit]
Description=NEXUS Autonomous Platform
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/app
ExecStart=/app/start_autonomous_247.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable nexus-autonomous.service
sudo systemctl start nexus-autonomous.service

echo "✅ Systemd service created and enabled!"
echo "🔄 Autonomous mode will auto-start on system reboot"
echo ""
echo "To check status: sudo systemctl status nexus-autonomous"
echo "To stop: sudo systemctl stop nexus-autonomous"
echo "To restart: sudo systemctl restart nexus-autonomous"
