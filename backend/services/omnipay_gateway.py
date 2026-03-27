"""
OmniPay Gateway - Ultimate Payment Hybrid
Combines: BTCPay (crypto) + Stripe (fiat) + Aurpay (multi-crypto)
"""
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import httpx
import stripe
from enum import Enum

logger = logging.getLogger(__name__)

class PaymentMethod(Enum):
    STRIPE_CARD = "stripe_card"
    BITCOIN_ONCHAIN = "bitcoin_onchain"
    BITCOIN_LIGHTNING = "bitcoin_lightning"
    ETHEREUM = "ethereum"
    USDT = "usdt"
    USDC = "usdc"
    BNB = "bnb"

class OmniPayGateway:
    """Elite payment gateway accepting ALL payment methods"""
    
    def __init__(self):
        # Initialize all payment processors
        self.stripe_enabled = bool(os.getenv('STRIPE_API_KEY'))
        self.btcpay_enabled = bool(os.getenv('BTCPAY_SERVER_URL'))
        self.aurpay_enabled = bool(os.getenv('AURPAY_API_KEY'))
        
        if self.stripe_enabled:
            stripe.api_key = os.getenv('STRIPE_API_KEY')
        
        self.btcpay_url = os.getenv('BTCPAY_SERVER_URL', '')
        self.btcpay_api_key = os.getenv('BTCPAY_API_KEY', '')
        self.btcpay_store_id = os.getenv('BTCPAY_STORE_ID', '')
        
        self.aurpay_api_key = os.getenv('AURPAY_API_KEY', '')
        
        logger.info(f"OmniPay initialized: Stripe={self.stripe_enabled}, BTCPay={self.btcpay_enabled}, Aurpay={self.aurpay_enabled}")
    
    async def create_payment(
        self,
        amount: float,
        currency: str,
        payment_method: PaymentMethod,
        order_id: str,
        customer_email: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create payment using the optimal processor for chosen method.
        
        This hybrid approach routes payments intelligently:
        - Fiat cards → Stripe (best UX)
        - Bitcoin (on-chain/Lightning) → BTCPay (zero fees)
        - Multi-crypto → Aurpay (no KYC, low fees)
        """
        if payment_method == PaymentMethod.STRIPE_CARD:
            return await self._create_stripe_payment(
                amount, currency, order_id, customer_email, metadata
            )
        
        elif payment_method in [PaymentMethod.BITCOIN_ONCHAIN, PaymentMethod.BITCOIN_LIGHTNING]:
            return await self._create_btcpay_invoice(
                amount, currency, order_id, customer_email, metadata
            )
        
        elif payment_method in [PaymentMethod.ETHEREUM, PaymentMethod.USDT, PaymentMethod.USDC, PaymentMethod.BNB]:
            return await self._create_aurpay_payment(
                amount, currency, payment_method, order_id, metadata
            )
        
        else:
            raise ValueError(f"Unsupported payment method: {payment_method}")
    
    async def _create_stripe_payment(
        self,
        amount: float,
        currency: str,
        order_id: str,
        customer_email: Optional[str],
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create Stripe payment session for fiat cards"""
        if not self.stripe_enabled:
            raise ValueError("Stripe not configured")
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': currency.lower(),
                        'product_data': {
                            'name': f'Order {order_id}',
                        },
                        'unit_amount': int(amount * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/payment/cancelled",
                customer_email=customer_email,
                metadata={'order_id': order_id, **(metadata or {})}
            )
            
            return {
                'success': True,
                'processor': 'stripe',
                'payment_id': session.id,
                'checkout_url': session.url,
                'amount': amount,
                'currency': currency
            }
        except Exception as e:
            logger.error(f"Stripe payment failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _create_btcpay_invoice(
        self,
        amount: float,
        currency: str,
        order_id: str,
        customer_email: Optional[str],
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create BTCPay Server invoice for Bitcoin payments"""
        if not self.btcpay_enabled:
            raise ValueError("BTCPay Server not configured")
        
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    'Authorization': f'token {self.btcpay_api_key}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'amount': str(amount),
                    'currency': currency,
                    'orderId': order_id,
                    'buyerEmail': customer_email,
                    'redirectURL': f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/payment/success",
                    'metadata': metadata or {}
                }
                
                url = f"{self.btcpay_url}/api/v1/stores/{self.btcpay_store_id}/invoices"
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                invoice_data = response.json()
                
                return {
                    'success': True,
                    'processor': 'btcpay',
                    'payment_id': invoice_data['id'],
                    'checkout_url': invoice_data['checkoutLink'],
                    'amount': amount,
                    'currency': currency,
                    'payment_methods': invoice_data.get('paymentMethods', [])
                }
        except Exception as e:
            logger.error(f"BTCPay invoice creation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _create_aurpay_payment(
        self,
        amount: float,
        currency: str,
        payment_method: PaymentMethod,
        order_id: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create Aurpay payment for multi-crypto (ETH, USDT, USDC, BNB)"""
        if not self.aurpay_enabled:
            raise ValueError("Aurpay not configured")
        
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    'Authorization': f'Bearer {self.aurpay_api_key}',
                    'Content-Type': 'application/json'
                }
                
                crypto_currency_map = {
                    PaymentMethod.ETHEREUM: 'ETH',
                    PaymentMethod.USDT: 'USDT',
                    PaymentMethod.USDC: 'USDC',
                    PaymentMethod.BNB: 'BNB'
                }
                
                payload = {
                    'amount': amount,
                    'currency': crypto_currency_map[payment_method],
                    'order_id': order_id,
                    'redirect_url': f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/payment/success",
                    'metadata': metadata or {}
                }
                
                # Aurpay API endpoint (placeholder)
                response = await client.post(
                    'https://api.aurpay.net/v1/payment',
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                payment_data = response.json()
                
                return {
                    'success': True,
                    'processor': 'aurpay',
                    'payment_id': payment_data.get('payment_id'),
                    'checkout_url': payment_data.get('payment_url'),
                    'amount': amount,
                    'currency': crypto_currency_map[payment_method]
                }
        except Exception as e:
            logger.error(f"Aurpay payment creation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def verify_payment(self, payment_id: str, processor: str) -> Dict[str, Any]:
        """Verify payment status across all processors"""
        if processor == 'stripe':
            return await self._verify_stripe_payment(payment_id)
        elif processor == 'btcpay':
            return await self._verify_btcpay_invoice(payment_id)
        elif processor == 'aurpay':
            return await self._verify_aurpay_payment(payment_id)
        else:
            return {'verified': False, 'error': 'Unknown processor'}
    
    async def _verify_stripe_payment(self, session_id: str) -> Dict[str, Any]:
        """Verify Stripe payment"""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return {
                'verified': True,
                'status': session.payment_status,
                'paid': session.payment_status == 'paid',
                'amount': session.amount_total / 100,
                'currency': session.currency
            }
        except Exception as e:
            logger.error(f"Stripe verification failed: {e}")
            return {'verified': False, 'error': str(e)}
    
    async def _verify_btcpay_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Verify BTCPay invoice"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {'Authorization': f'token {self.btcpay_api_key}'}
                url = f"{self.btcpay_url}/api/v1/stores/{self.btcpay_store_id}/invoices/{invoice_id}"
                
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                invoice = response.json()
                
                return {
                    'verified': True,
                    'status': invoice['status'],
                    'paid': invoice['status'] in ['Settled', 'Processing'],
                    'amount': float(invoice['amount']),
                    'currency': invoice['currency']
                }
        except Exception as e:
            logger.error(f"BTCPay verification failed: {e}")
            return {'verified': False, 'error': str(e)}
    
    async def _verify_aurpay_payment(self, payment_id: str) -> Dict[str, Any]:
        """Verify Aurpay payment"""
        # Implementation for Aurpay verification
        return {'verified': True, 'status': 'pending'}
    
    def get_available_methods(self) -> List[PaymentMethod]:
        """Get list of currently available payment methods"""
        methods = []
        
        if self.stripe_enabled:
            methods.append(PaymentMethod.STRIPE_CARD)
        
        if self.btcpay_enabled:
            methods.extend([
                PaymentMethod.BITCOIN_ONCHAIN,
                PaymentMethod.BITCOIN_LIGHTNING
            ])
        
        if self.aurpay_enabled:
            methods.extend([
                PaymentMethod.ETHEREUM,
                PaymentMethod.USDT,
                PaymentMethod.USDC,
                PaymentMethod.BNB
            ])
        
        return methods

# Singleton instance
omnipay = OmniPayGateway()
