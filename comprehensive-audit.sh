#!/bin/bash
echo "🔍 NEXUS COMPREHENSIVE AUDIT"
echo "============================"
echo ""

# Backend Health
echo "📊 Backend Status:"
curl -s http://localhost:8001/api/health 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"  ✅ Status: {d.get('status', 'N/A')}\")" || echo "  ❌ Backend not responding"

# Database
echo ""
echo "🗄️ Database:"
python3 -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
os.chdir('/app/backend')
from dotenv import load_dotenv
load_dotenv()
async def check():
    try:
        client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        await client.admin.command('ping')
        dbs = await client.list_database_names()
        print(f'  ✅ MongoDB: Connected ({len(dbs)} databases)')
        client.close()
    except Exception as e:
        print(f'  ❌ MongoDB: {e}')
asyncio.run(check())
"

# AI Services
echo ""
echo "🤖 AI Services:"
for service in sora_video gpt_image groq crewai; do
    status=$(curl -s http://localhost:8001/api/v2/hybrid/$service/capabilities 2>/dev/null | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    if [ "$status" = "active" ]; then
        echo "  ✅ $service: active"
    else
        echo "  ❌ $service: inactive"
    fi
done

# Frontend
echo ""
echo "🎨 Frontend:"
if curl -s http://localhost:3000 >/dev/null 2>&1; then
    echo "  ✅ React Dev Server: Running"
else
    echo "  ⚠️ React Dev Server: Not running (production build exists)"
fi

if [ -d "/app/frontend/build" ]; then
    size=$(du -sh /app/frontend/build | cut -f1)
    echo "  ✅ Production Build: $size"
else
    echo "  ❌ Production Build: Missing"
fi

# Resources
echo ""
echo "💾 Resources:"
df -h / | tail -1 | awk '{print "  Disk: "$3" used / "$2" total ("$5" used)"}'
free -h | grep Mem | awk '{print "  RAM: "$3" used / "$2" total"}'

# Git Status
echo ""
echo "📦 Repository:"
cd /app
commits=$(git log --oneline | wc -l)
echo "  ✅ Commits: $commits"
echo "  ✅ Branch: $(git branch --show-current)"
latest=$(git log -1 --pretty=format:"%h - %s" 2>/dev/null)
echo "  ✅ Latest: $latest"

echo ""
echo "✅ Audit Complete"
