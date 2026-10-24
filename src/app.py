import streamlit as st
import google.generativeai as genai
import requests
import PyPDF2
import pdfplumber
import io
import os
import tempfile
from deep_translator import GoogleTranslator

# ============================================
# PROFESSIONAL UI CONFIGURATION
# ============================================
st.set_page_config(
    page_title="ZaLingo Academic",
    page_icon="favicon.png", # If you don't have an icon, you can remove this line entirely
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for a clean, enterprise look
st.markdown("""
<style>
    /* Typography and Background */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #FFFFFF;
    }
    
    /* Hide default Streamlit elements */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main Title Styling */
    h1 {
        color: #111827;
        font-weight: 700;
        letter-spacing: -0.025em;
    }
    
    h3 {
        color: #4B5563;
        font-weight: 400;
    }
    
    /* Input fields */
    .stTextInput>div>div>input {
        border-radius: 6px;
        border: 1px solid #D1D5DB;
        padding: 12px;
        font-size: 14px;
    }
    
    /* Primary Button */
    .stButton>button {
        background-color: #111827;
        color: #FFFFFF;
        border-radius: 6px;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 500;
        font-size: 16px;
        width: 100%;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #374151;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 500;
        color: #6B7280;
    }
    .stTabs [aria-selected="true"] {
        color: #111827;
        border-bottom-color: #111827;
    }
    
    /* File uploader */
    [data-testid="stFileUploadDropzone"] {
        border: 1px dashed #D1D5DB;
        border-radius: 8px;
        background-color: #F9FAFB;
        padding: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# MAIN UI
# ============================================

st.write("") 
st.title("ZaLingo Academic")
st.markdown("### Multilingual Research Summarization")
st.write("") 

# Sidebar Settings (No Emojis)
with st.sidebar:
    st.header("Configuration")
    
    api_provider = st.radio("API Provider", ["Google Gemini", "Mistral AI"])
    
    if api_provider == "Google Gemini":
        st.markdown("[Get a free Gemini API Key](https://aistudio.google.com/apikey)")
        api_key = st.text_input("API Key", type="password", placeholder="Enter API key")
    else:
        st.markdown("[Get a free Mistral API Key](https://console.mistral.ai)")
        api_key = st.text_input("API Key", type="password", placeholder="Enter API key")
        
    st.divider()
    
    language = st.selectbox(
        "Output Language",
        ["English", "Afrikaans", "isiZulu", "isiXhosa", "Sepedi", "Sesotho", "Setswana", "siSwati", "Xitsonga", "Tshivenda"]
    )
    summary_type = st.selectbox(
        "Summary Format",
        ["Full paper summary", "Abstract only", "Introduction + Conclusion", "Key findings only", "Study notes"]
    )

# (Keep your existing backend functions here: extract_text_from_pdf, call_gemini_api, call_gemini_rest_api, call_mistral_api)
# ... [PASTE YOUR BACKEND FUNCTIONS HERE] ...

# ============================================
# TABS - CLEAN LAYOUT
# ============================================

tab1, tab2 = st.tabs(["Upload PDF", "Paste Text"])

with tab1:
    st.write("Upload a research paper to generate a summary in your chosen language.")
    uploaded_file = st.file_uploader("", type=['pdf'], label_visibility="collapsed")
    
    if st.button("Generate Summary"):
        if not api_key:
            st.error("API key required. Please configure in the sidebar.")
        elif uploaded_file:
            with st.spinner("Processing document..."):
                # (Your existing logic for PDF processing here)
                st.success("Summary generated successfully. (Add your logic back in)")

with tab2:
    st.write("Paste the text of a research paper below.")
    paper_text = st.text_area("", height=250, label_visibility="collapsed")
    
    if st.button("Generate Summary"):
        if not api_key:
            st.error("API key required. Please configure in the sidebar.")
        elif not paper_text:
            st.warning("Please paste some text.")
        else:
            with st.spinner("Generating summary..."):
                # (Your existing logic for text processing here)
                st.success("Summary generated successfully. (Add your logic back in)")