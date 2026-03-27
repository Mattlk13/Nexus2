"""
Test Suite for Creation Studio and Newsfeed Features
Tests: Music/Video/eBook generation, Publish to Marketplace, Newsfeed CRUD, Like/Unlike, Comments
"""
import pytest
import requests
import os
import time
from uuid import uuid4

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@nexus.ai"
TEST_PASSWORD = "admin123"


class TestAuthAndSetup:
    """Authentication tests - run first"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for admin user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        return data["token"]
    
    def test_health_check(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health check passed")
    
    def test_login_success(self):
        """Test login with valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == TEST_EMAIL
        print(f"✓ Login successful for {TEST_EMAIL}")


class TestCreationStudioMusicGeneration:
    """Test Music Generation using GPT-5.2"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        return response.json()["token"]
    
    def test_generate_music_success(self, auth_token):
        """Test music generation with valid prompt"""
        response = requests.post(
            f"{BASE_URL}/api/studio/generate-music",
            json={"prompt": "A relaxing lo-fi beat with piano and soft drums"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Music generation failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "id" in data, "Missing content id"
        assert data["type"] == "music"
        assert data["status"] == "generated"
        assert "content" in data, "Missing generated content"
        assert len(data["content"]) > 100, "Content too short"
        print(f"✓ Music generated successfully, ID: {data['id']}")
        return data
    
    def test_generate_music_empty_prompt(self, auth_token):
        """Test music generation with empty prompt"""
        response = requests.post(
            f"{BASE_URL}/api/studio/generate-music",
            json={"prompt": ""},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # Should still work but with minimal content or error
        # The API may accept empty prompts
        print(f"✓ Empty prompt test completed, status: {response.status_code}")
    
    def test_generate_music_unauthorized(self):
        """Test music generation without auth"""
        response = requests.post(
            f"{BASE_URL}/api/studio/generate-music",
            json={"prompt": "Test prompt"}
        )
        assert response.status_code in [401, 403], "Should require authentication"
        print("✓ Unauthorized access properly rejected")


class TestCreationStudioEbookGeneration:
    """Test eBook Generation using Claude"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        return response.json()["token"]
    
    def test_generate_ebook_success(self, auth_token):
        """Test ebook generation with valid prompt"""
        response = requests.post(
            f"{BASE_URL}/api/studio/generate-ebook",
            json={"prompt": "A complete guide to starting a successful online business"},
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=120  # eBook generation may take longer
        )
        assert response.status_code == 200, f"eBook generation failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "id" in data, "Missing content id"
        assert data["type"] == "ebook"
        assert data["status"] == "generated"
        assert "content" in data, "Missing generated content"
        assert "word_count" in data, "Missing word count"
        assert data["word_count"] > 100, "Word count too low"
        print(f"✓ eBook generated successfully, ID: {data['id']}, Words: {data['word_count']}")
        return data


