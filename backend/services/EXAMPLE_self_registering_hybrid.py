"""
Example: Self-Registering Hybrid Service
This demonstrates how hybrid services can define their own routes
"""
from fastapi import APIRouter, Depends
from typing import Dict, Optional

# Service implementation
class ExampleHybridEngine:
    def __init__(self, db=None):
        self.db = db
        
    def get_capabilities(self) -> Dict:
        return {
            "name": "Example Hybrid",
            "version": "1.0.0",
            "features": ["feature1", "feature2"]
        }
    
    async def do_something(self, param: str) -> Dict:
        return {"success": True, "result": f"Processed: {param}"}

# Global instance
hybrid_example = None

def create_example_engine(db):
    """Standard engine creation function"""
    global hybrid_example
    hybrid_example = ExampleHybridEngine(db)
    return hybrid_example

def register_routes(db, get_current_user, require_admin):
    """
    Self-registration function for dynamic router
    This function is called by the dynamic router to get this hybrid's routes
    """
    router = APIRouter()
    
    # Initialize engine
    engine = create_example_engine(db)
    
    # Define routes
    @router.get("/capabilities")
    async def get_capabilities():
        """Get hybrid capabilities"""
        return engine.get_capabilities()
    
    @router.post("/action")
    async def perform_action(
        param: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Perform an action (requires auth)"""
        return await engine.do_something(param)
    
    @router.get("/admin-only")
    async def admin_endpoint(
        current_user: dict = Depends(require_admin)
    ):
        """Admin-only endpoint"""
        return {"message": "Admin access granted"}
    
    return router
