"""NEXUS Web Games Hybrid
Browser-based games collection
"""
import logging
from typing import Dict, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class WebGamesEngine:
    def __init__(self, db=None):
        self.db = db
        self.games = ["2048", "BrowserQuest", "Untrusted", "A Dark Room", "Hextris"]
        logger.info(f"🎮 Web Games Engine initialized with {len(self.games)} games")
    
    async def list_games(self) -> Dict:
        return {"success": True, "games": self.games, "total": len(self.games)}
    
    async def get_game_embed(self, game_name: str) -> Dict:
        return {
            "success": True,
            "game": game_name,
            "embed_code": f'<iframe src="https://games.example.com/{game_name}" width="800" height="600"></iframe>'
        }
    
    def get_capabilities(self) -> Dict:
        return {
            "name": "Web Games Hybrid",
            "version": "1.0.0",
            "games_count": len(self.games),
            "categories": ["puzzle", "rpg", "action", "text-based"]
        }

hybrid_webgames = WebGamesEngine(db=None)

def create_webgames_engine(db):
    global hybrid_webgames
    hybrid_webgames = WebGamesEngine(db)
    return hybrid_webgames

def register_routes(db, get_current_user, require_admin):
    from fastapi import APIRouter, Depends
    router = APIRouter()
    engine = create_webgames_engine(db)
    
    @router.get("/capabilities")
    async def get_capabilities():
        return engine.get_capabilities()
    
    @router.get("/list")
    async def list_games():
        return await engine.list_games()
    
    @router.get("/{game_name}/embed")
    async def get_embed(game_name: str):
        return await engine.get_game_embed(game_name)
    
    return router
