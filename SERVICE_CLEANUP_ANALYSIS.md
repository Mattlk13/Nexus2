# Service Cleanup Analysis

## Active Services (DO NOT DELETE)

### Hybrid Services (Core - 12)
- nexus_ultimate_controller.py
- nexus_hybrid_llm.py
- nexus_hybrid_media.py
- nexus_hybrid_music.py
- nexus_hybrid_agents.py  
- nexus_hybrid_payments.py
- nexus_hybrid_analytics.py
- nexus_hybrid_auth.py
- nexus_hybrid_automation.py
- nexus_hybrid_discovery.py
- nexus_hybrid_mcp.py
- nexus_hybrid_notifications.py
- nexus_hybrid_comms.py

### New Services (Keep - 5)
- nexus_investor_dashboard.py
- nexus_marketing_dashboard.py
- nexus_investor_discovery.py
- nexus_unified_storage.py
- nexus_daily_automation.py
- nexus_automated_testing.py

### Active Dependencies (Keep - ~15)
- cloudflare_r2_service.py (used by unified storage)
- seaweedfs_client.py (used by unified storage)
- email_service.py (imported in server.py)
- manus_service.py (imported in server.py)
- automation_service.py (imported in server.py)
- cicd_service.py (imported in server.py)
- aixploria_service.py (imported in server.py)
- integration_status.py (imported in server.py)
- elevenlabs_service.py (imported in server.py)
- fal_ai_service.py (imported in server.py)
- openclaw_service.py (imported in server.py)
- text_to_video_service.py (imported in routes)
- runway_video_service.py (imported in routes)
- social_media_service.py (imported in server.py)
- redis_cache_service.py (imported in server.py)

### Ultra Services (Keep - 5)
- ultra_image_video_generator.py
- ultra_voice_service.py
- ultra_llm_service.py
- ultra_video_conferencing.py

### Other Active (Keep - 10+)
- performance_optimizer.py
- mega_discovery_service.py
- enhanced_user_profile_service.py
- investor_dashboard_service.py
- cloudflare_workers_service.py
- marketing_automation_service.py
- mcp_integration_service.py
- github_gitlab_service.py
- analytics_dashboard_service.py
- mcp_registry_service.py
- workflow_automation_service.py
- cloudflare_service.py

## Potentially Obsolete Services (Review Before Delete)

These services may have been consolidated into hybrids:
- advanced_agents.py (→ nexus_hybrid_agents)
- multi_agent_service.py (→ nexus_hybrid_agents)
- crewai_service.py (→ nexus_hybrid_agents)
- yolo_service.py (→ nexus_hybrid_agents)

- llm_finetuning_service.py (→ nexus_hybrid_llm)

- stripe_service.py (→ nexus_hybrid_payments)
- razorpay_service.py (→ nexus_hybrid_payments)
- paypal_service.py (→ nexus_hybrid_payments)

- notification_service.py (→ nexus_hybrid_notifications)
- notification_scheduler.py (→ nexus_hybrid_notifications)

- oauth.py (separate route, keep for now)

## Recommendation

**DO NOT DELETE** anything yet. The codebase is complex with many cross-dependencies.
Instead:
1. Run comprehensive tests
2. Monitor usage logs
3. Gradually deprecate unused services
4. Create migration plan for each service

**Current Status**: 83 service files, ~50 actively used, ~30 candidates for deprecation
