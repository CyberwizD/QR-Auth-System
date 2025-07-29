import cv2
import streamlit as st
import pyzbar.pyzbar as decode

# Scan the QR code
@st.cache_data
def scan_qr():
    # Load the image containing the QR code
    img = cv2.imread("./assets/qrcode.png")

    # Decode the QR code
    img_data = decode.decode(img)

    if img_data:
        # Extract the data from the QR code
        data = img_data[0].data.decode("utf-8")
        st.write(data)

        # Authentication Logic
    else:
        st.write("QR code not found")
