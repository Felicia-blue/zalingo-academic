import streamlit as st
import google.generativeai as genai
import requests
import PyPDF2
import pdfplumber

st.set_page_config(page_title="ZaLingo Academic", page_icon="📚", layout="wide",
                   initial_sidebar_state="expanded")

# ============================================
# DESIGN SYSTEM
# ink #12302D · teal #0F5F57 · mist #F4F7F6 · line #DCE5E2 · marigold #E0A100
# ============================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@600;700&family=Instrument+Sans:wght@400;500;600&display=swap');

html, body, .stApp, [data-testid="stSidebar"] * , .stMarkdown, label, input, textarea, button {
    font-family: 'Instrument Sans', sans-serif;
}
.stApp { background: #F4F7F6; color: #12302D; }

/* Hide Streamlit chrome */
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
.stDeployButton, [data-testid="stStatusWidget"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1040px; padding-top: 1.5rem; padding-bottom: 3rem; }

/* Hero */
.hero { background: #12302D; border-radius: 14px; padding: 3rem 3rem 2.5rem; margin-bottom: 1.5rem; }
.hero h1 { font-family: 'Source Serif 4', serif; color: #FFFFFF; font-size: 2.7rem;
           line-height: 1.15; font-weight: 700; margin: 0 0 .9rem; max-width: 18em; letter-spacing: -0.01em; }
.hero p { color: #BFD3CF; font-size: 1.1rem; line-height: 1.6; max-width: 36em; margin: 0 0 1.6rem; }
.langs { display: flex; flex-wrap: wrap; gap: .5rem; }
.langs span { border: 1px solid #3E6B65; color: #E3EFEC; border-radius: 999px;
              padding: .25rem .8rem; font-size: .85rem; }
.langs span.on { background: #E0A100; border-color: #E0A100; color: #12302D; font-weight: 600; }

/* Feature row */
.feat { background: #fff; border: 1px solid #DCE5E2; border-radius: 10px; padding: 1.1rem 1.25rem; height: 100%; }
.feat b { display: block; color: #12302D; margin-bottom: .25rem; font-size: 1rem; }
.feat span { color: #54706C; font-size: .92rem; line-height: 1.5; }

/* Sidebar */
[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #DCE5E2; }
[data-testid="stSidebar"] h2 { font-family: 'Source Serif 4', serif; font-size: 1.3rem; color: #12302D; }
.brand { font-family: 'Source Serif 4', serif; font-weight: 700; font-size: 1.35rem; color: #12302D; }
.brand small { display:block; font-family:'Instrument Sans',sans-serif; font-weight:400; font-size:.8rem; color:#54706C; }

/* Buttons */
.stButton > button, .stDownloadButton > button {
    border-radius: 8px; font-weight: 600; padding: .65rem 1.4rem; border: 1px solid #0F5F57;
    background: #0F5F57; color: #fff; transition: background .15s ease; }
.stButton > button:hover, .stDownloadButton > button:hover { background: #0B4A44; border-color: #0B4A44; color: #fff; }
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible { outline: 3px solid #E0A100; outline-offset: 2px; }
.stDownloadButton > button { background: #fff; color: #0F5F57; }
.stDownloadButton > button:hover { background: #E8F1EF; color: #0B4A44; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 1.8rem; border-bottom: 1px solid #DCE5E2; }
.stTabs [data-baseweb="tab"] { padding: .6rem 0; color: #54706C; font-weight: 500; }
.stTabs [aria-selected="true"] { color: #0F5F57; font-weight: 600; }
.stTabs [data-baseweb="tab-highlight"] { background-color: #0F5F57; }

/* Upload zone (current Streamlit test-id) */
[data-testid="stFileUploaderDropzone"] { border: 1.5px dashed #8DB5AF; border-radius: 10px;
    background: #fff; padding: 2rem; }
[data-testid="stFileUploaderDropzone"]:hover { border-color: #0F5F57; background: #F0F6F5; }

/* Inputs */
.stTextArea textarea, .stTextInput input { border-radius: 8px; }

/* Results */
.result-head { font-family: 'Source Serif 4', serif; font-size: 1.5rem; color: #12302D; margin: 0 0 .5rem; }
[data-testid="stVerticalBlockBorderWrapper"] { background: #fff; border-color: #DCE5E2 !important; border-radius: 10px; }

.footer { text-align: center; color: #7A918D; font-size: .85rem; margin-top: 3rem; }
@media (max-width: 700px) { .hero { padding: 2rem 1.4rem; } .hero h1 { font-size: 2rem; } }
</style>
""", unsafe_allow_html=True)

# ============================================
# CONFIG
# ============================================
LANGUAGES = ["English", "Afrikaans", "isiZulu", "isiXhosa", "Sepedi", "Sesotho",
             "Setswana", "siSwati", "Xitsonga", "Tshivenda"]

SUMMARY_PROMPTS = {
    "Full paper summary": "Summarize this entire academic paper. Include the research question, methodology, key findings, and conclusions. Do not include references.",
    "Abstract only": "Extract and summarize just the abstract of this paper. Do not include references.",
    "Introduction + Conclusion": "Summarize only the introduction and conclusion sections. Do not include references.",
    "Key findings only": "Extract and list the main findings and results. Do not include references.",
    "Study notes": "Convert this paper into study notes with bullet points. Focus only on the content, not references.",
}
LENGTHS = {
    "Short": "Keep it concise: 3-4 sentences.",
    "Medium": "Write a balanced summary of 1-2 paragraphs.",
    "Detailed": "Write a comprehensive summary of 3-4 paragraphs.",
}

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown('<div class="brand">ZaLingo Academic<small>by BA Digital</small></div>', unsafe_allow_html=True)
    st.write("")
    st.subheader("Summary options")
    language = st.selectbox("Output language", LANGUAGES)
    summary_type = st.selectbox("Format", list(SUMMARY_PROMPTS))
    summary_length = st.select_slider("Length", options=list(LENGTHS), value="Medium")
    include_citation = st.checkbox("Add citation line", value=True)

    # If you set GEMINI_API_KEY in Streamlit secrets, users never see or need a key.
    secret_key = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""
    api_provider, api_key = "Google Gemini", secret_key
    if not secret_key:
        with st.expander("AI provider (advanced)"):
            api_provider = st.radio("Provider", ["Google Gemini", "Mistral AI"])
            link = "https://aistudio.google.com/apikey" if "Gemini" in api_provider else "https://console.mistral.ai"
            st.markdown(f"[Get a free API key]({link})")
            api_key = st.text_input("API key", type="password", placeholder="Paste key here")

# ============================================
# BACKEND
# ============================================
def extract_text_from_pdf(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = "\n".join((p.extract_text() or "") for p in reader.pages)
        if len(text) < 100:
            pdf_file.seek(0)
            with pdfplumber.open(pdf_file) as pdf:
                text = "\n".join((p.extract_text() or "") for p in pdf.pages)
        return text
    except Exception as e:
        st.error(f"We couldn't read this PDF ({e}). Try another file or paste the text instead.")
        return None

def call_gemini(key, prompt, text):
    full = f"{prompt}\n\nPAPER TEXT:\n{text[:30000]}"
    genai.configure(api_key=key)
    for name in ("gemini-2.5-flash", "gemini-2.5-pro"):
        try:
            return genai.GenerativeModel(name).generate_content(full).text
        except Exception:
            continue
    try:  # REST fallback
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
        r = requests.post(url, json={"contents": [{"parts": [{"text": full}]}]}, timeout=90)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        pass
    st.error("The summary service didn't respond. Check your API key and try again.")
    return None

def call_mistral(key, prompt, text):
    try:
        r = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": "mistral-small-latest", "temperature": 0.3, "max_tokens": 2000,
                  "messages": [{"role": "system", "content": "You are an academic assistant."},
                               {"role": "user", "content": f"{prompt}\n\nPAPER TEXT:\n{text[:20000]}"}]},
            timeout=90)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        st.error(f"Mistral returned an error ({r.status_code}). Check your API key.")
    except Exception as e:
        st.error(f"Could not reach Mistral: {e}")
    return None

def summarize(text, source_name):
    if not api_key:
        st.warning("Add an API key in the sidebar under AI provider (advanced).")
        return
    prompt = (f"{SUMMARY_PROMPTS[summary_type]} {LENGTHS[summary_length]} "
              f"Write the entire response in {language}, using clear academic {language}. "
              f"Keep proper nouns and technical terms with no standard {language} equivalent in English.")
    with st.spinner(f"Writing your {language} summary..."):
        fn = call_gemini if "Gemini" in api_provider else call_mistral
        summary = fn(api_key, prompt, text)
    if summary:
        if include_citation:
            summary += f"\n\n---\n*Source: {source_name} · Summarized with ZaLingo Academic*"
        with st.container(border=True):
            st.markdown(f'<div class="result-head">Summary in {language}</div>', unsafe_allow_html=True)
            st.markdown(summary)
        st.download_button("Download summary (.txt)", data=summary, file_name="zalingo_summary.txt")

# ============================================
# PAGE
# ============================================
chips = "".join(f'<span class="{"on" if l == language else ""}">{l}</span>' for l in LANGUAGES)
st.markdown(f"""
<div class="hero">
  <h1>Read any research paper in your own language.</h1>
  <p>Upload a PDF or paste the text. ZaLingo returns a clear summary in one of ten South African languages, in seconds.</p>
  <div class="langs">{chips}</div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.markdown('<div class="feat"><b>Ten languages</b><span>From isiZulu to Tshivenda, plus English and Afrikaans.</span></div>', unsafe_allow_html=True)
c2.markdown('<div class="feat"><b>Five summary formats</b><span>Full summary, abstract, intro and conclusion, key findings, or study notes.</span></div>', unsafe_allow_html=True)
c3.markdown('<div class="feat"><b>Citation included</b><span>Every summary can carry a source line you can paste into your notes.</span></div>', unsafe_allow_html=True)
st.write("")

tab1, tab2 = st.tabs(["Upload PDF", "Paste text"])

with tab1:
    uploaded = st.file_uploader("Choose a PDF", type=["pdf"], label_visibility="collapsed")
    if uploaded and st.button("Summarize PDF", key="pdf", type="secondary"):
        text = extract_text_from_pdf(uploaded)
        if text and len(text) > 100:
            summarize(text, uploaded.name)
        elif text is not None:
            st.error("This PDF has too little readable text. Scanned papers need to be run through OCR first.")

with tab2:
    pasted = st.text_area("Paper text", height=240, placeholder="Paste the full paper text here")
    title = st.text_input("Paper title (optional)")
    if st.button("Summarize text", key="txt"):
        if not pasted.strip():
            st.warning("Paste the paper text first.")
        else:
            summarize(pasted, title or "Pasted text")

st.markdown('<div class="footer">© 2026 BA Digital · ZaLingo Academic</div>', unsafe_allow_html=True)