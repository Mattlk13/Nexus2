import requests
import sys
import time
from datetime import datetime

class NexusAPITester:
    def __init__(self, base_url="https://model-exchange-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api = f"{self.base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api}/{endpoint}" if endpoint else f"{self.api}/"
        default_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            default_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            default_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    json_response = response.json()
                    if isinstance(json_response, list) and len(json_response) > 0:
                        print(f"   Response: List with {len(json_response)} items")
                    elif isinstance(json_response, dict):
                        key_count = len(json_response.keys())
                        print(f"   Response: Dict with {key_count} keys")
                    return success, json_response
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Raw error: {response.text[:200]}")

            return success, response.json() if response.text else {}

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed - Network Error: {str(e)}")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_auth_flow(self):
        """Test complete authentication flow"""
        print("\n" + "="*50)
        print("TESTING AUTHENTICATION FLOW")
        print("="*50)
        
        # Test registration
        timestamp = int(time.time())
        test_email = f"test_user_{timestamp}@nexus.com"
        test_password = "TestPass123!"
        test_username = f"testuser_{timestamp}"
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={
                "email": test_email,
                "password": test_password,
                "username": test_username
            }
        )
        
        if success and response.get('token'):
            self.token = response['token']
            self.user_id = response.get('user', {}).get('id')
            print(f"   Registered user: {test_username}")
            
            # Test login with same credentials
            success, login_response = self.run_test(
                "User Login",
                "POST",
                "auth/login",
                200,
                data={
                    "email": test_email,
                    "password": test_password
                }
            )
            
            # Test /auth/me endpoint
            self.run_test(
                "Get Current User",
                "GET",
                "auth/me",
                200
            )
            
            return True
        else:
            print("❌ Registration failed, skipping rest of auth tests")
            return False

    def test_basic_endpoints(self):
        """Test basic API endpoints"""
        print("\n" + "="*50)
        print("TESTING BASIC ENDPOINTS")
        print("="*50)
        
        # Root API endpoint
        self.run_test("API Root", "GET", "", 200)
        
        # Health check
        self.run_test("Health Check", "GET", "health", 200)
        
        # Stats endpoint
        self.run_test("Stats", "GET", "stats", 200)
        
        # Categories endpoint
        self.run_test("Categories", "GET", "categories", 200)
        
        # Trending endpoint
        self.run_test("Trending Products", "GET", "trending", 200)
        
        # AI Agents endpoint
        self.run_test("AI Agents", "GET", "agents", 200)

    def test_products_flow(self):
        """Test products endpoints"""
        print("\n" + "="*50)
        print("TESTING PRODUCTS FLOW")
        print("="*50)
        
        # Get all products
        success, products = self.run_test("Get All Products", "GET", "products", 200)
        
        # Get products by category
        self.run_test("Get Products by Category", "GET", "products?category=music", 200)
        
        # Search products
        self.run_test("Search Products", "GET", "products?search=ai", 200)
        
        if self.token:
            # Create a product
            product_data = {
                "title": "Test AI Music Track",
                "description": "A test music track generated by AI",
                "price": 9.99,
                "category": "music",
                "is_ai_generated": True,
                "tags": ["ai", "music", "test"]
            }
            
            success, product_response = self.run_test(
                "Create Product",
                "POST",
                "products",
                200,
                data=product_data
            )
            
            if success and product_response.get('id'):
                product_id = product_response['id']
                
                # Get specific product
                self.run_test(f"Get Product {product_id}", "GET", f"products/{product_id}", 200)
                
                # Like product
                self.run_test(f"Like Product {product_id}", "POST", f"products/{product_id}/like", 200)

    def test_posts_flow(self):
        """Test social posts endpoints"""
        print("\n" + "="*50)
        print("TESTING SOCIAL POSTS FLOW")
        print("="*50)
        
        # Get all posts
        self.run_test("Get All Posts", "GET", "posts", 200)
        
        if self.token:
            # Create a post
            post_data = {
                "content": "Testing NEXUS platform! This is amazing! 🚀",
                "post_type": "text"
            }
            
            success, post_response = self.run_test(
                "Create Post",
                "POST",
                "posts",
                200,
                data=post_data
            )
            
            if success and post_response.get('id'):
                post_id = post_response['id']
                
                # Like post
                self.run_test(f"Like Post {post_id}", "POST", f"posts/{post_id}/like", 200)
                
                # Comment on post
                comment_data = {
                    "content": "Great post!",
                    "post_id": post_id
                }
                
                self.run_test(f"Comment on Post {post_id}", "POST", f"posts/{post_id}/comment", 200, data=comment_data)
                
                # Get comments
                self.run_test(f"Get Comments for Post {post_id}", "GET", f"posts/{post_id}/comments", 200)

    def test_ai_generation(self):
        """Test AI content generation"""
        print("\n" + "="*50)
        print("TESTING AI GENERATION")
        print("="*50)
        
        if not self.token:
            print("❌ Skipping AI tests - no authentication token")
            return
            
        ai_requests = [
            {
                "name": "AI Text Generation",
                "data": {
                    "prompt": "Write a short story about AI creativity",
                    "content_type": "text"
                }
            },
            {
                "name": "AI Music Generation",
                "data": {
                    "prompt": "Create a upbeat electronic music track",
                    "content_type": "music"
                }
            },
            {
                "name": "AI eBook Generation",
                "data": {
                    "prompt": "A guide to prompt engineering",
                    "content_type": "ebook"
                }
            }
        ]
        
        for ai_request in ai_requests:
            print(f"\n🤖 Testing {ai_request['name']}...")
            try:
                success, response = self.run_test(
                    ai_request['name'],
                    "POST",
                    "ai/generate",
                    200,
                    data=ai_request['data']
                )
                
                if success and response.get('result'):
                    print(f"   Generated content preview: {response['result'][:100]}...")
                
                # Add delay between AI requests
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ AI Generation failed: {str(e)}")

    def test_vendors_flow(self):
        """Test vendor endpoints"""
        print("\n" + "="*50)
        print("TESTING VENDORS FLOW")
        print("="*50)
        
        # Get all vendors
        self.run_test("Get All Vendors", "GET", "vendors", 200)
        
        if self.token:
            # Create vendor
            vendor_data = {
                "shop_name": "Test AI Shop",
                "description": "A test shop for AI-generated content",
                "category": "digital"
            }
            
            success, vendor_response = self.run_test(
                "Create Vendor",
                "POST",
                "vendors",
                200,
                data=vendor_data
            )
            
            if success and vendor_response.get('id'):
                vendor_id = vendor_response['id']
                
                # Get specific vendor
                self.run_test(f"Get Vendor {vendor_id}", "GET", f"vendors/{vendor_id}", 200)
                
                # Get vendor products
                self.run_test(f"Get Vendor Products {vendor_id}", "GET", f"vendors/{vendor_id}/products", 200)

    def test_spotlight_flow(self):
        """Test spotlight endpoints"""
        print("\n" + "="*50)
        print("TESTING SPOTLIGHT FLOW")
        print("="*50)
        
        # Get spotlight entries
        success, spotlight = self.run_test("Get Spotlight Entries", "GET", "spotlight", 200)
        
        if success and spotlight and len(spotlight) > 0:
            content_id = spotlight[0].get('content_id')
            if content_id and self.token:
                # Vote on spotlight entry
                self.run_test(f"Vote on Spotlight {content_id}", "POST", f"spotlight/{content_id}/vote", 200)

    def test_boost_flow(self):
        """Test Featured Listing boost functionality"""
        print("\n" + "="*50)
        print("TESTING FEATURED LISTING BOOST FLOW")
        print("="*50)
        
        # Test 1: Get boost packages (should work without auth)
        success, packages = self.run_test("Get Boost Packages", "GET", "boost/packages", 200)
        
        if success and packages:
            print(f"   Found {len(packages)} boost packages")
            # Verify package structure
            expected_packages = ["basic", "standard", "premium"]
            found_packages = [pkg.get('id') for pkg in packages]
            
            for expected in expected_packages:
                if expected in found_packages:
                    pkg = next(p for p in packages if p.get('id') == expected)
                    print(f"   ✅ {expected.title()} package: ${pkg.get('price')} for {pkg.get('days')} days")
                else:
                    print(f"   ❌ Missing {expected} package")
        
        if not self.token:
            print("❌ Skipping authenticated boost tests - no token")
            return
            
        # Test 2: Create a product first (needed for boost)
        product_data = {
            "title": "Test Boost Product",
            "description": "A product to test boost functionality",
            "price": 19.99,
            "category": "music",
            "is_ai_generated": True,
            "tags": ["test", "boost"]
        }
        
        success, product_response = self.run_test(
            "Create Product for Boost Test",
            "POST",
            "products",
            200,
            data=product_data
        )
        
        if not success or not product_response.get('id'):
            print("❌ Failed to create product for boost test")
            return
            
        product_id = product_response['id']
        print(f"   Created test product: {product_id}")
        
        # Test 3: Create boost checkout session
        checkout_data = {
            "product_id": product_id,
            "package_id": "basic",
            "origin_url": "https://model-exchange-2.preview.emergentagent.com"
        }
        
        success, checkout_response = self.run_test(
            "Create Boost Checkout Session",
            "POST",
            "boost/checkout",
            200,
            data=checkout_data
        )
        
        if success and checkout_response.get('session_id'):
            session_id = checkout_response['session_id']
            print(f"   Created checkout session: {session_id}")
            print(f"   Checkout URL: {checkout_response.get('checkout_url', 'N/A')}")
            
            # Test 4: Check payment status
            success, status_response = self.run_test(
                f"Check Boost Payment Status",
                "GET",
                f"boost/status/{session_id}",
                200
            )
            
            if success:
                print(f"   Payment status: {status_response.get('payment_status', 'unknown')}")
                print(f"   Session status: {status_response.get('status', 'unknown')}")
        
        # Test 5: Get user's boosts (if any)
        self.run_test("Get My Boosts", "GET", "boost/my-boosts", 200)

def main():
    print("🚀 Starting NEXUS API Testing Suite")
    print("=" * 60)
    
    tester = NexusAPITester()
    
    # Run all test suites
    auth_success = tester.test_auth_flow()
    tester.test_basic_endpoints()
    tester.test_products_flow()
    tester.test_posts_flow() 
    tester.test_vendors_flow()
    tester.test_spotlight_flow()
    tester.test_boost_flow()  # Test Featured Listing boost functionality
    
    if auth_success:
        tester.test_ai_generation()
    
    # Final results
    print("\n" + "="*60)
    print(f"📊 TEST RESULTS")
    print("="*60)
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Backend API is working well!")
        return 0
    elif success_rate >= 50:
        print("⚠️  Backend API has some issues but core functionality works")
        return 1
    else:
        print("❌ Backend API has major issues")
        return 2

if __name__ == "__main__":
    sys.exit(main())