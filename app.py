import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from PIL import Image
import json
import io
import re

# Page Configuration
st.set_page_config(
    page_title="Varsity Quiz Pro & PDF Reader", 
    page_icon="🎓", 
    layout="centered"
)

# Advanced Modern Glassmorphism & Book UI CSS Design
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Tiro+Bangla&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', 'Tiro Bangla', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0f172a 50%, #020617 100%);
        color: #f8fafc;
    }
    
    .glass-card {
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 28px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin-bottom: 24px;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }

    /* Flipbook Realistic Page Styling */
    .book-page-sepia {
        background: #fbf0d9;
        color: #2b2b2b;
        padding: 35px 30px;
        border-radius: 6px 18px 18px 6px;
        box-shadow: 12px 12px 35px rgba(0,0,0,0.6), inset 22px 0 30px rgba(0,0,0,0.08);
        border-left: 8px solid #8b5cf6;
        min-height: 480px;
        font-size: 1.15rem;
        line-height: 1.8;
        margin-bottom: 20px;
    }

    .book-page-dark {
        background: #0f172a;
        color: #f1f5f9;
        padding: 35px 30px;
        border-radius: 6px 18px 18px 6px;
        box-shadow: 12px 12px 35px rgba(0,0,0,0.8), inset 22px 0 30px rgba(255,255,255,0.03);
        border-left: 8px solid #6366f1;
        min-height: 480px;
        font-size: 1.15rem;
        line-height: 1.8;
        margin-bottom: 20px;
    }

    .book-page-white {
        background: #ffffff;
        color: #0f172a;
        padding: 35px 30px;
        border-radius: 6px 18px 18px 6px;
        box-shadow: 12px 12px 35px rgba(0,0,0,0.3), inset 22px 0 30px rgba(0,0,0,0.05);
        border-left: 8px solid #3b82f6;
        min-height: 480px;
        font-size: 1.15rem;
        line-height: 1.8;
        margin-bottom: 20px;
    }

    .main-title {
        font-size: 2.75rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 4px;
    }
    
    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 0.95rem;
        font-weight: 400;
        margin-bottom: 28px;
    }

    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: #ffffff;
        font-weight: 700;
        font-size: 0.95rem;
        padding: 12px 20px;
        border-radius: 14px;
        border: none;
        box-shadow: 0 8px 25px -5px rgba(99, 102, 241, 0.4);
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 30px -5px rgba(168, 85, 247, 0.6);
        background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%);
    }

    .stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
        background-color: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #f8fafc !important;
        border-radius: 14px !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.8);
        padding: 8px;
        border-radius: 18px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        color: #94a3b8;
        font-weight: 600;
        padding: 10px 18px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.4), rgba(124, 58, 237, 0.4)) !important;
        color: #ffffff !important;
        border: 1px solid rgba(129, 140, 248, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "mistakes" not in st.session_state:
    st.session_state.mistakes = []
if "stats" not in st.session_state:
    st.session_state.stats = {"total_attempted": 0, "total_correct": 0}
if "user_ans" not in st.session_state:
    st.session_state.user_ans = {}
if "checked_status" not in st.session_state:
    st.session_state.checked_status = {}

# Book Reader State
if "reader_pages" not in st.session_state:
    st.session_state.reader_pages = []
if "cleaned_pages" not in st.session_state:
    st.session_state.cleaned_pages = {}
if "current_page_idx" not in st.session_state:
    st.session_state.current_page_idx = 0
if "uploaded_file_id" not in st.session_state:
    st.session_state.uploaded_file_id = ""

# Sidebar for Custom API Key Input
with st.sidebar:
    st.header("⚙️ এপিআই সেটিংস")
    custom_api_key = st.text_input("আপনার Gemini API Key দিন:", type="password", help="Google AI Studio থেকে নতুন key এনে এখানে বসাতে পারেন।")
    api_key = custom_api_key if custom_api_key.strip() else st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

# Dynamic Working Model Generator
def generate_content_with_fallback(contents):
    valid_models = []
    try:
        fetched_models = [
            m.name for m in genai.list_models() 
            if 'generateContent' in m.supported_generation_methods
        ]
        if fetched_models:
            valid_models = fetched_models
    except Exception:
        pass

    if not valid_models:
        valid_models = ['models/gemini-1.5-flash', 'models/gemini-2.0-flash']

    last_error = None
    for model_name in valid_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(contents)
            return response.text
        except Exception as e:
            last_error = e
            continue
            
    raise RuntimeError(f"কন্টেন্ট তৈরি করা সম্ভব হয়নি। ভুল: {last_error}")

# Safe JSON Parser
def safe_parse_json(text):
    try:
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(text)
    except Exception as e:
        st.error(f"JSON রেসপন্স প্রসেস করতে সমস্যা হয়েছে: {e}")
        return []

@st.cache_data
def extract_pdf_pages(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        pages.append(text if text.strip() else "[এই পৃষ্ঠায় কোনো পড়ার উপযোগী টেক্সট পাওয়া যায়নি]")
    return pages

# Automatic Bijoy ANSI to Unicode Converter & English-to-Bangla Translator
def fix_and_translate_text(raw_text):
    if not raw_text.strip() or raw_text == "[এই পৃষ্ঠায় কোনো পড়ার উপযোগী টেক্সট পাওয়া যায়নি]":
        return raw_text

    # Detect Bijoy / Corrupted ANSI Text
    if re.search(r'[†‡‰ˆª¤«»ª]', raw_text) or "mvaviY" in raw_text or "nvBjvBUm" in raw_text:
        prompt = (
            "The following text is Bengali written in Bijoy/SutonnyMJ ANSI font, showing up as corrupted characters. "
            "Convert it accurately into clean Unicode Bengali text. Do not summarize or alter the meaning. "
            "Output ONLY the converted Unicode Bengali text:\n\n" + raw_text
        )
        try:
            return generate_content_with_fallback([prompt])
        except Exception:
            return raw_text
            
    return raw_text

# Header Component
st.markdown('<div class="main-title">Varsity Quiz & Book Reader</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">AI-Powered Exam Engine & Smart PDF Flipbook</div>', unsafe_allow_html=True)

if not api_key:
    st.error("⚠️ দয়া করে সাইডবারে আপনার Gemini API Key প্রদান করুন।")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🚀 ফাইল/টেক্সট কুইজ", 
    "📖 পিডিএফ বই রিডার", 
    "🌍 লাইভ ইন্টারনেট", 
    "✍️ লাইভ পরীক্ষা", 
    "❌ ভুল নোটবুক", 
    "📊 অ্যানালিটিক্স"
])

