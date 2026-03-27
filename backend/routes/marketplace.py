"""
Marketplace routes - Products, purchases, bidding
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field, ConfigDict
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import os
import stripe
import logging

from .dependencies import get_current_user, require_vendor

# Create dependency wrappers
def make_get_current_user(db):
    async def wrapper(credentials=Depends(HTTPBearer())):
        return await get_current_user(credentials, db)
    return wrapper

def make_require_vendor(db):
    async def wrapper(credentials=Depends(HTTPBearer())):
        user = await get_current_user(credentials, db)
        if user.get("role") not in ["vendor", "admin"]:
            raise HTTPException(status_code=403, detail="Vendor access required")
        return user
    return wrapper

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Marketplace"])

# Stripe setup
stripe.api_key = os.environ.get('STRIPE_API_KEY', '')

# ==================== MODELS ====================

class ProductCreate(BaseModel):
    title: str
    description: str
    price: float
    category: str
    tags: List[str] = []
    images: List[str] = []
    is_auction: bool = False
    starting_price: Optional[float] = None
    auction_end: Optional[str] = None

class ProductResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    title: str
    description: str
    price: float
    category: str
    vendor_id: str
    vendor_name: str
    images: List[str]
    likes: int
    views: int
    sales: int
    created_at: str

class PurchaseRequest(BaseModel):
    product_id: str
    payment_method: str = "stripe"

def get_marketplace_router(db: AsyncIOMotorDatabase, sio, notify_user_func, create_notification_func):
    """Create marketplace router with dependencies"""
    
    # Create dependency wrappers for this router
    get_user = make_get_current_user(db)
    require_vendor_role = make_require_vendor(db)
    
    # ==================== PRODUCTS ====================
    
    @router.get("/products", response_model=List[ProductResponse])
    async def get_products(category: Optional[str] = None, search: Optional[str] = None, limit: int = 50):
        """Get all products with optional filters"""
        query = {}
        if category and category != "all":
            query["category"] = category
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        products = await db.products.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
        return products
    
    @router.get("/products/{product_id}")
    async def get_product(product_id: str):
        """Get single product details"""
        product = await db.products.find_one({"id": product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        await db.products.update_one({"id": product_id}, {"$inc": {"views": 1}})
        vendor = await db.users.find_one({"id": product.get("vendor_id")}, {"_id": 0, "password": 0})
        
        return {
            **product,
            "vendor": vendor
        }
    
    @router.post("/products")
    async def create_product(product: ProductCreate, current_user: dict = Depends(get_user)):
        """Create a new product"""
        product_id = str(uuid.uuid4())
        product_doc = {
            "id": product_id,
            **product.model_dump(),
            "vendor_id": current_user["id"],
            "vendor_name": current_user["username"],
            "likes": 0,
            "views": 0,
            "sales": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.products.insert_one(product_doc)
        
        return {k: v for k, v in product_doc.items() if k != "_id"}
    
    @router.post("/products/{product_id}/like")
    async def like_product(product_id: str, current_user: dict = Depends(get_user)):
        """Like/unlike a product"""
        existing = await db.product_likes.find_one({"product_id": product_id, "user_id": current_user["id"]}, {"_id": 0})
        product = await db.products.find_one({"id": product_id}, {"_id": 0})
        
        if existing:
            await db.product_likes.delete_one({"product_id": product_id, "user_id": current_user["id"]})
            await db.products.update_one({"id": product_id}, {"$inc": {"likes": -1}})
            return {"liked": False}
        else:
            await db.product_likes.insert_one({
                "id": str(uuid.uuid4()),
                "product_id": product_id,
                "user_id": current_user["id"],
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            await db.products.update_one({"id": product_id}, {"$inc": {"likes": 1}})
            
            if product and product.get("vendor_id") != current_user["id"]:
                await create_notification_func(
                    product["vendor_id"], "like", "Product Liked",
                    f"{current_user['username']} liked your product",
                    {"product_id": product_id}
                )
            return {"liked": True}
    
    # ==================== BIDDING ====================
    
    @router.get("/products/{product_id}/bids")
    async def get_product_bids(product_id: str, limit: int = 20):
        """Get all bids for a product"""
        bids = await db.bids.find(
            {"product_id": product_id},
            {"_id": 0}
        ).sort("placed_at", -1).limit(limit).to_list(limit)
        
        return {
            "bids": bids,
            "count": len(bids),
            "highest_bid": bids[0] if bids else None
        }
    
    @router.post("/products/{product_id}/bid")
    async def place_bid(
        product_id: str,
        bid_data: Dict[str, Any],
        current_user: dict = Depends(get_user)
    ):
        """Place a bid on a product"""
        bid_amount = bid_data.get("amount")
        
        if not bid_amount or bid_amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid bid amount")
        
        product = await db.products.find_one({"id": product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if not product.get("is_auction", False):
            raise HTTPException(status_code=400, detail="Product is not an auction")
        
        highest_bid = await db.bids.find_one(
            {"product_id": product_id},
            {"_id": 0},
            sort=[("amount", -1)]
        )
        
        min_bid = highest_bid["amount"] + 1 if highest_bid else product.get("starting_price", 0)
        
        if bid_amount < min_bid:
            raise HTTPException(status_code=400, detail=f"Bid must be at least ${min_bid}")
        
        bid = {
            "id": f"bid-{int(datetime.now(timezone.utc).timestamp())}",
            "product_id": product_id,
            "user_id": current_user["id"],
            "username": current_user["username"],
            "amount": bid_amount,
            "placed_at": datetime.now(timezone.utc).isoformat(),
            "status": "active"
        }
        
        await db.bids.insert_one(bid)
        
        await sio.emit(f"new_bid:{product_id}", {
            "bid": bid,
            "product_id": product_id
        })
        
        logger.info(f"✓ New bid: ${bid_amount} on {product_id} by {current_user['username']}")
        
        return {
            "success": True,
            "bid": bid,
            "message": "Bid placed successfully"
        }
    
    # ==================== PURCHASES ====================
    
    @router.post("/products/{product_id}/purchase")
    async def purchase_product(
        product_id: str,
        request: PurchaseRequest,
        http_request: Request,
        current_user: dict = Depends(get_user)
    ):
        """Purchase a product via Stripe"""
        product = await db.products.find_one({"id": product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if product.get("vendor_id") == current_user["id"]:
            raise HTTPException(status_code=400, detail="Cannot purchase your own product")
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product['title'],
                            'description': product['description'],
                        },
                        'unit_amount': int(product['price'] * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{http_request.base_url}?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{http_request.base_url}marketplace",
                metadata={
                    'product_id': product_id,
                    'buyer_id': current_user['id'],
                    'vendor_id': product['vendor_id']
                }
            )
            
            return {"checkout_url": session.url, "session_id": session.id}
        except Exception as e:
            logger.error(f"Stripe session creation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/purchase/status/{session_id}")
    async def get_purchase_status(session_id: str, http_request: Request):
        """Check purchase status"""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == 'paid':
                metadata = session.metadata
                purchase_doc = {
                    "id": str(uuid.uuid4()),
                    "product_id": metadata['product_id'],
                    "buyer_id": metadata['buyer_id'],
                    "vendor_id": metadata['vendor_id'],
                    "amount": session.amount_total / 100,
                    "stripe_session_id": session_id,
                    "purchased_at": datetime.now(timezone.utc).isoformat(),
                    "status": "completed"
                }
                
                existing = await db.purchases.find_one({"stripe_session_id": session_id}, {"_id": 0})
                if not existing:
                    await db.purchases.insert_one(purchase_doc)
                    await db.products.update_one(
                        {"id": metadata['product_id']},
                        {"$inc": {"sales": 1}}
                    )
                    await db.users.update_one(
                        {"id": metadata['vendor_id']},
                        {"$inc": {"total_sales": 1, "total_earnings": purchase_doc["amount"]}}
                    )
                
                return {"status": "success", "purchase": purchase_doc}
            else:
                return {"status": session.payment_status}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/my-purchases")
    async def get_my_purchases(current_user: dict = Depends(get_user)):
        """Get user's purchase history"""
        purchases = await db.purchases.find(
            {"buyer_id": current_user["id"]},
            {"_id": 0}
        ).sort("purchased_at", -1).to_list(100)
        
        for purchase in purchases:
            product = await db.products.find_one({"id": purchase["product_id"]}, {"_id": 0})
            purchase["product"] = product
        
        return purchases
    
    @router.get("/categories")
    async def get_categories():
        """Get product categories"""
        products = await db.products.find({}, {"_id": 0, "category": 1}).to_list(1000)
        categories = list(set(p.get("category") for p in products if p.get("category")))
        return categories
    
    return router
