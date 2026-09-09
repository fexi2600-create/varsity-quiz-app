import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from PIL import Image
import json
import io

# Page Configuration
st.set_page_config(
    page_title="Varsity Quiz Pro - Executive Edition", 
    page_icon="🎓", 
    layout="centered"
)

# Pro-Level Custom CSS & Modern Design System
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #090d16 60%, #030712 100%);
        color: #f3f4f6;
        animation: fadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    .glass-card {
        background: rgba(17, 24, 39, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 28px;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(255, 255, 255, 0.03) inset;
        margin-bottom: 24px;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 25px 50px -12px rgba(99, 102, 241, 0.15);
    }

    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #60a5fa 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 4px;
    }
    
    .sub-title {
        text-align: center;
        color: #9ca3af;
        font-size: 0.95rem;
        font-weight: 400;
        margin-bottom: 30px;
        letter-spacing: -0.01em;
    }

    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 10px 20px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 4px 16px rgba(79, 70, 229, 0.35);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        box-shadow: 0 6px 24px rgba(124, 58, 237, 0.5);
        border-color: rgba(255, 255, 255, 0.3);
    }

    .stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
        background-color: rgba(31, 41, 55, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #f3f4f6 !important;
        border-radius: 12px !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(90deg, #60a5fa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(17, 24, 39, 0.5);
        padding: 6px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        color: #9ca3af;
        font-weight: 500;
        padding: 8px 16px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.3), rgba(124, 58, 237, 0.3)) !important;
        color: #ffffff !important;
        border: 1px solid rgba(99, 102, 241, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "mistakes" not in st.session_state:
    st.session_state.mistakes = []
if "stats" not in st.session_state:
    st.session_state.stats = {"total_attempted": 0, "total_correct": 0, "history": []}
if "user_ans" not in st.session_state:
    st.session_state.user_ans = {}
if "checked_status" not in st.session_state:
    st.session_state.checked_status = {}

api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else None
if not api_key:
    st.warning("⚠️ দয়া করে Streamlit Secrets-এ আপনার Gemini API Key যুক্ত করুন।")
else:
    genai.configure(api_key=api_key)

# App Header
st.markdown('<div class="main-title">Varsity Quiz Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Next-Generation AI Learning & Exam Preparation Platform</div>', unsafe_allow_html=True)

@st.cache_data
def extract_large_pdf_text(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))
    full_text = ""
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            full_text += f"\n--- Page {i+1} ---\n" + text
    return full_text

# Navigation Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚀 ফাইল/টেক্সট জেনারেটর", "🌍 লাইভ ইন্টারনেট", "✍️ লাইভ পরীক্ষা", "❌ ভুল নোটবুক", "📊 অ্যানালিটিক্স"])

