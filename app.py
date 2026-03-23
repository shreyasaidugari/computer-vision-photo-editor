import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import io

# PAGE CONFIG 
st.set_page_config(page_title="Photo Editor", layout="wide")

# UI STYLE 
st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        rgba(0, 0, 0, 0.4),
        rgba(0, 0, 0, 0.4)
    ),
    url("https://images.unsplash.com/photo-1501785888041-af3ef285b470");
    background-size: cover;
    background-position: center;
}

/* Center Title */
.title-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 30vh;
    text-align: center;
}

.title-container h1 {
    color: white;
    font-size: 45px;
}

.title-container p {
    color: white;
    font-size: 18px;
}

/* Instructions box */
.instructions {
    background-color: rgba(255, 255, 255, 0.2);
    padding: 15px;
    border-radius: 10px;
    color: white;
    backdrop-filter: blur(5px);
    margin-bottom: 20px;
}

/* Camera box only white */
section[data-testid="stCameraInput"] {
    background-color: white !important;
    padding: 15px;
    border-radius: 12px;
    width: 320px;
    margin: auto;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

section[data-testid="stCameraInput"] label {
    color: black !important;
}

/* Text visibility */
label, h3 {
    color: white !important;
}

section[data-testid="stSidebar"] * {
    color: black !important;
}

/* Download button */
.stDownloadButton>button {
    background-color: #2196f3;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# TITLE 
st.markdown("""
<div class="title-container">
    <h1>📸 Photo Editor</h1>
    <p>Simple and smart image editing</p>
</div>
""", unsafe_allow_html=True)

# INSTRUCTIONS 
st.markdown("""
<div class="instructions">
<h4>Instructions</h4>
<ul>
<li>Upload an image or use camera</li>
<li>Click "Take Photo" to open camera</li>
<li>Adjust settings from sidebar</li>
<li>Download edited image</li>
</ul>
</div>
""", unsafe_allow_html=True)

# INPUT 
st.markdown("### Choose Input")

if "camera_on" not in st.session_state:
    st.session_state.camera_on = False

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.session_state.camera_on = False

if st.button("📷 Take Photo"):
    st.session_state.camera_on = True

camera_image = None

if st.session_state.camera_on:
    camera_image = st.camera_input("Camera")

#  LOAD IMAGE
if uploaded_file is not None:
    img = Image.open(uploaded_file)

elif camera_image is not None:
    img = Image.open(camera_image)

else:
    st.info("Upload an image or click 'Take Photo'")
    st.stop()

# SIDEBAR 
st.sidebar.header("Controls")

width = st.sidebar.slider("Width", 100, 800, img.width)
height = st.sidebar.slider("Height", 100, 800, img.height)
img = img.resize((width, height))

brightness = st.sidebar.slider("Brightness", 0.5, 3.0, 1.0)
img = ImageEnhance.Brightness(img).enhance(brightness)

contrast = st.sidebar.slider("Contrast", 0.5, 3.0, 1.0)
img = ImageEnhance.Contrast(img).enhance(contrast)

img_np = np.array(img)

#  FILTER 
option = st.sidebar.selectbox("Filter", [
    "None", "Grayscale", "Blur", "Warm",
    "Sharpen", "Edge", "Sketch"
])

# FILTERS 
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

# DISPLAY 
col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3>Original</h3>", unsafe_allow_html=True)
    st.image(img)

with col2:
    st.markdown("<h3>Edited</h3>", unsafe_allow_html=True)
    st.image(img_np)

# DOWNLOAD 
result = Image.fromarray(img_np)

buf = io.BytesIO()
result.save(buf, format="PNG")

st.download_button(
    label="Download Image",
    data=buf.getvalue(),
    file_name="edited.png",
    mime="image/png"
)
