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
# INVITING EDTECH UI CONFIGURATION
# ============================================
st.set_page_config(
    page_title="ZaLingo Academic",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a friendly, premium look
st.markdown("""
<style>
    /* Soft, warm background */
    .stApp {
        background-color: #F7F9FC;
    }
    
    /* Friendly Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif;
    }
    h1 {
        color: #1E3A8A; /* University Blue */
        font-weight: 800;
        letter-spacing: -0.02em;
    }
    h3 {
        color: #475569;
        font-weight: 500;
    }
    
    /* Card-like sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
        padding-top: 1rem;
    }
    
    /* Inviting Primary Button */
    .stButton>button {
        background-color: #2563EB; /* Bright Blue */
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.2s ease;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px -1px rgba(37, 99, 235, 0.3);
    }
    
    /* Clean tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 2px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 0px;
        font-weight: 600;
        color: #64748B;
    }
    .stTabs [aria-selected="true"] {
        color: #2563EB;
        border-bottom-color: #2563EB;
    }
    
    /* Beautiful Dropzone */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #93C5FD;
        border-radius: 12px;
        background-color: #EFF6FF;
        padding: 3rem;
        transition: all 0.2s ease;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #2563EB;
        background-color: #DBEAFE;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.write("")
st.title("Welcome to ZaLingo Academic")
st.markdown("### Break down language barriers in research. Upload a paper and get a summary in your language in seconds.")
st.write("")

# ============================================
# SIDEBAR SETTINGS
# ============================================
with st.sidebar:
    st.header("Settings")
    
    api_provider = st.radio("AI Provider", ["Google Gemini (Recommended)", "Mistral AI"])
    
    if "Gemini" in api_provider:
        st.markdown("🔑 [Get a FREE Gemini API Key](https://aistudio.google.com/apikey)")
        api_key = st.text_input("Enter Gemini Key", type="password", placeholder="Paste key here...")
    else:
        st.markdown("🔑 [Get a FREE Mistral API Key](https://console.mistral.ai)")
        api_key = st.text_input("Enter Mistral Key", type="password", placeholder="Paste key here...")
        
    st.divider()
    
    language = st.selectbox(
        "Output Language",
        ["English", "Afrikaans", "isiZulu", "isiXhosa", "Sepedi", "Sesotho", "Setswana", "siSwati", "Xitsonga", "Tshivenda"]
    )
    summary_type = st.selectbox(
        "Summary Format",
        ["Full paper summary", "Abstract only", "Introduction + Conclusion", "Key findings only", "Study notes"]
    )
    summary_length = st.select_slider("Summary Length", options=["Short", "Medium", "Detailed"], value="Medium")
    include_citation = st.checkbox("Include citation info", value=True)


# ============================================
# BACKEND LOGIC (Your original functions)
# ============================================
summary_prompts = {
    "Full paper summary": "Summarize this entire academic paper comprehensively. Include the research question, methodology, key findings, and conclusions. Do not include references or citations in the summary.",
    "Abstract only": "Extract and summarize just the abstract of this paper. Do not include references.",
    "Introduction + Conclusion": "Summarize only the introduction and conclusion sections. Do not include references.",
    "Key findings only": "Extract and list the main findings and results. Do not include references.",
    "Study notes": "Convert this paper into study notes with bullet points. Focus only on the content, not references."
}
length_map = {"Short": "Write a concise summary in 3-4 sentences.", "Medium": "Write a balanced summary in 1-2 paragraphs.", "Detailed": "Write a comprehensive summary with 3-4 paragraphs."}
language_codes = {"English": "en", "Afrikaans": "af", "isiZulu": "zu", "isiXhosa": "xh", "Sepedi": "nso", "Sesotho": "st", "Setswana": "tn", "siSwati": "ss", "Xitsonga": "ts", "Tshivenda": "ve"}

def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        if len(text) < 100:
            pdf_file.seek(0)
            with pdfplumber.open(pdf_file) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting PDF: {str(e)}")
        return None

def call_gemini_api(api_key, prompt, paper_text):
    try:
        genai.configure(api_key=api_key)
        possible_models = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-1.5-flash-002']
        model = None
        for model_name in possible_models:
            try:
                model = genai.GenerativeModel(model_name)
                model.generate_content("test")
                break
            except:
                continue
        if model is None:
            return call_gemini_rest_api(api_key, prompt, paper_text)
        full_prompt = f"{prompt}\n\nPAPER TEXT:\n{paper_text[:30000]}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return call_gemini_rest_api(api_key, prompt, paper_text)

def call_gemini_rest_api(api_key, prompt, paper_text):
    try:
        api_urls = [f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"]
        headers = {"Content-Type": "application/json"}
        full_text = f"{prompt}\n\nPAPER TEXT:\n{paper_text[:20000]}"
        data = {"contents": [{"parts": [{"text": full_text}]}]}
        for url in api_urls:
            try:
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    return response.json()['candidates'][0]['content']['parts'][0]['text']
            except:
                continue
        st.error("API attempts failed. Please check your key.")
        return None
    except Exception as e:
        st.error(f"REST API Error: {str(e)}")
        return None

def call_mistral_api(api_key, prompt, paper_text):
    try:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        data = {
            "model": "mistral-small-latest",
            "messages": [{"role": "system", "content": "You are an academic assistant."}, {"role": "user", "content": f"{prompt}\n\nPAPER TEXT:\n{paper_text[:20000]}"}],
            "temperature": 0.3, "max_tokens": 2000
        }
        response = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            st.error(f"Mistral API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Mistral API Error: {str(e)}")
        return None

# ============================================
# TABS
# ============================================
tab1, tab2 = st.tabs(["📄 Upload PDF", "📝 Paste Text"])

with tab1:
    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
    
    if uploaded_file is not None:
        if st.button("Generate Summary from PDF", use_container_width=True):
            if not api_key:
                st.warning("Please enter your API key in the sidebar.")
            else:
                with st.spinner("Reading document and generating summary..."):
                    paper_text = extract_text_from_pdf(uploaded_file)
                    if paper_text and len(paper_text) > 100:
                        base_prompt = f"{summary_prompts[summary_type]} {length_map[summary_length]}"
                        translated_prompt = GoogleTranslator(source='en', target=language_codes[language]).translate(base_prompt) if language != "English" else base_prompt
                        
                        summary = call_gemini_api(api_key, translated_prompt, paper_text) if "Gemini" in api_provider else call_mistral_api(api_key, translated_prompt, paper_text)
                        
                        if summary:
                            if include_citation: summary += f"\n\n---\n**Citation:** {uploaded_file.name} | Summarized by ZaLingo"
                            st.success("Summary generated successfully!")
                            st.markdown(f"### Summary ({language})")
                            st.markdown(summary)
                            st.download_button("Download Summary", data=summary, file_name=f"summary_{uploaded_file.name[:-4]}.txt")
                    else:
                        st.error("Could not extract enough text from the PDF.")

with tab2:
    paper_text = st.text_area("Paste the full paper text here:", height=250)
    paper_title = st.text_input("Paper title (optional):")
    
    if st.button("Generate Summary from Text", use_container_width=True):
        if not api_key:
            st.warning("Please enter your API key in the sidebar.")
        elif not paper_text:
            st.warning("Please paste some text first.")
        else:
            with st.spinner("Generating summary..."):
                base_prompt = f"{summary_prompts[summary_type]} {length_map[summary_length]}"
                translated_prompt = GoogleTranslator(source='en', target=language_codes[language]).translate(base_prompt) if language != "English" else base_prompt
                
                summary = call_gemini_api(api_key, translated_prompt, paper_text) if "Gemini" in api_provider else call_mistral_api(api_key, translated_prompt, paper_text)
                
                if summary:
                    if include_citation:
                        title = paper_title if paper_title else "Uploaded text"
                        summary += f"\n\n---\n**Citation:** {title} | Summarized by ZaLingo"
                    st.success("Summary generated successfully!")
                    st.markdown(f"### Summary ({language})")
                    st.markdown(summary)
                    st.download_button("Download Summary", data=summary, file_name="summary.txt")