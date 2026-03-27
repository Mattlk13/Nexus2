"""
Script to automatically refactor server.py into modular routers
"""
import re
from pathlib import Path

def extract_route_sections():
    """Extract route sections from server.py"""
    server_file = Path("/app/backend/server.py")
    content = server_file.read_text()
    
    # Define route sections and their patterns
    sections = {
        "auth": {
            "start": "# ==================== AUTH ROUTES ====================",
            "routes": ["/auth/register", "/auth/login", "/auth/me"]
        },
        "notifications": {
            "start": "# ==================== NOTIFICATION ROUTES ====================",
            "routes": ["/notifications"]
        },
        "users": {
            "start": "# ==================== USER PROFILE ROUTES ====================",
            "routes": ["/users/"]
        },
        "products": {
            "start": "# ==================== PRODUCTS ROUTES ====================",
            "routes": ["/products", "/categories", "/trending"]
        },
        "purchases": {
            "start": "# ==================== PRODUCT PURCHASE ROUTES ====================",
            "routes": ["/checkout", "/purchase"]
        },
        "vendor": {
            "start": "# ==================== VENDOR ANALYTICS ROUTES ====================",
            "routes": ["/vendor/"]
        },
        "social": {
            "start": "# ==================== POSTS ROUTES ====================",
            "routes": ["/posts"]
        },
        "studio": {
            "start": "# ==================== AI GENERATION ROUTES ====================",
            "routes": ["/ai/generate", "/ai/chat", "/studio/"]
        },
        "agents": {
            "start": "# ==================== AI AGENTS ROUTES ====================",
            "routes": ["/agents"]
        },
        "admin": {
            "start": "# ==================== ADMIN",
            "routes": ["/admin/"]
        }
    }
    
    # Find line numbers for each section
    lines = content.split('\n')
    section_ranges = {}
    
    for name, info in sections.items():
        try:
            start_idx = next(i for i, line in enumerate(lines) if info["start"] in line)
            # Find next section or end
            next_section_idx = len(lines)
            for i in range(start_idx + 1, len(lines)):
                if "# ==================== " in lines[i] and "ROUTES" in lines[i]:
                    next_section_idx = i
                    break
            
            section_ranges[name] = (start_idx, next_section_idx)
            print(f"✓ Found {name}: lines {start_idx}-{next_section_idx}")
        except StopIteration:
            print(f"✗ Could not find section: {name}")
    
    return section_ranges, lines

if __name__ == "__main__":
    ranges, lines = extract_route_sections()
    print(f"\n📊 Total sections found: {len(ranges)}")
    print(f"📄 Total lines in server.py: {len(lines)}")
