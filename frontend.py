import base64
import os
import urllib.parse
import requests
import streamlit as st

# Configure modern responsive viewport and branding
st.set_page_config(
    page_title="ShareThat | Cloud Media Sharing",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Base API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Inject Modern Glassmorphism & High-End Design CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Gradient Brand Badges & Header Styling */
    .brand-title {
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    .brand-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    /* Glassmorphism Container Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.25);
        margin-bottom: 1.25rem;
    }

    /* Post Card Display */
    .post-container {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1.75rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .post-container:hover {
        border-color: rgba(99, 102, 241, 0.35);
        transform: translateY(-2px);
    }

    /* Author Avatar & Badge Pills */
    .badge-pill {
        display: inline-flex;
        align-items: center;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.3);
        color: #c7d2fe;
        border-radius: 9999px;
        padding: 0.2rem 0.65rem;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .owner-pill {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #6ee7b7;
        border-radius: 9999px;
        padding: 0.2rem 0.55rem;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }

    .date-text {
        color: #64748b;
        font-size: 0.82rem;
    }

    .caption-text {
        font-size: 1.05rem;
        color: #f1f5f9;
        margin: 0.85rem 0;
        line-height: 1.45;
    }

    /* Feature highlights box */
    .feature-card {
        background: rgba(15, 23, 42, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }

    .feature-title {
        font-weight: 700;
        font-size: 0.9rem;
        color: #e2e8f0;
        margin-bottom: 0.2rem;
    }

    .feature-desc {
        font-size: 0.8rem;
        color: #94a3b8;
        line-height: 1.35;
    }

    /* Rounded Image & Video Container */
    img, video {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None


def get_headers():
    """Build Authorization bearer header."""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


def encode_text_for_overlay(text: str) -> str:
    """Encodes caption text for dynamic ImageKit overlay transformation."""
    if not text:
        return ""
    base64_text = base64.b64encode(text.encode("utf-8")).decode("utf-8")
    return urllib.parse.quote(base64_text)


def create_transformed_url(original_url: str, transformation_params: str = "", caption: str = None) -> str:
    """Applies smart CDN transformations or overlays onto the media asset."""
    if "imagekit.io" not in original_url:
        return original_url

    if caption:
        encoded_caption = encode_text_for_overlay(caption)
        text_overlay = f"l-text,ie-{encoded_caption},ly-N20,lx-20,fs-100,co-white,bg-000000A0,l-end"
        transformation_params = text_overlay

    if not transformation_params:
        return original_url

    parts = original_url.split("/")
    file_path = "/".join(parts[4:])
    base_url = "/".join(parts[:4])
    return f"{base_url}/tr:{transformation_params}/{file_path}"


def render_auth_page():
    """Renders high-conversion authentication interface with tabs and architecture overview."""
    col_left, col_right = st.columns([1.1, 0.9], gap="large")

    with col_left:
        st.markdown('<h1 class="brand-title">ShareThat ✨</h1>', unsafe_allow_html=True)
        st.markdown(
            '<p class="brand-subtitle">Cloud-native media sharing platform engineered with FastAPI, Async SQLAlchemy, and ImageKit CDN.</p>',
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(["🔐 Sign In", "🚀 Create Account"])

        with tab_login:
            st.markdown("### Access your account")
            with st.form("login_form"):
                login_email = st.text_input("Email Address", placeholder="name@domain.com")
                login_password = st.text_input("Password", type="password", placeholder="••••••••")
                login_btn = st.form_submit_button("Sign In", type="primary", use_container_width=True)

                if login_btn:
                    if not login_email or not login_password:
                        st.warning("Please provide both email and password.")
                    else:
                        with st.spinner("Authenticating securely..."):
                            try:
                                resp = requests.post(
                                    f"{API_BASE_URL}/auth/jwt/login",
                                    data={"username": login_email, "password": login_password},
                                    timeout=8,
                                )
                                if resp.status_code == 200:
                                    token_data = resp.json()
                                    st.session_state.token = token_data["access_token"]

                                    # Retrieve profile
                                    user_resp = requests.get(f"{API_BASE_URL}/users/me", headers=get_headers(), timeout=8)
                                    if user_resp.status_code == 200:
                                        st.session_state.user = user_resp.json()
                                        st.success("Welcome back! Redirecting...")
                                        st.rerun()
                                    else:
                                        st.error("Authentication succeeded, but failed to load user profile.")
                                else:
                                    st.error("Invalid credentials. Please verify your email and password.")
                            except requests.RequestException as e:
                                st.error(f"Unable to connect to ShareThat backend: {e}")

        with tab_register:
            st.markdown("### Join ShareThat")
            with st.form("register_form"):
                reg_email = st.text_input("Email Address", placeholder="name@domain.com")
                reg_password = st.text_input("Choose Password", type="password", placeholder="At least 6 characters")
                reg_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
                register_btn = st.form_submit_button("Create Account", type="primary", use_container_width=True)

                if register_btn:
                    if not reg_email or not reg_password:
                        st.warning("Please fill in all registration fields.")
                    elif reg_password != reg_confirm:
                        st.error("Passwords do not match.")
                    elif len(reg_password) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        with st.spinner("Creating your account..."):
                            try:
                                reg_resp = requests.post(
                                    f"{API_BASE_URL}/auth/register",
                                    json={"email": reg_email, "password": reg_password},
                                    timeout=8,
                                )
                                if reg_resp.status_code == 201:
                                    st.success("Account created successfully! Switch to 'Sign In' to log in.")
                                else:
                                    detail = reg_resp.json().get("detail", "Registration rejected")
                                    st.error(f"Registration failed: {detail}")
                            except requests.RequestException as e:
                                st.error(f"Backend connection error: {e}")

    with col_right:
        st.markdown(
            """
            <div class="glass-card">
                <h3 style="margin-top:0; color:#f8fafc;">⚡ Core Architecture & Features</h3>
                <div class="feature-card">
                    <div class="feature-title">🧵 Non-Blocking Async Ingestion</div>
                    <div class="feature-desc">Offloads heavy multi-megabyte media uploads to worker thread pools with <code>asyncio.to_thread</code>, ensuring zero latency spikes for concurrent feed queries.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-title">🖼️ Real-Time CDN Transformations</div>
                    <div class="feature-desc">Dynamic on-the-fly caption overlay, aspect-ratio smart resizing, and video blur-padding powered by ImageKit CDN pipelines.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-title">🔐 Stateless JWT Security</div>
                    <div class="feature-desc">Cryptographically signed bearer tokens with Argon2 password hashing and granular authorization filters.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-title">🧹 Remote Asset Cascade Lifecycle</div>
                    <div class="feature-desc">Synchronized post deletion triggers remote cloud asset purge, preventing orphaned storage costs.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-title">🐳 Production Docker & 100% Test Coverage</div>
                    <div class="feature-desc">Multi-service docker-compose setup and end-to-end async Pytest validation.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_feed_page():
    """Renders chronological community feed with interactive cards and asset controls."""
    header_col, action_col = st.columns([3, 1])
    with header_col:
        st.markdown('<h1 class="brand-title">Community Feed 🏠</h1>', unsafe_allow_html=True)
        st.markdown('<p class="brand-subtitle">Real-time media shared by community members.</p>', unsafe_allow_html=True)
    with action_col:
        if st.button("🔄 Refresh Feed", use_container_width=True):
            st.rerun()

    try:
        response = requests.get(f"{API_BASE_URL}/feed", headers=get_headers(), timeout=10)
        if response.status_code == 200:
            posts = response.json().get("posts", [])

            if not posts:
                st.info("No posts shared yet! Be the first to share something via the Upload page.")
                return

            # Display Feed Posts
            for post in posts:
                post_id = post["id"]
                is_owner = post.get("is_owner", False)
                caption = post.get("caption", "")
                created_date = post.get("created_at", "")[:10]
                author_email = post.get("email", "Anonymous")

                st.markdown('<div class="post-container">', unsafe_allow_html=True)

                col_meta, col_del = st.columns([4, 1])
                with col_meta:
                    owner_badge = '<span class="owner-pill">You (Author)</span>' if is_owner else ""
                    st.markdown(
                        f"""
                        <div>
                            <span class="badge-pill">👤 {author_email}</span>
                            {owner_badge}
                            <span class="date-text" style="margin-left: 0.75rem;">📅 {created_date}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col_del:
                    if is_owner:
                        if st.button("🗑️ Delete", key=f"del_{post_id}", help="Delete your post and remote asset"):
                            with st.spinner("Deleting post and cleaning up cloud assets..."):
                                del_res = requests.delete(f"{API_BASE_URL}/posts/{post_id}", headers=get_headers())
                                if del_res.status_code == 200:
                                    st.success("Post removed successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete post.")

                if caption:
                    st.markdown(f'<div class="caption-text">{caption}</div>', unsafe_allow_html=True)

                # Media Content Display
                if post["file_type"] == "image":
                    transformed_url = create_transformed_url(post["url"], "", caption)
                    img_caption = None if "imagekit.io" in transformed_url else caption
                    st.image(transformed_url, caption=img_caption, use_container_width=True)
                else:
                    video_url = create_transformed_url(post["url"], "w-600,h-340,cm-pad_resize,bg-blurred")
                    st.video(video_url)

                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("Failed to load feed from backend.")
    except requests.RequestException as e:
        st.error(f"Network error while connecting to ShareThat API: {e}")


def render_upload_page():
    """Renders modern media upload form with preview and metadata input."""
    st.markdown('<h1 class="brand-title">Share Media 📸</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="brand-subtitle">Upload high-resolution images or videos with real-time CDN transformation.</p>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1.2, 0.8], gap="large")

    with col1:
        with st.form("media_upload_form", clear_on_submit=True):
            uploaded_file = st.file_uploader(
                "Select Media File",
                type=["png", "jpg", "jpeg", "mp4", "avi", "mov", "mkv", "webm"],
                help="Supported: PNG, JPG, MP4, MOV, WEBM",
            )

            caption = st.text_area(
                "Caption",
                placeholder="Write a descriptive caption or story...",
                max_chars=280,
            )

            submit_btn = st.form_submit_button("🚀 Publish Post", type="primary", use_container_width=True)

            if submit_btn:
                if not uploaded_file:
                    st.warning("Please select a file to upload.")
                else:
                    with st.spinner("Processing & uploading to cloud CDN..."):
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        data = {"caption": caption}
                        try:
                            upload_res = requests.post(
                                f"{API_BASE_URL}/upload",
                                files=files,
                                data=data,
                                headers=get_headers(),
                                timeout=20,
                            )
                            if upload_res.status_code == 200:
                                st.success("Post published successfully!")
                                st.rerun()
                            else:
                                st.error(f"Upload failed: {upload_res.text}")
                        except requests.RequestException as e:
                            st.error(f"Error communicating with upload service: {e}")

    with col2:
        st.markdown(
            """
            <div class="glass-card">
                <h4 style="margin-top:0; color:#f8fafc;">💡 Upload Guidelines</h4>
                <ul style="color:#94a3b8; font-size:0.88rem; line-height:1.6;">
                    <li><strong>Images:</strong> PNG, JPG, JPEG up to 25MB with auto-optimized compression.</li>
                    <li><strong>Videos:</strong> MP4, MOV, WEBM with automatic padding and blur backgrounds.</li>
                    <li><strong>CDN Overlays:</strong> Captions are automatically positioned and branded via cloud transformation parameters.</li>
                    <li><strong>Ownership:</strong> You maintain full deletion control over your published media assets.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


# Application Routing Logic
if st.session_state.user is None:
    render_auth_page()
else:
    # Sidebar Navigation & User Profile Card
    st.sidebar.markdown(
        f"""
        <div style="padding: 0.5rem 0 1rem 0;">
            <div style="font-size: 1.4rem; font-weight: 800; color: #f8fafc;">ShareThat ✨</div>
            <div style="font-size: 0.8rem; color: #94a3b8;">Cloud Media Platform</div>
        </div>
        <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 0.75rem; margin-bottom: 1rem;">
            <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: 700;">Signed in as</div>
            <div style="font-size: 0.88rem; color: #e2e8f0; font-weight: 600; word-break: break-all;">{st.session_state.user['email']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page_selection = st.sidebar.radio(
        "Navigation",
        ["🏠 Explore Feed", "📸 Share Media"],
        index=0,
    )

    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Sign Out", use_container_width=True):
        st.session_state.user = None
        st.session_state.token = None
        st.rerun()

    st.sidebar.markdown(
        """
        <div style="margin-top: 2rem; font-size: 0.75rem; color: #64748b; text-align: center;">
            ShareThat v1.0.0<br/>
            Engineered with FastAPI & Streamlit
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Route Page
    if page_selection == "🏠 Explore Feed":
        render_feed_page()
    else:
        render_upload_page()
