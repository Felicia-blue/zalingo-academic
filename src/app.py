# ============================================
# 🇿🇦 ZALINGO ACADEMIC - Research Paper Summarizer
# ============================================
# Translates academic papers into 10 South African languages
# Now using FREE APIs! No payment required 🎉

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
# PAGE CONFIGURATION & CUSTOM UI THEME
# ============================================

st.set_page_config(
    page_title="ZaLingo Academic | Multilingual Research Tool",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Clean academic background */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Main Title Styling */
    h1 {
        color: #0F172A;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
    }
    
    /* Subtitle and body text */
    p, .stMarkdown {
        color: #334155;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
        padding-top: 2rem;
    }
    
    /* Green "Free to Use" box */
    .stAlert {
        background-color: #ECFDF5;
        border: 1px solid #10B981;
        border-radius: 8px;
        color: #065F46;
    }
    
    /* Upload box styling */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #94A3B8;
        border-radius: 12px;
        background-color: #FFFFFF;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #3B82F6;
        background-color: #EFF6FF;
    }
    
    /* Hide the default Streamlit footer */
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================
# MAIN HEADER
# ============================================

st.title("🎓 ZaLingo Academic")
st.markdown("### *Making global research accessible in South African languages.*")
st.divider()

st.success("🎉 **FREE TO USE!** No payment required. Get your free API key below.")

st.write("""
Upload any research paper (PDF) and get a summary in YOUR language.
**Supported languages:** isiZulu • isiXhosa • Afrikaans • English • Sepedi • Sesotho • Setswana • siSwati • Xitsonga • Tshivenda
""")

# ============================================
# SIDEBAR - SETTINGS
# ============================================

with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Provider Selection
    api_provider = st.radio(
        "🤖 Choose AI Provider (All FREE)",
        ["Google Gemini (Recommended)", "Mistral AI", "Groq (Coming Soon)"],
        help="Google Gemini offers 60 requests/minute free. Mistral offers 1B tokens/month free."
    )
    
    if api_provider == "Google Gemini (Recommended)":
        st.markdown("""
        **🔑 Get your FREE Gemini API key:**
        1. Go to [aistudio.google.com](https://aistudio.google.com/apikey)
        2. Click "Get API Key"
        3. No credit card required!
        """)
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="Paste your API key here"
        )
        
    elif api_provider == "Mistral AI":
        st.markdown("""
        **🔑 Get your FREE Mistral API key:**
        1. Go to [console.mistral.ai](https://console.mistral.ai)
        2. Sign up (phone verification required)
        3. 1 Billion tokens FREE every month!
        """)
        api_key = st.text_input(
            "Mistral API Key",
            type="password",
            placeholder="Enter your Mistral key"
        )
    else:
        api_key = None
    
    # Add note about free credits
    st.info("💡 **1 Billion tokens ≈ 500-1000 research papers!**")
    
    language = st.selectbox(
        "🌍 Select output language",
        ["English", "Afrikaans", "isiZulu", "isiXhosa", 
         "Sepedi (Northern Sotho)", "Sesotho (Southern Sotho)", 
         "Setswana", "siSwati", "Xitsonga", "Tshivenda"]
    )
    
    summary_type = st.radio(
        "📋 Summary type",
        ["Full paper summary", "Abstract only", "Introduction + Conclusion", 
         "Key findings only", "Study notes (bullet points)"]
    )
    
    summary_length = st.select_slider(
        "Summary length",
        options=["Short", "Medium", "Detailed"],
        value="Medium"
    )
    
    include_citation = st.checkbox("Include citation information", value=True)
    
    st.markdown("---")
    st.caption("📚 Supporting 10 South African languages | 100% Free APIs")

# ============================================
# LANGUAGE MAPPINGS
# ============================================

