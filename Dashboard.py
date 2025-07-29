import streamlit as st
import base64
import logging
from utils import generator, scanner

st.set_page_config(
    page_title="QR Authentication System", 
    page_icon=":chart_with_upwards_trend:", 
    layout="wide"
)

st.logo(image="static/logo.png", size="small", link="https://github.com/CyberwizD/QR-Auth-System")

# Sidebar
# Insert custom CSS for glowing effect
st.markdown(
    """
    <style>
    .cover-glow {
        width: 100%;
        height: auto;
        padding: 3px;
        box-shadow: 
            0 0 5px #330000,
            0 0 10px #660000,
            0 0 15px #990000,
            0 0 20px #CC0000,
            0 0 25px #FF0000,
            0 0 30px #FF3333,
            0 0 35px #FF6666;
        position: relative;
        z-index: -1;
        border-radius: 45px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def img_to_base64(image_path):
    """Convert image to base64."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        logging.error(f"Error converting image to base64: {str(e)}")
        return None

# Load and display sidebar image
img_path = "static/logo.png"
img_base64 = img_to_base64(img_path)
if img_base64:
    st.sidebar.markdown(
        f'<img src="data:image/png;base64,{img_base64}" class="cover-glow">',
        unsafe_allow_html=True,
    )

# Streamlit UI
st.title("QR Authentication System")
st.write("Link your device to the QR code below to access your account.")

tabs = st.tabs(["📝 Generate QR Code", "🔗 Scan QR Code"])

# Generate QR Code Tab
with tabs[0]:
    st.subheader("This section will generate the QR code.")

    generate_btn = st.button("Generate QR Code")
    if generate_btn:
        # Generate QR code
        generator.generate_qr()

        st.success("QR code generated successfully!")

        # Display QR code
        st.image("./assets/qrcode.png", use_column_width=True)

# Scan QR Code Tab
with tabs[1]:
    st.subheader("This section will scan the QR code.")

    scan_btn = st.button("Scan QR Code")
    if scan_btn:
        # Scan QR code
        scanner.scan_qr()

        st.success("QR code scanned successfully!")

