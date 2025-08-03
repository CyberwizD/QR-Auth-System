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
import queue
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    </style>
    """, unsafe_allow_html=True)

# WebSocket Client Class with IMPROVED message handling
class WebSocketClient:
    def __init__(self, message_queue):
        self.ws = None
        self.connected = False
        self.session_id = None
        self.message_queue = message_queue
        self.running = False
        self.connection_thread = None
        
    def connect(self, session_id):
        try:
            self.session_id = session_id
            self.running = True
            ws_url = f"{WS_BASE_URL}/ws/{session_id}"
            logger.info(f"🔌 Connecting to WebSocket: {ws_url}")
            
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            
            # Run in separate thread
            def run_ws():
                try:
                    self.ws.run_forever(ping_interval=30, ping_timeout=10)
                except Exception as e:
                    logger.error(f"❌ WebSocket run_forever error: {e}")
            
            self.connection_thread = threading.Thread(target=run_ws, daemon=True)
            self.connection_thread.start()
            
        except Exception as e:
            logger.error(f"❌ WebSocket connection error: {str(e)}")
            self.message_queue.put({"type": "error", "message": str(e)})
    
    def on_open(self, ws):
        self.connected = True
        logger.info("✅ WebSocket connected successfully")
        self.message_queue.put({"type": "ws_connected", "message": "WebSocket connected"})
        
        # Send a ping to keep connection alive
        try:
            ws.send("ping")
        except Exception as e:
            logger.error(f"❌ Error sending initial ping: {e}")
    
    def on_message(self, ws, message):
        try:
            logger.info(f"📨 WebSocket message received: {message}")
            
            # Handle echo and ping messages
            if message.startswith("Echo:") or message == "pong":
                return
                
            # Try to parse as JSON
            try:
                data = json.loads(message)
                logger.info(f"📨 Parsed WebSocket data: {data}")
                
                if data.get('type') == 'login_success':
                    logger.info("🎉 Login success message received!")
                    self.message_queue.put({
                        "type": "login_success",
                        "user_data": data.get('user'),
                        "session_token": data.get('session_token'),
                        "device_id": data.get('device_id')
                    })
                elif data.get('type') == 'connected':
                    logger.info("🔌 WebSocket connection confirmed")
                    self.message_queue.put({"type": "ws_confirmed", "message": "Connection confirmed"})
                else:
                    self.message_queue.put(data)
            except json.JSONDecodeError:
                # Handle plain text messages
                logger.info(f"📨 Plain text message: {message}")
                self.message_queue.put({"type": "message", "content": message})
                
        except Exception as e:
            logger.error(f"❌ Error processing WebSocket message: {e}")
    
    def on_error(self, ws, error):
        logger.error(f"❌ WebSocket error: {error}")
        self.message_queue.put({"type": "error", "message": str(error)})
    
    def on_close(self, ws, close_status_code, close_msg):
        self.connected = False
        self.running = False
        logger.info(f"🔌 WebSocket closed: {close_status_code} - {close_msg}")
        self.message_queue.put({"type": "disconnected", "code": close_status_code, "message": close_msg})

    def disconnect(self):
        self.running = False
        if self.ws:
            try:
                self.ws.close()
            except Exception as e:
                logger.error(f"❌ Error closing WebSocket: {e}")

# API Functions
def generate_qr_session():
    try:
        logger.info("🎯 Generating QR session...")
        response = requests.post(f"{API_BASE_URL}/qr/generate", json={})
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ QR session generated: {data['session_id']}")
            return data
        else:
            logger.error(f"❌ Failed to generate QR code: {response.text}")
            return None
    except Exception as e:
        logger.error(f"❌ Connection error: {str(e)}")
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
            # Clear existing data
            for key in ['qr_data', 'ws_client', 'message_queue', 'login_success', 'user_data', 'session_token', 'ws_connected', 'ws_confirmed']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # Initialize message queue if not exists
    if 'message_queue' not in st.session_state:
        st.session_state.message_queue = queue.Queue()
    
    # Generate QR code if not exists
    if 'qr_data' not in st.session_state or st.session_state.qr_data is None:
        with st.spinner("Generating secure QR code..."):
            qr_data = generate_qr_session()
            if qr_data:
                st.session_state.qr_data = qr_data
                st.session_state.login_success = False
                st.session_state.ws_connected = False
                st.session_state.ws_confirmed = False
                
                # Initialize WebSocket connection
                logger.info("🔌 Initializing WebSocket connection...")
                ws_client = WebSocketClient(st.session_state.message_queue)
                ws_client.connect(qr_data['session_id'])
                st.session_state.ws_client = ws_client
                
                # Wait a moment for connection
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Failed to generate QR code. Please check your server connection.")
                return
    
    if 'qr_data' in st.session_state and st.session_state.qr_data:
        qr_data = st.session_state.qr_data
        
        # Display QR Code
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="qr-code-wrapper">', unsafe_allow_html=True)
            
            # Decode base64 QR code
            try:
                qr_image_data = base64.b64decode(qr_data['qr_code_data'])
                qr_image = Image.open(io.BytesIO(qr_image_data))
                st.image(qr_image, width=300)
            except Exception as e:
                st.error(f"❌ Error displaying QR code: {e}")
                return
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Process WebSocket messages - IMPROVED VERSION
        messages_processed = 0
        max_messages_per_cycle = 10  # Prevent infinite loops
        
        try:
            while not st.session_state.message_queue.empty() and messages_processed < max_messages_per_cycle:
                message = st.session_state.message_queue.get_nowait()
                messages_processed += 1
                logger.info(f"📨 Processing message #{messages_processed} from queue: {message}")
                
                message_type = message.get('type')
                
                if message_type == 'login_success':
                    logger.info("🎉 Login success detected, updating session state...")
                    st.session_state.login_success = True
                    st.session_state.user_data = message.get('user_data')
                    st.session_state.session_token = message.get('session_token')
                    st.session_state.device_id = message.get('device_id')
                    
                    # Show success message and redirect
                    st.success("🎉 Login successful! Redirecting to dashboard...")
                    time.sleep(2)
                    st.rerun()
                    
                elif message_type == 'ws_connected':
                    st.session_state.ws_connected = True
                    logger.info("🔌 WebSocket connection status updated")
                    
                elif message_type == 'ws_confirmed':
                    st.session_state.ws_confirmed = True
                    logger.info("🔌 WebSocket connection confirmed")
                    
                elif message_type == 'error':
                    st.error(f"❌ WebSocket Error: {message.get('message')}")
                    
                elif message_type == 'disconnected':
                    st.session_state.ws_connected = False
                    st.warning("🔌 WebSocket disconnected. Attempting to reconnect...")
                    
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"❌ Error processing messages: {e}")
        
        # Display status
        expires_at = datetime.fromisoformat(qr_data['expires_at'])
        time_left = expires_at - datetime.utcnow()
        
        if time_left.total_seconds() > 0:
            minutes_left = int(time_left.total_seconds() // 60)
            seconds_left = int(time_left.total_seconds() % 60)
            
            # Enhanced WebSocket status
            ws_status = "❌ Disconnected"
            if st.session_state.get('ws_connected', False):
                if st.session_state.get('ws_confirmed', False):
                    ws_status = "✅ Connected & Ready"
                else:
                    ws_status = "🔄 Connected (Confirming...)"
            elif hasattr(st.session_state, 'ws_client'):
                ws_status = "🔄 Connecting..."
            
            st.markdown(f"""
            <div class="status-waiting">
                <div class="loading-spinner"></div>
                Waiting for mobile scan... ({ws_status}) <br>
                Expires in {minutes_left}m {seconds_left}s
            </div>
            """, unsafe_allow_html=True)
            
            # Auto-refresh every 2 seconds (faster for better UX)
            time.sleep(2)
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
    
    logger.info(f"🎯 Rendering dashboard for user: {user_data}")
    
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
            for key in ['qr_data', 'ws_client', 'message_queue', 'login_success', 'user_data', 'session_token', 'ws_connected', 'ws_confirmed']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            # Disconnect WebSocket
            if hasattr(st.session_state, 'ws_client') and st.session_state.ws_client:
                st.session_state.ws_client.disconnect()
            
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
    
    # Debug info - enhanced for better troubleshooting
    if st.checkbox("🔍 Debug Info", value=False):
        st.write("**Session State:**")
        debug_state = {}
        for key, value in st.session_state.items():
            if key == 'message_queue':
                debug_state[key] = f"Queue with {value.qsize()} messages" if hasattr(value, 'qsize') else "Queue object"
            elif key == 'ws_client':
                if hasattr(value, 'connected'):
                    debug_state[key] = f"WebSocket client (connected: {value.connected})"
                else:
                    debug_state[key] = "WebSocket client object"
            else:
                debug_state[key] = value
        
        st.json(debug_state)
        
        # WebSocket diagnostics
        if hasattr(st.session_state, 'ws_client'):
            st.write("**WebSocket Status:**")
            ws = st.session_state.ws_client
            st.write(f"- Connected: {ws.connected}")
            st.write(f"- Running: {ws.running}")
            st.write(f"- Session ID: {ws.session_id}")
    
    # Check login status
    if st.session_state.login_success and 'user_data' in st.session_state and st.session_state.user_data:
        render_dashboard()
    else:
        render_qr_login_page()

if __name__ == "__main__":
    main()