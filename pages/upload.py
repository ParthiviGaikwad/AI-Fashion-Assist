import streamlit as st
from streamlit.components.v1 import html
import os
from PIL import Image
import uuid

# Set page configuration as the first command in the script
st.set_page_config(
    page_title="LuxeVogue - Find Your Style",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ensure the img folder exists
IMG_DIR = "img"
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# Custom CSS with full-screen background image
def inject_css():
    st.markdown("""
    <style>
    /* Reset and base styles */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        text-decoration: none;
        list-style: none;
    }

    /* Font imports */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Roboto:wght@300;400&display=swap');

    /* Full-screen background */
    body {
        font-family: 'Roboto', sans-serif;
        color: white;
        background-image: url('https://images.unsplash.com/photo-1483985988355-763728e1935b');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        min-height: 100vh;
    }

    /* Semi-transparent overlay for content */
    .content-overlay {
        background-color: rgba(0, 0, 0, 0.7);
        min-height: 100vh;
        padding: 20px;
        display: flex;
        flex-direction: column;
    }

    /* Header styles */
    header {
        background-color: rgba(51, 51, 51, 0.8);
        padding: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .logo {
        font-family: 'Playfair Display', serif;
        font-size: 28px;
        font-weight: 700;
    }

    nav ul {
        display: flex;
        gap: 15px;
    }

    nav ul li a {
        color: white;
        padding: 8px 16px;
        transition: background-color 0.3s ease;
    }

    nav ul li a:hover {
        background-color: #555;
        border-radius: 4px;
    }

    /* Upload content styles */
    .upload-content {
        max-width: 800px;
        margin: 40px auto;
        padding: 30px;
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        color: #333;
        text-align: center;
        flex-grow: 1;
    }

    .upload-content h1 {
        font-family: 'Playfair Display', serif;
        color: #e91e63;
        margin-bottom: 20px;
    }

    /* Button styles */
    .stButton>button {
        background-color: #e91e63 !important;
        color: white !important;
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 5px !important;
        font-size: 16px !important;
        transition: background-color 0.3s ease !important;
    }

    .stButton>button:hover {
        background-color: #c2185b !important;
    }

    /* Image preview */
    .image-preview {
        max-width: 100%;
        border-radius: 8px;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }

    /* Footer */
    footer {
        background-color: rgba(51, 51, 51, 0.8);
        color: white;
        text-align: center;
        padding: 15px;
        margin-top: auto;
    }

    /* Streamlit overrides */
    .stApp {
        padding: 0 !important;
        margin: 0 !important;
        background: transparent !important;
    }
    
    .stMarkdown {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* File uploader styling */
    .stFileUploader > label {
        display: none;
    }
    
    .stFileUploader > div {
        padding: 10px;
        border: 2px dashed #e91e63;
        border-radius: 8px;
        text-align: center;
        margin: 20px 0;
    }
    
    .stFileUploader > div:hover {
        border-color: #c2185b;
    }
    </style>
    """, unsafe_allow_html=True)

# Watson Assistant implementation
def watson_chat():
    return """
    <div id="watson-chat-container">
    <script>
      window.watsonAssistantChatOptions = {
        integrationID: "f42d8c8b-7fbf-472b-8522-443e0956d529",
        region: "au-syd",
        serviceInstanceID: "092e368d-f783-43c6-9a54-68b689045e9b",
        onLoad: function(instance) { 
          instance.render({
            target: document.getElementById('watson-chat-container'),
            serviceInstanceID: '092e368d-f783-43c6-9a54-68b689045e9b'
          }); 
        }
      };
      setTimeout(function(){
        const t = document.createElement('script');
        t.src = "https://web-chat.global.assistant.watson.appdomain.cloud/versions/" + 
               (window.watsonAssistantChatOptions.clientVersion || 'latest') + 
               "/WatsonAssistantChatEntry.js";
        document.head.appendChild(t);
      }, 1000);
    </script>
    </div>
    """

def get_nav_links(current_page):
    return f"""
    <nav>
        <ul>
            <li><a href="app.py" {'style="font-weight:bold;"' if current_page == 'home' else ''}>Home</a></li>
            <li><a href="collection.py" {'style="font-weight:bold;"' if current_page == 'collection' else ''}>Collections</a></li>
            <li><a href="about.py" {'style="font-weight:bold;"' if current_page == 'about' else ''}>About Us</a></li>
            <li><a href="contact.py" {'style="font-weight:bold;"' if current_page == 'contact' else ''}>Contact</a></li>
        </ul>
    </nav>
    """

def save_uploaded_file(uploaded_file):
    try:
        # Generate unique filename
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        save_path = os.path.join(IMG_DIR, unique_filename)
        
        # Open and convert image if needed
        image = Image.open(uploaded_file)
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        # Save image
        image.save(save_path)
        return save_path
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None

def upload_page():
    # Inject CSS first
    inject_css()
    
    
    # Header
    st.markdown(f"""
    <header>
        <div class="logo">LuxeVogue</div>
        {get_nav_links('upload')}
    </header>
    """, unsafe_allow_html=True)

    # Upload content
    st.markdown("""
    <div class="upload-content">
        <h1>Upload Your Style</h1>
        <p style="margin-bottom: 30px;">Get personalized fashion recommendations by uploading your photo</p>
    """, unsafe_allow_html=True)

    # File uploader
    uploaded_file = st.file_uploader(
        "Drag and drop or click to upload an image",
        type=["jpg", "jpeg", "png", "webp", "bmp", "tiff"],
        accept_multiple_files=False,
        key="file_uploader"
    )

    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Your Uploaded Image", use_container_width=True)

        
        # Save the file
        saved_path = save_uploaded_file(uploaded_file)
        
        if saved_path:
            st.success(f"Image saved successfully at: {saved_path}")
            
            # Store path in session state for recommendations page
            st.session_state['uploaded_image_path'] = saved_path
            
            # Recommendation button
            if st.button("Get Recommendations"):
                st.switch_page("pages/rec.py")
        else:
            st.error("Failed to save the image. Please try again.")

    st.markdown("</div>", unsafe_allow_html=True)  # Close upload-content
    

    # Footer
    st.markdown("""
    <footer>
        <p>&copy; 2024 LuxeVogue. All rights reserved.</p>
    </footer>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)  # Close content-overlay

    # Add Watson Chat
    html(watson_chat(), height=0, width=0)

def save_uploaded_file(uploaded_file):
    try:
        # Generate unique filename
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        save_path = os.path.join(IMG_DIR, unique_filename)
        
        # Open and convert image if needed
        image = Image.open(uploaded_file)
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        # Save image
        image.save(save_path)
        
        # Save the uploaded image path to a .txt file
        txt_file_path = os.path.join(IMG_DIR, "uploaded_image_path.txt")
        
        # Check if the file exists and delete it if it does
        if os.path.exists(txt_file_path):
            os.remove(txt_file_path)
        
        # Write the new image path to the file
        with open(txt_file_path, 'w') as file:
            file.write(save_path)
        
        return save_path
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None


def main():
    upload_page()

if __name__ == "__main__":
    main()