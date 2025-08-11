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

# Configuration - FIXED WebSocket URL
API_BASE_URL = "https://qr-auth-server.onrender.com"  # Removed trailing slash
WS_BASE_URL = "wss://qr-auth-server.onrender.com"      # Changed to wss:// for secure WebSocket

# Custom CSS for beautiful UI
def load_custom_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    /* Hide Streamlit elements */
    .stDeployButton {display: none;}
    header[data-testid="stHeader"] {display: none;}
    .stMainBlockContainer {padding-top: 2rem;}
    
    /* Header Styles */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 3rem;
        text-align: center;
        color: white;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    .main-subtitle {
        font-size: 1.3rem;
        font-weight: 300;
        opacity: 0.95;
        position: relative;
        z-index: 1;
    }
    
    /* QR Code Section */
    .qr-section {
        background: white;
        border-radius: 24px;
        padding: 3rem;
        text-align: center;
        box-shadow: 0 25px 50px rgba(0,0,0,0.1);
        border: 1px solid #f0f0f0;
        margin: 2rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .qr-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    .qr-title {
        font-size: 2rem;
        font-weight: 600;
        color: white;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    
    .qr-description {
        color: #7f8c8d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        line-height: 1.6;
        max-width: 500px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .qr-container {
        display: inline-block;
        padding: 2rem;
        background: linear-gradient(145deg, #f8f9fa, #e9ecef);
        border-radius: 20px;
        box-shadow: 
            inset 5px 5px 10px #d1d5db,
            inset -5px -5px 10px #ffffff,
            0 10px 30px rgba(0,0,0,0.1);
        margin: 2rem 0;
        transition: transform 0.3s ease;
    }
    
    .qr-container:hover {
        transform: translateY(-5px);
    }
    
    /* Status Cards */
    .status-card {
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
        font-weight: 500;
        font-size: 1.1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .status-card:hover {
        transform: translateY(-2px);
    }
    
    .status-waiting {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        color: #8b4513;
        border-left: 4px solid #ff9500;
    }
    
    .status-success {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #155724;
        border-left: 4px solid #28a745;
    }
    
    .status-error {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        color: #721c24;
        border-left: 4px solid #dc3545;
    }
    
    /* Dashboard Styles */
    .dashboard-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        margin: 1.5rem 0;
        border: 1px solid #f0f0f0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    /*.dashboard-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }*/
    
    .welcome-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .welcome-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: float 8s ease-in-out infinite reverse;
    }
    
    .welcome-title {
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .welcome-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
    }
    
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    /*.info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }*/
    
    .info-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 2px solid #dee2e6;
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .info-card:hover {
        border-color: #667eea;
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
    }
    
    .info-label {
        font-size: 0.9rem;
        color: #6c757d;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .info-value {
        font-size: 1.1rem;
        color: #2c3e50;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .device-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .device-item {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .device-item:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    .device-info {
        flex: 1;
    }
    
    .device-name {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .device-details {
        color: #7f8c8d;
        font-size: 0.9rem;
        margin-bottom: 0.3rem;
    }
    
    .device-status {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-active {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .status-inactive {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    .device-actions {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        cursor: pointer;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Action Button Variants */
    /*.action-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }*/
    
    .action-button {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 2px solid #dee2e6;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        color: #495057;
    }
    
    .action-button:hover {
        border-color: #667eea;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
    }
    
    .action-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    .action-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    
    .action-desc {
        font-size: 0.9rem;
        opacity: 0.8;
    }
    
    /* Loading Animation */
    .loading-spinner {
        display: inline-block;
        width: 24px;
        height: 24px;
        border: 3px solid rgba(102, 126, 234, 0.3);
        border-top: 3px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-right: 10px;
        vertical-align: middle;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Pulse Animation */
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
        display: inline-block;
    }
    
    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #7f8c8d;
    }
    
    .empty-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    
    .empty-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .empty-desc {
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem 1rem;
        }
        
        .main-title {
            font-size: 2.5rem;
        }
        
        .qr-section {
            padding: 2rem 1rem;
        }
        
        .dashboard-card {
            padding: 1.5rem;
        }
        
        .stats-grid {
            grid-template-columns: 1fr;
        }
        
        .device-item {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
        }
        
        .device-actions {
            width: 100%;
            justify-content: flex-end;
        }
    }
    
    /* Dark mode friendly adjustments */
    @media (prefers-color-scheme: dark) {
        .main {
            background: linear-gradient(135deg, #1a1a1a 0%, #2d3748 100%);
        }
        
        .dashboard-card, .qr-section {
            background: #2d3748;
            border-color: #4a5568;
            color: #e2e8f0;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# WebSocket Client Class with IMPROVED connection handling
class WebSocketClient:
    def __init__(self, message_queue):
        self.ws = None
        self.connected = False
        self.session_id = None
        self.message_queue = message_queue
        self.running = False
        self.connection_thread = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
    def connect(self, session_id):
        try:
            self.session_id = session_id
            self.running = True
            self.reconnect_attempts = 0
            ws_url = f"{WS_BASE_URL}/ws/{session_id}"
            logger.info(f"🔌 Connecting to WebSocket: {ws_url}")
            
            # Add headers for better compatibility with hosted services
            headers = {
                'User-Agent': 'StreamlitWebSocketClient/1.0'
            }
            
            self.ws = websocket.WebSocketApp(
                ws_url,
                header=headers,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            
            # Run in separate thread
            def run_ws():
                try:
                    # Increased ping interval for better stability on hosted services
                    self.ws.run_forever(
                        ping_interval=60,
                        ping_timeout=30,
                        ping_payload="ping"
                    )
                except Exception as e:
                    logger.error(f"❌ WebSocket run_forever error: {e}")
                    if self.running and self.reconnect_attempts < self.max_reconnect_attempts:
                        self.reconnect_attempts += 1
                        logger.info(f"🔄 Attempting reconnection {self.reconnect_attempts}/{self.max_reconnect_attempts}")
                        time.sleep(5)  # Wait before reconnecting
                        self.connect(session_id)  # Recursive reconnection
            
            self.connection_thread = threading.Thread(target=run_ws, daemon=True)
            self.connection_thread.start()
            
        except Exception as e:
            logger.error(f"❌ WebSocket connection error: {str(e)}")
            self.message_queue.put({"type": "error", "message": str(e)})
    
    def on_open(self, ws):
        self.connected = True
        self.reconnect_attempts = 0  # Reset reconnection counter on successful connection
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
        logger.info(f"🔌 WebSocket closed: {close_status_code} - {close_msg}")
        self.message_queue.put({"type": "disconnected", "code": close_status_code, "message": close_msg})
        
        # Attempt reconnection if we're still supposed to be running
        if self.running and self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            logger.info(f"🔄 Attempting reconnection {self.reconnect_attempts}/{self.max_reconnect_attempts}")
            time.sleep(3)
            self.connect(self.session_id)

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
        response = requests.post(f"{API_BASE_URL}/qr/generate", json={}, timeout=10)
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
        response = requests.get(f"{API_BASE_URL}/devices", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def revoke_device(token, device_id):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(f"{API_BASE_URL}/devices/{device_id}", headers=headers, timeout=10)
        return response.status_code == 200
    except:
        return False

# UI Components
def render_header():
    st.markdown("""
    <div class="main-header">
        <div class="main-title">🔐 SecureLink</div>
        <div class="main-subtitle">QR code device authentication</div>
    </div>
    """, unsafe_allow_html=True)

def render_qr_login_page():
    st.markdown("""
    <div class="qr-section">
        <div class="qr-title">
            📱 Connect Your Device
        </div>
        <div class="qr-description">
            Scan the QR code below with your mobile device to establish a secure connection. 
            Your device will be authenticated instantly without passwords.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate New QR Code Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Generate New QR Code", use_container_width=True, help="Generate a fresh QR code"):
            # Properly disconnect existing WebSocket
            if hasattr(st.session_state, 'ws_client') and st.session_state.ws_client:
                st.session_state.ws_client.disconnect()
            
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
        with st.spinner("🔄 Generating secure QR code..."):
            qr_data = generate_qr_session()
            if qr_data:
                st.session_state.qr_data = qr_data
                st.session_state.login_success = False
                st.session_state.ws_connected = False
                st.session_state.ws_confirmed = False
                
                # Initialize WebSocket connection with improved error handling
                logger.info("🔌 Initializing WebSocket connection...")
                try:
                    ws_client = WebSocketClient(st.session_state.message_queue)
                    ws_client.connect(qr_data['session_id'])
                    st.session_state.ws_client = ws_client
                    
                    # Wait a moment for connection
                    time.sleep(2)
                    st.rerun()
                except Exception as ws_error:
                    logger.error(f"❌ WebSocket initialization error: {ws_error}")
                    st.error(f"❌ WebSocket connection failed: {ws_error}")
            else:
                st.error("❌ Failed to generate QR code. Please check your server connection.")
                return
    
    if 'qr_data' in st.session_state and st.session_state.qr_data:
        qr_data = st.session_state.qr_data
        
        # Display QR Code in beautiful container
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="qr-container">', unsafe_allow_html=True)
            
            # Decode base64 QR code
            try:
                qr_image_data = base64.b64decode(qr_data['qr_code_data'])
                qr_image = Image.open(io.BytesIO(qr_image_data))
                st.image(qr_image, width=300, caption="Scan with your mobile device")
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
                    st.success("🎉 Authentication successful! Redirecting to dashboard...")
                    if hasattr(st.session_state, 'ws_client') and st.session_state.ws_client:
                        st.session_state.ws_client.disconnect()
                    time.sleep(2)
                    st.rerun()
                    
                elif message_type == 'ws_connected':
                    st.session_state.ws_connected = True
                    logger.info("🔌 WebSocket connection status updated")
                    
                elif message_type == 'ws_confirmed':
                    st.session_state.ws_confirmed = True
                    logger.info("🔌 WebSocket connection confirmed")
                    
                elif message_type == 'error':
                    st.error(f"❌ Connection Error: {message.get('message')}")
                    
                elif message_type == 'disconnected':
                    st.session_state.ws_connected = False
                    st.warning("🔌 Connection interrupted. Attempting to reconnect...")
                    
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"❌ Error processing messages: {e}")
        
        # Display status with improved UI
        expires_at = datetime.fromisoformat(qr_data['expires_at'])
        time_left = expires_at - datetime.utcnow()
        
        if time_left.total_seconds() > 0:
            minutes_left = int(time_left.total_seconds() // 60)
            seconds_left = int(time_left.total_seconds() % 60)
            
            # Enhanced WebSocket status
            if st.session_state.get('ws_connected', False):
                if st.session_state.get('ws_confirmed', False):
                    status_icon = "✅"
                    status_text = "Connected & Ready"
                    status_class = "status-success"
                else:
                    status_icon = "🔄"
                    status_text = "Connected (Confirming...)"
                    status_class = "status-waiting"
            elif hasattr(st.session_state, 'ws_client'):
                status_icon = "🔄"
                status_text = "Connecting..."
                status_class = "status-waiting"
            else:
                status_icon = "❌"
                status_text = "Disconnected"
                status_class = "status-error"
            
            st.markdown(f"""
            <div class="status-card {status_class}">
                <div class="loading-spinner pulse"></div>
                <strong>{status_icon} {status_text}</strong><br>
                Waiting for device authentication...<br>
                <small>⏱️ Expires in {minutes_left}m {seconds_left}s</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Auto-refresh every 3 seconds for better stability
            time.sleep(3)
            st.rerun()
        else:
            st.markdown("""
            <div class="status-card status-error">
                <strong>⏰ QR Code Expired</strong><br>
                This QR code has expired for security. Please generate a new one.
            </div>
            """, unsafe_allow_html=True)

def render_dashboard():
    user_data = st.session_state.user_data
    session_token = st.session_state.session_token
    
    logger.info(f"🎯 Rendering dashboard for user: {user_data}")
    
    # Welcome Section
    st.markdown(f"""
    <div class="welcome-section">
        <div class="welcome-title">Welcome back, {user_data['username']}! 👋</div>
        <div class="welcome-subtitle">Your secure authentication session is active</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get user devices for stats
    devices = get_user_devices(session_token)
    active_devices = [d for d in devices if d['is_active']]
    login_time = datetime.now().strftime("%H:%M")
    
    # Stats Section
    st.markdown("""
    <div class="stats-grid">
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(active_devices)}</div>
            <div class="stat-label">📱 Active Devices</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{login_time}</div>
            <div class="stat-label">🕒 Login Time</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">🛡️</div>
            <div class="stat-label">✅ Secure</div>
        </div>
        """, unsafe_allow_html=True)
    
    # User Information Section
    st.markdown("""
    <div class="dashboard-card">
        <h3 class="section-header">👤 User Information</h3>
        <div class="info-grid">
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">Username</div>
            <div class="info-value">{user_data['username']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">User ID</div>
            <div class="info-value">{user_data['id']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">Email Address</div>
            <div class="info-value">{user_data['email']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">Account Status</div>
            <div class="info-value">✅ Active</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Linked Devices Section
    st.markdown("""
    <div class="dashboard-card">
        <h3 class="section-header">📱 Linked Devices</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if devices:
        for device in devices:
            st.write("")
            status_class = "status-active" if device['is_active'] else "status-inactive"
            status_text = "Active" if device['is_active'] else "Inactive"
            status_icon = "🟢" if device['is_active'] else "🔴"
            
            created_date = datetime.fromisoformat(device['created_at']).strftime("%b %d, %Y at %H:%M")
            last_active = datetime.fromisoformat(device['last_active']).strftime("%b %d, %Y at %H:%M")
            
            # Create device item
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"""
                <div class="device-item">
                    <div class="device-info">
                        <div class="device-name">
                            {status_icon} {device['device_name']}
                        </div>
                        <div class="device-details">📅 Created: {created_date}</div>
                        <div class="device-details">🕒 Last Active: {last_active}</div>
                        <div class="device-status {status_class}">{status_text}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if device['is_active']:
                    if st.button(f"🗑️ Revoke", key=f"revoke_{device['id']}", help="Revoke device access", use_container_width=True):
                        with st.spinner("Revoking device..."):
                            if revoke_device(session_token, device['device_id']):
                                st.success("✅ Device revoked successfully!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Failed to revoke device")
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📱</div>
            <div class="empty-title">No Linked Devices</div>
            <div class="empty-desc">You haven't linked any devices yet. Scan a QR code to get started!</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick Actions Section
    st.markdown("""
    <div class="dashboard-card">
        <h3 class="section-header">⚡ Quick Actions</h3>
        <div class="action-grid">
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Data", use_container_width=True, help="Refresh device list and user data"):
            with st.spinner("Refreshing..."):
                time.sleep(1)
                st.rerun()
    
    with col2:
        if st.button("📱 Link New Device", use_container_width=True, help="Generate new QR code to link another device"):
            # Disconnect existing WebSocket
            if hasattr(st.session_state, 'ws_client') and st.session_state.ws_client:
                st.session_state.ws_client.disconnect()
            
            # Reset to QR generation
            for key in ['qr_data', 'ws_client', 'message_queue', 'login_success', 'user_data', 'session_token', 'ws_connected', 'ws_confirmed']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    with col3:
        if st.button("🚪 Sign Out", use_container_width=True, help="Sign out and clear session", type="secondary"):
            # Disconnect WebSocket
            if hasattr(st.session_state, 'ws_client') and st.session_state.ws_client:
                st.session_state.ws_client.disconnect()
            
            # Clear session with confirmation
            with st.spinner("Signing out..."):
                time.sleep(1)
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.success("✅ Signed out successfully!")
                time.sleep(1)
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
    
    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Check login status and render appropriate page
    if st.session_state.login_success and 'user_data' in st.session_state and st.session_state.user_data:
        render_dashboard()
    else:
        render_qr_login_page()
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #7f8c8d; font-size: 0.9rem; margin-top: 3rem;">
        <hr style="border: none; height: 1px; background: linear-gradient(90deg, transparent, #dee2e6, transparent); margin: 2rem 0;">
        🔐 SecureLink - Secure QR Code Authentication System<br>
        <small>• Protected by end-to-end encryption •</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()