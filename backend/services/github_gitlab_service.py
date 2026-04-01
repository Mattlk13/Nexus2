import logging
import os
import secrets
import hashlib
import base64
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class GitHubGitLabIntegrationService:
    """Service for GitHub and GitLab OAuth integration and repository syncing"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.github_client_id = os.environ.get('GITHUB_CLIENT_ID', 'demo_client_id')
        self.github_client_secret = os.environ.get('GITHUB_CLIENT_SECRET', 'demo_secret')
        self.gitlab_client_id = os.environ.get('GITLAB_CLIENT_ID', 'demo_client_id')
        self.gitlab_app_secret = os.environ.get('GITLAB_APP_SECRET', 'demo_secret')
        
        self.is_github_active = self.github_client_id != 'demo_client_id'
        self.is_gitlab_active = self.gitlab_client_id != 'demo_client_id'
    
    def generate_oauth_state(self) -> str:
        """Generate secure OAuth state parameter"""
        return secrets.token_urlsafe(32)
    
    def generate_pkce_params(self) -> tuple[str, str]:
        """Generate PKCE code verifier and challenge"""
        code_verifier = secrets.token_urlsafe(64)
        verifier_bytes = code_verifier.encode('ascii')
        sha256_digest = hashlib.sha256(verifier_bytes).digest()
        code_challenge = base64.urlsafe_b64encode(sha256_digest).decode('utf-8').rstrip('=')
        return code_verifier, code_challenge
    
    async def initiate_github_oauth(self, user_id: str, origin: str = None) -> Dict[str, Any]:
        """Initiate GitHub OAuth flow with dynamic redirect URL"""
        if not self.is_github_active:
            return {
                "success": False,
                "demo_mode": True,
                "message": "GitHub OAuth not configured - add GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET to .env"
            }
        
        # Get origin dynamically from environment
        if not origin:
            # Get the frontend URL from environment (without /api suffix)
            frontend_url = os.environ.get('FRONTEND_URL') or os.environ.get('REACT_APP_BACKEND_URL', '').replace('/api', '')
            if not frontend_url or frontend_url == 'https://yourdomain.com':
                # For OAuth to work, FRONTEND_URL must be configured
                raise ValueError("FRONTEND_URL environment variable must be set for OAuth authentication. Please configure it in your .env file.")
            origin = frontend_url
        
        state = self.generate_oauth_state()
        code_verifier, code_challenge = self.generate_pkce_params()
        
        # Store state in database
        await self.db.oauth_states.insert_one({
            "state": state,
            "code_verifier": code_verifier,
            "user_id": user_id,
            "platform": "github",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(),
            "used": False
        })
        
        # Dynamic redirect URL
        auth_url = (
            f"https://github.com/login/oauth/authorize?"
            f"client_id={self.github_client_id}&"
            f"redirect_uri={origin}/api/auth/github/callback&"
            f"scope=user:email,repo&"
            f"state={state}&"
            f"code_challenge={code_challenge}&"
            f"code_challenge_method=S256"
        )
        
        logger.info(f"✓ GitHub OAuth redirect: {origin}/api/auth/github/callback")
        
        return {
            "success": True,
            "auth_url": auth_url,
            "state": state
        }
    
    async def handle_github_callback(
        self, 
        code: str, 
        state: str
    ) -> Dict[str, Any]:
        """Handle GitHub OAuth callback and exchange code for token"""
        # Validate state
        oauth_state = await self.db.oauth_states.find_one({
            "state": state,
            "platform": "github",
            "used": False
        }, {"_id": 0})
        
        if not oauth_state:
            return {"success": False, "error": "Invalid or expired state"}
        
        # Check expiration
        expires_at = datetime.fromisoformat(oauth_state['expires_at'])
        if expires_at < datetime.now(timezone.utc):
            return {"success": False, "error": "State expired"}
        
        # Mark state as used
        await self.db.oauth_states.update_one(
            {"state": state},
            {"$set": {"used": True}}
        )
        
        # Exchange code for token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": self.github_client_id,
                    "client_secret": self.github_client_secret,
                    "code": code,
                    "code_verifier": oauth_state['code_verifier']
                },
                headers={"Accept": "application/json"}
            )
            
            if response.status_code != 200:
                return {"success": False, "error": "Token exchange failed"}
            
            token_data = response.json()
            access_token = token_data.get('access_token')
            
            if not access_token:
                return {"success": False, "error": "No access token received"}
        
        # Fetch user info
        user_info = await self._fetch_github_user(access_token)
        if not user_info:
            return {"success": False, "error": "Failed to fetch user info"}
        
        # Store connection
        await self.db.github_connections.update_one(
            {"user_id": oauth_state['user_id']},
            {
                "$set": {
                    "github_id": user_info['id'],
                    "username": user_info['login'],
                    "email": user_info.get('email'),
                    "avatar_url": user_info.get('avatar_url'),
                    "access_token": access_token,
                    "connected_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            },
            upsert=True
        )
        
        return {
            "success": True,
            "user": user_info,
            "message": "GitHub account connected successfully"
        }
    
    async def _fetch_github_user(self, access_token: str) -> Optional[dict]:
        """Fetch GitHub user info"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            return response.json() if response.status_code == 200 else None
    
    async def fetch_user_repositories(self, user_id: str) -> Dict[str, Any]:
        """Fetch all repositories for a connected GitHub user"""
        connection = await self.db.github_connections.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        
        if not connection:
            return {"success": False, "error": "GitHub not connected"}
        
        repos = []
        page = 1
        
        async with httpx.AsyncClient() as client:
            while page <= 5:  # Limit to 500 repos (5 pages * 100)
                response = await client.get(
                    "https://api.github.com/user/repos",
                    headers={"Authorization": f"Bearer {connection['access_token']}"},
                    params={
                        "per_page": 100,
                        "page": page,
                        "sort": "updated",
                        "direction": "desc"
                    }
                )
                
                if response.status_code != 200:
                    break
                
                page_repos = response.json()
                if not page_repos:
                    break
                
                repos.extend(page_repos)
                
                if len(page_repos) < 100:
                    break
                
                page += 1
        
        # Store repositories
        for repo in repos:
            await self.db.user_repositories.update_one(
                {"github_id": repo['id']},
                {
                    "$set": {
                        "user_id": user_id,
                        "github_id": repo['id'],
                        "name": repo['name'],
                        "full_name": repo['full_name'],
                        "description": repo.get('description'),
                        "url": repo['html_url'],
                        "stars": repo.get('stargazers_count', 0),
                        "forks": repo.get('forks_count', 0),
                        "language": repo.get('language'),
                        "is_private": repo.get('private', False),
                        "synced_at": datetime.now(timezone.utc).isoformat()
                    }
                },
                upsert=True
            )
        
        logger.info(f"✓ Synced {len(repos)} repositories for user {user_id}")
        
        return {
            "success": True,
            "repositories_count": len(repos),
            "repositories": repos[:20]  # Return first 20 for response
        }
    
    async def get_connection_status(self, user_id: str) -> Dict[str, Any]:
        """Get GitHub/GitLab connection status for user"""
        github_conn = await self.db.github_connections.find_one(
            {"user_id": user_id},
            {"_id": 0, "access_token": 0}
        )
        
        gitlab_conn = await self.db.gitlab_connections.find_one(
            {"user_id": user_id},
            {"_id": 0, "access_token": 0}
        )
        
        return {
            "github": {
                "connected": bool(github_conn),
                "username": github_conn.get('username') if github_conn else None,
                "repos_synced": await self.db.user_repositories.count_documents({
                    "user_id": user_id
                }) if github_conn else 0
            },
            "gitlab": {
                "connected": bool(gitlab_conn),
                "username": gitlab_conn.get('username') if gitlab_conn else None
            }
        }

def create_github_gitlab_service(db: AsyncIOMotorDatabase):
    return GitHubGitLabIntegrationService(db)