summary_prompts = {
    "Full paper summary": "Summarize this entire academic paper comprehensively. Include the research question, methodology, key findings, and conclusions. Do not include references or citations in the summary.",
    "Abstract only": "Extract and summarize just the abstract of this paper. Do not include references.",
    "Introduction + Conclusion": "Summarize only the introduction and conclusion sections. Do not include references.",
    "Key findings only": "Extract and list the main findings and results. Do not include references.",
    "Study notes (bullet points)": "Convert this paper into study notes with bullet points. Focus only on the content, not references."
}

length_map = {
    "Short": "Write a concise summary in 3-4 sentences.",
    "Medium": "Write a balanced summary in 1-2 paragraphs.",
    "Detailed": "Write a comprehensive summary with 3-4 paragraphs."
}

language_codes = {
    "English": "en", "Afrikaans": "af", "isiZulu": "zu", "isiXhosa": "xh",
    "Sepedi (Northern Sotho)": "nso", "Sesotho (Southern Sotho)": "st",
    "Setswana": "tn", "siSwati": "ss", "Xitsonga": "ts", "Tshivenda": "ve"
}

# ============================================
# PDF EXTRACTION FUNCTION
# ============================================

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

# ============================================
# UPDATED GEMINI API FUNCTIONS WITH 2026 MODEL NAMES
# ============================================

def call_gemini_api(api_key, prompt, paper_text):
    """Call Google's Gemini API with 2026 model names"""
    try:
        genai.configure(api_key=api_key)
        
        # Updated model names for 2026
        possible_models = [
            'gemini-2.5-flash',
            'gemini-2.5-pro',
            'gemini-3-flash',
            'gemini-3-pro',
            'models/gemini-2.5-flash',
            'models/gemini-2.5-pro'
        ]
        
        # Try each model until one works
        model = None
        for model_name in possible_models:
            try:
                model = genai.GenerativeModel(model_name)
                # Test with a simple prompt
                test = model.generate_content("test")
                st.success(f"✅ Using model: {model_name}")
                break
            except Exception as e:
                continue
        
        if model is None:
            # If none work, use REST API as fallback
            st.warning("SDK models failed, trying REST API...")
            return call_gemini_rest_api(api_key, prompt, paper_text)
        
        # Combine prompt and paper text
        full_prompt = f"{prompt}\n\nPAPER TEXT:\n{paper_text[:30000]}"
        
        response = model.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        st.warning(f"SDK Error: {str(e)}. Trying REST API...")
        return call_gemini_rest_api(api_key, prompt, paper_text)

def call_gemini_rest_api(api_key, prompt, paper_text):
    """Fallback: Call Gemini directly via REST API with 2026 model names"""
    try:
        # Updated model names for 2026
        api_urls = [
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}",
            f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={api_key}",
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key}",
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash:generateContent?key={api_key}",
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro:generateContent?key={api_key}",
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-002:generateContent?key={api_key}"
        ]
        
        headers = {
            "Content-Type": "application/json"
        }
        
        full_text = f"{prompt}\n\nPAPER TEXT:\n{paper_text[:20000]}"
        
        data = {
            "contents": [{
                "parts": [{"text": full_text}]
            }]
        }
        
        for url in api_urls:
            try:
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    result = response.json()
                    model_used = url.split('/')[-2]
                    st.success(f"✅ Using model: {model_used}")
                    return result['candidates'][0]['content']['parts'][0]['text']
                elif response.status_code == 404:
                    # Model not found, try next URL
                    continue
                else:
                    # Other error, show it but continue trying
                    st.warning(f"API Error {response.status_code} on {url}, trying next...")
            except Exception as e:
                continue
        
        st.error("All REST API attempts failed. Please try Mistral AI instead.")
        return None
            
    except Exception as e:
        st.error(f"REST API Error: {str(e)}")
        return None

