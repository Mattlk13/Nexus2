"""
NEXUS Hybrid Services Router
Routes for Ultimate Controller, Music, MCP, Investor Dashboard, Marketing Dashboard, CI/CD
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

from .dependencies import get_current_user, require_admin

logger = logging.getLogger(__name__)

# Import all hybrid services
from services.nexus_ultimate_controller import ultimate_controller
from services.nexus_hybrid_music import hybrid_music
from services.nexus_hybrid_mcp import hybrid_mcp
from services.nexus_hybrid_netneutrality import create_netneutrality_engine
from services.nexus_hybrid_ml import create_ml_engine
from services.nexus_hybrid_productivity import create_productivity_engine
from services.nexus_hybrid_languages import create_languages_engine
from services.nexus_hybrid_github_infra import create_github_infra_engine
from services.nexus_hybrid_drift import create_drift_engine
from services.nexus_hybrid_claude import create_claude_engine
from services.nexus_hybrid_privacy import create_privacy_engine
from services.nexus_hybrid_social_impact import create_social_impact_engine
from services.nexus_hybrid_accessibility import create_accessibility_engine
from services.nexus_hybrid_devtools import create_devtools_engine
from services.nexus_hybrid_editors import create_editors_engine
from services.nexus_hybrid_pixelart import create_pixelart_engine
from services.nexus_hybrid_sdr import create_sdr_engine
from services.nexus_hybrid_webgames import create_webgames_engine
from services.nexus_hybrid_opensource_tools import create_opensource_tools_engine
from services.nexus_hybrid_ai_model_zoos import create_ai_model_zoos_engine
from services.nexus_hybrid_probot import create_probot_engine
from services.nexus_hybrid_php_quality import create_php_quality_engine
from services.nexus_hybrid_js_state import create_js_state_engine
from services.nexus_investor_dashboard import create_investor_dashboard_service
from services.nexus_marketing_dashboard import create_marketing_dashboard_service
from services.nexus_investor_discovery import create_investor_discovery_service
from services.nexus_unified_storage import unified_storage
from services.nexus_master_cicd import master_cicd
from services.nexus_hybrid_devops import hybrid_devops, create_devops_engine
from services.nexus_collection_processor import collection_processor
from services.nexus_hybrid_frontend import hybrid_frontend, create_frontend_engine

router = APIRouter(tags=["Hybrid Services"])

# Request models
class TaskRequest(BaseModel):
    task: str
    auto_route: bool = True

class WorkflowStep(BaseModel):
    hybrid: str
    task: str
    wait: bool = False

class WorkflowRequest(BaseModel):
    workflow: List[WorkflowStep]

class MusicGenerationRequest(BaseModel):
    prompt: str
    style: str = "general"
    duration: int = 30

class MCPConnectRequest(BaseModel):
    server_id: str
    config: Optional[Dict] = None

class MCPToolRequest(BaseModel):
    server_id: str
    tool_name: str
    arguments: Optional[Dict] = None

def get_hybrid_services_router(db=None):
    """Create hybrid services router"""
    
    # Initialize dashboard services
    investor_dashboard = create_investor_dashboard_service(db)
    marketing_dashboard = create_marketing_dashboard_service(db)
    investor_discovery = create_investor_discovery_service(db)
    devops_engine = create_devops_engine(db)
    frontend_engine = create_frontend_engine(db)
    netneutrality_engine = create_netneutrality_engine(db)
    ml_engine = create_ml_engine(db)
    productivity_engine = create_productivity_engine(db)
    languages_engine = create_languages_engine(db)
    github_infra_engine = create_github_infra_engine(db)
    drift_engine = create_drift_engine(db)
    claude_engine = create_claude_engine(db)
    
    # Initialize Wave 2 engines (Security, Community & Development)
    privacy_engine = create_privacy_engine(db)
    social_impact_engine = create_social_impact_engine(db)
    accessibility_engine = create_accessibility_engine(db)
    devtools_engine = create_devtools_engine(db)
    editors_engine = create_editors_engine(db)
    pixelart_engine = create_pixelart_engine(db)
    sdr_engine = create_sdr_engine(db)
    webgames_engine = create_webgames_engine(db)
    
    # Initialize Wave 3 engines (Open Source, AI & Frontend)
    opensource_tools_engine = create_opensource_tools_engine(db)
    ai_model_zoos_engine = create_ai_model_zoos_engine(db)
    probot_engine = create_probot_engine(db)
    php_quality_engine = create_php_quality_engine(db)
    js_state_engine = create_js_state_engine(db)
    
    # ==================== ULTIMATE CONTROLLER ====================
    
    @router.post("/controller/execute")
    async def execute_task(
        request: TaskRequest,
        current_user: dict = Depends(get_current_user)
    ):
        """Execute any task via Ultimate Controller (auto-routes to best hybrid)"""
        try:
            result = await ultimate_controller.execute_task(
                request.task,
                request.auto_route
            )
            return result
        except Exception as e:
            logger.error(f"Controller execution failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/controller/workflow")
    async def orchestrate_workflow(
        request: WorkflowRequest,
        current_user: dict = Depends(get_current_user)
    ):
        """Execute complex multi-hybrid workflow"""
        try:
            workflow_list = [step.dict() for step in request.workflow]
            result = await ultimate_controller.orchestrate_workflow(workflow_list)
            return result
        except Exception as e:
            logger.error(f"Workflow orchestration failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/controller/status")
    async def get_system_status():
        """Get complete system status of all hybrids"""
        try:
            status = ultimate_controller.get_system_status()
            return status
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/controller/auto-task")
    async def intelligent_auto_task(
        request: TaskRequest,
        current_user: dict = Depends(get_current_user)
    ):
        """AI-powered auto-execution of any goal"""
        try:
            result = await ultimate_controller.intelligent_auto_task(request.task)
            return result
        except Exception as e:
            logger.error(f"Auto-task failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ==================== MUSIC HYBRID ====================
    
    @router.post("/music/generate")
    async def generate_music(
        request: MusicGenerationRequest,
        current_user: dict = Depends(get_current_user)
    ):
        """Generate AI music composition"""
        try:
            result = await hybrid_music.generate_music(
                request.prompt,
                request.style,
                request.duration
            )
            return result
        except Exception as e:
            logger.error(f"Music generation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/music/live-session")
    async def create_live_session(
        current_user: dict = Depends(get_current_user)
    ):
        """Create live coding music session"""
        try:
            result = await hybrid_music.create_live_coding_session(current_user['id'])
            return result
        except Exception as e:
            logger.error(f"Live session creation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/music/playlist")
    async def create_playlist(
        name: str,
        tracks: List[str] = None,
        current_user: dict = Depends(get_current_user)
    ):
        """Create smart playlist"""
        try:
            result = await hybrid_music.create_playlist(
                current_user['id'],
                name,
                tracks
            )
            return result
        except Exception as e:
            logger.error(f"Playlist creation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/music/capabilities")
    async def get_music_capabilities():
        """Get all music engine capabilities"""
        try:
            capabilities = hybrid_music.get_capabilities()
            return capabilities
        except Exception as e:
            logger.error(f"Failed to get music capabilities: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ==================== MCP HYBRID ====================
    
    @router.get("/mcp/discover")
    async def discover_mcp_servers():
        """Discover all available MCP servers"""
        try:
            result = await hybrid_mcp.discover_all_mcp_servers()
            return result
        except Exception as e:
            logger.error(f"MCP discovery failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/mcp/connect")
    async def connect_mcp(
        request: MCPConnectRequest,
        current_user: dict = Depends(get_current_user)
    ):
        """Connect to an MCP server"""
        try:
            result = await hybrid_mcp.connect_mcp_server(
                request.server_id,
                request.config
            )
            return result
        except Exception as e:
            logger.error(f"MCP connection failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/mcp/execute")
    async def execute_mcp_tool(
        request: MCPToolRequest,
        current_user: dict = Depends(get_current_user)
    ):
        """Execute a tool on an MCP server"""
        try:
            result = await hybrid_mcp.execute_mcp_tool(
                request.server_id,
                request.tool_name,
                request.arguments
            )
            return result
        except Exception as e:
            logger.error(f"MCP tool execution failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/mcp/active")
    async def get_active_mcp_servers():
        """Get all active MCP server connections"""
        try:
            connections = hybrid_mcp.get_active_connections()
            return connections
        except Exception as e:
            logger.error(f"Failed to get active MCP servers: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/mcp/capabilities")
    async def get_mcp_capabilities():
        """Get all MCP capabilities"""
        try:
            capabilities = hybrid_mcp.get_mcp_capabilities()
            return capabilities
        except Exception as e:
            logger.error(f"Failed to get MCP capabilities: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/mcp/auto-connect")
    async def auto_connect_critical_servers(
        current_user: dict = Depends(require_admin)
    ):
        """Auto-connect to all critical MCP servers"""
        try:
            result = await hybrid_mcp.auto_connect_critical_servers()
            return result
        except Exception as e:
            logger.error(f"Auto-connect failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ==================== INVESTOR DASHBOARD ====================
    
    @router.get("/investor/overview")
    async def get_investor_overview(
        current_user: dict = Depends(require_admin)
    ):
        """Get investor dashboard overview metrics"""
        try:
            metrics = await investor_dashboard.get_overview_metrics()
            return metrics
        except Exception as e:
            logger.error(f"Failed to get investor overview: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/investor/revenue")
    async def get_revenue_breakdown(
        current_user: dict = Depends(require_admin)
    ):
        """Get revenue breakdown by source"""
        try:
            revenue = await investor_dashboard.get_revenue_breakdown()
            return revenue
        except Exception as e:
            logger.error(f"Failed to get revenue breakdown: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/investor/users")
    async def get_user_analytics(
        current_user: dict = Depends(require_admin)
    ):
        """Get detailed user analytics"""
        try:
            analytics = await investor_dashboard.get_user_analytics()
            return analytics
        except Exception as e:
            logger.error(f"Failed to get user analytics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/investor/marketplace")
    async def get_marketplace_performance(
        current_user: dict = Depends(require_admin)
    ):
        """Get marketplace performance metrics"""
        try:
            performance = await investor_dashboard.get_marketplace_performance()
            return performance
        except Exception as e:
            logger.error(f"Failed to get marketplace performance: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/investor/projections")
    async def get_financial_projections(
        current_user: dict = Depends(require_admin)
    ):
        """Get 12-month financial projections"""
        try:
            projections = await investor_dashboard.get_financial_projections()
            return projections
        except Exception as e:
            logger.error(f"Failed to get projections: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/investor/report")
    async def generate_investor_report(
        report_type: str = "monthly",
        current_user: dict = Depends(require_admin)
    ):
        """Generate comprehensive investor report"""
        try:
            report = await investor_dashboard.generate_investor_report(report_type)
            return report
        except Exception as e:
            logger.error(f"Failed to generate investor report: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ==================== MARKETING DASHBOARD ====================
    
    @router.get("/marketing/campaigns")
    async def get_campaigns(
        current_user: dict = Depends(require_admin)
    ):
        """Get all marketing campaigns overview"""
        try:
            campaigns = await marketing_dashboard.get_campaign_overview()
            return campaigns
        except Exception as e:
            logger.error(f"Failed to get campaigns: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/marketing/traffic")
    async def get_traffic(
        current_user: dict = Depends(require_admin)
    ):
        """Get website traffic analytics"""
        try:
            traffic = await marketing_dashboard.get_traffic_analytics()
            return traffic
        except Exception as e:
            logger.error(f"Failed to get traffic analytics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/marketing/funnel")
    async def get_funnel(
        current_user: dict = Depends(require_admin)
    ):
        """Get conversion funnel analytics"""
        try:
            funnel = await marketing_dashboard.get_conversion_funnel()
            return funnel
        except Exception as e:
            logger.error(f"Failed to get funnel: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/marketing/seo")
    async def get_seo(
        current_user: dict = Depends(require_admin)
    ):
        """Get SEO performance metrics"""
        try:
            seo = await marketing_dashboard.get_seo_metrics()
            return seo
        except Exception as e:
            logger.error(f"Failed to get SEO metrics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/marketing/social")
    async def get_social(
        current_user: dict = Depends(require_admin)
    ):
        """Get social media analytics"""
        try:
            social = await marketing_dashboard.get_social_media_analytics()
            return social
        except Exception as e:
            logger.error(f"Failed to get social analytics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/marketing/report")
    async def generate_marketing_report(
        report_type: str = "weekly",
        current_user: dict = Depends(require_admin)
    ):
        """Generate comprehensive marketing report"""
        try:
            report = await marketing_dashboard.generate_marketing_report(report_type)
            return report
        except Exception as e:
            logger.error(f"Failed to generate marketing report: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ==================== INVESTOR DISCOVERY ====================
    
    @router.post("/investors/discover")
    async def discover_investors(
        criteria: Optional[Dict] = None,
        current_user: dict = Depends(require_admin)
    ):
        """Discover investors using AI based on criteria"""
        try:
            result = await investor_discovery.discover_investors(criteria or {})
            return result
        except Exception as e:
            logger.error(f"Investor discovery failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/investors/list")
    async def get_all_investors(
        limit: int = 100,
        current_user: dict = Depends(require_admin)
    ):
        """Get all investors from database"""
        try:
            result = await investor_discovery.get_all_investors(limit)
            return result
        except Exception as e:
            logger.error(f"Failed to get investors: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/investors/search")
    async def search_investors(
        query: Dict,
        current_user: dict = Depends(require_admin)
    ):
        """Search investors by criteria"""
        try:
            result = await investor_discovery.search_investors(query)
            return result
        except Exception as e:
            logger.error(f"Investor search failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/investors/add")
    async def add_investor(
        investor_data: Dict,
        current_user: dict = Depends(require_admin)
    ):
        """Add investor to database"""
        try:
            result = await investor_discovery.add_investor_to_database(investor_data)
            return result
        except Exception as e:
            logger.error(f"Failed to add investor: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.put("/investors/{investor_id}/status")
    async def update_investor_status(
        investor_id: str,
        status: str,
        note: Optional[str] = None,
        current_user: dict = Depends(require_admin)
    ):
        """Update investor status"""
        try:
            result = await investor_discovery.update_investor_status(investor_id, status, note)
            return result
        except Exception as e:
            logger.error(f"Failed to update investor status: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/investors/{investor_id}/interaction")
    async def track_interaction(
        investor_id: str,
        interaction_type: str,
        details: Dict,
        current_user: dict = Depends(require_admin)
    ):
        """Track interaction with investor"""
        try:
            result = await investor_discovery.track_interaction(investor_id, interaction_type, details)
            return result
        except Exception as e:
            logger.error(f"Failed to track interaction: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/investors/{investor_id}/email")
    async def generate_outreach_email(
        investor_id: str,
        current_user: dict = Depends(require_admin)
    ):
        """Generate personalized outreach email"""
        try:
            result = await investor_discovery.generate_outreach_email(investor_id)
            return result
        except Exception as e:
            logger.error(f"Failed to generate email: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/investors/daily-update")
    async def trigger_daily_update(
        current_user: dict = Depends(require_admin)
    ):
        """Trigger daily investor discovery automation"""
        try:
            result = await investor_discovery.daily_investor_update()
            return result
        except Exception as e:
            logger.error(f"Daily update failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/investor/pipeline")
    async def get_investor_pipeline(
        current_user: dict = Depends(require_admin)
    ):
        """Get investor outreach pipeline"""
        try:
            result = await investor_dashboard.get_investor_pipeline()
            return result
        except Exception as e:
            logger.error(f"Failed to get pipeline: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ==================== UNIFIED STORAGE ====================
    
    @router.get("/storage/status")
    async def get_storage_status(
        current_user: dict = Depends(require_admin)
    ):
        """Get storage backend status"""
        try:
            status = await unified_storage.get_backend_status()
            return status
        except Exception as e:
            logger.error(f"Failed to get storage status: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ==================== CI/CD ORCHESTRATION ====================
    
    @router.post("/cicd/workflow/{workflow_type}")
    async def execute_cicd_workflow(
        workflow_type: str,
        services: Optional[List[str]] = Query(None),
        parallel: bool = Query(True),
        current_user: dict = Depends(require_admin)
    ):
        """
        Execute CI/CD workflow
        
        Workflow types:
        - build: Build services
        - test: Test services
        - deploy: Deploy services
        - full: Build → Test → Deploy
        
        Example: /cicd/workflow/build?services=llm&services=music&parallel=true
        """
        try:
            result = await master_cicd.execute_workflow(
                workflow_type,
                services,
                parallel
            )
            return result
        except Exception as e:
            logger.error(f"CI/CD workflow failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/cicd/status")
    async def get_cicd_status(
        current_user: dict = Depends(require_admin)
    ):
        """Get CI/CD orchestrator status"""
        try:
            status = master_cicd.get_workflow_status()
            return status
        except Exception as e:
            logger.error(f"Failed to get CI/CD status: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/cicd/health-check")
    async def run_health_check(
        services: Optional[List[str]] = None,
        current_user: dict = Depends(require_admin)
    ):
        """Run health check on services"""
        try:
            result = await master_cicd.health_check(services)
            return result
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/cicd/rollback/{service}")
    async def rollback_service(
        service: str,
        version: str = "previous",
        current_user: dict = Depends(require_admin)
    ):
        """Rollback a service to previous version"""
        try:
            result = await master_cicd.rollback_service(service, version)
            return result
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/cicd/dependencies/{service}")
    async def get_service_dependencies(
        service: str,
        current_user: dict = Depends(require_admin)
    ):
        """Get service dependency graph"""
        try:
            # Resolve dependencies for a single service
            layers = master_cicd.dep_graph.resolve_dependencies([service])
            info = master_cicd.dep_graph.get_service_info(service)
            
            return {
                "service": service,
                "info": info,
                "execution_layers": layers,
                "total_dependencies": sum(len(layer) for layer in layers)
            }
        except Exception as e:
            logger.error(f"Failed to get dependencies: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/cicd/services")
    async def list_all_services(
        category: Optional[str] = None,
        priority: Optional[int] = None,
        current_user: dict = Depends(require_admin)
    ):
        """List all services with filters"""
        try:
            if category:
                services = master_cicd.dep_graph.get_services_by_category(category)
            elif priority:
                services = master_cicd.dep_graph.get_services_by_priority(priority)
            else:
                services = list(master_cicd.dep_graph.services.keys())
            
            services_info = {
                svc: master_cicd.dep_graph.get_service_info(svc)
                for svc in services
            }
            
            return {
                "total": len(services),
                "services": services_info
            }
        except Exception as e:
            logger.error(f"Failed to list services: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ==================== DEVOPS HYBRID ====================
    
    @router.post("/devops/infrastructure")
    async def create_infrastructure(
        config: Dict,
        current_user: dict = Depends(require_admin)
    ):
        """Create infrastructure using IaC"""
        try:
            result = await devops_engine.create_infrastructure(config)
            return result
        except Exception as e:
            logger.error(f"Infrastructure creation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/devops/infrastructure")
    async def get_infrastructure_state(
        current_user: dict = Depends(require_admin)
    ):
        """Get current infrastructure state"""
        try:
            result = await devops_engine.get_infrastructure_state()
            return result
        except Exception as e:
            logger.error(f"Failed to get infrastructure: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/devops/container")
    async def create_container(
        config: Dict,
        current_user: dict = Depends(require_admin)
    ):
        """Create and run container"""
        try:
            result = await devops_engine.create_container(config)
            return result
        except Exception as e:
            logger.error(f"Container creation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/devops/deploy")
    async def deploy_service(
        service: str,
        environment: str,
        version: str,
        strategy: str = "rolling",
        current_user: dict = Depends(require_admin)
    ):
        """Deploy service"""
        try:
            result = await devops_engine.deploy_service(
                service, environment, version, strategy
            )
            return result
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/devops/metrics")
    async def collect_metrics(
        service: str,
        metrics: Dict,
        current_user: dict = Depends(require_admin)
    ):
        """Collect service metrics"""
        try:
            result = await devops_engine.collect_metrics(service, metrics)
            return result
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/devops/metrics")
    async def query_metrics(
        service: Optional[str] = None,
        metric_type: Optional[str] = None,
        current_user: dict = Depends(require_admin)
    ):
        """Query metrics"""
        try:
            result = await devops_engine.query_metrics(service, "1h", metric_type)
            return result
        except Exception as e:
            logger.error(f"Metrics query failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/devops/error")
    async def track_error(
        error_data: Dict,
        current_user: dict = Depends(get_current_user)
    ):
        """Track application error"""
        try:
            result = await devops_engine.track_error(error_data)
            return result
        except Exception as e:
            logger.error(f"Error tracking failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/devops/capabilities")
    async def get_devops_capabilities():
        """Get DevOps engine capabilities"""
        try:
            capabilities = devops_engine.get_capabilities()
            return capabilities
        except Exception as e:
            logger.error(f"Failed to get capabilities: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ==================== COLLECTION PROCESSOR ====================
    
    @router.post("/collections/process")
    async def process_github_collection(
        collection_url: str,
        current_user: dict = Depends(require_admin)
    ):
        """Process any GitHub collection"""
        try:
            result = await collection_processor.process_collection(collection_url)
            return result
        except Exception as e:
            logger.error(f"Collection processing failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/collections/processed")
    async def get_processed_collections(
        current_user: dict = Depends(require_admin)
    ):
        """Get all processed collections"""
        try:
            result = await collection_processor.get_processed_collections()
            return result
        except Exception as e:
            logger.error(f"Failed to get collections: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/collections/batch")
    async def batch_process_collections(
        collection_urls: List[str],
        current_user: dict = Depends(require_admin)
    ):
        """Process multiple collections"""
        try:
            result = await collection_processor.batch_process_collections(collection_urls)
            return result
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ==================== FRONTEND HYBRID ====================
    
    @router.post("/frontend/detect")
    async def detect_framework(
        code: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Detect JavaScript framework from code"""
        try:
            result = await frontend_engine.detect_framework(code)
            return result
        except Exception as e:
            logger.error(f"Framework detection failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/frontend/frameworks")
    async def list_frameworks():
        """List all supported frameworks"""
        try:
            return {
                "frameworks": list(frontend_engine.frameworks.keys()),
                "total": len(frontend_engine.frameworks),
                "primary": frontend_engine.primary_framework
            }
        except Exception as e:
            logger.error(f"Failed to list frameworks: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/frontend/framework/{framework}")
    async def get_framework_info(
        framework: str
    ):
        """Get information about a specific framework"""
        try:
            result = await frontend_engine.get_framework_info(framework)
            return result
        except Exception as e:
            logger.error(f"Failed to get framework info: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/frontend/compare")
    async def compare_frameworks(
        frameworks: List[str],
        current_user: dict = Depends(require_admin)
    ):
        """Compare multiple frameworks"""
        try:
            result = await frontend_engine.compare_frameworks(frameworks)
            return result
        except Exception as e:
            logger.error(f"Framework comparison failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/frontend/component")
    async def register_component(
        component_data: Dict,
        current_user: dict = Depends(require_admin)
    ):
        """Register a universal component"""
        try:
            result = await frontend_engine.register_component(component_data)
            return result
        except Exception as e:
            logger.error(f"Component registration failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/frontend/component/{component_id}")
    async def get_component(
        component_id: str,
        framework: Optional[str] = None,
        current_user: dict = Depends(get_current_user)
    ):
        """Get component for specific framework"""
        try:
            result = await frontend_engine.get_component(component_id, framework)
            return result
        except Exception as e:
            logger.error(f"Failed to get component: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/frontend/performance")
    async def track_performance(
        metrics_data: Dict,
        current_user: dict = Depends(get_current_user)
    ):
        """Track frontend performance metrics"""
        try:
            result = await frontend_engine.track_performance(metrics_data)
            return result
        except Exception as e:
            logger.error(f"Performance tracking failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/frontend/performance")
    async def get_performance_report(
        framework: Optional[str] = None,
        current_user: dict = Depends(require_admin)
    ):
        """Get performance report"""
        try:
            result = await frontend_engine.get_performance_report(framework)
            return result
        except Exception as e:
            logger.error(f"Performance report failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/frontend/bundle-analysis")
    async def analyze_bundle(
        bundle_data: Dict,
        current_user: dict = Depends(require_admin)
    ):
        """Analyze JavaScript bundle"""
        try:
            result = await frontend_engine.analyze_bundle(bundle_data)
            return result
        except Exception as e:
            logger.error(f"Bundle analysis failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/frontend/capabilities")
    async def get_frontend_capabilities():
        """Get frontend engine capabilities"""
        try:
            capabilities = frontend_engine.get_capabilities()
            return capabilities
        except Exception as e:
            logger.error(f"Failed to get capabilities: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ==================== GAMING HYBRID ====================
    
    from services.nexus_hybrid_gaming import hybrid_gaming, create_gaming_engine
    gaming_engine = create_gaming_engine(db)
    
    @router.post("/gaming/create")
    async def create_game(
        config: Dict,
        current_user: dict = Depends(get_current_user)
    ):
        """Create a new game"""
        result = await gaming_engine.create_game(config)
        return result
    
    @router.get("/gaming/game/{game_id}")
    async def get_game(game_id: str):
        """Get game by ID"""
        result = await gaming_engine.get_game(game_id)
        return result
    
    @router.post("/gaming/game/{game_id}/entity")
    async def add_entity(
        game_id: str,
        entity: Dict,
        current_user: dict = Depends(get_current_user)
    ):
        """Add entity to game"""
        result = await gaming_engine.add_entity(game_id, entity)
        return result
    
    @router.post("/gaming/game/{game_id}/publish")
    async def publish_game(
        game_id: str,
        publish_config: Dict,
        current_user: dict = Depends(get_current_user)
    ):
        """Publish game"""
        result = await gaming_engine.publish_game(game_id, publish_config)
        return result
    
    @router.get("/gaming/published")
    async def get_published_games(
        engine: Optional[str] = None,
        game_type: Optional[str] = None
    ):
        """Get published games"""
        filters = {"engine": engine, "type": game_type}
        result = await gaming_engine.get_published_games(filters)
        return result
    
    @router.get("/gaming/templates")
    async def get_templates():
        """Get game templates"""
        return gaming_engine.get_templates()
    
    @router.get("/gaming/capabilities")
    async def get_gaming_capabilities():
        """Get gaming engine capabilities"""
        return gaming_engine.get_capabilities()

    # ==================== NET NEUTRALITY & DIGITAL RIGHTS ====================
    
    @router.post("/netneutrality/campaign")
    async def create_campaign(
        campaign_data: Dict,
        current_user: dict = Depends(require_admin)
    ):
        """Create a new digital rights campaign"""
        result = await netneutrality_engine.create_campaign(campaign_data)
        return result
    
    @router.get("/netneutrality/campaign/{campaign_id}")
    async def get_campaign(campaign_id: str):
        """Get campaign details"""
        result = await netneutrality_engine.get_campaign(campaign_id)
        return result
    
    @router.post("/netneutrality/petition/sign")
    async def sign_petition(
        signature_data: Dict,
        current_user: dict = Depends(get_current_user)
    ):
        """Sign a petition"""
        result = await netneutrality_engine.sign_petition(
            signature_data["campaign_id"],
            signature_data
        )
        return result
    
    @router.post("/netneutrality/widget/{campaign_id}")
    async def generate_widget(
        campaign_id: str,
        widget_type: str = "modal",
        current_user: dict = Depends(require_admin)
    ):
        """Generate embeddable campaign widget"""
        result = await netneutrality_engine.generate_widget(campaign_id, widget_type)
        return result
    
    @router.get("/netneutrality/representatives/{zip_code}")
    async def find_representatives(zip_code: str):
        """Find US representatives by ZIP code"""
        result = await netneutrality_engine.find_representatives(zip_code)
        return result
    
    @router.post("/netneutrality/email")
    async def send_email_to_representative(
        email_data: Dict,
        current_user: dict = Depends(get_current_user)
    ):
        """Send email to representative"""
        result = await netneutrality_engine.send_email_to_representative(email_data)
        return result
    
    @router.get("/netneutrality/call-script/{issue}")
    async def get_call_script(issue: str):
        """Get call script for contacting representatives"""
        result = await netneutrality_engine.get_call_script(issue)
        return result
    
    @router.post("/netneutrality/simulate-throttling")
    async def simulate_throttling(
        config: Dict,
        current_user: dict = Depends(get_current_user)
    ):
        """Simulate net neutrality violations (educational demo)"""
        result = await netneutrality_engine.simulate_throttling(config)
        return result
    
    @router.post("/netneutrality/check-censorship")
    async def check_censorship(
        target: Dict,
        current_user: dict = Depends(get_current_user)
    ):
        """Check for content blocking/censorship"""
        result = await netneutrality_engine.check_censorship(target)
        return result
    
    @router.get("/netneutrality/internet-health")
    async def monitor_internet_health(
        region: str = "global"
    ):
        """Monitor global internet health and freedom"""
        result = await netneutrality_engine.monitor_internet_health(region)
        return result
    
    @router.post("/netneutrality/analyze-comments")
    async def analyze_public_comments(
        dataset_id: str,
        current_user: dict = Depends(require_admin)
    ):
        """Analyze public comments (e.g., FCC comments)"""
        result = await netneutrality_engine.analyze_public_comments(dataset_id)
        return result
    
    @router.post("/netneutrality/detect-astroturfing")
    async def detect_astroturfing(
        campaign_data: Dict,
        current_user: dict = Depends(require_admin)
    ):
        """Detect fake grassroots campaigns"""
        result = await netneutrality_engine.detect_astroturfing(campaign_data)
        return result
    
    @router.get("/netneutrality/capabilities")
    async def get_netneutrality_capabilities():
        """Get net neutrality engine capabilities"""
        return netneutrality_engine.get_capabilities()


    # ==================== MACHINE LEARNING ====================
    
    @router.post("/ml/training-job")
    async def create_training_job(
        job_config: Dict,
        current_user: dict = Depends(get_current_user)
    ):
        """Create a new ML training job"""
        result = await ml_engine.create_training_job(job_config)
        return result
    
    @router.post("/ml/training-job/{job_id}/start")
    async def start_training(
        job_id: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Start model training"""
        result = await ml_engine.start_training(job_id)
        return result
    
    @router.get("/ml/training-job/{job_id}/status")
    async def get_training_status(
        job_id: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Get training job status"""
        result = await ml_engine.get_training_status(job_id)
        return result
    
    @router.post("/ml/automl")
    async def auto_train_model(
        dataset_id: str,
        task_type: str,
        current_user: dict = Depends(get_current_user)
    ):
        """AutoML - automatically train best model"""
        result = await ml_engine.auto_train_model(dataset_id, task_type)
        return result
    
    @router.post("/ml/dataset")
    async def upload_dataset(
        dataset_data: Dict,
        current_user: dict = Depends(get_current_user)
    ):
        """Upload and register dataset"""
        result = await ml_engine.upload_dataset(dataset_data)
        return result
    
    @router.post("/ml/dataset/{dataset_id}/preprocess")
    async def preprocess_dataset(
        dataset_id: str,
        config: Dict,
        current_user: dict = Depends(get_current_user)
    ):
        """Preprocess dataset for training"""
        result = await ml_engine.preprocess_dataset(dataset_id, config)
        return result
    
    @router.post("/ml/model/{model_id}/deploy")
    async def deploy_model(
        model_id: str,
        deployment_config: Dict,
        current_user: dict = Depends(require_admin)
    ):
        """Deploy trained model"""
        result = await ml_engine.deploy_model(model_id, deployment_config)
        return result
    
    @router.post("/ml/predict/{model_id}")
    async def predict(
        model_id: str,
        input_data: Dict,
        current_user: dict = Depends(get_current_user)
    ):
        """Make prediction using deployed model"""
        result = await ml_engine.predict(model_id, input_data)
        return result
    
    @router.post("/ml/predict/{model_id}/batch")
    async def batch_predict(
        model_id: str,
        inputs: List[Dict],
        current_user: dict = Depends(get_current_user)
    ):
        """Batch prediction"""
        result = await ml_engine.batch_predict(model_id, inputs)
        return result
    
    @router.get("/ml/pretrained-models")
    async def get_pretrained_models(
        category: Optional[str] = None
    ):
        """Get available pre-trained models"""
        result = await ml_engine.get_pretrained_models(category)
        return result
    
    @router.post("/ml/pretrained-models/{model_name}/use")
    async def use_pretrained_model(
        model_name: str,
        task_config: Dict,
        current_user: dict = Depends(get_current_user)
    ):
        """Use pre-trained model"""
        result = await ml_engine.use_pretrained_model(model_name, task_config)
        return result
    
    @router.post("/ml/marketplace/publish")
    async def publish_to_marketplace(
        model_data: Dict,
        current_user: dict = Depends(get_current_user)
    ):
        """Publish model to marketplace"""
        result = await ml_engine.publish_model_to_marketplace(model_data)

    # ==================== PRODUCTIVITY TOOLS ====================
    
    @router.post("/productivity/search-code")
    async def search_code(query: Dict, current_user: dict = Depends(get_current_user)):
        """Fast code search using ripgrep"""
        return await productivity_engine.search_code(query)
    
    @router.get("/productivity/find-files/{pattern}")
    async def find_files(pattern: str, current_user: dict = Depends(get_current_user)):
        """Fast file finding"""
        return await productivity_engine.find_files(pattern)
    
    @router.post("/productivity/process-json")
    async def process_json(data: str, jq_query: str, current_user: dict = Depends(get_current_user)):
        """JSON processing with jq"""
        return await productivity_engine.process_json(data, jq_query)
    
    @router.post("/productivity/git-cleanup")
    async def git_cleanup(repo_path: str, current_user: dict = Depends(get_current_user)):
        """Clean up git branches"""
        return await productivity_engine.git_cleanup(repo_path)
    
    @router.get("/productivity/capabilities")
    async def get_productivity_capabilities():
        return productivity_engine.get_capabilities()
    
    # ==================== PROGRAMMING LANGUAGES ====================
    
    @router.post("/languages/execute")
    async def execute_code(code: str, language: str, current_user: dict = Depends(get_current_user)):
        """Execute code in any language"""
        return await languages_engine.execute_code(code, language)
    
    @router.post("/languages/compare")
    async def compare_languages(langs: List[str]):
        """Compare programming languages"""
        return await languages_engine.compare_languages(langs)
    
    @router.get("/languages/learning-path/{goal}")
    async def get_learning_path(goal: str):
        """Get recommended learning path"""
        return await languages_engine.get_learning_path(goal)
    
    @router.get("/languages/capabilities")
    async def get_languages_capabilities():
        return languages_engine.get_capabilities()
    
    # ==================== GITHUB INFRASTRUCTURE ====================
    
    @router.get("/github-infra/stack")
    async def get_github_stack():
        """Get GitHub's infrastructure stack"""
        return await github_infra_engine.get_stack_info()
    
    @router.post("/github-infra/deploy")
    async def deploy_github_stack(config: Dict, current_user: dict = Depends(require_admin)):
        """Deploy GitHub-like infrastructure"""
        return await github_infra_engine.deploy_github_stack(config)
    
    @router.get("/github-infra/monitor")
    async def monitor_infrastructure(current_user: dict = Depends(get_current_user)):
        """Monitor infrastructure health"""
        return await github_infra_engine.monitor_infrastructure()
    
    @router.get("/github-infra/capabilities")
    async def get_github_infra_capabilities():
        return github_infra_engine.get_capabilities()

    # ==================== DRIFT AI ROBOTICS ====================
    
    @router.post("/drift/install")
    async def install_drift(current_user: dict = Depends(require_admin)):
        """Install Drift AI CLI"""
        return await drift_engine.install_drift()
    
    @router.post("/drift/simulation")
    async def create_simulation(sim_config: Dict, current_user: dict = Depends(get_current_user)):
        """Create robot simulation"""
        return await drift_engine.create_simulation(sim_config)
    
    @router.post("/drift/simulation/{sim_id}/start")
    async def start_simulation(sim_id: str, current_user: dict = Depends(get_current_user)):
        """Start simulation"""
        return await drift_engine.start_simulation(sim_id)
    
    @router.get("/drift/simulation/{sim_id}/status")
    async def get_simulation_status(sim_id: str, current_user: dict = Depends(get_current_user)):
        """Get simulation status"""
        return await drift_engine.get_simulation_status(sim_id)
    
    @router.post("/drift/simulation/{sim_id}/stop")
    async def stop_simulation(sim_id: str, current_user: dict = Depends(get_current_user)):
        """Stop simulation"""
        return await drift_engine.stop_simulation(sim_id)
    
    @router.post("/drift/simulation/{sim_id}/debug")
    async def debug_simulation(sim_id: str, current_user: dict = Depends(get_current_user)):
        """Auto-debug simulation"""
        return await drift_engine.debug_simulation(sim_id)
    
    @router.get("/drift/templates")
    async def list_robot_templates():
        """List robot templates"""
        return await drift_engine.list_robot_templates()

    # ==================== CLAUDE OPUS ====================
    
    @router.post("/claude/chat")
    async def claude_chat(
        message: str, 
        session_id: str,
        system_prompt: Optional[str] = None,
        current_user: dict = Depends(get_current_user)
    ):
        """Chat with Claude Opus"""
        return await claude_engine.chat(message, session_id, system_prompt)
    
    @router.post("/claude/reasoning")
    async def advanced_reasoning(
        problem: str,
        context: Optional[Dict] = None,
        current_user: dict = Depends(get_current_user)
    ):
        """Advanced reasoning with Claude Opus"""
        return await claude_engine.advanced_reasoning(problem, context)
    
    @router.post("/claude/code-review")
    async def code_review(
        code: str,
        language: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Code review with Claude Opus"""
        return await claude_engine.code_review(code, language)
    
    @router.post("/claude/content")
    async def generate_content(
        topic: str,
        style: str = "professional",
        length: str = "medium",
        current_user: dict = Depends(get_current_user)
    ):
        """Generate content with Claude Opus"""
        return await claude_engine.content_generation(topic, style, length)
    
    @router.post("/claude/analyze")
    async def analyze_data(
        data: Dict,
        analysis_type: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Analyze data with Claude Opus"""
        return await claude_engine.data_analysis(data, analysis_type)
    
    @router.get("/claude/history/{session_id}")
    async def get_conversation_history(
        session_id: str,
        limit: int = 20,
        current_user: dict = Depends(get_current_user)
    ):
        """Get conversation history"""
        return await claude_engine.get_conversation_history(session_id, limit)
    
    @router.get("/claude/capabilities")
    async def get_claude_capabilities():
        """Get Claude Opus capabilities"""
        return claude_engine.get_capabilities()

    
    @router.get("/ml/capabilities")
    async def get_ml_capabilities():
        """Get ML engine capabilities"""
        return ml_engine.get_capabilities()

    # ==================== PRIVACY & SECURITY ====================
    
    @router.get("/privacy/capabilities")
    async def get_privacy_capabilities():
        """Get Privacy engine capabilities"""
        return privacy_engine.get_capabilities()
    
    @router.post("/privacy/scan-secrets")
    async def scan_repo_secrets(
        repo_url: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Scan repository for secrets"""
        return await privacy_engine.scan_secrets(repo_url)
    
    @router.post("/privacy/u2f-setup")
    async def setup_u2f(
        current_user: dict = Depends(get_current_user)
    ):
        """Set up U2F authentication"""
        return await privacy_engine.u2f_setup(current_user["id"])
    
    # ==================== SOCIAL IMPACT ====================
    
    @router.get("/social-impact/capabilities")
    async def get_social_impact_capabilities():
        """Get Social Impact engine capabilities"""
        return social_impact_engine.get_capabilities()
    
    @router.get("/social-impact/projects")
    async def list_impact_projects(
        category: str = "all"
    ):
        """List social impact projects"""
        return await social_impact_engine.list_impact_projects(category)
    
    @router.get("/social-impact/analyze/{project_id}")
    async def analyze_project_impact(
        project_id: str
    ):
        """Analyze project's social impact"""
        return await social_impact_engine.analyze_social_impact(project_id)
    
    # ==================== ACCESSIBILITY ====================
    
    @router.get("/accessibility/capabilities")
    async def get_accessibility_capabilities():
        """Get Accessibility engine capabilities"""
        return accessibility_engine.get_capabilities()
    
    @router.post("/accessibility/audit")
    async def audit_page_accessibility(
        url: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Audit page for accessibility issues"""
        return await accessibility_engine.audit_page(url)
    
    @router.post("/accessibility/contrast-check")
    async def check_color_contrast(
        foreground: str,
        background: str
    ):
        """Check color contrast ratio"""
        return await accessibility_engine.check_contrast(foreground, background)
    
    # ==================== DEV TOOLS ====================
    
    @router.get("/devtools/capabilities")
    async def get_devtools_capabilities():
        """Get Dev Tools engine capabilities"""
        return devtools_engine.get_capabilities()
    
    @router.post("/devtools/error-tracking")
    async def setup_error_tracking(
        project: str,
        current_user: dict = Depends(require_admin)
    ):
        """Set up error tracking with Sentry"""
        return await devtools_engine.setup_error_tracking(project)
    
    @router.post("/devtools/ci-pipeline")
    async def create_ci_pipeline(
        config: Dict,
        current_user: dict = Depends(require_admin)
    ):
        """Create CI pipeline"""
        return await devtools_engine.create_ci_pipeline(config)
    
    # ==================== TEXT EDITORS ====================
    
    @router.get("/editors/capabilities")
    async def get_editors_capabilities():
        """Get Text Editors engine capabilities"""
        return editors_engine.get_capabilities()
    
    @router.get("/editors/list")
    async def list_text_editors():
        """List all text editors"""
        return await editors_engine.get_editors()
    
    @router.post("/editors/compare")
    async def compare_text_editors(
        editor_names: List[str]
    ):
        """Compare text editors"""
        return await editors_engine.compare_editors(editor_names)
    
    # ==================== PIXEL ART ====================
    
    @router.get("/pixelart/capabilities")
    async def get_pixelart_capabilities():
        """Get Pixel Art engine capabilities"""
        return pixelart_engine.get_capabilities()
    
    @router.post("/pixelart/canvas")
    async def create_pixel_canvas(
        width: int = 32,
        height: int = 32,
        current_user: dict = Depends(get_current_user)
    ):
        """Create pixel art canvas"""
        return await pixelart_engine.create_canvas(width, height)
    
    @router.post("/pixelart/export")
    async def export_pixel_sprite(
        canvas_id: str,
        format: str = "png",
        current_user: dict = Depends(get_current_user)
    ):
        """Export pixel art sprite"""
        return await pixelart_engine.export_sprite(canvas_id, format)
    
    # ==================== SOFTWARE DEFINED RADIO ====================
    
    @router.get("/sdr/capabilities")
    async def get_sdr_capabilities():
        """Get SDR engine capabilities"""
        return sdr_engine.get_capabilities()
    
    @router.post("/sdr/receiver/start")
    async def start_sdr_receiver(
        config: Dict = None,
        current_user: dict = Depends(require_admin)
    ):
        """Start SDR receiver"""
        if config is None:
            config = {}
        return await sdr_engine.start_receiver(config)
    
    @router.post("/sdr/signal/analyze")
    async def analyze_radio_signal(
        signal_data: Dict = None,
        current_user: dict = Depends(require_admin)
    ):
        """Analyze radio signal"""
        if signal_data is None:
            signal_data = {}
        return await sdr_engine.analyze_signal(signal_data)
    
    # ==================== WEB GAMES ====================
    
    @router.get("/webgames/capabilities")
    async def get_webgames_capabilities():
        """Get Web Games engine capabilities"""
        return webgames_engine.get_capabilities()
    
    @router.get("/webgames/list")
    async def list_web_games():
        """List all web games"""
        return await webgames_engine.list_games()
    
    @router.get("/webgames/{game_name}/embed")
    async def get_game_embed_code(
        game_name: str
    ):
        """Get game embed code"""
        return await webgames_engine.get_game_embed(game_name)
    
    # ==================== OPEN SOURCE TOOLS ====================
    
    @router.get("/opensource-tools/capabilities")
    async def get_opensource_tools_capabilities():
        """Get Open Source Tools engine capabilities"""
        return opensource_tools_engine.get_capabilities()
    
    @router.get("/opensource-tools/list")
    async def list_opensource_tools(
        category: str = "all"
    ):
        """List open source management tools"""
        return await opensource_tools_engine.list_tools(category)
    
    @router.post("/opensource-tools/automate-release")
    async def automate_release_process(
        repo: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Automate release with semantic-release"""
        return await opensource_tools_engine.automate_release(repo)
    
    @router.get("/opensource-tools/notifications/{user_id}")
    async def manage_github_notifications(
        user_id: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Manage GitHub notifications"""
        return await opensource_tools_engine.manage_notifications(user_id)
    
    # ==================== AI MODEL ZOOS ====================
    
    @router.get("/ai-model-zoos/capabilities")
    async def get_ai_model_zoos_capabilities():
        """Get AI Model Zoos engine capabilities"""
        return ai_model_zoos_engine.get_capabilities()
    
    @router.get("/ai-model-zoos/frameworks")
    async def list_ml_frameworks():
        """List all AI/ML frameworks"""
        return await ai_model_zoos_engine.list_frameworks()
    
    @router.get("/ai-model-zoos/search")
    async def search_pretrained_models(
        query: str,
        framework: Optional[str] = None
    ):
        """Search for pre-trained models"""
        return await ai_model_zoos_engine.search_models(query, framework)
    
    @router.get("/ai-model-zoos/{framework}/{model_name}")
    async def get_model_details(
        framework: str,
        model_name: str
    ):
        """Get model information"""
        return await ai_model_zoos_engine.get_model_info(framework, model_name)
    
    # ==================== PROBOT APPS ====================
    
    @router.get("/probot/capabilities")
    async def get_probot_capabilities():
        """Get Probot engine capabilities"""
        return probot_engine.get_capabilities()
    
    @router.get("/probot/apps")
    async def list_probot_apps(
        category: Optional[str] = None
    ):
        """List Probot apps"""
        return await probot_engine.list_apps(category)
    
    @router.post("/probot/install")
    async def install_probot_app(
        app_name: str,
        repo: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Install Probot app to repository"""
        return await probot_engine.install_app(app_name, repo)
    
    @router.post("/probot/configure")
    async def configure_probot_app(
        app_name: str,
        config: Dict = None,
        current_user: dict = Depends(get_current_user)
    ):
        """Configure Probot app"""
        if config is None:
            config = {}
        return await probot_engine.configure_app(app_name, config)
    
    # ==================== PHP CODE QUALITY ====================
    
    @router.get("/php-quality/capabilities")
    async def get_php_quality_capabilities():
        """Get PHP Quality engine capabilities"""
        return php_quality_engine.get_capabilities()
    
    @router.post("/php-quality/analyze")
    async def analyze_php_code(
        project_path: str,
        tool: str = "phpstan",
        current_user: dict = Depends(get_current_user)
    ):
        """Analyze PHP code"""
        return await php_quality_engine.analyze_code(project_path, tool)
    
    @router.post("/php-quality/fix-style")
    async def fix_php_code_style(
        project_path: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Auto-fix PHP code style"""
        return await php_quality_engine.fix_code_style(project_path)
    
    @router.post("/php-quality/detect-duplicates")
    async def detect_php_duplicates(
        project_path: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Detect code duplication"""
        return await php_quality_engine.detect_duplicates(project_path)
    
    # ==================== JAVASCRIPT STATE MANAGEMENT ====================
    
    @router.get("/js-state/capabilities")
    async def get_js_state_capabilities():
        """Get JavaScript State engine capabilities"""
        return js_state_engine.get_capabilities()
    
    @router.get("/js-state/libraries")
    async def list_state_libraries(
        framework: Optional[str] = None
    ):
        """List state management libraries"""
        return await js_state_engine.list_libraries(framework)
    
    @router.post("/js-state/compare")
    async def compare_state_libraries(
        lib_names: List[str]
    ):
        """Compare state management libraries"""
        return await js_state_engine.compare_libraries(lib_names)
    
    @router.post("/js-state/boilerplate")
    async def generate_state_boilerplate(
        library: str,
        framework: str = "react"
    ):
        """Generate boilerplate for state library"""
        return await js_state_engine.generate_boilerplate(library, framework)


    return router