with tab1:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            subject = st.selectbox("📚 বিষয় নির্বাচন করো:", ["বাংলা", "ইংরেজি", "সাধারণ জ্ঞান", "বিজ্ঞান ও আইসিটি"], key="sub1")
        with col2:
            num_questions = st.number_input("🔢 প্রশ্নের সংখ্যা (৫-৫০০):", min_value=5, max_value=500, value=15, key="num1")

        upload_type = st.radio("📥 ইনপুট মাধ্যম:", ["একাধিক পিডিএফ বা ছবি/স্ক্রিনশট আপলোড", "সরাসরি টেক্সট পেস্ট"])
        extracted_content = ""
        uploaded_images = []

        if upload_type == "একাধিক পিডিএফ বা ছবি/স্ক্রিনশট আপলোড":
            uploaded_files = st.file_uploader(
                "একাধিক পিডিএফ বা ছবি/স্ক্রিনশট (PDF, PNG, JPG) একসাথে আপলোড করুন", 
                type=["pdf", "png", "jpg", "jpeg"], 
                accept_multiple_files=True
            )
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    if uploaded_file.type == "application/pdf":
                        bytes_data = uploaded_file.read()
                        extracted_content += extract_large_pdf_text(bytes_data) + "\n"
                    else:
                        img = Image.open(uploaded_file)
                        uploaded_images.append(img)
                st.success(f"⚡ সফলভাবে আপলোড হয়েছে: {len(uploaded_images)} টি ছবি এবং পিডিএফ ডেটা প্রসেস হয়েছে!")
        else:
            extracted_content = st.text_area("✍️ পড়ার টপিক বা বড় নোটস পেস্ট করুন:")

        generate_btn = st.button("✨ স্পিড কুইজ তৈরি করো")
        st.markdown('</div>', unsafe_allow_html=True)

    if generate_btn:
        if not api_key:
            st.error("প্রথমে এপিআই কি সেট করুন!")
        elif not extracted_content.strip() and not uploaded_images:
            st.error("⚠️ কোনো ফাইল বা টেক্সট ইনপুট দিন!")
        else:
            with st.spinner("🚀 ডকুমেন্ট ও ছবিগুলো প্রসেস করে এক্সিকিউটিভ প্রশ্ন তৈরি হচ্ছে..."):
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    prompt = (
                        f"তুমি ঢাকা বিশ্ববিদ্যালয় ভর্তি পরীক্ষার একজন এক্সপার্ট প্রশ্ন প্রণেতা। "
                        f"নিচের আপলোডকৃত কন্টেন্ট/ছবিগুলো থেকে খুব সতর্কতার সাথে ঠিক {num_questions} টি উচ্চমানের বহুনির্বাচনী প্রশ্ন (MCQ) তৈরি করো '{subject}' বিষয়ের জন্য। "
                        "প্রশ্নগুলো যেন স্ট্যান্ডার্ড ও মানসম্মত হয়। "
                        "শুধুমাত্র একটি নিখুঁত JSON Array আউটপুট দেবে অন্য কোনো টেক্সট বা ব্যাকটিক্স ছাড়া:\n"
                        "[\n"
                        "  {\n"
                        '    "question": "প্রশ্ন এখানে লিখবে?",\n'
                        '    "options": ["অপশন ক", "অপশন খ", "অপশন গ", "অপশন ঘ"],\n'
                        '    "correct_answer": "সঠিক অপশনটি (পুরো টেক্সট)",\n'
                        '    "explanation": "কেন এই উত্তর সঠিক তার বিস্তারিত ব্যাখ্যা"\n'
                        "  }\n"
                        "]"
                    )
                    
                    # Prepare contents list for Gemini (can take multiple images + text prompt)
                    contents = [prompt]
                    if uploaded_images:
                        contents.extend(uploaded_images)
                    if extracted_content.strip():
                        safe_content = extracted_content[:50000] if len(extracted_content) > 50000 else extracted_content
                        contents.append(f"\nডকুমেন্ট কন্টেন্ট:\n{safe_content}")
                        
                    response = model.generate_content(contents)
                    
                    clean_text = response.text.strip().replace("```json", "").replace("```", "").strip()
                    st.session_state.quiz_questions = json.loads(clean_text)
                    st.session_state.user_ans = {}
                    st.session_state.checked_status = {}
                    st.success("🎉 কুইজ সফলভাবে তৈরি হয়েছে! 'লাইভ পরীক্ষা' ট্যাবে গিয়ে প্র্যাকটিস শুরু করো 👇")
                except Exception as e:
                    st.error(f"ত্রুটি দেখা দিয়েছে: {e}")

