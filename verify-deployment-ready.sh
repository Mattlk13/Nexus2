#!/bin/bash
# Deployment Readiness Verification Script

echo "🔍 NEXUS Deployment Readiness Check"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0

# Check frontend build
echo -n "Frontend build exists... "
if [ -d "/app/frontend/build" ] && [ -f "/app/frontend/build/index.html" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL++))
fi

# Check backend server
echo -n "Backend server file exists... "
if [ -f "/app/backend/server.py" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL++))
fi

# Check requirements.txt
echo -n "Backend requirements.txt exists... "
if [ -f "/app/backend/requirements.txt" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL++))
fi

# Check deployment guides
echo -n "Deployment guides created... "
if [ -f "/app/PRODUCTION_DEPLOYMENT_PACKAGE.md" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL++))
fi

# Check environment template
echo -n "Environment template exists... "
if [ -f "/app/PRODUCTION_ENV_TEMPLATE.env" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL++))
fi

# Check backend health
echo -n "Backend health check... "
HEALTH=$(curl -s http://localhost:8001/api/health 2>/dev/null | grep -o '"status":"healthy"')
if [ ! -z "$HEALTH" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS++))
else
    echo -e "${YELLOW}⚠️  SKIP (Backend may not be running)${NC}"
fi

# Check frontend routes
echo -n "App.js has new routes... "
if grep -q "/messages" /app/frontend/src/App.js && \
   grep -q "/profile-new" /app/frontend/src/App.js && \
   grep -q "/admin-dashboard" /app/frontend/src/App.js; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL++))
fi

# Check Git status
echo -n "Git repository clean... "
if git -C /app diff --quiet; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS++))
else
    echo -e "${YELLOW}⚠️  Uncommitted changes${NC}"
fi

echo ""
echo "===================================="
echo -e "Results: ${GREEN}${PASS} passed${NC}"
if [ $FAIL -gt 0 ]; then
    echo -e "         ${RED}${FAIL} failed${NC}"
fi
echo "===================================="
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 DEPLOYMENT READY!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Read: /app/PRODUCTION_DEPLOYMENT_PACKAGE.md"
    echo "2. Run: ./deploy-to-production.sh"
    echo "3. Or follow manual deployment steps"
    exit 0
else
    echo -e "${RED}⚠️  Some checks failed. Review above.${NC}"
    exit 1
fi
