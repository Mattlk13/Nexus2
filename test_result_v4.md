#====================================================================================================
# NEXUS v4.0 Testing State
#====================================================================================================

## user_problem_statement
Continue building NEXUS and integrate: Resend (email), Manus AI (autonomous agents), tool discovery across GitHub/GitLab, marketing automation, investor outreach, CI/CD monitoring. Make platform fully autonomous with 10 agents.

## backend
  - task: "10 AI agents system (5 core + 5 Manus)"
    implemented: true
    working: true
    file: "server.py, services/advanced_agents.py"
    priority: "high"
    needs_retesting: true
    
  - task: "Resend email service"
    implemented: true
    working: true
    file: "services/email_service.py"
    priority: "high"
    needs_retesting: true
    
  - task: "WebSocket notifications"
    implemented: true
    working: true
    file: "server.py"
    priority: "high"
    needs_retesting: true
    
  - task: "Vendor analytics API"
    implemented: true
    working: true
    file: "server.py:535-565"
    priority: "high"
    needs_retesting: true
    
  - task: "Tool discovery service"
    implemented: true
    working: true
    file: "services/automation_service.py"
    priority: "medium"
    needs_retesting: true
    
  - task: "Manus AI service"
    implemented: true
    working: true
    file: "services/manus_service.py"
    priority: "medium"
    needs_retesting: true
    
  - task: "CI/CD monitoring service"
    implemented: true
    working: true
    file: "services/cicd_service.py"
    priority: "medium"
    needs_retesting: true

## frontend
  - task: "Notification bell component"
    implemented: true
    working: true
    file: "pages/VendorPages.js"
    priority: "high"
    needs_retesting: true
    
  - task: "Vendor analytics dashboard"
    implemented: true
    working: true
    file: "pages/VendorPages.js"
    priority: "high"
    needs_retesting: true
    
  - task: "10 agents display on homepage"
    implemented: true
    working: true
    file: "App.js"
    priority: "high"
    needs_retesting: false
    
  - task: "Agents page with 10 agents"
    implemented: true
    working: true
    file: "pages/CorePages.js"
    priority: "high"
    needs_retesting: true
    
  - task: "Admin automation panel"
    implemented: true
    working: true
    file: "pages/AdminPages.js"
    priority: "medium"
    needs_retesting: true

## metadata
  created_by: "main_agent"
  version: "4.0"
  test_sequence: 4
  run_ui: true

## test_plan
  - name: "User registration with email"
    endpoint: "/api/auth/register"
    method: "POST"
    validation: "User created, welcome email queued"
  
  - name: "Get 10 agents"
    endpoint: "/api/agents"
    method: "GET"
    validation: "Returns 10 agents (5 base + 5 manus)"
  
  - name: "Vendor analytics"
    endpoint: "/api/vendor/analytics"
    method: "GET"
    validation: "Returns metrics for authenticated vendor"
  
  - name: "Get notifications"
    endpoint: "/api/notifications"
    method: "GET"
    validation: "Returns notification array"
  
  - name: "Tool discovery"
    endpoint: "/api/automation/discover-tools"
    method: "POST"
    validation: "Admin only, returns discovered tools with scores"
  
  - name: "Manus task creation"
    endpoint: "/api/manus/task"
    method: "POST"
    validation: "Admin only, creates autonomous task"
  
  - name: "CI/CD status"
    endpoint: "/api/cicd/status"
    method: "GET"
    validation: "Admin only, returns repo health"
  
  - name: "Homepage 10 agents display"
    endpoint: "/"
    method: "UI"
    validation: "Shows '10 AI Agents' stat and all 10 agent cards"
  
  - name: "Agents page"
    endpoint: "/agents"
    method: "UI"
    validation: "Shows all 10 agents with CORE/MANUS labels"
  
  - name: "Notification bell"
    endpoint: "/marketplace (logged in)"
    method: "UI"
    validation: "Bell icon visible, shows unread count"
  
  - name: "Vendor analytics page"
    endpoint: "/vendor/analytics"
    method: "UI"
    validation: "Charts and metrics display for vendor"
  
  - name: "Admin automation tab"
    endpoint: "/admin"
    method: "UI"
    validation: "Automation tab shows Manus status, tools, integrations"
  
  - name: "Follow triggers email"
    endpoint: "User follow action"
    method: "E2E"
    validation: "Notification created + email queued (check logs)"
  
  - name: "Purchase triggers sale email"
    endpoint: "Product purchase"
    method: "E2E"
    validation: "Vendor notification + sale email queued"

## Incorporate User Feedback
User wants full autonomous platform with advanced integrations. All core features implemented. Ready for comprehensive testing.

## Notes for testing subagent
- Test ALL 10 agents via /api/agents endpoint
- Verify email queueing in logs (won't actually send without Resend key)
- Test WebSocket connection establishes
- Validate vendor analytics shows data for authenticated vendor
- Check admin automation panel renders all sections
- Test notification bell component shows in navbar when logged in
- Verify backward compatibility - all original features work
- Test agent manual trigger from admin panel
- Validate tool discovery returns scored results
- Test Manus task creation (will be mock mode)
