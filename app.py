import streamlit as st
import random
import string
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="Have fun! :)",
    layout="centered"
)

# Database setup
Base = declarative_base()

class RandomString(Base):
    __tablename__ = 'random_strings'
    
    id = Column(Integer, primary_key=True)
    string_value = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    st.error("Database connection not available")
    st.stop()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def save_string_to_db(string_value):
    """Save the generated string to the database"""
    session = SessionLocal()
    try:
        new_string = RandomString(string_value=string_value)
        session.add(new_string)
        session.commit()
        return new_string.id
    except Exception as e:
        session.rollback()
        st.error(f"Database error: {e}")
        return None
    finally:
        session.close()

def get_string_count():
    """Get the total count of strings in the database"""
    session = SessionLocal()
    try:
        count = session.query(RandomString).count()
        return count
    except Exception as e:
        st.error(f"Database error: {e}")
        return 0
    finally:
        session.close()

# Custom CSS for white and black theme
st.markdown("""
<style>
    /* Hide Streamlit menu, header, and footer */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stAppHeader {display: none;}
    header {visibility: hidden;}
    
    .main {
        background-color: #000000;
        color: #ffffff;
    }
    
    .stApp {
        background-color: #000000;
    }
    
    .theme-toggle {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 999;
    }
    
    .random-string-container {
        background-color: #ffffff;
        color: #000000;
        padding: 30px;
        border-radius: 10px;
        text-align: center;
        margin: 20px 0;
        border: 2px solid #333333;
    }
    
    .random-string-text {
        font-family: 'Courier New', monospace;
        font-size: 24px;
        font-weight: bold;
        letter-spacing: 2px;
        word-break: break-all;
        margin: 10px 0;
    }
    
    .title-text {
        color: #ffffff;
        text-align: center;
        font-size: 2.5rem;
        margin-bottom: 30px;
    }
    
    .subtitle-text {
        color: #cccccc;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 30px;
    }
    
    .white-theme .main {
        background-color: #ffffff;
        color: #000000;
    }
    
    .white-theme .stApp {
        background-color: #ffffff;
    }
    
    .white-theme .title-text {
        color: #000000;
    }
    
    .white-theme .subtitle-text {
        color: #333333;
    }
    
    .white-theme .random-string-container {
        background-color: #000000;
        color: #ffffff;
        border: 2px solid #cccccc;
    }
    
    .refresh-info {
        color: #888888;
        text-align: center;
        font-style: italic;
        margin-top: 20px;
    }
    
    .white-theme .refresh-info {
        color: #666666;
    }
</style>
""", unsafe_allow_html=True)

def generate_random_string(length=20):
    """Generate a random alphanumeric string of specified length"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Set default theme to black (no theme switching)
st.session_state.theme = 'black'

# Generate only one key - check if we already have one in the database
if 'random_string' not in st.session_state:
    # Check if we already have a key in the database
    total_existing = get_string_count()
    if total_existing == 0:
        # Generate the first and only key
        st.session_state.random_string = generate_random_string()
        # Save to database
        string_id = save_string_to_db(st.session_state.random_string)
        if string_id is not None:
            st.session_state.string_id = string_id
    else:
        # Use the existing key from database
        session = SessionLocal()
        try:
            existing_string = session.query(RandomString).first()
            if existing_string:
                st.session_state.random_string = existing_string.string_value
                st.session_state.string_id = existing_string.id
        except Exception as e:
            st.error(f"Database error: {e}")
        finally:
            session.close()

# Main content
st.markdown('<h1 class="title-text">Have fun! :)</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Your key:</p>', unsafe_allow_html=True)

# Display the random string in a styled container
st.markdown(f"""
<div class="random-string-container">
    <div class="random-string-text">{st.session_state.random_string}</div>
</div>
""", unsafe_allow_html=True)




