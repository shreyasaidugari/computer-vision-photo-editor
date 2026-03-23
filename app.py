import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import io

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Photo Editor", layout="wide")

# -------------------- UI STYLE --------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        rgba(0, 0, 0, 0.3),
        rgba(0, 0, 0, 0.3)
    ),
    url("https://images.unsplash.com/photo-1501785888041-af3ef285b470");
    background-size: cover;
    background-position: center;
}

h1 {
    text-align: center;
    color: white;
}

label, .stSlider, .stSelectbox {
    color: white !important;
}

.stDownloadButton>button {
    background-color: #2196f3;
    color: white;
    border-radius: 8px;
}

/* White input box */
.input-box {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# -------------------- TITLE --------------------
st.markdown("<h1>Photo Editor App</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center; color:white;'>Simple and smart image editing</h4>", unsafe_allow_html=True)

st.divider()

# -------------------- INSTRUCTIONS --------------------
st.markdown("""
<div style="
background-color: rgba(255, 255, 255, 0.2);
padding: 15px;
border-radius: 10px;
color: white;
backdrop-filter: blur(5px);
">
<h4>Instructions</h4>
<ul>
<li>Upload an image or use camera</li>
<li>Click "Take Photo" to open camera</li>
<li>If camera does not work, try Chrome</li>
</ul>
</div>
""", unsafe_allow_html=True)

# -------------------- INPUT SECTION --------------------
st.markdown('<div class="input-box">', unsafe_allow_html=True)
st.markdown("<h4 style='color:black;'>Choose Input</h4>", unsafe_allow_html=True)

# Initialize state
if "camera_on" not in st.session_state:
    st.session_state.camera_on = False

# Upload
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

# If upload → turn OFF camera
if uploaded_file:
    st.session_state.camera_on = False

# Button to open camera
if st.button("📷 Take Photo"):
    st.session_state.camera_on = True

camera_image = None

# Show camera only when button clicked
if st.session_state.camera_on:
    camera_image = st.camera_input("Camera")

st.markdown('</div>', unsafe_allow_html=True)

# -------------------- LOAD IMAGE --------------------
if uploaded_file is not None:
    img = Image.open(uploaded_file)

elif camera_image is not None:
    img = Image.open(camera_image)

else:
    st.info("Upload an image or click 'Take Photo'")
    st.stop()

# -------------------- SIDEBAR --------------------
st.sidebar.header("Controls")

# Resize
width = st.sidebar.slider("Width", 100, 800, img.width)
height = st.sidebar.slider("Height", 100, 800, img.height)
img = img.resize((width, height))

# Brightness
brightness = st.sidebar.slider("Brightness", 0.5, 3.0, 1.0)
img = ImageEnhance.Brightness(img).enhance(brightness)

# Contrast
contrast = st.sidebar.slider("Contrast", 0.5, 3.0, 1.0)
img = ImageEnhance.Contrast(img).enhance(contrast)

# Convert to numpy
img_np = np.array(img)

# -------------------- FILTER --------------------
option = st.sidebar.selectbox("Filter", [
    "None", "Grayscale", "Blur", "Warm",
    "Sharpen", "Edge", "Sketch"
])

# -------------------- FILTERS --------------------
if option == "Grayscale":
    img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

elif option == "Blur":
    img_np = cv2.GaussianBlur(img_np, (15, 15), 0)

elif option == "Warm":
    r, g, b = cv2.split(img_np)
    r = cv2.add(r, 40)
    img_np = cv2.merge((r, g, b))

elif option == "Sharpen":
    kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
    img_np = cv2.filter2D(img_np, -1, kernel)

elif option == "Edge":
    img_np = cv2.Canny(img_np, 100, 200)

elif option == "Sketch":
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    inv = 255 - gray
    blur = cv2.GaussianBlur(inv, (21, 21), 0)
    img_np = cv2.divide(gray, 255 - blur, scale=256)

# -------------------- DISPLAY --------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Original")
    st.image(img)

with col2:
    st.subheader("Edited")
    st.image(img_np)

# -------------------- DOWNLOAD --------------------
result = Image.fromarray(img_np)

buf = io.BytesIO()
result.save(buf, format="PNG")

st.download_button(
    label="Download Image",
    data=buf.getvalue(),
    file_name="edited.png",
    mime="image/png"
)