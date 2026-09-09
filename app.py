import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from PIL import Image
import json
import io
import re

# Page Configuration
st.set_page_config(
    page_title="Varsity Quiz Pro - Executive Edition", 
    page_icon="🎓", 
    layout="centered"
)

# Advanced Modern Glassmorphism CSS Design
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
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
    
    .glass-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 25px 60px rgba(99, 102, 241, 0.2);
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
        padding: 12px 24px;
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

    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
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

api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else None
if api_key:
    genai.configure(api_key=api_key)

# Dynamic Working Model Generator
def generate_content_with_fallback(contents):
    valid_models = []
    try:
        # Fetch active models dynamically supported by your specific API key
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
            
    raise RuntimeError(f"কুইজ তৈরি করা সম্ভব হয়নি। নতুন API Key ব্যবহার করুন বা কিছুক্ষণ অপেক্ষা করুন। ত্রুটি: {last_error}")

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
def extract_large_pdf_text(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))
    full_text = ""
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            full_text += f"\n--- Page {i+1} ---\n" + text
    return full_text

# Header Component
st.markdown('<div class="main-title">Varsity Quiz Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">AI-Powered Next Generation Admission Exam Engine</div>', unsafe_allow_html=True)

if not api_key:
    st.error("⚠️ দয়া করে Streamlit Secrets-এ আপনার GEMINI_API_KEY যুক্ত করুন।")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚀 ফাইল/টেক্সট কুইজ", "🌍 লাইভ ইন্টারনেট", "✍️ লাইভ পরীক্ষা", "❌ ভুল নোটবুক", "📊 অ্যানালিটিক্স"])

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
                    bytes_data = uploaded_file.read()
                    extracted_content += extract_large_pdf_text(bytes_data) + "\n"
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
            with st.spinner("🚀 সচল মডেল নির্বাচন করে প্রশ্ন তৈরি হচ্ছে..."):
                try:
                    prompt = (
                        f"তুমি ঢাকা বিশ্ববিদ্যালয় ভর্তি পরীক্ষার একজন এক্সপার্ট প্রশ্ন প্রণেতা। "
                        f"নিচের আপলোডকৃত ফাইল/টেক্সট থেকে ঠিক {num_questions} টি উচ্চমানের বহুনির্বাচনী প্রশ্ন (MCQ) তৈরি করো '{subject}' বিষয়ের জন্য। "
                        "শুধুমাত্র একটি বিশুদ্ধ JSON Array আউটপুট দেবে অন্য কোনো টেক্সট ছাড়া:\n"
                        "[\n"
                        "  {\n"
                        '    "question": "প্রশ্ন এখানে?",\n'
                        '    "options": ["অপশন ক", "অপশন খ", "অপশন গ", "অপশন ঘ"],\n'
                        '    "correct_answer": "সঠিক অপশনটি",\n'
                        '    "explanation": "সংক্ষিপ্ত ব্যাখ্যা"\n'
                        "  }\n"
                        "]"
                    )
                    
                    contents = [prompt]
                    if uploaded_images:
                        contents.extend(uploaded_images)
                    if extracted_content.strip():
                        contents.append(f"\nকন্টেন্ট:\n{extracted_content[:40000]}")
                        
                    raw_response = generate_content_with_fallback(contents)
                    st.session_state.quiz_questions = safe_parse_json(raw_response)
                    st.session_state.user_ans = {}
                    st.session_state.checked_status = {}
                    st.success("🎉 কুইজ তৈরি সম্পন্ন হয়েছে! 'লাইভ পরীক্ষা' ট্যাবে চলে যাও।")
                except Exception as e:
                    st.error(f"{e}")

