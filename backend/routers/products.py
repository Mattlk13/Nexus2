from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from .auth import get_current_user, get_optional_user
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Products"])

def get_db():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    return client[os.environ['DB_NAME']]

async def notify_user(user_id: str, notification: dict):
    """Helper to send notification (imported from server.py context)"""
    pass

async def create_notification(user_id: str, notif_type: str, title: str, message: str, data: dict = None):
    """Create notification helper"""
    db = get_db()
    notification = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "type": notif_type,
        "title": title,
        "message": message,
        "data": data or {},
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.notifications.insert_one(notification)
    return notification

# Models
class ProductCreate(BaseModel):
    title: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    tags: List[str] = []
    is_ai_generated: bool = False
    file_url: Optional[str] = None

class ProductResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    title: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    tags: List[str] = []
    is_ai_generated: bool
    vendor_id: str
    vendor_name: str
    likes: int = 0
    views: int = 0
    sales: int = 0
    created_at: str

class PurchaseRequest(BaseModel):
    product_id: str
    origin_url: str

# Routes
@router.get("/products", response_model=List[ProductResponse])
async def get_products(category: Optional[str] = None, search: Optional[str] = None, limit: int = 50):
    db = get_db()
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
    db = get_db()
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await db.products.update_one({"id": product_id}, {"$inc": {"views": 1}})
    vendor = await db.users.find_one({"id": product.get("vendor_id")}, {"_id": 0, "password_hash": 0})
    related = await db.products.find({"category": product.get("category"), "id": {"$ne": product_id}}, {"_id": 0}).limit(4).to_list(4)
    
    return {**product, "vendor": vendor, "related_products": related}

@router.post("/products", response_model=ProductResponse)
async def create_product(product: ProductCreate, current_user: dict = Depends(get_current_user)):
    from services.advanced_agents import AIAgentSystem
    db = get_db()
    
    # Content moderation
    agent_system = AIAgentSystem()
    moderation = await agent_system.moderate_content(f"{product.title} {product.description}", "product")
    if not moderation.get("approved", True):
        raise HTTPException(status_code=400, detail=f"Content rejected: {moderation.get('reason')}")
    
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
async def like_product(product_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    existing = await db.product_likes.find_one({"product_id": product_id, "user_id": current_user["id"]})
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
        
        # Notify vendor
        if product and product.get("vendor_id") != current_user["id"]:
            await create_notification(
                product["vendor_id"], "like", "Product Liked",
                f"{current_user['username']} liked your product '{product['title']}'",
                {"product_id": product_id}
            )
        return {"liked": True}

@router.post("/products/{product_id}/purchase")
async def purchase_product(product_id: str, request: PurchaseRequest, http_request: Request, current_user: dict = Depends(get_current_user)):
    from services.email_service import email_service
    db = get_db()
    
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    api_key = os.environ.get('STRIPE_API_KEY')
    host_url = str(http_request.base_url).rstrip('/')
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=f"{host_url}/api/webhook/stripe")
    
    checkout_request = CheckoutSessionRequest(
        amount=float(product["price"]),
        currency="usd",
        success_url=f"{request.origin_url}/purchase/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{request.origin_url}/products/{product_id}",
        metadata={
            "type": "product_purchase",
            "product_id": product_id,
            "buyer_id": current_user["id"],
            "vendor_id": product.get("vendor_id"),
            "product_title": product.get("title")
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    await db.payment_transactions.insert_one({
        "id": str(uuid.uuid4()),
        "session_id": session.session_id,
        "type": "product_purchase",
        "buyer_id": current_user["id"],
        "vendor_id": product.get("vendor_id"),
        "product_id": product_id,
        "amount": product["price"],
        "currency": "usd",
        "payment_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"checkout_url": session.url, "session_id": session.session_id}

@router.get("/purchase/status/{session_id}")
async def get_purchase_status(session_id: str, http_request: Request):
    from services.email_service import email_service
    db = get_db()
    
    api_key = os.environ.get('STRIPE_API_KEY')
    host_url = str(http_request.base_url).rstrip('/')
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=f"{host_url}/api/webhook/stripe")
    
    status = await stripe_checkout.get_checkout_status(session_id)
    transaction = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if status.payment_status == "paid" and transaction.get("payment_status") != "completed":
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {"payment_status": "completed", "completed_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        await db.products.update_one({"id": transaction["product_id"]}, {"$inc": {"sales": 1}})
        
        vendor_cut = transaction["amount"] * 0.85
        await db.users.update_one(
            {"id": transaction["vendor_id"]},
            {"$inc": {"total_sales": 1, "total_earnings": vendor_cut}}
        )
        
        await db.purchases.insert_one({
            "id": str(uuid.uuid4()),
            "buyer_id": transaction["buyer_id"],
            "product_id": transaction["product_id"],
            "transaction_id": transaction["id"],
            "purchased_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Notify vendor of sale
        product = await db.products.find_one({"id": transaction["product_id"]}, {"_id": 0})
        if product:
            await create_notification(
                transaction["vendor_id"], "sale", "New Sale!",
                f"Someone purchased '{product['title']}' for ${transaction['amount']:.2f}",
                {"product_id": transaction["product_id"], "amount": transaction["amount"]}
            )
            
            # Send email to vendor
            vendor = await db.users.find_one({"id": transaction["vendor_id"]}, {"_id": 0, "password_hash": 0})
            if vendor and vendor.get("email"):
                vendor_cut = transaction["amount"] * 0.85
                asyncio.create_task(email_service.send_sale_notification(
                    vendor["email"],
                    vendor["username"],
                    product["title"],
                    vendor_cut
                ))
    
    return {
        "status": status.status,
        "payment_status": status.payment_status,
        "transaction_status": transaction.get("payment_status")
    }

@router.get("/my-purchases")
async def get_my_purchases(current_user: dict = Depends(get_current_user)):
    db = get_db()
    purchases = await db.purchases.find({"buyer_id": current_user["id"]}, {"_id": 0}).to_list(100)
    product_ids = [p["product_id"] for p in purchases]
    products = await db.products.find({"id": {"$in": product_ids}}, {"_id": 0}).to_list(100)
    products_map = {p["id"]: p for p in products}
    
    return [{"purchase": purchase, "product": products_map.get(purchase["product_id"], {})} for purchase in purchases]