with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🌍 লাইভ ইন্টারনেট কারেন্ট অ্যাফেয়ার্স কুইজ")
    live_topic = st.text_input("🔍 সাম্প্রতিক কোন বিষয়ের ওপর কুইজ চাও?", placeholder="যেমন: Recent Bangladesh Affairs 2026")
    live_num = st.slider("প্রশ্নের সংখ্যা:", 5, 30, 10, key="live_n")
    web_generate_btn = st.button("🌐 ইন্টারনেট থেকে ফাস্ট কুইজ আনো")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if web_generate_btn:
        if not live_topic:
            st.warning("দয়া করে টপিক লিখুন।")
        else:
            with st.spinner("🌐 ইন্টারনেট থেকে লেটেস্ট তথ্য আনা হচ্ছে..."):
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    web_prompt = (
                        f"ইন্টারনেট থেকে সাম্প্রতিকতম তথ্য নিয়ে '{live_topic}' বিষয়ের ওপর ঠিক {live_num} টি উচ্চমানের MCQ তৈরি করো। "
                        "শুধুমাত্র নিখুঁত JSON Array ফরম্যাটে আউটপুট দেবে অন্য কোনো টেক্সট ছাড়া:\n"
                        "[\n"
                        "  {\n"
                        '    "question": "প্রশ্ন?",\n'
                        '    "options": ["অপশন ক", "অপশন খ", "অপশন গ", "অপশন ঘ"],\n'
                        '    "correct_answer": "সঠিক অপশনটি",\n'
                        '    "explanation": "কেন সঠিক তার ব্যাখ্যা"\n'
                        "  }\n"
                        "]"
                    )
                    response = model.generate_content(web_prompt)
                    clean_text = response.text.strip().replace("```json", "").replace("```", "").strip()
                    st.session_state.quiz_questions = json.loads(clean_text)
                    st.session_state.user_ans = {}
                    st.session_state.checked_status = {}
                    st.success("🎉 ইন্টারনেটের লেটেস্ট ডেটা দিয়ে কুইজ তৈরি হয়ে গেছে! 'লাইভ পরীক্ষা' ট্যাবে যাও।")
                except Exception as e:
                    st.error(f"ত্রুটি: {e}")

