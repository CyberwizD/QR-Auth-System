# import streamlit as st
# import base64
# import logging
# from utils import generator, scanner

# st.set_page_config(
#     page_title="QR Authentication System", 
#     page_icon=":chart_with_upwards_trend:", 
#     layout="wide"
# )

# st.logo(image="static/logo.png", size="small", link="https://github.com/CyberwizD/QR-Auth-System")

# # Sidebar
# # Insert custom CSS for glowing effect
# st.markdown(
#     """
#     <style>
#     .cover-glow {
#         width: 100%;
#         height: auto;
#         padding: 3px;
#         box-shadow: 
#             0 0 5px #330000,
#             0 0 10px #660000,
#             0 0 15px #990000,
#             0 0 20px #CC0000,
#             0 0 25px #FF0000,
#             0 0 30px #FF3333,
#             0 0 35px #FF6666;
#         position: relative;
#         z-index: -1;
#         border-radius: 45px;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# def img_to_base64(image_path):
#     """Convert image to base64."""
#     try:
#         with open(image_path, "rb") as img_file:
#             return base64.b64encode(img_file.read()).decode()
#     except Exception as e:
#         logging.error(f"Error converting image to base64: {str(e)}")
#         return None

# # Load and display sidebar image
# img_path = "static/logo.png"
# img_base64 = img_to_base64(img_path)
# if img_base64:
#     st.sidebar.markdown(
#         f'<img src="data:image/png;base64,{img_base64}" class="cover-glow">',
#         unsafe_allow_html=True,
#     )

# # Streamlit UI
# st.title("QR Authentication System")
# st.write("Link your device to the QR code below to access your account.")

# tabs = st.tabs(["📝 Generate QR Code", "🔗 Scan QR Code"])

# # Generate QR Code Tab
# with tabs[0]:
#     st.subheader("This section will generate the QR code.")

#     generate_btn = st.button("Generate QR Code")
#     if generate_btn:
#         # Generate QR code
#         generator.generate_qr()

#         st.success("QR code generated successfully!")

#         # Display QR code
#         st.image("./assets/qrcode.png", use_column_width=True)

# # Scan QR Code Tab
# with tabs[1]:
#     st.subheader("This section will scan the QR code.")

#     scan_btn = st.button("Scan QR Code")
#     if scan_btn:
#         # Scan QR code
#         scanner.scan_qr()

#         st.success("QR code scanned successfully!")



import streamlit as st
import requests
import websocket
import json
import threading
import time
from datetime import datetime, timedelta
import base64
from PIL import Image
import io
import asyncio
import streamlit.components.v1 as components

# Configuration
API_BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"

