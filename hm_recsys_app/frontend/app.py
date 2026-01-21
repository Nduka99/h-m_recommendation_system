import streamlit as st
import requests
import os

# --- Configuration ---
# Default to localhost for local testing if env var not set
# In Docker, this should be set to "http://backend:8000"
API_URL = os.getenv("API_URL", "http://localhost:8000")

# --- Page Setup ---
st.set_page_config(
    page_title="H&M Style Curator",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for "Rich Aesthetics" ---
st.markdown("""
<style>
    /* Global Styles */
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Typography */
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 300;
        letter-spacing: 0.05em;
    }
    
    /* Cards for Items */
    .stImage {
        border-radius: 12px;
        transition: transform 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .stImage:hover {
        transform: scale(1.03);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.5);
    }
    
    /* Button Styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #FF4B2B 0%, #FF416C 100%);
        border: none;
        color: white;
        padding: 0.6rem 1rem;
        border-radius: 30px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 0 15px rgba(255, 75, 43, 0.5);
        transform: translateY(-2px);
    }
    
    /* Sidebar Aesthetics */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #21262d;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #30363d;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
# Default to web, but can be overridden for local images
# Example: "C:/path/to/images" or "/app/images"
IMAGE_BASE_PATH = os.getenv("IMAGE_BASE_PATH", None)

def get_image_url(article_id_str):
    """
    Constructs image path or URL.
    1. If IMAGE_BASE_PATH is valid, try local file: {base}/{folder}/{id}.jpg
    2. Fallback to H&M Web URL (often broken for old items)
    """
    # Ensure ID is 10 chars (leading zeros)
    if len(article_id_str) != 10:
        article_id_str = "0" * (10 - len(article_id_str)) + article_id_str
        
    folder = article_id_str[:3]
    
    # 1. Local File Check
    if IMAGE_BASE_PATH and os.path.exists(IMAGE_BASE_PATH):
        local_path = os.path.join(IMAGE_BASE_PATH, folder, f"{article_id_str}.jpg")
        if os.path.exists(local_path):
            return local_path
            
    # 2. Fallback to Web (with validation)
    # These items are from 2020, so many public URLs are dead. 
    # We use a placeholder if the H&M link is broken to keep the UI clean.
    url = f"https://lp2.hm.com/hmgoepprod?set=source[/{folder}/{article_id_str}.jpg],origin[dam],category[],type[LOOKBOOK],res[m],hmver[1]&call=url[file:/product/main]"
    
    return url


def get_recommendations(customer_id):
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json={"customer_id": int(customer_id), "top_k": 12},
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get("recommendations", [])
        else:
            st.error(f"Backend Error: {response.status_code} - {response.text}")
            return []
    except requests.exceptions.ConnectionError:
        st.error("🚨 Could not connect to AI Engine. Is the Backend running?")
        return []
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return []

# --- Main Interface ---

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/H%26M-Logo.svg/1024px-H%26M-Logo.svg.png", width=100)
    st.markdown("### User Profile")
    st.markdown("Enter your Customer ID to get personalized fashion curations powered by our **Hybrid LightGBM Engine**.")
    
    customer_id = st.text_input("Customer ID", value="123456")
    
    st.markdown("---")
    st.markdown("**Engine Status**")
    if st.button("Check Connectivity"):
        try:
            res = requests.get(f"{API_URL}/")
            if res.status_code == 200:
                st.success("Online 🟢")
                st.json(res.json())
            else:
                st.warning("Issues Detected 🟡")
        except:
            st.error("Offline 🔴")
            
    st.markdown("---")
    show_debug = st.checkbox("Show Debug Info", value=False)

# Main Content
st.title("Top Picks For You")
st.markdown("Based on your purchase history and visual style preferences.")


def validate_image_url(url):
    """
    Checks if an image URL is alive. Returns the URL if yes, else a placeholder.
    """
    try:
        # H&M often returns 200 for broken images (soft 404). 
        # We MUST check Content-Type to ensure it's a real image and not an error page/pixel.
        r = requests.head(url, timeout=1.5)
        content_type = r.headers.get("Content-Type", "").lower()
        if r.status_code == 200 and "image" in content_type:
            return url
    except:
        pass
    # Reliable Placeholder
    return "https://placehold.co/300x445/EEE/31343C?text=Image+Unavailable"



if customer_id:
    # Fetch Recommendations
    with st.spinner("Curating your unique look..."):
        recs = get_recommendations(customer_id)
    
    if recs:
        # Display Grid
        cols = st.columns(4) # 4 columns grid
        for idx, article_id in enumerate(recs):
            col = cols[idx % 4]
            with col:
                # Image
                raw_url = get_image_url(article_id)
                img_url = validate_image_url(raw_url)
                st.image(img_url, use_container_width=True)
                
                # Caption / Details
                st.markdown(f"**{article_id}**")
                st.caption("Premium Selection")
                if show_debug:
                    st.text(f"URL: {img_url}")
                
    elif customer_id and not recs:
        st.info("No specific recommendations found. Try another User ID.")

else:
    st.info("Please enter a Customer ID to start.")