with tab3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("✍️ প্রফেশনাল লাইভ পরীক্ষা ও ইনস্ট্যান্ট ফিডব্যাক")
    
    if st.session_state.quiz_questions:
        st.markdown("<p style='color: #9ca3af; font-size: 0.9rem; margin-bottom: 20px;'>বাঁয়ে প্রশ্ন এবং ডানে উপর থেকে নিচে প্রফেশনাল স্টাইলে অপশনগুলো দেওয়া হয়েছে। উত্তর সিলেক্ট করে **'উত্তর চেক করো'** বাটনে ক্লিক করলেই ঠিক সেইখানেই সঠিক উত্তর ও ব্যাখ্যা দেখতে পাবে।</p>", unsafe_allow_html=True)
        
        for i, q in enumerate(st.session_state.quiz_questions):
            st.markdown(f"""
                <div style="background: rgba(31, 41, 55, 0.45); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 22px; margin-bottom: 24px;">
            """, unsafe_allow_html=True)
            
            q_col, opt_col = st.columns([3, 2])
            
            with q_col:
                st.markdown(f"**প্রশ্ন {i+1}:** {q['question']}")
                
            with opt_col:
                st.markdown("<p style='font-size: 0.85rem; color: #9ca3af; margin-bottom: 2px; font-weight: 600;'>অপশনসমূহ:</p>", unsafe_allow_html=True)
                selected_option = st.radio(
                    f"উত্তর নির্বাচন করো #{i+1}", 
                    q['options'], 
                    key=f"q_radio_{i}", 
                    label_visibility="collapsed",
                    index=None
                )
            
            col_b1, col_b2 = st.columns([1, 3])
            with col_b1:
                check_btn = st.button(f"উত্তর চেক #{i+1}", key=f"check_btn_{i}")
            
            if check_btn:
                st.session_state.user_ans[i] = selected_option
                st.session_state.checked_status[i] = True
                
                if selected_option == q['correct_answer']:
                    st.session_state.stats["total_attempted"] += 1
                    st.session_state.stats["total_correct"] += 1
                elif selected_option is not None:
                    st.session_state.stats["total_attempted"] += 1
                    mistake_item = {
                        "question": q['question'],
                        "options": q['options'],
                        "correct_answer": q['correct_answer'],
                        "explanation": q['explanation']
                    }
                    if mistake_item not in st.session_state.mistakes:
                        st.session_state.mistakes.append(mistake_item)

            if st.session_state.checked_status.get(i, False):
                user_choice = st.session_state.user_ans.get(i)
                if user_choice is None:
                    st.warning("⚠️ দয়া করে যেকোনো একটি অপশন সিলেক্ট করুন।")
                elif user_choice == q['correct_answer']:
                    st.markdown(f"""
                        <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); padding: 12px 16px; border-radius: 12px; margin-top: 14px; color: #34d399;">
                            <b>✅ দুর্দান্ত! সঠিক উত্তর।</b><br><span style="font-size: 0.9rem; color: #e5e7eb;">💡 ব্যাখ্যা: {q['explanation']}</span>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style="background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.3); padding: 12px 16px; border-radius: 12px; margin-top: 14px; color: #f87171;">
                            <b>❌ ভুল হয়েছে!</b> সঠিক উত্তরটি হলো: <b>{q['correct_answer']}</b><br><span style="font-size: 0.9rem; color: #e5e7eb;">💡 ব্যাখ্যা: {q['explanation']}</span>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("প্রথমে 'ফাইল/টেক্সট জেনারেটর' বা 'লাইভ ইন্টারনেট' ট্যাব থেকে কুইজ জেনারেট করে নিন।")
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("❌ ভুল সংশোধন ও রিটেস্ট মোড")
    if st.session_state.mistakes:
        st.markdown(f"টোটাল সংরক্ষিত ভুল প্রশ্ন: **{len(st.session_state.mistakes)} টি**")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔄 শুধু ভুল প্রশ্নগুলো নিয়ে রিটেস্ট দাও"):
                st.session_state.quiz_questions = st.session_state.mistakes
                st.session_state.user_ans = {}
                st.session_state.checked_status = {}
                st.success("ভুল প্রশ্নগুলো দিয়ে রিটেস্ট লোড করা হয়েছে! 'লাইভ পরীক্ষা' ট্যাবে গিয়ে পরীক্ষা দাও।")
                st.rerun()
        with col_b:
            if st.button("🗑️ ভুলের খাতা ক্লিয়ার করো"):
                st.session_state.mistakes = []
                st.rerun()
                
        for idx, m in enumerate(st.session_state.mistakes):
            with st.expander(f"ভুল #{idx+1}: {m['question'][:50]}..."):
                st.write(f"✅ সঠিক উত্তর: {m['correct_answer']}")
                st.info(f"💡 ব্যাখ্যা: {m['explanation']}")
    else:
        st.success("অভিনন্দন! আপনার কোনো ভুল রেকর্ড করা হয়নি।")
    st.markdown('</div>', unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📊 পারফরম্যান্স অ্যানালিটিক্স ও রিপোর্ট এক্সপোর্ট")
    stats = st.session_state.stats
    total_att = stats["total_attempted"]
    total_corr = stats["total_correct"]
    overall_acc = (total_corr / total_att * 100) if total_att > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("মোট প্রশ্ন এটেন্ড", total_att)
    with col2:
        st.metric("সঠিক উত্তর", total_corr)
    with col3:
        st.metric("গ্রোথ / একুরেসি", f"{overall_acc:.1f}%")
    
    if stats["history"] or total_att > 0:
        report_text = f"--- Varsity Quiz Pro Growth Report ---\nTotal Attempted: {total_att}\nTotal Correct: {total_corr}\nOverall Accuracy: {overall_acc:.1f}%\nSaved Mistakes: {len(st.session_state.mistakes)}\n"
        st.download_button(
            label="📥 গ্রোথ রিপোর্ট ডাউনলোড করো (TXT)",
            data=report_text,
            file_name="growth_report.txt",
            mime="text/plain"
        )
    else:
        st.info("কুইজ সাবমিট করার পর এখানে রিপোর্ট এক্সপোর্ট অপশন দেখতে পাবে।")
    st.markdown('</div>', unsafe_allow_html=True)
            