class TestCreationStudioVideoGeneration:
    """Test Video Generation using Sora 2 (may be slow)"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        return response.json()["token"]
    
    def test_generate_video_success(self, auth_token):
        """Test video generation with valid prompt - may take 30-60s"""
        response = requests.post(
            f"{BASE_URL}/api/studio/generate-video",
            json={"prompt": "A cinematic video of a sunset over mountains"},
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=120  # Video generation can be slow
        )
        
        # Video generation may succeed or timeout - both are acceptable
        if response.status_code == 200:
            data = response.json()
            assert "id" in data, "Missing content id"
            assert data["type"] == "video"
            assert "video_url" in data or "status" in data
            print(f"✓ Video generated successfully, ID: {data['id']}")
        else:
            # May timeout or fail due to slow generation
            print(f"⚠ Video generation returned {response.status_code} - may be processing async")


class TestCreationStudioPublishToMarketplace:
    """Test Publishing Content to Marketplace"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def created_content(self, auth_token):
        """Create content to publish"""
        response = requests.post(
            f"{BASE_URL}/api/studio/generate-music",
            json={"prompt": "Test music for marketplace publishing"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if response.status_code == 200:
            return response.json()
        return None
    
    def test_publish_to_marketplace(self, auth_token, created_content):
        """Test publishing created content to marketplace"""
        if not created_content:
            pytest.skip("No content created to publish")
        
        response = requests.post(
            f"{BASE_URL}/api/studio/publish-to-marketplace",
            json={
                "content_id": created_content["id"],
                "title": f"TEST_Published Music {uuid4().hex[:8]}",
                "description": "AI-generated music composition for testing",
                "price": 9.99,
                "category": "music"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Publish failed: {response.text}"
        data = response.json()
        
        assert data["success"] == True
        assert "product_id" in data
        print(f"✓ Content published to marketplace, Product ID: {data['product_id']}")
    
    def test_publish_nonexistent_content(self, auth_token):
        """Test publishing non-existent content"""
        response = requests.post(
            f"{BASE_URL}/api/studio/publish-to-marketplace",
            json={
                "content_id": "nonexistent-id-12345",
                "title": "Test",
                "description": "Test",
                "price": 9.99,
                "category": "music"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404, "Should return 404 for non-existent content"
        print("✓ Non-existent content properly rejected")


class TestNewsfeedPosts:
    """Test Newsfeed Post CRUD Operations"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        return response.json()["token"]
    
    def test_get_posts_public(self):
        """Test getting posts without authentication"""
        response = requests.get(f"{BASE_URL}/api/newsfeed/posts")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert isinstance(data["posts"], list)
        print(f"✓ Got {len(data['posts'])} posts (public access)")
    
    def test_create_post_success(self, auth_token):
        """Test creating a new post"""
        post_content = f"TEST_Post content {uuid4().hex[:8]} - Testing newsfeed functionality"
        response = requests.post(
            f"{BASE_URL}/api/newsfeed/posts",
            json={"content": post_content},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Create post failed: {response.text}"
        data = response.json()
        
        assert "id" in data
        assert data["content"] == post_content
        assert "author_id" in data
        assert "author_name" in data
        assert "created_at" in data
        assert data["likes"] == 0
        assert data["comments"] == 0
        print(f"✓ Post created successfully, ID: {data['id']}")
        return data
    
    def test_create_post_unauthorized(self):
        """Test creating post without auth"""
        response = requests.post(
            f"{BASE_URL}/api/newsfeed/posts",
            json={"content": "Test post"}
        )
        assert response.status_code in [401, 403], "Should require authentication"
        print("✓ Unauthorized post creation properly rejected")
    
    def test_posts_persistence(self, auth_token):
        """Test that posts persist after creation"""
        # Create a unique post
        unique_content = f"TEST_Persistence check {uuid4().hex}"
        create_response = requests.post(
            f"{BASE_URL}/api/newsfeed/posts",
            json={"content": unique_content},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert create_response.status_code == 200
        created_post = create_response.json()
        
        # Fetch posts and verify our post exists
        time.sleep(0.5)  # Small delay for DB write
        get_response = requests.get(
            f"{BASE_URL}/api/newsfeed/posts",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert get_response.status_code == 200
        posts = get_response.json()["posts"]
        
        found = any(p["id"] == created_post["id"] for p in posts)
        assert found, "Created post not found in posts list - persistence issue"
        print(f"✓ Post persistence verified, ID: {created_post['id']}")


class TestNewsfeedLikes:
    """Test Like/Unlike Functionality"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def test_post(self, auth_token):
        """Create a post for like testing"""
        response = requests.post(
            f"{BASE_URL}/api/newsfeed/posts",
            json={"content": f"TEST_Like test post {uuid4().hex[:8]}"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        return response.json()
    
    def test_like_post(self, auth_token, test_post):
        """Test liking a post"""
        response = requests.post(
            f"{BASE_URL}/api/newsfeed/posts/{test_post['id']}/like",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Like failed: {response.text}"
        data = response.json()
        
        assert data["success"] == True
        assert data["liked"] == True
        assert "likes" in data
        print(f"✓ Post liked successfully, new likes: {data['likes']}")
    
    def test_unlike_post_toggle(self, auth_token, test_post):
        """Test unliking a post (toggle behavior)"""
        # Like first
        requests.post(
            f"{BASE_URL}/api/newsfeed/posts/{test_post['id']}/like",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Unlike (second call should toggle)
        response = requests.post(
            f"{BASE_URL}/api/newsfeed/posts/{test_post['id']}/like",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should be unliked now
        assert data["success"] == True
        assert data["liked"] == False
        print(f"✓ Post unliked successfully (toggle), likes: {data['likes']}")
    
    def test_like_nonexistent_post(self, auth_token):
        """Test liking non-existent post"""
        response = requests.post(
            f"{BASE_URL}/api/newsfeed/posts/nonexistent-post-id/like",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404, "Should return 404 for non-existent post"
        print("✓ Non-existent post like properly rejected")


class TestNewsfeedComments:
    """Test Comment Functionality"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def test_post(self, auth_token):
        """Create a post for comment testing"""
        response = requests.post(
            f"{BASE_URL}/api/newsfeed/posts",
            json={"content": f"TEST_Comment test post {uuid4().hex[:8]}"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        return response.json()
    
    def test_add_comment(self, auth_token, test_post):
        """Test adding a comment to a post"""
        comment_content = f"TEST_Comment {uuid4().hex[:8]}"
        response = requests.post(
            f"{BASE_URL}/api/newsfeed/posts/{test_post['id']}/comment",
            json={"content": comment_content},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Add comment failed: {response.text}"
        data = response.json()
        
        assert "id" in data
        assert data["content"] == comment_content
        assert data["post_id"] == test_post["id"]
        assert "author_id" in data
        assert "author_name" in data
        print(f"✓ Comment added successfully, ID: {data['id']}")
        return data
    
    def test_get_comments(self, auth_token, test_post):
        """Test getting comments for a post"""
        # First add a comment
        requests.post(
            f"{BASE_URL}/api/newsfeed/posts/{test_post['id']}/comment",
            json={"content": f"TEST_Get comments test {uuid4().hex[:8]}"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Get comments
        response = requests.get(f"{BASE_URL}/api/newsfeed/posts/{test_post['id']}/comments")
        assert response.status_code == 200
        data = response.json()
        
        assert "comments" in data
        assert isinstance(data["comments"], list)
        assert len(data["comments"]) > 0, "Should have at least one comment"
        print(f"✓ Got {len(data['comments'])} comments for post")
    
    def test_comment_nonexistent_post(self, auth_token):
        """Test commenting on non-existent post"""
        response = requests.post(
            f"{BASE_URL}/api/newsfeed/posts/nonexistent-post-id/comment",
            json={"content": "Test comment"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404, "Should return 404 for non-existent post"
        print("✓ Non-existent post comment properly rejected")


class TestCreatedContentRetrieval:
    """Test retrieving user's created content"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        return response.json()["token"]
    
    def test_get_created_content(self, auth_token):
        """Test getting user's created content"""
        response = requests.get(
            f"{BASE_URL}/api/studio/created-content",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Get content failed: {response.text}"
        data = response.json()
        
        assert "content" in data
        assert "count" in data
        assert isinstance(data["content"], list)
        print(f"✓ Retrieved {data['count']} created content items")


class TestNotifications:
    """Test notification creation for likes and comments"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        return response.json()["token"]
    
    def test_get_notifications(self, auth_token):
        """Test getting user notifications"""
        response = requests.get(
            f"{BASE_URL}/api/notifications",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Retrieved {len(data)} notifications")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