# ----------------- TAB 1: QUIZ GENERATOR -----------------
with tab1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        subject = st.selectbox("📚 বিষয় নির্বাচন করো:", ["বাংলা", "ইংরেজি", "সাধারণ জ্ঞান", "বিজ্ঞান ও আইসিটি"], key="sub1")
    with col2:
        num_questions = st.number_input("🔢 প্রশ্নের সংখ্যা (৫-১০০):", min_value=5, max_value=100, value=15, key="num1")

    upload_type = st.radio("📥 ইনপুট মাধ্যম:", ["একাধিক পিডিএফ বা ছবি/স্ক্রিনশট আপলোড", "সরাসরি টেক্সট পেস্ট"])
    extracted_content = ""
    uploaded_images = []

    if upload_type == "একাধিক পিডিএফ বা ছবি/স্ক্রিনশট আপলোড":
        uploaded_files = st.file_uploader(
            "ফাইল নির্বাচন করুন (PDF, PNG, JPG)", 
            type=["pdf", "png", "jpg", "jpeg"], 
            accept_multiple_files=True
        )
        if uploaded_files:
            for uploaded_file in uploaded_files:
                if uploaded_file.type == "application/pdf":
                    pages = extract_pdf_pages(uploaded_file.read())
                    extracted_content += "\n".join(pages) + "\n"
                else:
                    uploaded_images.append(Image.open(uploaded_file))
            st.success(f"⚡ সফলভাবে আপলোড হয়েছে: {len(uploaded_files)} টি ফাইল প্রসেস করা হয়েছে!")
    else:
        extracted_content = st.text_area("✍️ নোটস বা পড়ার বিষয়বস্তু পেস্ট করুন:")

    generate_btn = st.button("✨ আল্ট্রা ফাস্ট কুইজ তৈরি করো")
    st.markdown('</div>', unsafe_allow_html=True)

    if generate_btn and api_key:
        if not extracted_content.strip() and not uploaded_images:
            st.error("⚠️ কোনো ইনপুট পাওয়া যায়নি!")
        else:
            with st.spinner("🚀 প্রশ্ন তৈরি হচ্ছে..."):
                try:
                    prompt = (
                        f"তুমি ভর্তি পরীক্ষার একজন এক্সপার্ট প্রশ্ন প্রণেতা। "
                        f"নিচের কন্টেন্ট থেকে ঠিক {num_questions} টি উচ্চমানের MCQ তৈরি করো '{subject}' বিষয়ের জন্য। "
                        "শুধুমাত্র একটি বিশুদ্ধ JSON Array আউটপুট দেবে:\n"
                        "[\n  {\n    \"question\": \"প্রশ্ন?\",\n    \"options\": [\"অপশন ১\", \"অপশন ২\", \"অপশন ৩\", \"অপশন ৪\"],\n    \"correct_answer\": \"সঠিক উত্তর\",\n    \"explanation\": \"ব্যাখ্যা\"\n  }\n]"
                    )
                    contents = [prompt]
                    if uploaded_images: contents.extend(uploaded_images)
                    if extracted_content.strip(): contents.append(f"\nকন্টেন্ট:\n{extracted_content[:40000]}")
                        
                    raw_response = generate_content_with_fallback(contents)
                    st.session_state.quiz_questions = safe_parse_json(raw_response)
                    st.session_state.user_ans = {}
                    st.session_state.checked_status = {}
                    st.success("🎉 কুইজ তৈরি সম্পন্ন হয়েছে! 'লাইভ পরীক্ষা' ট্যাবে চলে যাও।")
                except Exception as e:
                    st.error(f"{e}")

