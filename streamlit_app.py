import streamlit as st
import requests
import json
from PIL import Image
import io
import time

# Streamlit UI for the API
st.set_page_config(
    page_title="AI Image Captioning & Search",
    page_icon="🖼️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .image-container {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f9f9f9;
    }
    .similarity-score {
        background-color: #4CAF50;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .upload-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🖼️ AI Image Captioning & Search</h1><p>Upload images and search them using natural language!</p></div>', unsafe_allow_html=True)

# API base URL
API_BASE_URL = st.text_input("API Base URL", value="http://localhost:8000", help="Enter the base URL of your API")

# Helper functions
def download_image(image_id, headers):
    try:
        response = requests.get(f"{API_BASE_URL}/images/{image_id}/download", headers=headers)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        return None
    except Exception as e:
        st.error(f"Error downloading image: {str(e)}")
        return None

def display_image_with_info(image_data, headers, show_similarity=False):
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Download and display image
        with st.spinner("Loading image..."):
            image = download_image(image_data["id"], headers)
            if image:
                st.image(image, caption=f"ID: {image_data['id']}", use_column_width=True)
            else:
                st.error("Failed to load image")
    
    with col2:
        st.markdown(f"**Caption:** {image_data['caption']}")
        st.markdown(f"**Filename:** {image_data['filename']}")
        st.markdown(f"**Upload Time:** {image_data['upload_time']}")
        st.markdown(f"**File Size:** {image_data['file_size']:,} bytes")
        st.markdown(f"**Content Type:** {image_data['content_type']}")
        
        if show_similarity and 'similarity_score' in image_data:
            similarity_percentage = image_data['similarity_score'] * 100
            st.markdown(f'<span class="similarity-score">Similarity: {similarity_percentage:.1f}%</span>', 
                       unsafe_allow_html=True)

# Authentication section
st.sidebar.header("🔐 Authentication")

if "token" not in st.session_state:
    st.session_state.token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None

if st.session_state.token is None:
    auth_tab1, auth_tab2 = st.sidebar.tabs(["Login", "Register"])
    
    with auth_tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("🚀 Login", use_container_width=True):
            if username and password:
                with st.spinner("Logging in..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/auth/token",
                            data={"username": username, "password": password}
                        )
                        if response.status_code == 200:
                            st.session_state.token = response.json()["access_token"]
                            st.success("✅ Logged in successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            error_detail = response.json().get("detail", "Login failed")
                            st.error(f"❌ {error_detail}")
                    except Exception as e:
                        st.error(f"❌ Connection error: {str(e)}")
            else:
                st.warning("⚠️ Please enter both username and password")
    
    with auth_tab2:
        st.subheader("Register")
        reg_username = st.text_input("Username", key="reg_username", help="At least 3 alphanumeric characters")
        reg_password = st.text_input("Password", type="password", key="reg_password", help="At least 6 characters")
        
        if st.button("📝 Register", use_container_width=True):
            if reg_username and reg_password:
                with st.spinner("Creating account..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/auth/register",
                            json={"username": reg_username, "password": reg_password}
                        )
                        if response.status_code == 200:
                            st.success("✅ Registration successful! Please login.")
                        else:
                            error_detail = response.json().get("detail", "Registration failed")
                            st.error(f"❌ {error_detail}")
                    except Exception as e:
                        st.error(f"❌ Connection error: {str(e)}")
            else:
                st.warning("⚠️ Please enter both username and password")

else:
    # Get user info
    if st.session_state.user_info is None:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        try:
            response = requests.get(f"{API_BASE_URL}/auth/me", headers=headers)
            if response.status_code == 200:
                st.session_state.user_info = response.json()
        except:
            pass
    
    # Display user info
    if st.session_state.user_info:
        st.sidebar.success(f"👋 Welcome, {st.session_state.user_info['username']}!")
    else:
        st.sidebar.success("👋 Logged in!")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.token = None
        st.session_state.user_info = None
        st.rerun()
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # Main interface
    tab1, tab2, tab3 = st.tabs(["📤 Upload Image", "🔍 Search Images", "📚 History"])
    
    with tab1:
        st.header("📤 Upload Image")
        st.markdown("Upload an image to generate an automatic caption using AI.")
        
        uploaded_file = st.file_uploader(
            "Choose an image...", 
            type=['jpg', 'jpeg', 'png'],
            help="Supported formats: JPG, JPEG, PNG (Max 10MB)"
        )
        
        if uploaded_file is not None:
            # Display preview
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Preview")
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                
                # Show file info
                st.info(f"""
                **File Info:**
                - Name: {uploaded_file.name}
                - Size: {len(uploaded_file.getvalue()):,} bytes
                - Type: {uploaded_file.type}
                """)
            
            with col2:
                st.subheader("Upload & Process")
                
                if st.button("🚀 Upload and Generate Caption", use_container_width=True, type="primary"):
                    with st.spinner("Uploading image and generating caption... This may take a moment."):
                        try:
                            # Reset file pointer
                            uploaded_file.seek(0)
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                            
                            response = requests.post(
                                f"{API_BASE_URL}/images/upload",
                                files=files,
                                headers=headers
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                st.markdown(f"""
                                <div class="upload-success">
                                    <h4>✅ Upload Successful!</h4>
                                    <p><strong>Generated Caption:</strong> {result['caption']}</p>
                                    <p><strong>Image ID:</strong> {result['id']}</p>
                                    <p><strong>Upload Time:</strong> {result['upload_time']}</p>
                                    <p><strong>File Size:</strong> {result['file_size']:,} bytes</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Auto-refresh other tabs
                                st.balloons()
                            else:
                                error_detail = response.json().get("detail", "Upload failed")
                                st.markdown(f"""
                                <div class="error-message">
                                    <h4>❌ Upload Failed</h4>
                                    <p>{error_detail}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"❌ Connection error: {str(e)}")
    
    with tab2:
        st.header("🔍 Search Images")
        st.markdown("Search your uploaded images using natural language queries.")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_input(
                "Enter search query:", 
                placeholder="e.g., 'cat sitting on a chair', 'sunset over mountains', 'red car'",
                help="Describe what you're looking for in natural language"
            )
        
        with col2:
            search_limit = st.selectbox("Results", [3, 5, 10], index=0, help="Number of results to return")
        
        # Advanced options
        with st.expander("🔧 Advanced Options"):
            threshold = st.slider(
                "Similarity Threshold", 
                0.0, 1.0, 0.0, 0.1,
                help="Minimum similarity score (0.0 = show all, 1.0 = exact match only)"
            )
        
        if st.button("🔍 Search Images", use_container_width=True, type="primary") and search_query:
            with st.spinner("Searching images... Analyzing semantic similarity..."):
                try:
                    response = requests.get(
                        f"{API_BASE_URL}/images/search",
                        params={"query": search_query, "limit": search_limit, "threshold": threshold},
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        results = response.json()
                        
                        if results['total_results'] > 0:
                            st.success(f"🎯 Found {results['total_results']} matching images for: **{results['query']}**")
                            
                            for i, result in enumerate(results['results'], 1):
                                st.markdown(f"### 🖼️ Result {i}")
                                with st.container():
                                    st.markdown('<div class="image-container">', unsafe_allow_html=True)
                                    display_image_with_info(result, headers, show_similarity=True)
                                    st.markdown('</div>', unsafe_allow_html=True)
                                
                                if i < len(results['results']):
                                    st.divider()
                        else:
                            st.info(f"🤷‍♂️ No images found matching: **{search_query}**")
                            st.markdown("**Suggestions:**")
                            st.markdown("- Try different keywords")
                            st.markdown("- Lower the similarity threshold")
                            st.markdown("- Upload more images first")
                    else:
                        error_detail = response.json().get("detail", "Search failed")
                        st.error(f"❌ {error_detail}")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")
    
    with tab3:
        st.header("📚 Upload History")
        st.markdown("View all your uploaded images and their generated captions.")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🔄 Refresh History", use_container_width=True):
                st.rerun()
        
        with col2:
            items_per_page = st.selectbox("Items per page", [5, 10, 20], index=1)
        
        # Pagination controls
        if "history_page" not in st.session_state:
            st.session_state.history_page = 0
        
        with st.spinner("Loading image history..."):
            try:
                offset = st.session_state.history_page * items_per_page
                response = requests.get(
                    f"{API_BASE_URL}/images/history",
                    params={"limit": items_per_page, "offset": offset},
                    headers=headers
                )
                
                if response.status_code == 200:
                    history = response.json()
                    
                    if history:
                        st.success(f"📊 Showing {len(history)} images (Page {st.session_state.history_page + 1})")
                        
                        # Pagination controls
                        col1, col2, col3 = st.columns([1, 2, 1])
                        
                        with col1:
                            if st.button("⬅️ Previous", disabled=st.session_state.history_page == 0):
                                st.session_state.history_page -= 1
                                st.rerun()
                        
                        with col3:
                            if st.button("➡️ Next", disabled=len(history) < items_per_page):
                                st.session_state.history_page += 1
                                st.rerun()
                        
                        # Display images
                        for i, item in enumerate(history, 1):
                            st.markdown(f"### 🖼️ Image {offset + i}")
                            with st.container():
                                st.markdown('<div class="image-container">', unsafe_allow_html=True)
                                
                                # Add action buttons
                                col1, col2 = st.columns([4, 1])
                                
                                with col1:
                                    display_image_with_info(item, headers)
                                
                                with col2:
                                    st.markdown("**Actions:**")
                                    
                                    # Download button
                                    if st.button(f"💾 Download", key=f"download_{item['id']}"):
                                        with st.spinner("Downloading..."):
                                            try:
                                                response = requests.get(
                                                    f"{API_BASE_URL}/images/{item['id']}/download",
                                                    headers=headers
                                                )
                                                if response.status_code == 200:
                                                    st.download_button(
                                                        label="📥 Save File",
                                                        data=response.content,
                                                        file_name=item['filename'],
                                                        mime=item['content_type'],
                                                        key=f"save_{item['id']}"
                                                    )
                                                else:
                                                    st.error("Download failed")
                                            except Exception as e:
                                                st.error(f"Error: {str(e)}")
                                    
                                    # Delete button
                                    if st.button(f"🗑️ Delete", key=f"delete_{item['id']}", type="secondary"):
                                        if st.session_state.get(f"confirm_delete_{item['id']}", False):
                                            with st.spinner("Deleting..."):
                                                try:
                                                    response = requests.delete(
                                                        f"{API_BASE_URL}/images/{item['id']}",
                                                        headers=headers
                                                    )
                                                    if response.status_code == 200:
                                                        st.success("✅ Image deleted!")
                                                        time.sleep(1)
                                                        st.rerun()
                                                    else:
                                                        st.error("❌ Delete failed")
                                                except Exception as e:
                                                    st.error(f"❌ Error: {str(e)}")
                                        else:
                                            st.session_state[f"confirm_delete_{item['id']}"] = True
                                            st.warning("⚠️ Click again to confirm deletion")
                                
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            if i < len(history):
                                st.divider()
                    else:
                        st.info("📭 No images uploaded yet.")
                else:
                    error_detail = response.json().get("detail", "Failed to load history")
                    st.error(f"❌ {error_detail}")
            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🤖 Powered by AI Image Captioning & Search API</p>
    <p>Built with FastAPI, Hugging Face Transformers, and Streamlit</p>
</div>
""", unsafe_allow_html=True)

# Sidebar info
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 API Status")

# Check API health
try:
    health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
    if health_response.status_code == 200:
        st.sidebar.success("🟢 API Online")
    else:
        st.sidebar.error("🔴 API Issues")
except:
    st.sidebar.error("🔴 API Offline")
