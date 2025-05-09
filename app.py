import streamlit as st
from streamlit.components.v1 import html
import time
import os

# Custom CSS with all original styles
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

    /* Body styles */
    body {
        font-family: 'Roboto', sans-serif;
        line-height: 1.6;
        color: #333;
        background-color: #f9f9f9;
    }

    /* Header styles */
    header {
        background-color: #333;
        color: white;
        padding: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: sticky;
        top: 0;
        z-index: 1000;
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

    /* Hero section */
    .hero {
        background-image: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url('https://images.unsplash.com/photo-1483985988355-763728e1935b');
        background-size: cover;
        background-position: center;
        height: 500px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        text-align: center;
    }

    .hero-content h1 {
        font-family: 'Playfair Display', serif;
        font-size: 48px;
        margin-bottom: 20px;
    }

    .hero-content p {
        font-size: 20px;
        margin-bottom: 30px;
    }

    .cta-button {
        background-color: #e91e63;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        font-size: 18px;
        transition: background-color 0.3s ease;
        display: inline-block;
        cursor: pointer;
    }

    .cta-button:hover {
        background-color: #c2185b;
    }

    /* Features section */
    .features {
        display: flex;
        justify-content: space-around;
        padding: 60px 20px;
        background-color: white;
        flex-wrap: wrap;
    }

    .feature-box {
        text-align: center;
        max-width: 300px;
        margin: 20px;
    }
                
    .center-button-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 30px;
    }


    .feature-box h2 {
        font-family: 'Playfair Display', serif;
        font-size: 24px;
        margin-bottom: 20px;
        color: #000000;
    }

    .feature-box p {
        font-size: 16px;
        color: #000000;
    }

    /* Footer */
    footer {
        background-color: #333;
        color: white;
        text-align: center;
        padding: 20px 0;
        font-size: 14px;
    }

    /* Streamlit overrides */
    .stApp {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .stMarkdown {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Chatbot specific styles */
    iframe[title="Web chat"] {
        display: block !important;
        position: fixed !important;
        right: 20px !important;
        bottom: 20px !important;
        width: 376px !important;
        height: 646px !important;
        border: none !important;
        z-index: 1001 !important;
    }
    
    /* Upload page styles */
    .upload-container {
        padding: 40px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Watson Assistant implementation with container
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

def home_page():
    # Header
    st.markdown(f"""
    <header>
        <div class="logo">LuxeVogue</div>
        {get_nav_links('home')}
    </header>
    """, unsafe_allow_html=True)

    # Hero Section - MODIFIED SECTION
    st.markdown(f"""
    <section class="hero">
        <div class="hero-content">
            <h1>Discover the Latest in Fashion</h1>
            <p>Stay ahead with LuxeVogue - where fashion meets elegance.</p>
        </div>
    </section>
    """, unsafe_allow_html=True)
    
    # Centered button using columns
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        # Add Streamlit button that will handle the navigation
        if st.button("Explore Now", key="explore_button", 
                    help="Click to upload your fashion images",
                    use_container_width=True):  # Make button full width of its column
            st.switch_page("pages/upload.py")

    # Features Section
    st.markdown("""
    <section class="features">
        <div class="feature-box">
            <h2>Latest Trends</h2>
            <p>Catch up on the latest fashion trends from around the world.</p>
        </div>
        <div class="feature-box">
            <h2>Exclusive Collections</h2>
            <p>Browse our handpicked collections tailored just for you.</p>
        </div>
        <div class="feature-box">
            <h2>Color Analysis</h2>
            <p>Find out which colors suit you best with our color analysis tool.</p>
        </div>
    </section>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <footer>
        <p>&copy; 2024 LuxeVogue. All rights reserved.</p>
    </footer>
    """, unsafe_allow_html=True)
def upload_page():
    # Header
    st.markdown(f"""
    <header>
        <div class="logo">LuxeVogue</div>
        {get_nav_links('upload')}
    </header>
    """, unsafe_allow_html=True)



    # Footer
    st.markdown("""
    <footer>
        <p>&copy; 2024 LuxeVogue. All rights reserved.</p>
    </footer>
    """, unsafe_allow_html=True)

def generic_page(title, current_page):
    # Header
    st.markdown(f"""
    <header>
        <div class="logo">LuxeVogue</div>
        {get_nav_links(current_page)}
    </header>
    """, unsafe_allow_html=True)

    # Page Content
    st.markdown(f"""
    <div class="page-content">
        <h1>{title}</h1>
        <p>Welcome to the {title} page. This content is under development.</p>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <footer>
        <p>&copy; 2024 LuxeVogue. All rights reserved.</p>
    </footer>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="LuxeVogue - Fashion Redefined",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Inject CSS first
    inject_css()
    
    # Get current script name to determine which page to show
    script_name = os.path.basename(__file__).lower()
    
    # Display the appropriate page based on script name
    if script_name == 'app.py':
        home_page()
    elif script_name == "C:\\Users\\PARTHIVI\\OneDrive\\Desktop\\PROJECT\\Aids\\Aids 8\\Major\\pages\\upload.py":
        upload_page()
    elif script_name == 'collection.py':
        generic_page("Collections", "collection")
    elif script_name == 'about.py':
        generic_page("About Us", "about")
    elif script_name == 'contact.py':
        generic_page("Contact", "contact")
    else:
        home_page()
    
    # Add Watson Chat with container
    html(watson_chat(), height=600)

if __name__ == "__main__":
    main()