# ----------------- TAB 2: PDF BOOK FLIPBOOK READER & INSTANT TRANSLATOR -----------------
with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📖 পিডিএফ বই রিডার ও ইনস্ট্যান্ট অটো-অনুবাদক")
    
    reader_file = st.file_uploader("📚 পড়ার জন্য পিডিএফ বইটি আপলোড করুন:", type=["pdf"], key="book_reader_file")
    
    if reader_file:
        file_bytes = reader_file.read()
        file_id = f"{reader_file.name}_{reader_file.size}"

        # If a NEW PDF is uploaded -> Auto convert/translate ALL pages immediately at upload time
        if st.session_state.uploaded_file_id != file_id:
            st.session_state.uploaded_file_id = file_id
            st.session_state.reader_pages = extract_pdf_pages(file_bytes)
            st.session_state.cleaned_pages = {}
            st.session_state.current_page_idx = 0

            if st.session_state.reader_pages and api_key:
                total_p = len(st.session_state.reader_pages)
                progress_bar = st.progress(0, text="⚡ পিডিএফ আপলোড সম্পন্ন! বিজয় ফন্ট থেকে শুদ্ধ বাংলায় রূপান্তর করা হচ্ছে...")
                
                for i, page_txt in enumerate(st.session_state.reader_pages):
                    st.session_state.cleaned_pages[i] = fix_and_translate_text(page_txt)
                    progress_bar.progress((i + 1) / total_p, text=f"⏳ অনুবাদ ও ফন্ট রূপান্তর করা হচ্ছে: {i+1}/{total_p} নম্বর পাতা")
                
                progress_bar.empty()
                st.success("🎉 পিডিএফ-এর সকল পৃষ্ঠা সফলভাবে একবারে অনুবাদ ও রূপান্তর করা হয়েছে!")

        if st.session_state.reader_pages:
            total_p = len(st.session_state.reader_pages)
            
            # Top Controls
            col_theme, col_slider = st.columns([1, 2])
            with col_theme:
                theme = st.selectbox("🎨 থিম নির্বাচন করুন:", ["📜 সেপিয়া (বইয়ের পাতা)", "🌙 ডার্ক মোড", "☀️ ক্লাসিক হোয়াইট"])
            with col_slider:
                st.session_state.current_page_idx = st.slider(
                    "পৃষ্ঠা জাম্প করুন:", 
                    min_value=1, 
                    max_value=total_p, 
                    value=st.session_state.current_page_idx + 1 if st.session_state.current_page_idx < total_p else 1
                ) - 1

            curr_idx = st.session_state.current_page_idx
            raw_page_content = st.session_state.reader_pages[curr_idx]
            page_content = st.session_state.cleaned_pages.get(curr_idx, raw_page_content)
            
            # Line break handling outside f-string to prevent SyntaxError
            html_page_content = page_content.replace('\n', '<br>')

            # Theme Selection
            theme_class = "book-page-sepia"
            if "ডার্ক" in theme:
                theme_class = "book-page-dark"
            elif "হোয়াইট" in theme:
                theme_class = "book-page-white"

            # Render Page
            page_html = f"""
                <div class="{theme_class}">
                    <div style="text-align: right; font-size: 0.85rem; opacity: 0.6; margin-bottom: 12px;">পৃষ্ঠা {curr_idx + 1} / {total_p}</div>
                    <div>{html_page_content}</div>
                </div>
            """
            st.markdown(page_html, unsafe_allow_html=True)

            # --- Page Navigation Bar (Bottom) ---
            col_prev, col_info, col_next = st.columns([1, 1, 1])
            with col_prev:
                if st.button("◀ পূর্ববর্তী পাতা", key="prev_p_bottom"):
                    if st.session_state.current_page_idx > 0:
                        st.session_state.current_page_idx -= 1
                        st.rerun()
            with col_info:
                st.markdown(f"<h4 style='text-align:center; color:#38bdf8; margin:8px 0;'>পৃষ্ঠা {curr_idx + 1} / {total_p}</h4>", unsafe_allow_html=True)
            with col_next:
                if st.button("পরবর্তী পাতা ▶", key="next_p_bottom"):
                    if st.session_state.current_page_idx < total_p - 1:
                        st.session_state.current_page_idx += 1
                        st.rerun()

            # --- AI TOOLS: IMPORTANT TOPIC EXTRACTOR & ASSISTANT ---
            st.write("---")
            st.markdown("### 🎯 AI Smart Tools (স্মার্ট টুলস)")
            
            col_ai1, col_ai2 = st.columns(2)
            
            with col_ai1:
                if st.button("🎯 এই পাতার ইম্পর্টেন্ট টপিক আলাদা করো"):
                    if api_key:
                        with st.spinner("🔍 গুরুত্বপূর্ণ টপিক ও বুলেট পয়েন্ট আলাদা করা হচ্ছে..."):
                            try:
                                topic_prompt = (
                                    "নিচের টেক্সট থেকে পরীক্ষার জন্য সবচেয়ে গুরুত্বপূর্ণ টপিকগুলো বুলেট পয়েন্ট আকারে সুন্দরভাবে সাজিয়ে দাও। "
                                    "গুরুত্বপূর্ণ শব্দগুলো **Bold** করে দাও:\n\n" + page_content[:4000]
                                )
                                topics = generate_content_with_fallback([topic_prompt])
                                st.success("📌 **এই পাতার গুরুত্বপূর্ণ টপিকসমূহ:**")
                                st.markdown(f"<div style='background: rgba(15,23,42,0.8); padding: 18px; border-radius: 14px; border: 1px solid rgba(56,189,248,0.3);'>{topics}</div>", unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"টপিক বের করতে সমস্যা হয়েছে: {e}")
                    else:
                        st.warning("সাইডবারে API Key দিন।")

            with col_ai2:
                if st.button("📌 পুরো বইয়ের গুরুত্বপূর্ণ মাস্টার নোটস"):
                    if api_key:
                        with st.spinner("📚 পুরো পিডিএফ বিশ্লেষণ করে মাস্টার নোটস তৈরি করা হচ্ছে..."):
                            try:
                                full_text = "\n".join([st.session_state.cleaned_pages.get(i, p) for i, p in enumerate(st.session_state.reader_pages)])[:30000]
                                master_prompt = (
                                    "তুমি একজন এডমিশন ও এক্সাম স্পেশালিস্ট। নিচের পুরো পিডিএফ থেকে সবচেয়ে গুরুত্বপূর্ণ হেডলাইন, "
                                    "সাধারণ জ্ঞান/জরুরি তথ্য এবং রিভিশন পয়েন্ট তালিকা আকারে তৈরি করে দাও:\n\n" + full_text
                                )
                                master_notes = generate_content_with_fallback([master_prompt])
                                st.info("🏆 **সম্পূর্ণ পিডিএফ-এর মাস্টার ইম্পর্টেন্ট পয়েন্ট:**")
                                st.markdown(f"<div style='background: rgba(15,23,42,0.8); padding: 18px; border-radius: 14px; border: 1px solid rgba(168,85,247,0.3);'>{master_notes}</div>", unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"মাস্টার নোট তৈরি করা সম্ভব হয়নি: {e}")
                    else:
                        st.warning("সাইডবারে API Key দিন।")
    else:
        st.info("👆 একটি পিডিএফ বই আপলোড করলেই তা অটো-কনভার্ট ও অনুবাদ হয়ে যাবে।")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------- TAB 3: LIVE INTERNET QUIZ -----------------
