import streamlit as st
from utils import generator, scanner

st.set_page_config(
    page_title="QR Authentication System", 
    page_icon=":chart_with_upwards_trend:", 
    layout="wide"
)

st.logo(image="static/logo.png", size="small", link="https://github.com/CyberwizD/QR-Auth-System")

# Sidebar
st.sidebar.title("QR Auth")

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

st.sidebar.write("This is the sidebar.")
