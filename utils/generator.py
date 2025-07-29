import streamlit as st

# Data to encode in the QR code (unique session token)
session_token = "1234567890"

# Generate the QR code
@st.cache_data(ttl=600)
def generate_qr():
    import qrcode as qr
    qr = qr.QRCode(
        version=1,
        error_correction=qr.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(session_token)
    qr.make(fit=True)

    # Create an image from the QR code instance
    img = qr.make_image(fill_color="black", back_color="white")

    # Save the QR code as an image
    img.save("./assets/qrcode.png")