import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient, ASGITransport
from app.app import app
from app.db import create_db_and_tables


@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_database():
    """Ensure database tables exist before running test suite."""
    await create_db_and_tables()
    yield


@pytest.fixture
def client_transport():
    """Create ASGI transport for httpx.AsyncClient."""
    return ASGITransport(app=app)


@pytest.mark.asyncio
async def test_register_user(client_transport):
    """Test user registration endpoint with valid credentials."""
    unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePassword123!"

    async with AsyncClient(transport=client_transport, base_url="http://test") as ac:
        response = await ac.post(
            "/auth/register",
            json={"email": unique_email, "password": password}
        )

    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["email"] == unique_email
    assert "id" in data
    assert "hashed_password" not in data  # Ensure password is not exposed


@pytest.mark.asyncio
async def test_login_user(client_transport):
    """Test login endpoint returning JWT bearer token."""
    unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePassword123!"

    async with AsyncClient(transport=client_transport, base_url="http://test") as ac:
        # Register user first
        reg_response = await ac.post(
            "/auth/register",
            json={"email": unique_email, "password": password}
        )
        assert reg_response.status_code == 201

        # Attempt login
        login_response = await ac.post(
            "/auth/jwt/login",
            data={"username": unique_email, "password": password}
        )

    assert login_response.status_code == 200, f"Expected 200, got {login_response.status_code}"
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_feed_retrieval_authenticated(client_transport):
    """Test authenticated retrieval of posts feed."""
    unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePassword123!"

    async with AsyncClient(transport=client_transport, base_url="http://test") as ac:
        # Register and login to obtain JWT token
        await ac.post(
            "/auth/register",
            json={"email": unique_email, "password": password}
        )
        login_res = await ac.post(
            "/auth/jwt/login",
            data={"username": unique_email, "password": password}
        )
        token = login_res.json()["access_token"]

        # Fetch feed
        feed_response = await ac.get(
            "/feed",
            headers={"Authorization": f"Bearer {token}"}
        )

    assert feed_response.status_code == 200
    feed_data = feed_response.json()
    assert "posts" in feed_data
    assert isinstance(feed_data["posts"], list)


@pytest.mark.asyncio
async def test_feed_unauthenticated_rejected(client_transport):
    """Verify that unauthenticated requests to the feed return 401 Unauthorized."""
    async with AsyncClient(transport=client_transport, base_url="http://test") as ac:
        response = await ac.get("/feed")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_duplicate_registration_rejected(client_transport):
    """Verify that registering with an already existing email returns 400."""
    email = f"duplicate_{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPassword123!"

    async with AsyncClient(transport=client_transport, base_url="http://test") as ac:
        first_resp = await ac.post("/auth/register", json={"email": email, "password": password})
        assert first_resp.status_code == 201

        second_resp = await ac.post("/auth/register", json={"email": email, "password": password})
        assert second_resp.status_code == 400


@pytest.mark.asyncio
async def test_login_invalid_credentials(client_transport):
    """Verify that logging in with incorrect credentials returns 400."""
    async with AsyncClient(transport=client_transport, base_url="http://test") as ac:
        response = await ac.post(
            "/auth/jwt/login",
            data={"username": "nonexistent@example.com", "password": "wrongpassword"}
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_post_unauthenticated(client_transport):
    """Verify that unauthenticated deletion attempts are rejected with 401."""
    random_id = str(uuid.uuid4())
    async with AsyncClient(transport=client_transport, base_url="http://test") as ac:
        response = await ac.delete(f"/posts/{random_id}")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_media_and_delete_flow(client_transport):
    """End-to-end test of media upload, feed listing with ownership check, and deletion."""
    email = f"creator_{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePassword123!"

    async with AsyncClient(transport=client_transport, base_url="http://test") as ac:
        # 1. Register & login
        await ac.post("/auth/register", json={"email": email, "password": password})
        login_res = await ac.post("/auth/jwt/login", data={"username": email, "password": password})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Upload photo
        fake_image_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        files = {"file": ("test_photo.png", fake_image_bytes, "image/png")}
        data = {"caption": "Sunset at the beach!"}

        upload_res = await ac.post("/upload", files=files, data=data, headers=headers)
        assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
        post_data = upload_res.json()
        assert "id" in post_data
        assert post_data["caption"] == "Sunset at the beach!"
        assert post_data["file_type"] == "image"
        post_id = post_data["id"]

        # 3. Check feed: post should be present and is_owner should be True
        feed_res = await ac.get("/feed", headers=headers)
        assert feed_res.status_code == 200
        posts = feed_res.json()["posts"]
        matched_posts = [p for p in posts if p["id"] == post_id]
        assert len(matched_posts) == 1
        assert matched_posts[0]["is_owner"] is True
        assert matched_posts[0]["caption"] == "Sunset at the beach!"

        # 4. Delete post
        delete_res = await ac.delete(f"/posts/{post_id}", headers=headers)
        assert delete_res.status_code == 200
        assert delete_res.json()["success"] is True

        # 5. Check feed: post should now be removed
        feed_after = await ac.get("/feed", headers=headers)
        posts_after = feed_after.json()["posts"]
        assert not any(p["id"] == post_id for p in posts_after)

        # 6. Deleting non-existent post should return 404
        delete_again = await ac.delete(f"/posts/{post_id}", headers=headers)
        assert delete_again.status_code == 404