with tab3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🌍 লাইভ ইন্টারনেট সাম্প্রতিক কুইজ")
    live_topic = st.text_input("🔍 টপিক লিখুন:", placeholder="যেমন: Bangladesh Affairs 2026 / World Sports")
    live_num = st.slider("প্রশ্নের সংখ্যা:", 5, 30, 10, key="live_n")
    web_generate_btn = st.button("🌐 ইন্টারনেট থেকে প্রশ্ন আনো")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if web_generate_btn and api_key:
        if not live_topic:
            st.warning("টপিক লিখুন।")
        else:
            with st.spinner("🌐 সাম্প্রতিক তথ্য সংগ্রহ করা হচ্ছে..."):
                try:
                    web_prompt = f"ইন্টারনেট থেকে তথ্য নিয়ে '{live_topic}' এর ওপর {live_num} টি MCQ তৈরি করো JSON Array আকারে।"
                    raw_response = generate_content_with_fallback([web_prompt])
                    st.session_state.quiz_questions = safe_parse_json(raw_response)
                    st.session_state.user_ans = {}
                    st.session_state.checked_status = {}
                    st.success("🎉 কুইজ তৈরি হয়েছে! 'লাইভ পরীক্ষা' ট্যাবে পরীক্ষা দিন।")
                except Exception as e:
                    st.error(f"{e}")

# ----------------- TAB 4: MOCK TEST -----------------
with tab4:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("✍️ লাইভ মক টেস্ট")
    
    # ❌ The error was here. I
