import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class AnalyticsDashboardService:
    """Service for comprehensive admin analytics with charts and insights"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_revenue_analytics(self) -> Dict[str, Any]:
        """Get revenue analytics with time-series data"""
        # Get orders from last 12 months
        twelve_months_ago = datetime.now(timezone.utc) - timedelta(days=365)
        
        orders = await self.db.orders.find({
            "created_at": {"$gte": twelve_months_ago.isoformat()}
        }, {"_id": 0}).to_list(10000)
        
        # Group by month
        monthly_revenue = {}
        for order in orders:
            order_date = datetime.fromisoformat(order['created_at'])
            month_key = order_date.strftime('%Y-%m')
            monthly_revenue[month_key] = monthly_revenue.get(month_key, 0) + order.get('amount', 0)
        
        # Generate last 12 months data
        revenue_data = []
        current_date = datetime.now(timezone.utc)
        for i in range(11, -1, -1):
            date = current_date - timedelta(days=i*30)
            month_key = date.strftime('%Y-%m')
            revenue_data.append({
                "month": date.strftime('%b %Y'),
                "revenue": monthly_revenue.get(month_key, 0),
                "month_key": month_key
            })
        
        total_revenue = sum(monthly_revenue.values())
        avg_monthly = total_revenue / 12 if len(monthly_revenue) > 0 else 0
        
        return {
            "total_revenue": total_revenue,
            "average_monthly": avg_monthly,
            "chart_data": revenue_data,
            "growth_rate": self._calculate_growth_rate(revenue_data)
        }
    
    async def get_user_growth_analytics(self) -> Dict[str, Any]:
        """Get user growth analytics"""
        users = await self.db.users.find({}, {"_id": 0, "id": 1, "created_at": 1}).to_list(10000)
        
        # Group by month
        monthly_users = {}
        for user in users:
            if user.get('created_at'):
                user_date = datetime.fromisoformat(user['created_at'])
                month_key = user_date.strftime('%Y-%m')
                monthly_users[month_key] = monthly_users.get(month_key, 0) + 1
        
        # Generate cumulative data
        growth_data = []
        cumulative = 0
        current_date = datetime.now(timezone.utc)
        
        for i in range(11, -1, -1):
            date = current_date - timedelta(days=i*30)
            month_key = date.strftime('%Y-%m')
            new_users = monthly_users.get(month_key, 0)
            cumulative += new_users
            
            growth_data.append({
                "month": date.strftime('%b %Y'),
                "new_users": new_users,
                "total_users": cumulative
            })
        
        return {
            "total_users": len(users),
            "chart_data": growth_data,
            "growth_rate": self._calculate_growth_rate(growth_data, key='new_users')
        }
    
    async def get_top_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing products"""
        products = await self.db.products.find(
            {},
            {"_id": 0}
        ).sort("sales", -1).limit(limit).to_list(limit)
        
        return products
    
    async def get_top_vendors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing vendors"""
        # Aggregate sales by vendor
        pipeline = [
            {
                "$group": {
                    "_id": "$vendor_id",
                    "vendor_name": {"$first": "$vendor_name"},
                    "total_sales": {"$sum": "$sales"},
                    "total_revenue": {"$sum": {"$multiply": ["$sales", "$price"]}},
                    "products_count": {"$sum": 1}
                }
            },
            {"$sort": {"total_revenue": -1}},
            {"$limit": limit}
        ]
        
        top_vendors = await self.db.products.aggregate(pipeline).to_list(limit)
        
        return [
            {
                "vendor_id": v['_id'],
                "vendor_name": v['vendor_name'],
                "total_sales": v['total_sales'],
                "total_revenue": v['total_revenue'],
                "products_count": v['products_count']
            }
            for v in top_vendors
        ]
    
    async def get_category_distribution(self) -> Dict[str, Any]:
        """Get product distribution by category"""
        pipeline = [
            {
                "$group": {
                    "_id": "$category",
                    "count": {"$sum": 1},
                    "total_sales": {"$sum": "$sales"},
                    "total_revenue": {"$sum": {"$multiply": ["$sales", "$price"]}}
                }
            },
            {"$sort": {"total_revenue": -1}}
        ]
        
        categories = await self.db.products.aggregate(pipeline).to_list(100)
        
        return {
            "categories": [
                {
                    "name": c['_id'] or "Uncategorized",
                    "products": c['count'],
                    "sales": c['total_sales'],
                    "revenue": c['total_revenue']
                }
                for c in categories
            ]
        }
    
    async def get_engagement_metrics(self) -> Dict[str, Any]:
        """Get platform engagement metrics"""
        # Get activity from last 30 days
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        posts_count = await self.db.posts.count_documents({
            "created_at": {"$gte": thirty_days_ago.isoformat()}
        })
        
        likes_count = await self.db.products.aggregate([
            {"$group": {"_id": None, "total_likes": {"$sum": "$likes"}}}
        ]).to_list(1)
        
        views_count = await self.db.products.aggregate([
            {"$group": {"_id": None, "total_views": {"$sum": "$views"}}}
        ]).to_list(1)
        
        return {
            "posts_last_30d": posts_count,
            "total_likes": likes_count[0]['total_likes'] if likes_count else 0,
            "total_views": views_count[0]['total_views'] if views_count else 0,
            "engagement_rate": self._calculate_engagement_rate(
                likes_count[0]['total_likes'] if likes_count else 0,
                views_count[0]['total_views'] if views_count else 0
            )
        }
    
    async def get_comprehensive_dashboard(self) -> Dict[str, Any]:
        """Get all analytics data for admin dashboard"""
        revenue_analytics = await self.get_revenue_analytics()
        user_growth = await self.get_user_growth_analytics()
        top_products = await self.get_top_products(10)
        top_vendors = await self.get_top_vendors(10)
        category_dist = await self.get_category_distribution()
        engagement = await self.get_engagement_metrics()
        
        # Platform overview stats
        total_products = await self.db.products.count_documents({})
        total_vendors = await self.db.users.count_documents({"role": "vendor"})
        total_users = await self.db.users.count_documents({})
        total_orders = await self.db.orders.count_documents({})
        
        return {
            "overview": {
                "total_revenue": revenue_analytics['total_revenue'],
                "total_users": total_users,
                "total_vendors": total_vendors,
                "total_products": total_products,
                "total_orders": total_orders
            },
            "revenue": revenue_analytics,
            "user_growth": user_growth,
            "top_products": top_products,
            "top_vendors": top_vendors,
            "category_distribution": category_dist,
            "engagement": engagement
        }
    
    def _calculate_growth_rate(self, data: List[Dict], key: str = 'revenue') -> str:
        """Calculate growth rate from time-series data"""
        if len(data) < 2:
            return "+0%"
        
        recent = data[-1].get(key, 0)
        previous = data[-2].get(key, 0)
        
        if previous == 0:
            return "+100%" if recent > 0 else "+0%"
        
        growth = ((recent - previous) / previous) * 100
        return f"{growth:+.1f}%"
    
    def _calculate_engagement_rate(self, likes: int, views: int) -> str:
        """Calculate engagement rate percentage"""
        if views == 0:
            return "0%"
        return f"{(likes / views * 100):.1f}%"

def create_analytics_dashboard_service(db: AsyncIOMotorDatabase):
    return AnalyticsDashboardService(db)