# Custom CSS for beautiful UI
def load_custom_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styles */
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .app-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .app-subtitle {
        font-size: 1.2rem;
        font-weight: 300;
        opacity: 0.9;
    }
    
    /* QR Code Container */
    .qr-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        border: 1px solid #f0f0f0;
        margin: 2rem 0;
    }
    
    .qr-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 1rem;
    }
    
    .qr-instruction {
        color: #666;
        font-size: 1rem;
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }
    
    .qr-code-wrapper {
        display: inline-block;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 15px;
        border: 2px dashed #dee2e6;
        margin: 1rem 0;
    }
    
    /* Status Messages */
    .status-waiting {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: #8b4513;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    .status-success {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: #155724;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    .status-error {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: #721c24;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    /* Dashboard Styles */
    .dashboard-container {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .welcome-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .welcome-title {
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .welcome-subtitle {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .stats-number {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .stats-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .device-card {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        transition: transform 0.2s ease;
    }
    
    .device-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .device-name {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    .device-info {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .device-status {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .status-active {
        background: #d4edda;
        color: #155724;
    }
    
    .status-inactive {
        background: #f8d7da;
        color: #721c24;
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar Styles */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .css-1d391kg .css-1v0mbdj {
        color: white;
    }
    
    /* Loading Animation */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-right: 10px;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .app-title {
            font-size: 2rem;
        }
        
        .qr-container {
            padding: 1rem;
        }
        
        .dashboard-container {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# WebSocket Client Class
class WebSocketClient:
    def __init__(self):
        self.ws = None
        self.connected = False
        self.session_id = None
        
    def connect(self, session_id):
        try:
            self.session_id = session_id
            ws_url = f"{WS_BASE_URL}/ws/{session_id}"
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            
            # Run in separate thread
            def run_ws():
                self.ws.run_forever()
            
            ws_thread = threading.Thread(target=run_ws, daemon=True)
            ws_thread.start()
            
        except Exception as e:
            st.error(f"WebSocket connection error: {str(e)}")
    
    def on_open(self, ws):
        self.connected = True
        if 'ws_status' not in st.session_state:
            st.session_state.ws_status = "Connected"
    
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            if data.get('type') == 'login_success':
                st.session_state.login_data = data
                st.session_state.login_success = True
                st.session_state.user_data = data.get('user')
                st.session_state.session_token = data.get('session_token')
                st.rerun()
        except Exception as e:
            print(f"Error processing WebSocket message: {e}")
    
    def on_error(self, ws, error):
        st.session_state.ws_status = f"Error: {error}"
    
    def on_close(self, ws, close_status_code, close_msg):
        self.connected = False
        st.session_state.ws_status = "Disconnected"

# API Functions
def generate_qr_session():
    try:
        response = requests.post(f"{API_BASE_URL}/qr/generate", json={})
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to generate QR code: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def get_user_devices(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE_URL}/devices", headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def revoke_device(token, device_id):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(f"{API_BASE_URL}/devices/{device_id}", headers=headers)
        return response.status_code == 200
    except:
        return False

# UI Components
def render_header():
    st.markdown("""
    <div class="app-header">
        <div class="app-title">🔐 SecureLink</div>
        <div class="app-subtitle">Secure QR Code Device Authentication</div>
    </div>
    """, unsafe_allow_html=True)

def render_qr_login_page():
    st.markdown("""
    <div class="qr-container">
        <div class="qr-title">📱 Link Your Device</div>
        <div class="qr-instruction">
            Open your mobile app and scan the QR code below to securely link your device
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🔄 Generate New QR Code", use_container_width=True):
            st.session_state.qr_data = None
            st.session_state.login_success = False
            st.session_state.ws_client = None
            st.rerun()
    
    # Generate QR code if not exists
    if 'qr_data' not in st.session_state or st.session_state.qr_data is None:
        with st.spinner("Generating secure QR code..."):
            qr_data = generate_qr_session()
            if qr_data:
                st.session_state.qr_data = qr_data
                st.session_state.login_success = False
                
                # Initialize WebSocket connection
                ws_client = WebSocketClient()
                ws_client.connect(qr_data['session_id'])
                st.session_state.ws_client = ws_client
                st.rerun()
    
    if 'qr_data' in st.session_state and st.session_state.qr_data:
        qr_data = st.session_state.qr_data
        
        # Display QR Code
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="qr-code-wrapper">', unsafe_allow_html=True)
            
            # Decode base64 QR code
            qr_image_data = base64.b64decode(qr_data['qr_code_data'])
            qr_image = Image.open(io.BytesIO(qr_image_data))
            st.image(qr_image, width=300)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Display status
        expires_at = datetime.fromisoformat(qr_data['expires_at'].replace('Z', '+00:00'))
        time_left = expires_at - datetime.now()
        
        if time_left.total_seconds() > 0:
            minutes_left = int(time_left.total_seconds() // 60)
            seconds_left = int(time_left.total_seconds() % 60)
            
            st.markdown(f"""
            <div class="status-waiting">
                <div class="loading-spinner"></div>
                Waiting for mobile scan... Expires in {minutes_left}m {seconds_left}s
            </div>
            """, unsafe_allow_html=True)
            
            # Auto-refresh every 5 seconds
            time.sleep(5)
            st.rerun()
        else:
            st.markdown("""
            <div class="status-error">
                ⏰ QR Code has expired. Please generate a new one.
            </div>
            """, unsafe_allow_html=True)

def render_dashboard():
    user_data = st.session_state.user_data
    session_token = st.session_state.session_token
    
    # Welcome Card
    st.markdown(f"""
    <div class="welcome-card">
        <div class="welcome-title">Welcome back, {user_data['username']}! 👋</div>
        <div class="welcome-subtitle">Your device has been successfully linked</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats Row
    col1, col2, col3 = st.columns(3)
    
    # Get user devices
    devices = get_user_devices(session_token)
    active_devices = [d for d in devices if d['is_active']]
    
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{len(active_devices)}</div>
            <div class="stats-label">Active Devices</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        login_time = datetime.now().strftime("%H:%M")
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{login_time}</div>
            <div class="stats-label">Login Time</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">✓</div>
            <div class="stats-label">Secure Connection</div>
        </div>
        """, unsafe_allow_html=True)
    
    # User Information
    st.markdown("""
    <div class="dashboard-container">
        <h3>👤 User Information</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Username:** {user_data['username']}")
        st.info(f"**Email:** {user_data['email']}")
    with col2:
        st.info(f"**User ID:** {user_data['id']}")
        st.info(f"**Status:** Active ✅")
    
    # Linked Devices
    st.markdown("""
    <div class="dashboard-container">
        <h3>📱 Linked Devices</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if devices:
        for device in devices:
            status_class = "status-active" if device['is_active'] else "status-inactive"
            status_text = "Active" if device['is_active'] else "Inactive"
            status_icon = "🟢" if device['is_active'] else "🔴"
            
            created_date = datetime.fromisoformat(device['created_at']).strftime("%B %d, %Y at %H:%M")
            last_active = datetime.fromisoformat(device['last_active']).strftime("%B %d, %Y at %H:%M")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div class="device-card">
                    <div class="device-name">{device['device_name']} {status_icon}</div>
                    <div class="device-info">Created: {created_date}</div>
                    <div class="device-info">Last Active: {last_active}</div>
                    <span class="device-status {status_class}">{status_text}</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if device['is_active']:
                    if st.button(f"🗑️ Revoke", key=f"revoke_{device['id']}", help="Revoke device access"):
                        if revoke_device(session_token, device['device_id']):
                            st.success("Device revoked successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to revoke device")
    else:
        st.warning("No linked devices found.")
    
    # Actions
    st.markdown("""
    <div class="dashboard-container">
        <h3>⚡ Quick Actions</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Devices", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("📱 Link New Device", use_container_width=True):
            # Reset to QR generation
            st.session_state.qr_data = None
            st.session_state.login_success = False
            st.session_state.user_data = None
            st.session_state.session_token = None
            st.rerun()
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            # Clear session
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# Main App
def main():
    st.set_page_config(
        page_title="SecureLink - QR Authentication",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    if 'login_success' not in st.session_state:
        st.session_state.login_success = False
    
    # Render header
    render_header()
    
    # Check login status
    if st.session_state.login_success and 'user_data' in st.session_state:
        render_dashboard()
    else:
        render_qr_login_page()
    
    # Check if login was successful via WebSocket
    if 'login_success' in st.session_state and st.session_state.login_success:
        if 'user_data' not in st.session_state and 'login_data' in st.session_state:
            login_data = st.session_state.login_data
            st.session_state.user_data = login_data.get('user')
            st.session_state.session_token = login_data.get('session_token')
            
            # Show success message
            st.markdown("""
            <div class="status-success">
                🎉 Login successful! Welcome to your dashboard.
            </div>
            """, unsafe_allow_html=True)
            
            time.sleep(2)
            st.rerun()

if __name__ == "__main__":
    main()