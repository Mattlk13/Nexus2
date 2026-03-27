import os
import asyncio
import logging
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from typing import Dict, Any, List
from dotenv import load_dotenv
from pathlib import Path
import random
from .screenshot_tools import PRIORITY_TOOLS
from .softr_service import softr_service

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

# User agent rotation for ethical scraping
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
]

class AIxploriaScraperService:
    """Service for discovering and evaluating AI tools from multiple sources"""
    
    def __init__(self):
        self.base_url = "https://www.aixploria.com/en"
        
        # ALL 50+ AIxploria categories for comprehensive scraping
        self.categories = {
            # AI Productivity Tools
            "e-mail-en": "Email", "education-en": "Education", "extensions-chatgpt": "ChatGPT Extensions",
            "files-spreadsheets": "Files & Spreadsheets", "memory-en": "Memory", "search-engine": "Search Engine",
            "presentation-en": "Presentation", "productivity-en": "Productivity", "translation-ai": "Translation",
            
            # AI Assistants
            "legal-assistants": "Legal Assistants", "life-assistants": "Life Assistants",
            "ai-chat-assistant": "AI Chat & Assistant", "chatbot-ai": "ChatBots",
            
            # AI Video Tools
            "video-edition": "Video Editing", "video-generators": "Video Generators", "text-to-video-en": "Text-to-Video",
            
            # AI Text Generators
            "storytelling-generator": "Storytelling", "ai-text-generators": "Text Generators",
            "prompts-help": "Prompts & Aids", "writing-web-seo": "Writing & SEO", "ai-summarizer": "Summarizer",
            
            # AI Art Generators
            "art-en": "Art", "avatars-en": "Avatars", "best-ai-logo-generators": "Logo Creation",
            "image-editing": "Image Editing", "image-ai-en": "Image Generators", "3d-model": "3D Model",
            
            # Automation Tools
            "best-ai-agents": "AI Agents", "automation-ai-workflows": "Automation",
            
            # AI Audio & Music
            "ai-voice-cloning": "Voice Cloning", "audio-editing": "Audio Editing",
            "voice-reading": "Text-to-Speech", "music": "Music", "transcriber": "Transcriber",
            
            # AI Business Tools
            "business-study": "Business", "e-commerce-en": "E-commerce", "finance-en": "Finance",
            "marketing-ai": "Marketing", "social-assistants-en": "Social Networks",
            "human-resources-ai": "Human Resources", "seo-ai-tools": "SEO",
            "customer-support": "Customer Support", "sales-conversion-leads": "Sales & Conversion",
            
            # AI Data & Research
            "data-analytics-ai": "Data & Analytics", "ai-detection-en": "AI Detection",
            "research-science-en": "Research & Science",
            
            # AI Code Tools
            "assistant-code-en": "Assistant Code", "llm-model-ai-en": "LLM Models",
            "no-code-en": "No Code/Low Code", "developer-tools": "Developer Tools",
            "github-project-ai": "Github Projects", "websites-ai": "Websites & Design",
            
            # AI Industry Tools
            "real-estate": "Real Estate / Architect", "robots-devices-ai": "Robots and Devices",
            "healthcare": "Healthcare", "ai-assistive-technology-at": "Assistive Technology",
            
            # AI Entertainment
            "face-swap-deepfake-en": "Face Swap & DeepFake", "fashion-en": "Fashion",
            "amazing": "Amazing", "games-en": "Games", "best-ai-characters-chatbots-lists": "AI Characters",
            "dating-relationships-ai": "Dating & Relationships", "ai-rip-en": "RIP AI",
            "ai-simulation-3d-world": "AI Simulation", "travel": "Travel"
        }
        
        self.max_retries = 3
        self.retry_delay = 2
        self.producthunt_api_key = os.environ.get('PRODUCTHUNT_API_KEY', '')
        
    async def _fetch_with_retry(self, url: str, session: aiohttp.ClientSession) -> str:
        """Fetch URL with retry logic and rate limiting"""
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        
        for attempt in range(self.max_retries):
            try:
                await asyncio.sleep(random.uniform(1, 3))  # Rate limiting
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status == 429:  # Rate limited
                        wait_time = self.retry_delay ** (attempt + 1)
                        logger.warning(f"Rate limited, waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.warning(f"Status {response.status} for {url}")
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay ** attempt)
            except Exception as e:
                logger.error(f"Fetch error on attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay ** attempt)
        
        return ""
    
    async def scrape_top_100(self) -> List[Dict[str, Any]]:
        """Scrape top 100 trending AI tools with retry logic"""
        logger.info("🔍 Scraping AIxploria Top 100...")
        
        tools = []
        url = f"{self.base_url}/top-100-ai/"
        
        try:
            async with aiohttp.ClientSession() as session:
                html = await self._fetch_with_retry(url, session)
                if not html:
                    logger.error("Failed to fetch top 100 after retries")
                    return []
                
                soup = BeautifulSoup(html, 'html.parser')
                
                # Parse tool listings - try multiple selectors
                tool_items = soup.find_all('li', class_=lambda x: x and 'tool' in str(x).lower())
                if not tool_items:
                    tool_items = soup.find_all('article', class_=lambda x: x and 'card' in str(x).lower())
                if not tool_items:
                    tool_items = soup.find_all('div', class_=lambda x: x and 'item' in str(x).lower())
                
                for item in tool_items[:50]:  # Limit to top 50 for performance
                    try:
                        name_tag = item.find('a')
                        if not name_tag:
                            continue
                            
                        name = name_tag.text.strip() if name_tag else "Unknown"
                        tool_url = name_tag.get('href', '')
                        
                        # Extract category from URL or text
                        category = "General"
                        if '/category/' in tool_url:
                            category = tool_url.split('/category/')[-1].split('/')[0]
                        
                        # Extract description if available
                        desc_tag = item.find('p', class_=lambda x: x and 'desc' in str(x).lower())
                        description = desc_tag.text.strip() if desc_tag else ""
                        
                        tools.append({
                            "name": name,
                            "url": tool_url,
                            "description": description,
                            "category": category,
                            "source": "aixploria_top_100",
                            "discovered_at": datetime.now(timezone.utc).isoformat()
                        })
                    except Exception as e:
                        logger.debug(f"Skipping tool item: {e}")
                        continue
            
            logger.info(f"✓ Scraped {len(tools)} tools from AIxploria Top 100")
            return tools
            
        except Exception as e:
            logger.error(f"Failed to scrape top 100: {str(e)}")
            return []
    
    async def scrape_latest_ai(self) -> List[Dict[str, Any]]:
        """Scrape latest new AI tools with retry logic"""
        logger.info("🔍 Scraping AIxploria Latest AI...")
        
        tools = []
        url = f"{self.base_url}/last-ai/"
        
        try:
            async with aiohttp.ClientSession() as session:
                html = await self._fetch_with_retry(url, session)
                if not html:
                    return []
                
                soup = BeautifulSoup(html, 'html.parser')
                tool_items = soup.find_all(['li', 'article'], class_=lambda x: x and 'tool' in str(x).lower())
                
                for item in tool_items[:30]:
                    try:
                        name_tag = item.find('a', href=True)
                        if name_tag:
                            name = name_tag.text.strip()
                            tool_url = name_tag.get('href', '')
                            
                            # Extract description
                            desc_tag = item.find('p')
                            description = desc_tag.text.strip() if desc_tag else ""
                            
                            tools.append({
                                "name": name,
                                "url": tool_url,
                                "description": description,
                                "category": "Latest",
                                "source": "aixploria_latest",
                                "discovered_at": datetime.now(timezone.utc).isoformat()
                            })
                    except Exception:
                        continue
            
            logger.info(f"✓ Scraped {len(tools)} latest AI tools")
            return tools
            
        except Exception as e:
            logger.error(f"Failed to scrape latest AI: {str(e)}")
            return []
    
    async def scrape_github_trending_ai(self) -> List[Dict[str, Any]]:
        """Scrape GitHub trending AI repositories"""
        logger.info("🔍 Discovering GitHub Trending AI tools...")
        
        tools = []
        url = "https://github.com/trending/python?since=daily&spoken_language_code=en"
        
        try:
            async with aiohttp.ClientSession() as session:
                html = await self._fetch_with_retry(url, session)
                if not html:
                    return []
                
                soup = BeautifulSoup(html, 'html.parser')
                articles = soup.find_all('article', class_='Box-row')
                
                for article in articles[:20]:
                    try:
                        h2_tag = article.find('h2')
                        if not h2_tag:
                            continue
                        
                        a_tag = h2_tag.find('a')
                        if not a_tag:
                            continue
                        
                        repo_path = a_tag.get('href', '').strip()
                        name = repo_path.split('/')[-1] if repo_path else "Unknown"
                        
                        # Get description
                        desc_tag = article.find('p', class_='col-9')
                        description = desc_tag.text.strip() if desc_tag else ""
                        
                        # Check if it's AI-related
                        text_content = (name + description).lower()
                        ai_keywords = ['ai', 'ml', 'machine learning', 'llm', 'gpt', 'neural', 'model', 'agent', 'chatbot', 'generation']
                        
                        if any(kw in text_content for kw in ai_keywords):
                            # Get stars
                            stars_tag = article.find('span', class_='d-inline-block float-sm-right')
                            stars = stars_tag.text.strip() if stars_tag else "0"
                            
                            tools.append({
                                "name": name,
                                "url": f"https://github.com{repo_path}",
                                "description": description,
                                "category": "Open Source",
                                "stars": stars,
                                "source": "github_trending",
                                "discovered_at": datetime.now(timezone.utc).isoformat()
                            })
                    except Exception as e:
                        logger.debug(f"Skipping GitHub article: {e}")
                        continue
            
            logger.info(f"✓ Found {len(tools)} trending AI tools on GitHub")
            return tools
            
        except Exception as e:
            logger.error(f"Failed to scrape GitHub trending: {str(e)}")
            return []
    
    async def scrape_aixploria_category(self, category_slug: str, category_name: str, max_tools: int = 10) -> List[Dict[str, Any]]:
        """Scrape a specific AIxploria category for tools"""
        tools = []
        url = f"{self.base_url}/category/{category_slug}/"
        
        try:
            async with aiohttp.ClientSession() as session:
                html = await self._fetch_with_retry(url, session)
                if not html:
                    return []
                
                soup = BeautifulSoup(html, 'html.parser')
                
                # Try multiple selectors for tool items
                tool_items = soup.find_all(['article', 'div', 'li'], class_=lambda x: x and ('tool' in str(x).lower() or 'item' in str(x).lower() or 'card' in str(x).lower()))
                
                for item in tool_items[:max_tools]:
                    try:
                        name_tag = item.find('a', href=True)
                        if not name_tag:
                            continue
                        
                        name = name_tag.text.strip()
                        if not name or len(name) < 2:
                            continue
                        
                        tool_url = name_tag.get('href', '')
                        
                        # Extract description
                        desc_tag = item.find('p')
                        description = desc_tag.text.strip() if desc_tag else ""
                        
                        tools.append({
                            "name": name,
                            "url": tool_url if tool_url.startswith('http') else f"{self.base_url}{tool_url}",
                            "description": description,
                            "category": category_name,
                            "source": f"aixploria_category_{category_slug}",
                            "discovered_at": datetime.now(timezone.utc).isoformat()
                        })
                    except Exception as e:
                        logger.debug(f"Skipping item in {category_name}: {e}")
                        continue
                
                return tools
                
        except Exception as e:
            logger.debug(f"Category {category_name} scrape error: {e}")
            return []
    
    async def scrape_all_categories(self, max_per_category: int = 5) -> List[Dict[str, Any]]:
        """Scrape top tools from ALL 50+ AIxploria categories"""
        logger.info(f"🔍 Scraping ALL {len(self.categories)} AIxploria categories...")
        
        all_tools = []
        
        # Scrape categories in batches to avoid overwhelming the server
        category_items = list(self.categories.items())
        batch_size = 10
        
        for i in range(0, len(category_items), batch_size):
            batch = category_items[i:i+batch_size]
            
            # Scrape batch in parallel
            tasks = [self.scrape_aixploria_category(slug, name, max_per_category) for slug, name in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_tools.extend(result)
            
            # Rate limiting between batches
            if i + batch_size < len(category_items):
                await asyncio.sleep(random.uniform(3, 5))
        
        logger.info(f"✓ Scraped {len(all_tools)} tools from {len(self.categories)} categories")
        return all_tools
    
    async def scrape_producthunt_ai(self) -> List[Dict[str, Any]]:
        """Scrape ProductHunt using official API v2 (GraphQL)"""
        logger.info("🔍 Discovering ProductHunt AI tools via API...")
        
        tools = []
        api_key = self.producthunt_api_key
        
        # Use API if key is provided, otherwise skip
        if not api_key or 'demo' in api_key.lower():
            logger.warning("ProductHunt API key not configured - skipping ProductHunt")
            return []
        
        try:
            # ProductHunt V2 GraphQL API
            url = "https://api.producthunt.com/v2/api/graphql"
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            # GraphQL query for AI tools
            query = """
            {
              posts(first: 20, topic: "artificial-intelligence", order: VOTES) {
                edges {
                  node {
                    name
                    tagline
                    description
                    url
                    votesCount
                    topics {
                      edges {
                        node {
                          name
                        }
                      }
                    }
                  }
                }
              }
            }
            """
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json={'query': query}, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        posts = data.get('data', {}).get('posts', {}).get('edges', [])
                        
                        for edge in posts:
                            node = edge.get('node', {})
                            topics = [t.get('node', {}).get('name', '') for t in node.get('topics', {}).get('edges', [])]
                            
                            tools.append({
                                "name": node.get('name', 'Unknown'),
                                "url": node.get('url', ''),
                                "description": node.get('tagline', '') or node.get('description', ''),
                                "category": ", ".join(topics[:3]) if topics else "AI",
                                "votes": node.get('votesCount', 0),
                                "source": "producthunt_api",
                                "discovered_at": datetime.now(timezone.utc).isoformat()
                            })
                        
                        logger.info(f"✓ Found {len(tools)} AI tools on ProductHunt via API")
                    else:
                        logger.warning(f"ProductHunt API returned status {response.status}")
            
            return tools
            
        except Exception as e:
            logger.error(f"ProductHunt API error: {str(e)}")
            return []
    
    def categorize_for_nexus(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        """Categorize tool by potential benefit to NEXUS"""
        
        name_lower = tool["name"].lower()
        category_lower = tool.get("category", "").lower()
        description_lower = tool.get("description", "").lower()
        
        # Scoring criteria
        score = 0
        nexus_categories = []
        integration_type = []
        reasons = []
        
        # Bonus for trending tools (from screenshots)
        if tool.get("trend"):
            trend_bonus = min(tool["trend"] * 0.5, 20)
            score += trend_bonus
            reasons.append(f"Trending: {tool['trend']} points")
        
        # Bonus for screenshot priority tools
        if "screenshot" in tool.get("source", ""):
            score += 15
            reasons.append("User-identified priority tool")
        
        # Bonus for GitHub stars
        if tool.get("stars"):
            try:
                stars_str = str(tool["stars"]).replace(',', '').replace('k', '000')
                stars_num = int(stars_str) if stars_str.isdigit() else 0
                if stars_num > 1000:
                    score += 10
                    reasons.append(f"{tool['stars']} GitHub stars")
            except (ValueError, TypeError):
                pass
        
        # Bonus for ProductHunt votes
        if tool.get("votes", 0) > 100:
            score += 8
            reasons.append(f"{tool['votes']} ProductHunt votes")
        
        # Creator Studio Tools (High Priority)
        creator_keywords = ["music", "video", "image", "art", "3d", "audio", "voice", "song", "design"]
        if any(kw in name_lower or kw in category_lower or kw in description_lower for kw in creator_keywords):
            score += 40
            nexus_categories.append("Creator Studio")
            integration_type.append("ai_generation_tool")
            reasons.append("Enhances creator content generation capabilities")
        
        # Marketing & SEO (High Priority)
        marketing_keywords = ["marketing", "seo", "social", "ads", "campaign", "email", "content"]
        if any(kw in name_lower or kw in category_lower or kw in description_lower for kw in marketing_keywords):
            score += 35
            nexus_categories.append("Marketing Automation")
            integration_type.append("marketing_agent")
            reasons.append("Boosts platform marketing and user acquisition")
        
        # Business & Analytics (Medium Priority)
        business_keywords = ["analytics", "business", "crm", "data", "dashboard", "metrics"]
        if any(kw in name_lower or kw in category_lower for kw in business_keywords):
            score += 30
            nexus_categories.append("Admin Dashboard")
            integration_type.append("analytics_tool")
            reasons.append("Improves admin insights and decision making")
        
        # E-commerce & Sales (High Priority)
        ecommerce_keywords = ["commerce", "payment", "shop", "sales", "checkout", "conversion"]
        if any(kw in name_lower or kw in category_lower for kw in ecommerce_keywords):
            score += 35
            nexus_categories.append("Marketplace Enhancement")
            integration_type.append("ecommerce_tool")
            reasons.append("Increases sales and conversion rates")
        
        # Automation & Agents (Very High Priority)
        automation_keywords = ["agent", "automation", "workflow", "task", "bot", "assistant"]
        if any(kw in name_lower or kw in category_lower for kw in automation_keywords):
            score += 45
            nexus_categories.append("AI Agents")
            integration_type.append("autonomous_agent")
            reasons.append("Adds autonomous capabilities to agent system")
        
        # Developer Tools (Medium Priority)
        dev_keywords = ["code", "developer", "api", "github", "no-code", "deploy"]
        if any(kw in name_lower or kw in category_lower for kw in dev_keywords):
            score += 25
            nexus_categories.append("Development Tools")
            integration_type.append("dev_tool")
            reasons.append("Speeds up development and deployment")
        
        # LLM Models (High Priority)
        if "llm" in category_lower or "model" in name_lower or "gpt" in name_lower or "claude" in name_lower:
            score += 40
            nexus_categories.append("AI Models")
            integration_type.append("llm_model")
            reasons.append("Provides additional AI generation capabilities")
        
        # Determine benefit level and recommendation
        benefit_level = "low"
        recommendation = "monitor"
        
        if score >= 70:
            benefit_level = "critical"
            recommendation = "integrate_immediately"
        elif score >= 50:
            benefit_level = "high"
            recommendation = "integrate_soon"
        elif score >= 30:
            benefit_level = "medium"
            recommendation = "evaluate_further"
        
        return {
            **tool,
            "nexus_score": score,
            "benefit_level": benefit_level,
            "nexus_categories": nexus_categories,
            "integration_type": integration_type,
            "recommendation": recommendation,
            "reasons": reasons,
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def discover_and_evaluate(self, include_all_categories: bool = False) -> Dict[str, Any]:
        """Full discovery and evaluation workflow from multiple sources
        
        Args:
            include_all_categories: If True, scrapes ALL 50+ AIxploria categories (slower but comprehensive)
        """
        logger.info("🔍 Starting Multi-Source AI Discovery workflow...")
        
        # Start with priority tools from user screenshots
        logger.info(f"📸 Loading {len(PRIORITY_TOOLS)} priority tools from screenshots...")
        all_tools = PRIORITY_TOOLS.copy()
        
        # Base sources (fast)
        tasks = [
            self.scrape_top_100(),
            self.scrape_latest_ai(),
            self.scrape_github_trending_ai(),
            self.scrape_producthunt_ai(),
            softr_service.scrape_softr_integrations()  # NEW: Softr database
        ]
        
        # Add comprehensive category scraping if requested
        if include_all_categories:
            logger.info(f"📚 Including ALL {len(self.categories)} categories - this will take 2-3 minutes")
            tasks.append(self.scrape_all_categories(max_per_category=5))
        
        # Scrape all sources in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results and handle exceptions
        for result in results:
            if isinstance(result, list):
                all_tools.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Scraping error: {result}")
        
        # Remove duplicates by name (case-insensitive)
        unique_tools = {}
        for tool in all_tools:
            name_key = tool["name"].lower().strip()
            if name_key and name_key not in unique_tools:
                unique_tools[name_key] = tool
        
        # Evaluate each tool
        evaluated_tools = []
        critical_integrations = []
        high_priority = []
        medium_priority = []
        
        for tool in unique_tools.values():
            evaluated = self.categorize_for_nexus(tool)
            evaluated_tools.append(evaluated)
            
            if evaluated["benefit_level"] == "critical":
                critical_integrations.append(evaluated)
            elif evaluated["benefit_level"] == "high":
                high_priority.append(evaluated)
            elif evaluated["benefit_level"] == "medium":
                medium_priority.append(evaluated)
        
        # Sort by score
        critical_integrations.sort(key=lambda x: x["nexus_score"], reverse=True)
        high_priority.sort(key=lambda x: x["nexus_score"], reverse=True)
        medium_priority.sort(key=lambda x: x["nexus_score"], reverse=True)
        
        sources_scanned = ["screenshot_priority_tools", "aixploria_top_100", "aixploria_latest", "github_trending", "softr_database"]
        if include_all_categories:
            sources_scanned.append("aixploria_all_categories")
        if self.producthunt_api_key and 'demo' not in self.producthunt_api_key.lower():
            sources_scanned.append("producthunt_api")
        
        result = {
            "scan_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_tools_discovered": len(evaluated_tools),
            "sources_scanned": sources_scanned,
            "scan_mode": "comprehensive" if include_all_categories else "standard",
            "critical_integrations": critical_integrations[:20],
            "high_priority": high_priority[:30],
            "medium_priority": medium_priority[:20],
            "summary": {
                "critical_count": len(critical_integrations),
                "high_count": len(high_priority),
                "medium_count": len(medium_priority),
                "low_count": len(evaluated_tools) - len(critical_integrations) - len(high_priority) - len(medium_priority),
                "categories_scanned": len(self.categories) if include_all_categories else 2,
                "screenshot_tools_included": len(PRIORITY_TOOLS)
            }
        }
        
        logger.info(f"✓ Multi-Source Discovery complete: {len(evaluated_tools)} total, {len(critical_integrations)} critical, {len(high_priority)} high")
        return result

aixploria_service = AIxploriaScraperService()
