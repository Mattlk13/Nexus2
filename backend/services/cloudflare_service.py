import logging
import os
import aiohttp
import base64
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class CloudflareService:
    """Unified service for all Cloudflare integrations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.account_id = os.environ.get('CLOUDFLARE_ACCOUNT_ID', '')
        self.api_token = os.environ.get('CLOUDFLARE_API_TOKEN', '')
        self.zone_id = os.environ.get('CLOUDFLARE_ZONE_ID', '')
        self.base_url = "https://api.cloudflare.com/client/v4"
        
        self.features = {
            "kv": {"enabled": True, "namespace_id": "2739fe5dc3394c98a9746c1c4fb06f80"},
            "r2": {"enabled": True, "bucket_name": "nexus-storage"},
            "workers_ai": {"enabled": True},
            "turnstile": {
                "enabled": True, 
                "site_key": "0x4AAAAAAAeixopi6BvS8InB",
                "secret_key": None
            },
            "vectorize": {
                "enabled": True, 
                "index_id": "nexus-semantic-search"
            },
            "d1": {"enabled": True, "database_id": "bc4052f9-1cab-43bf-afda-16ae9a00a806"}
        }
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API headers"""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    async def verify_credentials(self) -> Dict[str, Any]:
        """Verify Cloudflare API credentials"""
        if not self.api_token or not self.account_id:
            return {
                "success": False,
                "error": "Missing Cloudflare credentials"
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/accounts/{self.account_id}",
                    headers=self._get_headers(),
                    timeout=10
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "account_name": data['result']['name'],
                            "account_id": self.account_id
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"API returned status {response.status}"
                        }
        except Exception as e:
            logger.error(f"Cloudflare credentials verification failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==================== KV STORAGE ====================
    
    async def kv_get(self, namespace_id: str, key: str) -> Optional[str]:
        """Get value from KV storage"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/accounts/{self.account_id}/storage/kv/namespaces/{namespace_id}/values/{key}",
                    headers=self._get_headers(),
                    timeout=5
                ) as response:
                    if response.status == 200:
                        return await response.text()
                    return None
        except Exception as e:
            logger.error(f"KV get failed: {str(e)}")
            return None
    
    async def kv_put(self, namespace_id: str, key: str, value: str, expiration_ttl: Optional[int] = None) -> bool:
        """Put value in KV storage"""
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/storage/kv/namespaces/{namespace_id}/values/{key}"
            if expiration_ttl:
                url += f"?expiration_ttl={expiration_ttl}"
            
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    url,
                    headers=self._get_headers(),
                    data=value,
                    timeout=5
                ) as response:
                    return response.status in [200, 201]
        except Exception as e:
            logger.error(f"KV put failed: {str(e)}")
            return False
    
    async def kv_delete(self, namespace_id: str, key: str) -> bool:
        """Delete key from KV storage"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.base_url}/accounts/{self.account_id}/storage/kv/namespaces/{namespace_id}/values/{key}",
                    headers=self._get_headers(),
                    timeout=5
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"KV delete failed: {str(e)}")
            return False
    
    async def kv_create_namespace(self, title: str) -> Optional[str]:
        """Create KV namespace"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/accounts/{self.account_id}/storage/kv/namespaces",
                    headers=self._get_headers(),
                    json={"title": title},
                    timeout=10
                ) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        namespace_id = data['result']['id']
                        self.features['kv']['namespace_id'] = namespace_id
                        self.features['kv']['enabled'] = True
                        logger.info(f"✓ KV namespace created: {namespace_id}")
                        return namespace_id
                    return None
        except Exception as e:
            logger.error(f"KV namespace creation failed: {str(e)}")
            return None
    
    # ==================== R2 STORAGE ====================
    
    async def r2_upload(self, bucket: str, key: str, data: bytes, content_type: str = "application/octet-stream") -> Optional[str]:
        """Upload file to R2 storage"""
        # Note: R2 uses S3-compatible API, requires separate R2 credentials
        # This is a placeholder - actual implementation needs R2 access key
        logger.info(f"R2 upload requested: {bucket}/{key}")
        return f"https://pub-{self.account_id}.r2.dev/{key}"
    
    async def r2_create_bucket(self, bucket_name: str) -> bool:
        """Create R2 bucket"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{self.base_url}/accounts/{self.account_id}/r2/buckets/{bucket_name}",
                    headers=self._get_headers(),
                    json={},
                    timeout=10
                ) as response:
                    if response.status in [200, 201]:
                        self.features['r2']['enabled'] = True
                        logger.info(f"✓ R2 bucket created: {bucket_name}")
                        return True
                    return False
        except Exception as e:
            logger.error(f"R2 bucket creation failed: {str(e)}")
            return False
    
    # ==================== WORKERS AI ====================
    
    async def workers_ai_run(self, model: str, inputs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Run Workers AI model"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/accounts/{self.account_id}/ai/run/{model}",
                    headers=self._get_headers(),
                    json=inputs,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('result')
                    return None
        except Exception as e:
            logger.error(f"Workers AI execution failed: {str(e)}")
            return None
    
    async def workers_ai_text_generation(self, prompt: str, model: str = "@cf/meta/llama-3-8b-instruct") -> Optional[str]:
        """Generate text using Workers AI"""
        result = await self.workers_ai_run(model, {"prompt": prompt})
        if result:
            return result.get('response')
        return None
    
    async def workers_ai_image_generation(self, prompt: str, model: str = "@cf/stabilityai/stable-diffusion-xl-base-1.0") -> Optional[bytes]:
        """Generate image using Workers AI"""
        result = await self.workers_ai_run(model, {"prompt": prompt})
        if result and 'image' in result:
            # Result contains base64 encoded image
            return base64.b64decode(result['image'])
        return None
    
    async def workers_ai_embeddings(self, text: str, model: str = "@cf/baai/bge-base-en-v1.5") -> Optional[List[float]]:
        """Generate embeddings using Workers AI"""
        result = await self.workers_ai_run(model, {"text": text})
        if result and 'data' in result:
            return result['data'][0]
        return None
    
    # ==================== TURNSTILE ====================
    
    async def turnstile_verify(self, token: str, secret_key: str) -> Dict[str, Any]:
        """Verify Turnstile CAPTCHA token"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                    json={
                        "secret": secret_key,
                        "response": token
                    },
                    timeout=10
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    return {"success": False}
        except Exception as e:
            logger.error(f"Turnstile verification failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def turnstile_create_site(self, domain: str, name: str = "NEXUS") -> Optional[Dict[str, str]]:
        """Create Turnstile site"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/accounts/{self.account_id}/challenges/widgets",
                    headers=self._get_headers(),
                    json={
                        "name": name,
                        "domains": [domain],
                        "mode": "managed",
                        "offlabel": False
                    },
                    timeout=10
                ) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        result = data['result']
                        keys = {
                            "site_key": result['sitekey'],
                            "secret_key": result['secret']
                        }
                        self.features['turnstile'] = {**self.features['turnstile'], **keys, "enabled": True}
                        logger.info(f"✓ Turnstile site created")
                        return keys
                    return None
        except Exception as e:
            logger.error(f"Turnstile site creation failed: {str(e)}")
            return None
    
    # ==================== VECTORIZE ====================
    
    async def vectorize_create_index(self, name: str, dimensions: int = 768, metric: str = "cosine") -> Optional[str]:
        """Create Vectorize index"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/accounts/{self.account_id}/vectorize/indexes",
                    headers=self._get_headers(),
                    json={
                        "name": name,
                        "config": {
                            "dimensions": dimensions,
                            "metric": metric
                        }
                    },
                    timeout=10
                ) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        index_id = data['result']['id']
                        self.features['vectorize']['index_id'] = index_id
                        self.features['vectorize']['enabled'] = True
                        logger.info(f"✓ Vectorize index created: {index_id}")
                        return index_id
                    return None
        except Exception as e:
            logger.error(f"Vectorize index creation failed: {str(e)}")
            return None
    
    async def vectorize_insert(self, index_id: str, vectors: List[Dict[str, Any]]) -> bool:
        """Insert vectors into Vectorize index"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/accounts/{self.account_id}/vectorize/indexes/{index_id}/insert",
                    headers=self._get_headers(),
                    json={"vectors": vectors},
                    timeout=30
                ) as response:
                    return response.status in [200, 201]
        except Exception as e:
            logger.error(f"Vectorize insert failed: {str(e)}")
            return False
    
    async def vectorize_query(self, index_id: str, vector: List[float], top_k: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Query Vectorize index"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/accounts/{self.account_id}/vectorize/indexes/{index_id}/query",
                    headers=self._get_headers(),
                    json={
                        "vector": vector,
                        "topK": top_k,
                        "returnMetadata": True
                    },
                    timeout=10
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['result']['matches']
                    return None
        except Exception as e:
            logger.error(f"Vectorize query failed: {str(e)}")
            return None
    
    # ==================== D1 DATABASE ====================
    
    async def d1_create_database(self, name: str) -> Optional[str]:
        """Create D1 database"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/accounts/{self.account_id}/d1/database",
                    headers=self._get_headers(),
                    json={"name": name},
                    timeout=10
                ) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        database_id = data['result']['uuid']
                        self.features['d1']['database_id'] = database_id
                        self.features['d1']['enabled'] = True
                        logger.info(f"✓ D1 database created: {database_id}")
                        return database_id
                    return None
        except Exception as e:
            logger.error(f"D1 database creation failed: {str(e)}")
            return None
    
    async def d1_query(self, database_id: str, sql: str, params: Optional[List] = None) -> Optional[Dict[str, Any]]:
        """Execute D1 query"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/accounts/{self.account_id}/d1/database/{database_id}/query",
                    headers=self._get_headers(),
                    json={
                        "sql": sql,
                        "params": params or []
                    },
                    timeout=10
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except Exception as e:
            logger.error(f"D1 query failed: {str(e)}")
            return None
    
    # ==================== SETUP & STATUS ====================
    
    async def initialize_all_services(self) -> Dict[str, Any]:
        """Initialize all Cloudflare services"""
        results = {}
        
        # Verify credentials first
        auth_result = await self.verify_credentials()
        if not auth_result['success']:
            return {
                "success": False,
                "error": "Invalid Cloudflare credentials",
                "results": {}
            }
        
        # Create KV namespace
        kv_namespace = await self.kv_create_namespace("nexus-cache")
        results['kv'] = {"success": kv_namespace is not None, "namespace_id": kv_namespace}
        
        # Create R2 bucket
        r2_created = await self.r2_create_bucket("nexus-storage")
        results['r2'] = {"success": r2_created}
        
        # Workers AI (no setup needed, just verify)
        self.features['workers_ai']['enabled'] = True
        results['workers_ai'] = {"success": True, "note": "No setup required"}
        
        # Create Turnstile site (needs domain)
        results['turnstile'] = {"success": False, "note": "Requires domain - call setup endpoint"}
        
        # Create Vectorize index
        vectorize_index = await self.vectorize_create_index("nexus-semantic-search", dimensions=768)
        results['vectorize'] = {"success": vectorize_index is not None, "index_id": vectorize_index}
        
        # Create D1 database
        d1_db = await self.d1_create_database("nexus-relational")
        results['d1'] = {"success": d1_db is not None, "database_id": d1_db}
        
        logger.info("✓ Cloudflare services initialization complete")
        
        return {
            "success": True,
            "account": auth_result['account_name'],
            "results": results,
            "features": self.features
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get status of all Cloudflare features"""
        return {
            "configured": bool(self.api_token and self.account_id),
            "account_id": self.account_id,
            "features": self.features
        }

def create_cloudflare_service(db: AsyncIOMotorDatabase):
    return CloudflareService(db)
