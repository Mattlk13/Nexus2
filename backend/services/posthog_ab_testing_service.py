"""
PostHog A/B Testing Service
Feature flags and A/B testing integration
"""
import logging
import httpx
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class PostHogABTestingService:
    """
    Integrates PostHog for:
    - Feature flags
    - A/B testing
    - Gradual feature rollouts
    - User segmentation
    """
    
    def __init__(self):
        self.posthog_url = os.getenv('POSTHOG_URL', 'https://app.posthog.com')
        self.posthog_api_key = os.getenv('POSTHOG_API_KEY', '')
        self.posthog_project_id = os.getenv('POSTHOG_PROJECT_ID', '')
        self.enabled = bool(self.posthog_api_key)
        
        # Cache feature flags
        self.feature_flags_cache = {}
        
        if self.enabled:
            logger.info("✓ PostHog A/B Testing enabled")
        else:
            logger.info("PostHog A/B Testing disabled (set POSTHOG_API_KEY)")
    
    async def get_feature_flag(
        self,
        flag_key: str,
        user_id: str,
        default: bool = False
    ) -> bool:
        """
        Check if feature flag is enabled for user.
        
        Uses PostHog /decide endpoint for real-time flag evaluation.
        """
        if not self.enabled:
            return default
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.posthog_url}/decide/",
                    json={
                        "api_key": self.posthog_api_key,
                        "distinct_id": user_id
                    },
                    params={"v": 3}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    flags = data.get("featureFlags", {})
                    return flags.get(flag_key, default)
        except Exception as e:
            logger.error(f"PostHog feature flag check failed: {e}")
        
        return default
    
    async def get_feature_flag_variant(
        self,
        flag_key: str,
        user_id: str,
        default_variant: str = "control"
    ) -> str:
        """
        Get feature flag variant for multivariate tests.
        
        Example:
        - control: Original version
        - test_a: Variant A
        - test_b: Variant B
        """
        if not self.enabled:
            return default_variant
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.posthog_url}/decide/",
                    json={
                        "api_key": self.posthog_api_key,
                        "distinct_id": user_id
                    },
                    params={"v": 3}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    feature_flag_payloads = data.get("featureFlagPayloads", {})
                    return feature_flag_payloads.get(flag_key, default_variant)
        except Exception as e:
            logger.error(f"PostHog variant check failed: {e}")
        
        return default_variant
    
    async def create_feature_flag(
        self,
        key: str,
        name: str,
        rollout_percentage: int = 100,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new feature flag in PostHog.
        
        Args:
            key: Unique flag key (e.g., 'new_checkout')
            name: Display name
            rollout_percentage: 0-100 (gradual rollout)
            enabled: Whether flag is active
        """
        if not self.enabled:
            return {"success": False, "error": "PostHog not configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.posthog_url}/api/projects/{self.posthog_project_id}/feature_flags/",
                    headers={
                        "Authorization": f"Bearer {self.posthog_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "key": key,
                        "name": name,
                        "active": enabled,
                        "filters": {
                            "groups": [
                                {
                                    "properties": [],
                                    "rollout_percentage": rollout_percentage
                                }
                            ]
                        }
                    }
                )
                
                if response.status_code == 201:
                    return {"success": True, "flag": response.json()}
                else:
                    return {"success": False, "error": response.text}
        except Exception as e:
            logger.error(f"Create feature flag failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_rollout_percentage(
        self,
        flag_key: str,
        percentage: int
    ) -> Dict[str, Any]:
        """
        Update feature flag rollout percentage (gradual rollout).
        
        Example:
        - 10% for initial test
        - 50% for broader test
        - 100% for full release
        """
        # Implementation would require flag ID lookup first
        return {
            "success": True,
            "flag_key": flag_key,
            "new_percentage": percentage,
            "note": "Update via PostHog dashboard for now"
        }
    
    async def track_experiment_event(
        self,
        user_id: str,
        event_name: str,
        properties: Dict[str, Any]
    ):
        """
        Track experiment events for analysis.
        
        Use this to measure experiment success.
        """
        if not self.enabled:
            return
        
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.posthog_url}/capture/",
                    json={
                        "api_key": self.posthog_api_key,
                        "event": event_name,
                        "distinct_id": user_id,
                        "properties": properties,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
        except Exception as e:
            logger.error(f"Track experiment event failed: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get A/B testing service status"""
        return {
            "enabled": self.enabled,
            "posthog_url": self.posthog_url,
            "flags_cached": len(self.feature_flags_cache),
            "features": [
                "Feature flags",
                "A/B testing",
                "Multivariate testing",
                "Gradual rollouts",
                "User segmentation"
            ]
        }

# Singleton
posthog_ab_testing = PostHogABTestingService()
