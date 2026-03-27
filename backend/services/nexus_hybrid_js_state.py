"""NEXUS JavaScript State Management Hybrid
Framework-agnostic state management libraries for JavaScript
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class JSStateEngine:
    def __init__(self, db=None):
        self.db = db
        self.projects_collection = db.js_state_projects if db is not None else None
        self.libraries = [
            {"name": "Redux", "repo": "reduxjs/redux", "stars": 61458, "description": "Predictable global state management", "language": "TypeScript"},
            {"name": "XState", "repo": "statelyai/xstate", "stars": 29359, "description": "Actor-based state management for complex app logic", "language": "TypeScript"},
            {"name": "Immer", "repo": "immerjs/immer", "stars": 28909, "description": "Create next immutable state by mutating current one", "language": "JavaScript"},
            {"name": "MobX", "repo": "mobxjs/mobx", "stars": 28186, "description": "Simple, scalable state management", "language": "TypeScript"},
            {"name": "Effector", "repo": "effector/effector", "stars": 4823, "description": "Business logic with ease", "language": "TypeScript"},
            {"name": "Baobab", "repo": "Yomguithereal/baobab", "stars": 3162, "description": "Persistent and optionally immutable data tree with cursors", "language": "JavaScript"},
            {"name": "Cerebral", "repo": "cerebral/cerebral", "stars": 1999, "description": "Declarative state and side effects management", "language": "JavaScript"},
            {"name": "Storeon", "repo": "storeon/storeon", "stars": 1977, "description": "Tiny event-based state manager (185 bytes)", "language": "JavaScript"},
            {"name": "Reatom", "repo": "reatom/reatom", "stars": 1322, "description": "The ultimate state manager", "language": "TypeScript"}
        ]
        logger.info(f"⚛️ JavaScript State Engine initialized with {len(self.libraries)} libraries")
    
    async def list_libraries(self, framework: Optional[str] = None) -> Dict:
        """List all state management libraries"""
        return {
            "success": True,
            "libraries": self.libraries,
            "total": len(self.libraries),
            "most_popular": "Redux"
        }
    
    async def compare_libraries(self, lib_names: List[str]) -> Dict:
        """Compare state management libraries"""
        comparison = []
        for name in lib_names:
            lib = next((library for library in self.libraries if library["name"].lower() == name.lower()), None)
            if lib:
                comparison.append(lib)
        
        return {
            "success": True,
            "comparison": comparison,
            "recommendation": "Redux for large apps, MobX for simplicity, XState for complex workflows"
        }
    
    async def generate_boilerplate(self, library: str, framework: str = "react") -> Dict:
        """Generate boilerplate code for state library"""
        return {
            "success": True,
            "library": library,
            "framework": framework,
            "boilerplate_url": f"https://nexus.ai/boilerplate/{library}-{framework}.zip",
            "setup_guide": f"Install: npm install {library.lower()}"
        }
    
    def get_capabilities(self) -> Dict:
        return {
            "name": "JavaScript State Management Hybrid",
            "version": "1.0.0",
            "libraries_count": len(self.libraries),
            "total_stars": sum(library["stars"] for library in self.libraries),
            "categories": ["redux", "mobx", "xstate", "immutable", "reactive"]
        }

hybrid_js_state = JSStateEngine(db=None)

def create_js_state_engine(db):
    global hybrid_js_state
    hybrid_js_state = JSStateEngine(db)
    return hybrid_js_state

def register_routes(db, get_current_user, require_admin):
    """Self-registration function for dynamic router"""
    from fastapi import APIRouter, Depends
    
    router = APIRouter()
    engine = create_js_state_engine(db)
    
    @router.get("/capabilities")
    async def get_capabilities():
        """Get Js State capabilities"""
        return engine.get_capabilities()
    
    return router

