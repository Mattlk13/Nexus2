import asyncio
import logging
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from typing import Dict, Any, List
import re

logger = logging.getLogger(__name__)

class MegaDiscoveryEngine:
    """Comprehensive discovery engine that scrapes multiple sources:
    - GitHub repositories (trending, search)
    - GitLab projects
    - Maven Central (Java packages)
    - NPM (JavaScript packages)
    - PyPI (Python packages)
    - MCP Servers (Model Context Protocol)
    - FOSS directories (Sourceforge, etc.)
    - Eclipse Marketplace
    - Netbeans plugins
    """
    
    def __init__(self):
        self.sources = {
            'github': 'https://github.com',
            'gitlab': 'https://gitlab.com',
            'npm': 'https://www.npmjs.com',
            'pypi': 'https://pypi.org',
            'maven': 'https://search.maven.org',
            'sourceforge': 'https://sourceforge.net',
            'mcp_servers': 'https://github.com/topics/mcp-server',
            'eclipse': 'https://marketplace.eclipse.org',
            'cloudflare_workers': 'https://github.com/topics/cloudflare-workers'
        }
        
    async def discover_all_sources(self) -> Dict[str, Any]:
        """Run comprehensive discovery across all sources"""
        logger.info("🔍 Starting MEGA Discovery Engine...")
        
        results = {
            'started_at': datetime.now(timezone.utc).isoformat(),
            'sources': {},
            'total_discovered': 0
        }
        
        # Discover from each source in parallel
        tasks = [
            self.discover_github_ai_tools(),
            self.discover_gitlab_projects(),
            self.discover_npm_ai_packages(),
            self.discover_pypi_ai_packages(),
            self.discover_mcp_servers(),
            self.discover_cloudflare_workers(),
            self.discover_maven_ai_libs(),
            self.discover_eclipse_ai_plugins()
        ]
        
        discoveries = await asyncio.gather(*tasks, return_exceptions=True)
        
        source_names = ['github', 'gitlab', 'npm', 'pypi', 'mcp_servers', 'cloudflare', 'maven', 'eclipse']
        
        for i, discovery in enumerate(discoveries):
            if isinstance(discovery, Exception):
                logger.error(f"Failed to discover from {source_names[i]}: {discovery}")
                results['sources'][source_names[i]] = {'error': str(discovery), 'count': 0}
            else:
                results['sources'][source_names[i]] = discovery
                # Count from various possible keys
                count = discovery.get('count', 0)
                if count == 0:
                    # Try alternative keys
                    if 'tools' in discovery:
                        count = len(discovery.get('tools', []))
                    elif 'projects' in discovery:
                        count = len(discovery.get('projects', []))
                    elif 'packages' in discovery:
                        count = len(discovery.get('packages', []))
                    elif 'workers' in discovery:
                        count = len(discovery.get('workers', []))
                    elif 'servers' in discovery:
                        count = len(discovery.get('servers', []))
                results['total_discovered'] += count
        
        results['completed_at'] = datetime.now(timezone.utc).isoformat()
        logger.info(f"✅ MEGA Discovery complete: {results['total_discovered']} tools found")
        
        return results
    
    async def discover_github_ai_tools(self) -> Dict[str, Any]:
        """Discover AI tools from GitHub"""
        logger.info("🔍 Scanning GitHub for AI tools...")
        
        tools = []
        topics = [
            'ai-agent', 'artificial-intelligence', 'machine-learning',
            'llm', 'chatbot', 'ai-tools', 'generative-ai',
            'image-generation', 'voice-synthesis', 'video-generation',
            'mcp-server', 'ai-integration', 'automation'
        ]
        
        try:
            async with aiohttp.ClientSession() as session:
                for topic in topics[:5]:  # Limit to avoid rate limits
                    url = f"https://github.com/topics/{topic}"
                    
                    try:
                        async with session.get(url, timeout=10) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                # Find repository cards
                                repo_links = soup.find_all('a', href=re.compile(r'^/[^/]+/[^/]+$'))
                                
                                for link in repo_links[:20]:
                                    repo_name = link.get('href', '').strip('/')
                                    if repo_name and '/' in repo_name:
                                        tools.append({
                                            'name': repo_name.split('/')[-1],
                                            'full_name': repo_name,
                                            'url': f"https://github.com/{repo_name}",
                                            'source': 'github',
                                            'topic': topic
                                        })
                        
                        await asyncio.sleep(1)  # Rate limiting
                    except Exception as e:
                        logger.error(f"Failed to scan topic {topic}: {e}")
                        continue
            
            # Deduplicate
            unique_tools = {tool['full_name']: tool for tool in tools}
            tools = list(unique_tools.values())
            
            logger.info(f"✓ Discovered {len(tools)} tools from GitHub")
            return {
                'count': len(tools),
                'tools': tools[:50],  # Limit response size
                'topics_scanned': len(topics[:5])
            }
            
        except Exception as e:
            logger.error(f"GitHub discovery failed: {e}")
            return {'count': 0, 'error': str(e)}
    
    async def discover_gitlab_projects(self) -> Dict[str, Any]:
        """Discover AI projects from GitLab"""
        logger.info("🔍 Scanning GitLab for AI projects...")
        
        try:
            projects = []
            async with aiohttp.ClientSession() as session:
                # Search for AI-related projects
                search_terms = ['ai-agent', 'llm', 'artificial-intelligence']
                
                for term in search_terms:
                    url = f"https://gitlab.com/explore/projects?topic={term}"
                    
                    try:
                        async with session.get(url, timeout=10) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                # Extract project links
                                project_links = soup.find_all('a', class_=re.compile(r'project'))
                                
                                for link in project_links[:15]:
                                    href = link.get('href', '')
                                    if href and href.startswith('/'):
                                        projects.append({
                                            'name': href.split('/')[-1],
                                            'url': f"https://gitlab.com{href}",
                                            'source': 'gitlab',
                                            'search_term': term
                                        })
                        
                        await asyncio.sleep(1)
                    except Exception as e:
                        logger.error(f"Failed to scan GitLab term {term}: {e}")
                        continue
            
            # Deduplicate
            unique = {p['url']: p for p in projects}
            projects = list(unique.values())
            
            logger.info(f"✓ Discovered {len(projects)} projects from GitLab")
            return {'count': len(projects), 'projects': projects[:30]}
            
        except Exception as e:
            logger.error(f"GitLab discovery failed: {e}")
            return {'count': 0, 'error': str(e)}
    
    async def discover_npm_ai_packages(self) -> Dict[str, Any]:
        """Discover AI packages from NPM"""
        logger.info("🔍 Scanning NPM for AI packages...")
        
        try:
            packages = []
            keywords = ['ai', 'artificial-intelligence', 'machine-learning', 'llm', 'chatbot']
            
            async with aiohttp.ClientSession() as session:
                for keyword in keywords[:3]:
                    url = f"https://www.npmjs.com/search?q={keyword}"
                    
                    try:
                        async with session.get(url, timeout=10) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                # Find package names
                                package_links = soup.find_all('a', href=re.compile(r'^/package/'))
                                
                                for link in package_links[:20]:
                                    pkg_name = link.get('href', '').replace('/package/', '')
                                    if pkg_name:
                                        packages.append({
                                            'name': pkg_name,
                                            'url': f"https://www.npmjs.com/package/{pkg_name}",
                                            'source': 'npm',
                                            'type': 'javascript'
                                        })
                        
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        logger.error(f"Failed NPM search for {keyword}: {e}")
                        continue
            
            unique = {p['name']: p for p in packages}
            packages = list(unique.values())
            
            logger.info(f"✓ Discovered {len(packages)} packages from NPM")
            return {'count': len(packages), 'packages': packages[:30]}
            
        except Exception as e:
            logger.error(f"NPM discovery failed: {e}")
            return {'count': 0, 'error': str(e)}
    
    async def discover_pypi_ai_packages(self) -> Dict[str, Any]:
        """Discover AI packages from PyPI"""
        logger.info("🔍 Scanning PyPI for AI packages...")
        
        try:
            packages = []
            keywords = ['artificial-intelligence', 'machine-learning', 'llm', 'ai-agent']
            
            async with aiohttp.ClientSession() as session:
                for keyword in keywords[:3]:
                    url = f"https://pypi.org/search/?q={keyword}"
                    
                    try:
                        async with session.get(url, timeout=10) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                # Find package names
                                pkg_links = soup.find_all('a', class_='package-snippet')
                                
                                for link in pkg_links[:20]:
                                    pkg_name = link.find('span', class_='package-snippet__name')
                                    if pkg_name:
                                        name = pkg_name.text.strip()
                                        packages.append({
                                            'name': name,
                                            'url': f"https://pypi.org/project/{name}",
                                            'source': 'pypi',
                                            'type': 'python'
                                        })
                        
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        logger.error(f"Failed PyPI search for {keyword}: {e}")
                        continue
            
            unique = {p['name']: p for p in packages}
            packages = list(unique.values())
            
            logger.info(f"✓ Discovered {len(packages)} packages from PyPI")
            return {'count': len(packages), 'packages': packages[:30]}
            
        except Exception as e:
            logger.error(f"PyPI discovery failed: {e}")
            return {'count': 0, 'error': str(e)}
    
    async def discover_mcp_servers(self) -> Dict[str, Any]:
        """Discover MCP (Model Context Protocol) servers"""
        logger.info("🔍 Scanning for MCP servers...")
        
        try:
            servers = []
            async with aiohttp.ClientSession() as session:
                url = "https://github.com/topics/mcp-server"
                
                async with session.get(url, timeout=15) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        repo_links = soup.find_all('a', href=re.compile(r'^/[^/]+/[^/]+$'))
                        
                        for link in repo_links[:30]:
                            repo = link.get('href', '').strip('/')
                            if repo and 'mcp' in repo.lower():
                                servers.append({
                                    'name': repo.split('/')[-1],
                                    'full_name': repo,
                                    'url': f"https://github.com/{repo}",
                                    'source': 'mcp_server',
                                    'type': 'integration'
                                })
            
            unique = {s['full_name']: s for s in servers}
            servers = list(unique.values())
            
            logger.info(f"✓ Discovered {len(servers)} MCP servers")
            return {'count': len(servers), 'servers': servers}
            
        except Exception as e:
            logger.error(f"MCP server discovery failed: {e}")
            return {'count': 0, 'error': str(e)}
    
    async def discover_cloudflare_workers(self) -> Dict[str, Any]:
        """Discover Cloudflare Workers templates and tools"""
        logger.info("🔍 Scanning for Cloudflare Workers...")
        
        try:
            workers = []
            async with aiohttp.ClientSession() as session:
                url = "https://github.com/topics/cloudflare-workers"
                
                async with session.get(url, timeout=15) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        repo_links = soup.find_all('a', href=re.compile(r'^/[^/]+/[^/]+$'))
                        
                        for link in repo_links[:25]:
                            repo = link.get('href', '').strip('/')
                            if repo and '/' in repo:
                                workers.append({
                                    'name': repo.split('/')[-1],
                                    'full_name': repo,
                                    'url': f"https://github.com/{repo}",
                                    'source': 'cloudflare_workers',
                                    'type': 'edge_function'
                                })
            
            unique = {w['full_name']: w for w in workers}
            workers = list(unique.values())
            
            logger.info(f"✓ Discovered {len(workers)} Cloudflare Workers")
            return {'count': len(workers), 'workers': workers}
            
        except Exception as e:
            logger.error(f"Cloudflare Workers discovery failed: {e}")
            return {'count': 0, 'error': str(e)}
    
    async def discover_maven_ai_libs(self) -> Dict[str, Any]:
        """Discover AI libraries from Maven Central"""
        logger.info("🔍 Scanning Maven Central for AI libraries...")
        
        try:
            libraries = []
            keywords = ['artificial-intelligence', 'machine-learning', 'neural-network']
            
            async with aiohttp.ClientSession() as session:
                for keyword in keywords[:2]:
                    url = f"https://search.maven.org/search?q={keyword}"
                    
                    try:
                        async with session.get(url, timeout=10) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                # Extract library names (simplified parsing)
                                links = soup.find_all('a', href=re.compile(r'/artifact/'))
                                
                                for link in links[:15]:
                                    text = link.text.strip()
                                    if text and 'ai' in text.lower():
                                        libraries.append({
                                            'name': text,
                                            'url': f"https://search.maven.org{link.get('href', '')}",
                                            'source': 'maven',
                                            'type': 'java_library'
                                        })
                        
                        await asyncio.sleep(1)
                    except Exception as e:
                        logger.error(f"Maven search failed for {keyword}: {e}")
                        continue
            
            logger.info(f"✓ Discovered {len(libraries)} libraries from Maven")
            return {'count': len(libraries), 'libraries': libraries}
            
        except Exception as e:
            logger.error(f"Maven discovery failed: {e}")
            return {'count': 0, 'error': str(e)}
    
    async def discover_eclipse_ai_plugins(self) -> Dict[str, Any]:
        """Discover AI plugins from Eclipse Marketplace"""
        logger.info("🔍 Scanning Eclipse Marketplace...")
        
        try:
            plugins = []
            url = "https://marketplace.eclipse.org/search/site/ai"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Find plugin listings
                        plugin_links = soup.find_all('a', href=re.compile(r'/content/'))
                        
                        for link in plugin_links[:20]:
                            name = link.text.strip()
                            if name and len(name) > 3:
                                plugins.append({
                                    'name': name,
                                    'url': f"https://marketplace.eclipse.org{link.get('href', '')}",
                                    'source': 'eclipse',
                                    'type': 'ide_plugin'
                                })
            
            logger.info(f"✓ Discovered {len(plugins)} plugins from Eclipse")
            return {'count': len(plugins), 'plugins': plugins}
            
        except Exception as e:
            logger.error(f"Eclipse discovery failed: {e}")
            return {'count': 0, 'error': str(e)}

mega_discovery_engine = MegaDiscoveryEngine()
