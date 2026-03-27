"""
NEXUS Hybrid Router - Dynamic Route Loading System
Auto-discovers and loads routes from hybrid service modules
"""
from fastapi import APIRouter, Depends
from typing import Optional, Dict, List
import importlib
import pkgutil
import logging
from functools import partial

logger = logging.getLogger(__name__)

def _create_capabilities_route(engine):
    """Factory function to avoid closure issues"""
    async def get_capabilities():
        return engine.get_capabilities()
    return get_capabilities

def create_dynamic_hybrid_router(db):
    """
    Dynamically discover and load all nexus_hybrid_* services
    Returns a router with all hybrid routes automatically registered
    """
    router = APIRouter(tags=["Hybrid Services"])  # NO PREFIX HERE
    
    # Import dependencies
    from routes.dependencies import get_current_user, require_admin
    
    # Track loaded hybrids
    loaded_hybrids = []
    
    # Discover all nexus_hybrid_* modules
    import services
    services_path = services.__path__
    
    for importer, modname, ispkg in pkgutil.iter_modules(services_path):
        if modname.startswith('nexus_hybrid_'):
            try:
                # Import the module
                module = importlib.import_module(f'services.{modname}')
                
                # Extract hybrid name (e.g., nexus_hybrid_privacy -> privacy)
                hybrid_name = modname.replace('nexus_hybrid_', '')
                
                # Check if module has route registration function
                if hasattr(module, 'register_routes'):
                    # Module defines its own routes
                    sub_router = module.register_routes(db, get_current_user, require_admin)
                    router.include_router(sub_router, prefix=f"/{hybrid_name}")
                    loaded_hybrids.append(hybrid_name)
                    logger.info(f"✅ Loaded self-registered hybrid: {hybrid_name}")
                    
                elif hasattr(module, f'create_{hybrid_name}_engine'):
                    # Module has standard engine pattern - create default routes
                    create_func = getattr(module, f'create_{hybrid_name}_engine')
                    engine = create_func(db)
                    
                    # Create basic route using factory to avoid closure bug
                    capabilities_func = _create_capabilities_route(engine)
                    router.add_api_route(
                        f"/{hybrid_name}/capabilities",
                        capabilities_func,
                        methods=["GET"],
                        summary=f"Get {hybrid_name} capabilities"
                    )
                    
                    loaded_hybrids.append(f"{hybrid_name} (auto)")
                    logger.info(f"✅ Auto-generated routes for: {hybrid_name}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to load hybrid {modname}: {e}")
    
    logger.info(f"🚀 Dynamic router loaded {len(loaded_hybrids)} hybrids: {', '.join(loaded_hybrids)}")
    
    return router, loaded_hybrids
