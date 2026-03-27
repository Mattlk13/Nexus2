"""
Hybrid Analytics Service - Elite Analytics
Combines: PostHog (session replay, feature flags) + Matomo (detailed) + Plausible (lightweight) + Real-time
"""
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import httpx
import json
import os

logger = logging.getLogger(__name__)

class HybridAnalyticsService:
    """Elite analytics combining PostHog, Matomo, Plausible, and real-time tracking"""
    
    def __init__(self):
        # PostHog configuration (NEW)
        self.posthog_url = os.getenv('POSTHOG_URL', 'https://app.posthog.com')
        self.posthog_api_key = os.getenv('POSTHOG_API_KEY', '')
        self.posthog_enabled = bool(self.posthog_api_key)
        
        self.matomo_enabled = True
        self.plausible_enabled = True
        self.realtime_buffer = []
        self.max_buffer_size = 1000
        
        if self.posthog_enabled:
            logger.info("✓ Hybrid Analytics: PostHog + Matomo + Plausible + Real-time")
        else:
            logger.info("Hybrid Analytics: Matomo + Plausible + Real-time (Add POSTHOG_API_KEY for session replay)")
    
    async def track_event(
        self,
        event_type: str,
        properties: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> bool:
        """
        Track event to multiple analytics backends simultaneously.
        
        This hybrid approach ensures:
        - Session replay & feature flags in PostHog
        - Detailed tracking in Matomo
        - Lightweight tracking in Plausible
        - Real-time dashboard updates
        - Redundancy if one backend fails
        """
        tasks = []
        
        # 1. PostHog tracking (session replay, feature flags)
        if self.posthog_enabled:
            tasks.append(self._track_posthog(event_type, properties, user_id, session_id))
        
        # 2. Matomo tracking (detailed)
        if self.matomo_enabled:
            tasks.append(self._track_matomo(event_type, properties, user_id))
        
        # 3. Plausible tracking (lightweight)
        if self.plausible_enabled:
            tasks.append(self._track_plausible(event_type, properties))
        
        # 4. Real-time buffer (instant dashboards)
        self._buffer_realtime_event(event_type, properties, user_id, session_id)
        
        # Execute all tracking in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Return True if at least one backend succeeded
        return any(r for r in results if not isinstance(r, Exception))
    
    async def _track_posthog(
        self,
        event_type: str,
        properties: Dict[str, Any],
        user_id: Optional[str],
        session_id: Optional[str]
    ) -> bool:
        """Track to PostHog for session replay and product analytics"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                payload = {
                    "api_key": self.posthog_api_key,
                    "event": event_type,
                    "properties": {
                        **properties,
                        "$session_id": session_id,
                        "distinct_id": user_id or "anonymous"
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                response = await client.post(
                    f"{self.posthog_url}/capture/",
                    json=payload
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"PostHog tracking failed: {e}")
            return False
    
    async def _track_matomo(
        self,
        event_type: str,
        properties: Dict[str, Any],
        user_id: Optional[str]
    ) -> bool:
        """Track to Matomo for detailed analytics"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                params = {
                    'rec': 1,
                    'apiv': 1,
                    'idsite': 1,  # From env
                    'action_name': event_type,
                    'url': properties.get('url', '/'),
                    'e_c': properties.get('category', 'General'),
                    'e_a': event_type,
                    'e_n': properties.get('name', ''),
                }
                
                if user_id:
                    params['uid'] = user_id
                
                # Add custom dimensions
                if 'custom' in properties:
                    params['cvar'] = json.dumps(properties['custom'])
                
                # Matomo endpoint (will be configured)
                response = await client.post(
                    'http://localhost:8080/matomo.php',
                    params=params
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Matomo tracking failed: {e}")
            return False
    
    async def _track_plausible(
        self,
        event_type: str,
        properties: Dict[str, Any]
    ) -> bool:
        """Track to Plausible for lightweight analytics"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                payload = {
                    'name': event_type,
                    'url': properties.get('url', '/'),
                    'domain': 'nexus.ai',
                    'props': {
                        k: v for k, v in properties.items()
                        if k not in ['url', 'timestamp']
                    }
                }
                
                # Plausible endpoint (lightweight)
                response = await client.post(
                    'http://localhost:8000/api/event',
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                )
                return response.status_code == 202
        except Exception as e:
            logger.error(f"Plausible tracking failed: {e}")
            return False
    
    def _buffer_realtime_event(
        self,
        event_type: str,
        properties: Dict[str, Any],
        user_id: Optional[str],
        session_id: Optional[str]
    ):
        """Buffer event for real-time dashboard"""
        event = {
            'type': event_type,
            'properties': properties,
            'user_id': user_id,
            'session_id': session_id,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        self.realtime_buffer.append(event)
        
        # Keep buffer size manageable
        if len(self.realtime_buffer) > self.max_buffer_size:
            self.realtime_buffer = self.realtime_buffer[-self.max_buffer_size:]
    
    async def get_realtime_stats(self, minutes: int = 5) -> Dict[str, Any]:
        """Get real-time analytics for dashboard"""
        cutoff_time = datetime.now(timezone.utc).timestamp() - (minutes * 60)
        
        recent_events = [
            e for e in self.realtime_buffer
            if datetime.fromisoformat(e['timestamp'].replace('Z', '+00:00')).timestamp() > cutoff_time
        ]
        
        # Aggregate stats
        event_types = {}
        users = set()
        
        for event in recent_events:
            event_type = event['type']
            event_types[event_type] = event_types.get(event_type, 0) + 1
            if event['user_id']:
                users.add(event['user_id'])
    
    async def get_feature_flag(self, flag_key: str, user_id: str) -> Dict[str, Any]:
        """
        Get feature flag value from PostHog.
        Used for A/B testing and gradual rollouts.
        """
        if not self.posthog_enabled:
            return {"enabled": False, "error": "PostHog not configured"}
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.posthog_url}/decide/",
                    json={
                        "api_key": self.posthog_api_key,
                        "distinct_id": user_id
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    flags = data.get("featureFlags", {})
                    return {
                        "enabled": flags.get(flag_key, False),
                        "variant": flags.get(f"{flag_key}_variant")
                    }
        except Exception as e:
            logger.error(f"PostHog feature flag check failed: {e}")
        
        return {"enabled": False}
    
    async def start_session_recording(self, session_id: str, user_id: str) -> bool:
        """
        Start session recording in PostHog.
        Captures user interactions for UX debugging.
        """
        if not self.posthog_enabled:
            return False
        
        try:
            await self._track_posthog(
                "$session_recording_start",
                {"recording": True},
                user_id,
                session_id
            )
            return True
        except Exception as e:
            logger.error(f"PostHog session recording start failed: {e}")
            return False
    
    async def get_session_replay_url(self, session_id: str) -> Optional[str]:
        """Get URL to view session replay in PostHog dashboard"""
        if not self.posthog_enabled:
            return None
        
        # Construct replay URL
        return f"{self.posthog_url}/project/recordings/{session_id}"
    
    def get_status(self) -> Dict[str, Any]:
        """Get hybrid analytics status"""
        return {
            "backends": {
                "posthog": {
                    "enabled": self.posthog_enabled,
                    "features": ["session_replay", "feature_flags", "product_analytics"] if self.posthog_enabled else []
                },
                "matomo": {
                    "enabled": self.matomo_enabled,
                    "features": ["web_analytics", "heatmaps", "ecommerce"]
                },
                "plausible": {
                    "enabled": self.plausible_enabled,
                    "features": ["lightweight", "privacy_focused"]
                },
                "realtime": {
                    "enabled": True,
                    "buffer_size": len(self.realtime_buffer)
                }
            },
            "total_backends": sum([
                self.posthog_enabled,
                self.matomo_enabled,
                self.plausible_enabled,
                True  # realtime
            ]),
            "recommendation": "Add POSTHOG_API_KEY for session replay and feature flags" if not self.posthog_enabled else "All backends active"
        }

        
        return {
            'total_events': len(recent_events),
            'active_users': len(users),
            'event_breakdown': event_types,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    
    async def get_comprehensive_report(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Get comprehensive analytics from all sources"""
        tasks = []
        
        # Fetch from Matomo (detailed metrics)
        if self.matomo_enabled:
            tasks.append(self._fetch_matomo_report(start_date, end_date))
        
        # Fetch from Plausible (overview)
        if self.plausible_enabled:
            tasks.append(self._fetch_plausible_report(start_date, end_date))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        return {
            'matomo': results[0] if len(results) > 0 else {},
            'plausible': results[1] if len(results) > 1 else {},
            'realtime': await self.get_realtime_stats()
        }
    
    async def _fetch_matomo_report(self, start_date: str, end_date: str) -> Dict:
        """Fetch detailed report from Matomo"""
        # Implementation for Matomo API
        return {'source': 'matomo', 'data': {}}
    
    async def _fetch_plausible_report(self, start_date: str, end_date: str) -> Dict:
        """Fetch lightweight report from Plausible"""
        # Implementation for Plausible API
        return {'source': 'plausible', 'data': {}}

# Singleton instance
hybrid_analytics = HybridAnalyticsService()
