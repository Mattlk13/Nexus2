import os
import asyncio
import logging
import resend
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

resend.api_key = os.environ.get('RESEND_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')

logger = logging.getLogger(__name__)

class EmailService:
    """Enhanced service for sending transactional emails via Resend with fallback"""
    
    def __init__(self):
        self.api_key = os.environ.get('RESEND_API_KEY', '')
        self.sender_email = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
        self.is_active = self._check_active()
    
    def _check_active(self) -> bool:
        """Check if Resend is properly configured"""
        if not self.api_key:
            return False
        placeholder_terms = ['demo', 'placeholder', 'your_key']
        return not any(term in self.api_key.lower() for term in placeholder_terms)
    
    async def send_email(self, to: str, subject: str, html: str):
        """Send email with fallback to console logging"""
        
        if not self.is_active:
            logger.warning(f"📧 RESEND NOT CONFIGURED - Email would be sent:")
            logger.warning(f"   To: {to}")
            logger.warning(f"   Subject: {subject}")
            logger.warning(f"   (Add RESEND_API_KEY to /app/backend/.env to send real emails)")
            return {"success": True, "mode": "demo", "message": "Email logged to console"}
        
        params = {
            "from": self.sender_email,
            "to": [to],
            "subject": subject,
            "html": html
        }
        
        try:
            result = await asyncio.to_thread(resend.Emails.send, params)
            logger.info(f"✓ Email sent to {to}: {subject}")
            return {"success": True, "email_id": result.get("id"), "mode": "sent"}
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {str(e)}")
            # Fallback to console logging
            logger.warning(f"📧 EMAIL FALLBACK - Would send to {to}: {subject}")
            return {"success": False, "error": str(e), "mode": "failed"}

    
    async def send_sale_notification(self, seller_email: str, seller_name: str, product_name: str, amount: float):
        """Send email when vendor makes a sale"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #0a0a0a; color: #ffffff; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 16px; padding: 40px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .logo {{ font-size: 32px; font-weight: bold; color: #06b6d4; }}
                .amount {{ font-size: 48px; font-weight: bold; color: #10b981; margin: 20px 0; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #06b6d4 0%, #8b5cf6 100%); color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">⚡ NEXUS</div>
                    <h1>🎉 You Made a Sale!</h1>
                </div>
                <p>Hey {seller_name},</p>
                <p>Great news! Your product <strong>{product_name}</strong> just sold.</p>
                <div style="text-align: center;">
                    <div class="amount">${amount:.2f}</div>
                    <p style="color: #9ca3af;">Your earnings (after 15% platform fee)</p>
                </div>
                <p>Keep creating amazing content! Your products are making an impact.</p>
                <div style="text-align: center;">
                    <a href="https://model-exchange-2.preview.emergentagent.com/vendor/analytics" class="button">View Analytics</a>
                </div>
            </div>
        </body>
        </html>
        """
        return await self.send_email(seller_email, f"💰 Sale Alert: {product_name}", html)
    
    async def send_welcome_email(self, user_email: str, username: str):
        """Send welcome email to new users"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #0a0a0a; color: #ffffff; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 16px; padding: 40px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .logo {{ font-size: 32px; font-weight: bold; color: #06b6d4; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #06b6d4 0%, #8b5cf6 100%); color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">⚡ NEXUS</div>
                    <h1>Welcome to NEXUS!</h1>
                </div>
                <p>Hey {username},</p>
                <p>Welcome to the future of AI-powered marketplaces! You're now part of a community where creators and 11 AI agents work together to build amazing digital products.</p>
                <h3>🚀 Get Started:</h3>
                <ul>
                    <li>Browse the <strong>Marketplace</strong> for AI-generated content</li>
                    <li>Create products in the <strong>Studio</strong> using our AI tools</li>
                    <li>Connect with creators in the <strong>Feed</strong></li>
                    <li>Open your own <strong>Shop</strong> and start selling</li>
                </ul>
                <p>Our 11 AI agents (including autonomous discovery) are working 24/7 to help you succeed. Questions? Chat with our AI support anytime.</p>
                <div style="text-align: center;">
                    <a href="https://model-exchange-2.preview.emergentagent.com/marketplace" class="button">Explore Marketplace</a>
                </div>
            </div>
        </body>
        </html>
        """
        return await self.send_email(user_email, "Welcome to NEXUS - Start Creating!", html)
    
    async def send_follower_notification(self, user_email: str, follower_name: str):
        """Send email when someone follows you"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #0a0a0a; color: #ffffff; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 16px; padding: 40px; text-align: center; }}
                .logo {{ font-size: 32px; font-weight: bold; color: #06b6d4; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">⚡ NEXUS</div>
                <h1>👋 New Follower!</h1>
                <p><strong>{follower_name}</strong> started following you.</p>
                <p>Keep creating and engaging to grow your audience!</p>
            </div>
        </body>
        </html>
        """
        return await self.send_email(user_email, f"👋 {follower_name} followed you!", html)


email_service = EmailService()
