import os
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import json

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Service for optimizing database queries and caching"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 300  # 5 minutes default TTL
    
    async def create_indexes(self):
        """Create optimized indexes for all collections"""
        try:
            # Users
            await self.db.users.create_index("email", unique=True)
            await self.db.users.create_index("username")
            await self.db.users.create_index([("followers_count", -1)])
            await self.db.users.create_index("role")
            
            # Products
            await self.db.products.create_index([("views", -1)])
            await self.db.products.create_index([("created_at", -1)])
            await self.db.products.create_index([("likes", -1)])
            await self.db.products.create_index("vendor_id")
            await self.db.products.create_index("category")
            await self.db.products.create_index("is_boosted")
            
            # Posts
            await self.db.posts.create_index([("created_at", -1)])
            await self.db.posts.create_index("user_id")
            await self.db.posts.create_index([("likes", -1)])
            
            # AIxploria Scans
            await self.db.aixploria_scans.create_index([("scan_timestamp", -1)])
            await self.db.aixploria_scans.create_index("scan_id", unique=True)
            
            # Agent Reports
            await self.db.agent_reports.create_index([("created_at", -1)])
            await self.db.agent_reports.create_index("agent_type")
            await self.db.agent_reports.create_index("agent_name")
            
            # Notifications
            await self.db.notifications.create_index([("user_id", 1), ("created_at", -1)])
            await self.db.notifications.create_index("read")
            
            # Transactions
            await self.db.payment_transactions.create_index("user_id")
            await self.db.payment_transactions.create_index("session_id")
            await self.db.payment_transactions.create_index("payment_status")
            
            logger.info("✓ All database indexes created successfully")
            return {"status": "success", "message": "Indexes created"}
        except Exception as e:
            logger.error(f"Index creation error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_cached(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if (datetime.now(timezone.utc).timestamp() - timestamp) < self.cache_ttl:
                logger.debug(f"Cache hit: {key}")
                return data
            else:
                del self.cache[key]
        return None
    
    def set_cache(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with TTL"""
        self.cache[key] = (value, datetime.now(timezone.utc).timestamp())
        logger.debug(f"Cache set: {key}")
    
    def clear_cache(self, pattern: Optional[str] = None):
        """Clear cache, optionally by pattern"""
        if pattern:
            keys_to_delete = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self.cache[key]
            logger.info(f"Cleared {len(keys_to_delete)} cache entries matching '{pattern}'")
        else:
            self.cache.clear()
            logger.info("Cache cleared completely")
    
    async def optimize_collection(self, collection_name: str) -> Dict[str, Any]:
        """Run optimization on a specific collection"""
        try:
            # Get collection stats
            stats = await self.db.command("collStats", collection_name)
            
            return {
                "collection": collection_name,
                "documents": stats.get("count", 0),
                "size_bytes": stats.get("size", 0),
                "avg_doc_size": stats.get("avgObjSize", 0),
                "indexes": len(stats.get("indexSizes", {})),
                "status": "healthy"
            }
        except Exception as e:
            logger.error(f"Failed to optimize {collection_name}: {str(e)}")
            return {"collection": collection_name, "status": "error", "error": str(e)}
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        try:
            collections = ["users", "products", "posts", "agent_reports", "aixploria_scans"]
            metrics = []
            
            for col_name in collections:
                metric = await self.optimize_collection(col_name)
                metrics.append(metric)
            
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "collections": metrics,
                "cache_size": len(self.cache),
                "total_documents": sum(m.get("documents", 0) for m in metrics)
            }
        except Exception as e:
            logger.error(f"Performance metrics error: {str(e)}")
            return {"error": str(e)}

def create_performance_optimizer(db: AsyncIOMotorDatabase):
    return PerformanceOptimizer(db)