with tab2:
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
                    web_prompt = (
                        f"ইন্টারনেট থেকে সাম্প্রতিকতম তথ্য নিয়ে '{live_topic}' বিষয়ের ওপর ঠিক {live_num} টি MCQ তৈরি করো। "
                        "শুধুমাত্র একটি নিখুঁত JSON Array আউটপুট দেবে:\n"
                        "[\n"
                        "  {\n"
                        '    "question": "প্রশ্ন?",\n'
                        '    "options": ["অপশন ১", "অপশন ২", "অপশন ৩", "অপশন ৪"],\n'
                        '    "correct_answer": "সঠিক অপশনটি",\n'
                        '    "explanation": "ব্যাখ্যা"\n'
                        "  }\n"
                        "]"
                    )
                    raw_response = generate_content_with_fallback([web_prompt])
                    st.session_state.quiz_questions = safe_parse_json(raw_response)
                    st.session_state.user_ans = {}
                    st.session_state.checked_status = {}
                    st.success("🎉 কুইজ তৈরি হয়েছে! 'লাইভ পরীক্ষা' ট্যাবে পরীক্ষা দিন।")
                except Exception as e:
                    st.error(f"{e}")

with tab3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("✍️ লাইভ মক টেস্ট")
    
    if st.session_state.quiz_questions:
        for i, q in enumerate(st.session_state.quiz_questions):
            st.markdown(f"""
                <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 18px; padding: 20px; margin-bottom: 20px;">
                    <h4 style="color: #38bdf8; margin-top:0;">প্রশ্ন {i+1}: {q['question']}</h4>
                </div>
            """, unsafe_allow_html=True)
            
            selected_option = st.radio(
                f"অপশন বাছাই করুন #{i+1}", 
                q['options'], 
                key=f"q_radio_{i}", 
                index=None
            )
            
            if st.button(f"উত্তর যাচাই করো #{i+1}", key=f"check_btn_{i}"):
                st.session_state.user_ans[i] = selected_option
                st.session_state.checked_status[i] = True
                
                if selected_option == q['correct_answer']:
                    st.session_state.stats["total_attempted"] += 1
                    st.session_state.stats["total_correct"] += 1
                elif selected_option is not None:
                    st.session_state.stats["total_attempted"] += 1
                    mistake_item = {
                        "question": q['question'],
                        "correct_answer": q['correct_answer'],
                        "explanation": q['explanation']
                    }
                    if mistake_item not in st.session_state.mistakes:
                        st.session_state.mistakes.append(mistake_item)

            if st.session_state.checked_status.get(i, False):
                user_choice = st.session_state.user_ans.get(i)
                if user_choice is None:
                    st.warning("⚠️ একটি অপশন নির্বাচন করুন।")
                elif user_choice == q['correct_answer']:
                    st.success(f"✅ সঠিক উত্তর! 💡 ব্যাখ্যা: {q['explanation']}")
                else:
                    st.error(f"❌ ভুল উত্তর! সঠিক উত্তর: {q['correct_answer']} | 💡 ব্যাখ্যা: {q['explanation']}")

    else:
        st.info("প্রথমে প্রথম বা দ্বিতীয় ট্যাব থেকে কুইজ জেনারেট করে নিন।")
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("❌ ভুলের খাতা")
    if st.session_state.mistakes:
        st.write(f"মোট ভুল প্রশ্ন: **{len(st.session_state.mistakes)} টি**")
        if st.button("🗑️ ভুলের রেকর্ড ক্লিয়ার করো"):
            st.session_state.mistakes = []
            st.rerun()
            
        for idx, m in enumerate(st.session_state.mistakes):
            with st.expander(f"ভুল #{idx+1}: {m['question']}"):
                st.write(f"✅ সঠিক উত্তর: {m['correct_answer']}")
                st.info(f"💡 ব্যাখ্যা: {m['explanation']}")
    else:
        st.success("এখনো কোনো ভুলের রেকর্ড নেই!")
    st.markdown('</div>', unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📊 পারফরম্যান্স অ্যানালিটিক্স")
    stats = st.session_state.stats
    total_att = stats["total_attempted"]
    total_corr = stats["total_correct"]
    accuracy = (total_corr / total_att * 100) if total_att > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("মোট এটেন্ড", total_att)
    with col2:
        st.metric("সঠিক উত্তর", total_corr)
    with col3:
        st.metric("একুরেসি", f"{accuracy:.1f}%")
    st.markdown('</div>', unsafe_allow_html=True)
    