def call_mistral_api(api_key, prompt, paper_text):
    """Call Mistral AI API (FREE - 1B tokens/month)"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "mistral-small-latest",  # Free tier model
            "messages": [
                {"role": "system", "content": "You are an expert academic research assistant. Provide summaries without references."},
                {"role": "user", "content": f"{prompt}\n\nPAPER TEXT:\n{paper_text[:20000]}"}
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            st.error(f"Mistral API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Mistral API Error: {str(e)}")
        return None

# ============================================
# CREATE TABS
# ============================================

tab1, tab2, tab3 = st.tabs(["📄 Upload PDF", "📝 Paste Text", "ℹ️ How to Get Free API Keys"])

# ============================================
# TAB 3 - HOW TO GET FREE API KEYS
# ============================================

with tab3:
    st.header("🎁 Get Your FREE API Key")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🤖 Google Gemini (Recommended)")
        st.markdown("""
        **Advantages:**
        - ✅ 60 requests per minute FREE
        - ✅ No phone verification needed
        - ✅ 1 Million token context (entire books!)
        - ✅ Great with multiple languages
        
        **How to get:**
        1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
        2. Sign in with any Google account
        3. Click "Create API Key"
        4. Copy your key (starts with "AIza...")
        
        ⚡ **Takes 2 minutes, no credit card!**
        """)
        
    with col2:
        st.subheader("⚡ Mistral AI (MOST RELIABLE)")
        st.markdown("""
        **Advantages:**
        - ✅ 1 Billion tokens FREE every month
        - ✅ Very fast responses
        - ✅ European open-source model
        - ✅ **Works every time!**
        
        **How to get:**
        1. Go to [console.mistral.ai](https://console.mistral.ai)
        2. Sign up (requires phone verification)
        3. Go to API Keys section
        4. Create new key
        
        📱 **Phone verification required but 100% reliable**
        """)
    
    st.info("""
    💡 **Tip:** If Gemini gives you model errors, switch to Mistral AI - it's more stable!
    """)
    
    st.success("""
    **With 1 Billion free tokens, you can summarize:**
    - 📚 500-1000 research papers
    - 📖 20-30 full textbooks
    - 🎓 An entire semester of readings
    
    All for FREE!
    """)

# ============================================
# TAB 1 - PDF UPLOAD
# ============================================

with tab1:
    st.subheader("Upload a research paper")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
    
    if uploaded_file is not None:
        st.info(f"📁 File: {uploaded_file.name}")
        st.info(f"📏 Size: {uploaded_file.size / 1024:.1f} KB")
        
        if st.button("📚 Summarize Paper (FREE)", type="primary", use_container_width=True):
            
            if not api_key:
                st.error("⚠️ Please enter your API key - get one for FREE from the 'How to Get Free API Keys' tab!")
            
            else:
                with st.spinner("📖 Reading PDF and generating summary..."):
                    
                    try:
                        paper_text = extract_text_from_pdf(uploaded_file)
                        
                        if not paper_text or len(paper_text) < 100:
                            st.warning("⚠️ Couldn't extract enough text. Try the 'Paste Text' tab instead.")
                        
                        else:
                            with st.expander("📄 Show extracted text (first 1000 chars)"):
                                st.write(paper_text[:1000] + "...")
                            
                            # Build the prompt
                            base_prompt = f"{summary_prompts[summary_type]} {length_map[summary_length]}"
                            
                            # Translate prompt if needed
                            if language != "English":
                                try:
                                    translator = GoogleTranslator(source='en', target=language_codes[language])
                                    translated_prompt = translator.translate(base_prompt)
                                except:
                                    # If translation fails, use English with instruction
                                    translated_prompt = base_prompt + f" (Please respond in {language})"
                            else:
                                translated_prompt = base_prompt
                            
                            # Call appropriate API
                            if api_provider == "Google Gemini (Recommended)":
                                summary = call_gemini_api(api_key, translated_prompt, paper_text)
                            else:  # Mistral
                                summary = call_mistral_api(api_key, translated_prompt, paper_text)
                            
                            if summary:
                                if include_citation:
                                    summary += f"\n\n---\n**Citation:** {uploaded_file.name} | Summarized by ZaLingo Academic"
                                
                                st.success("✅ Summary generated successfully! (100% FREE)")
                                
                                col1, col2 = st.columns([1, 2])
                                
                                with col1:
                                    st.markdown("### 📋 Paper Info")
                                    st.write(f"**Title:** {uploaded_file.name}")
                                    st.write(f"**Language:** {language}")
                                    st.write(f"**Summary type:** {summary_type}")
                                    st.write(f"**AI Provider:** {api_provider}")
                                
                                with col2:
                                    st.markdown(f"### 📝 Summary ({language})")
                                    st.markdown(summary)
                                    
                                    st.download_button(
                                        label="📥 Download Summary",
                                        data=summary,
                                        file_name=f"summary_{uploaded_file.name[:-4]}.txt",
                                        mime="text/plain"
                                    )
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# ============================================
# TAB 2 - TEXT INPUT
# ============================================

with tab2:
    st.subheader("Paste paper text directly")
    
    paper_text = st.text_area("Paste the full paper text here:", height=300)
    paper_title = st.text_input("Paper title (optional):")
    
    if st.button("📚 Summarize Text (FREE)", type="primary", use_container_width=True):
        
        if not api_key:
            st.error("⚠️ Please enter your API key - get one for FREE from the 'How to Get Free API Keys' tab!")
        
        elif not paper_text:
            st.warning("⚠️ Please paste some text")
        
        else:
            with st.spinner("🔄 Generating summary..."):
                
                try:
                    # Build the prompt
                    base_prompt = f"{summary_prompts[summary_type]} {length_map[summary_length]}"
                    
                    # Translate prompt if needed
                    if language != "English":
                        try:
                            translator = GoogleTranslator(source='en', target=language_codes[language])
                            translated_prompt = translator.translate(base_prompt)
                        except:
                            # If translation fails, use English with instruction
                            translated_prompt = base_prompt + f" (Please respond in {language})"
                    else:
                        translated_prompt = base_prompt
                    
                    # Call appropriate API
                    if api_provider == "Google Gemini (Recommended)":
                        summary = call_gemini_api(api_key, translated_prompt, paper_text)
                    else:  # Mistral
                        summary = call_mistral_api(api_key, translated_prompt, paper_text)
                    
                    if summary:
                        if include_citation:
                            if paper_title:
                                summary += f"\n\n---\n**Citation:** {paper_title} | Summarized by ZaLingo Academic"
                            else:
                                summary += f"\n\n---\n**Citation:** Uploaded text | Summarized by ZaLingo Academic"
                        
                        st.success("✅ Summary generated successfully! (100% FREE)")
                        
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            st.markdown("### 📋 Summary Info")
                            st.write(f"**Language:** {language}")
                            st.write(f"**Summary type:** {summary_type}")
                            st.write(f"**AI Provider:** {api_provider}")
                        
                        with col2:
                            st.markdown(f"### 📝 Summary ({language})")
                            st.markdown(summary)
                            
                            st.download_button(
                                label="📥 Download Summary",
                                data=summary,
                                file_name="summary.txt",
                                mime="text/plain"
                            )
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown("""
### 📚 About ZaLingo Academic

**The first FREE academic paper summarizer for South African languages**

✅ **100% FREE to use** - No credit card required!
✅ **1 Million tokens** - Summarize entire textbooks!
✅ **10 South African languages supported**

Supported languages: isiZulu • isiXhosa • Afrikaans • English • Sepedi • Sesotho • Setswana • siSwati • Xitsonga • Tshivenda

Built with ❤️ during LLM Training (DS-I Africa, 2026) using FREE AI APIs
""")

st.caption("📌 **FREE FOREVER:** Get your API key at aistudio.google.com - no payment needed! v2")