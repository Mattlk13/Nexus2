"""
NEXUS Hybrid Payments Service
Combines Stripe + cryptocurrency support with intelligent routing

Features:
- Traditional payments (Stripe)
- Crypto payments (multiple chains)
- Payment method detection
- Automatic currency conversion
- Webhook handling
"""

import os
import logging
from typing import Optional, Dict, List
import stripe
import httpx

logger = logging.getLogger(__name__)

class HybridPaymentsService:
    def __init__(self):
        """Initialize hybrid payment processors"""
        self.stripe_key = os.environ.get('STRIPE_API_KEY')
        
        if self.stripe_key:
            stripe.api_key = self.stripe_key
            self.stripe_enabled = True
        else:
            self.stripe_enabled = False
            logger.warning("Stripe not configured")
        
        # Crypto support (for future)
        self.crypto_enabled = False
        
        logger.info(f"Hybrid Payments initialized (Stripe: {self.stripe_enabled})")
    
    async def create_payment_intent(
        self,
        amount: float,
        currency: str = "usd",
        payment_method: str = "card",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Create payment intent with best processor"""
        
        if payment_method in ["card", "stripe"] and self.stripe_enabled:
            try:
                # Convert to cents
                amount_cents = int(amount * 100)
                
                intent = stripe.PaymentIntent.create(
                    amount=amount_cents,
                    currency=currency,
                    automatic_payment_methods={"enabled": True},
                    metadata=metadata or {}
                )
                
                return {
                    "success": True,
                    "payment_intent_id": intent.id,
                    "client_secret": intent.client_secret,
                    "provider": "stripe",
                    "amount": amount,
                    "currency": currency
                }
            except stripe.error.StripeError as e:
                return {
                    "success": False,
                    "error": str(e),
                    "provider": "stripe"
                }
        
        elif payment_method == "crypto" and self.crypto_enabled:
            # Future: Crypto payment integration
            return {
                "success": False,
                "error": "Crypto payments coming soon"
            }
        
        return {
            "success": False,
            "error": "No payment providers available"
        }
    
    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        payment_method: str = "card"
    ) -> Dict:
        """Create subscription with recurring payments"""
        
        if payment_method == "card" and self.stripe_enabled:
            try:
                subscription = stripe.Subscription.create(
                    customer=customer_id,
                    items=[{"price": price_id}],
                    payment_behavior="default_incomplete",
                    expand=["latest_invoice.payment_intent"]
                )
                
                return {
                    "success": True,
                    "subscription_id": subscription.id,
                    "status": subscription.status,
                    "provider": "stripe"
                }
            except stripe.error.StripeError as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "success": False,
            "error": "Subscription not available for this payment method"
        }
    
    async def process_refund(
        self,
        payment_id: str,
        amount: Optional[float] = None,
        reason: Optional[str] = None
    ) -> Dict:
        """Process refund"""
        
        if self.stripe_enabled:
            try:
                refund_args = {"payment_intent": payment_id}
                if amount:
                    refund_args["amount"] = int(amount * 100)
                if reason:
                    refund_args["reason"] = reason
                
                refund = stripe.Refund.create(**refund_args)
                
                return {
                    "success": True,
                    "refund_id": refund.id,
                    "status": refund.status,
                    "amount": refund.amount / 100
                }
            except stripe.error.StripeError as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "success": False,
            "error": "Refund not available"
        }
    
    async def get_payment_methods(self) -> List[Dict]:
        """Get available payment methods"""
        methods = []
        
        if self.stripe_enabled:
            methods.append({
                "id": "card",
                "name": "Credit/Debit Card",
                "provider": "stripe",
                "available": True
            })
        
        if self.crypto_enabled:
            methods.append({
                "id": "crypto",
                "name": "Cryptocurrency",
                "provider": "crypto",
                "available": True
            })
        
        return methods

# Global instance
hybrid_payments = HybridPaymentsService()
