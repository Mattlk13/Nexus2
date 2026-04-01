"""
Database Optimization - Add indexes for performance
Fixes: Audit Issue #9
"""

from motor.motor_asyncio import AsyncIOMotorClient
import logging

logger = logging.getLogger(__name__)

async def create_database_indexes(db):
    """Create all recommended indexes for optimal performance"""
    try:
        logger.info("Creating database indexes...")
        
        # Universal AI conversations - optimize session queries
        await db.universal_conversations.create_index([
            ("session_id", 1),
            ("timestamp", -1)
        ])
        logger.info("✓ Created index: universal_conversations(session_id, timestamp)")
        
        # AIO Sandboxes - quick lookups
        await db.aio_sandboxes.create_index("sandbox_id", unique=True)
        logger.info("✓ Created index: aio_sandboxes(sandbox_id)")
        
        # Users - email lookup
        await db.users.create_index("email", unique=True)
        logger.info("✓ Created index: users(email)")
        
        # Users - username lookup
        await db.users.create_index("username", unique=True)
        logger.info("✓ Created index: users(username)")
        
        # Code reviews - task and time queries
        await db.code_reviews.create_index([
            ("task", 1),
            ("timestamp", -1)
        ])
        logger.info("✓ Created index: code_reviews(task, timestamp)")
        
        # Posts - feed queries
        await db.posts.create_index([
            ("created_at", -1)
        ])
        logger.info("✓ Created index: posts(created_at)")
        
        # Messages - conversation queries
        await db.messages.create_index([
            ("conversation_id", 1),
            ("timestamp", -1)
        ])
        logger.info("✓ Created index: messages(conversation_id, timestamp)")
        
        # TTL indexes for temporary data (auto-cleanup)
        # Sandboxes expire after 24 hours if inactive
        await db.aio_sandboxes.create_index(
            "created_at",
            expireAfterSeconds=86400  # 24 hours
        )
        logger.info("✓ Created TTL index: aio_sandboxes(created_at, 24h expiry)")
        
        # Session data expires after 7 days
        await db.sessions.create_index(
            "created_at",
            expireAfterSeconds=604800  # 7 days
        )
        logger.info("✓ Created TTL index: sessions(created_at, 7d expiry)")
        
        logger.info("✅ All database indexes created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create indexes: {e}")
        return False

async def optimize_database_connection(mongo_url: str, db_name: str):
    """Optimize MongoDB connection with pooling"""
    try:
        client = AsyncIOMotorClient(
            mongo_url,
            maxPoolSize=50,  # Increased from default
            minPoolSize=10,
            maxIdleTimeMS=45000,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=45000
        )
        
        db = client[db_name]
        
        # Create indexes
        await create_database_indexes(db)
        
        logger.info("✅ Database connection optimized")
        return db
        
    except Exception as e:
        logger.error(f"❌ Database optimization failed: {e}")
        raise
