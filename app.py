import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from PIL import Image
import json

# Page Configuration
st.set_page_config(
    page_title="Varsity Quiz Pro - Growth Tracker", 
    page_icon="🎓", 
    layout="centered"
)

# Custom CSS for Animations & Glassmorphism UI
st.markdown("""
    <style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #311042 100%);
        color: #f8fafc;
        animation: fadeIn 0.6s ease-out;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 25px;
    }
    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        font-weight: 700;
        padding: 12px 24px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(168, 85, 247, 0.6);
    }
    .metric-container {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 12px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State for Tracking Mistakes & Growth
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "mistakes" not in st.session_state:
    st.session_state.mistakes = []
if "stats" not in st.session_state:
    st.session_state.stats = {"total_attempted": 0, "total_correct": 0, "history": []}

# API Configuration
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else None
if not api_key:
    st.warning("⚠️ দয়া করে Streamlit Secrets-এ আপনার Gemini API Key যুক্ত করুন।")
else:
    genai.configure(api_key=api_key)

# App Header
st.markdown('<div class="main-title">🎓 Varsity Quiz Master & Growth Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">স্মার্ট কুইজ প্র্যাকটিস, ভুল অ্যানালিসিস এবং গ্রোথ ট্র্যাক করার পার্মানেন্ট প্ল্যাটফর্ম</div>', unsafe_allow_html=True)

# Tabs for Navigation
tab1, tab2, tab3 = st.tabs(["🚀 কুইজ জেনারেট ও প্র্যাকটিস", "📊 গ্রোথ ও অ্যানালিটিক্স", "❌ ভুল নোটবুক (Mistakes)"])

with tab1:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            subject = st.selectbox("📚 বিষয় নির্বাচন করো:", ["বাংলা", "ইংরেজি", "সাধারণ জ্ঞান", "বিজ্ঞান ও আইসিটি"])
        with col2:
            num_questions = st.number_input("🔢 প্রশ্নের সংখ্যা (৫-৫০):", min_value=5, max_value=50, value=10)

        upload_type = st.radio("📥 ইনপুট মাধ্যম:", ["ফাইল বা স্ক্রিনশট আপলোড (PDF/Image)", "সরাসরি টেক্সট পেস্ট"])

        extracted_content = None
        uploaded_image = None

        if upload_type == "ফাইল বা স্ক্রিনশট আপলোড (PDF/Image)":
            uploaded_file = st.file_uploader("পিডিএফ বা ছবি আপলোড করুন", type=["pdf", "png", "jpg", "jpeg"])
            if uploaded_file is not None:
                if uploaded_file.type == "application/pdf":
                    reader = PdfReader(uploaded_file)
                    extracted_content = "".join([page.extract_text() or "" for page in reader.pages])
                    st.success("✅ পিডিএফ সফলভাবে পড়া হয়েছে!")
                else:
                    uploaded_image = Image.open(uploaded_file)
                    st.success("✅ ছবি সফলভাবে আপলোড হয়েছে!")
        else:
            extracted_content = st.text_area("✍️ পড়ার টপিক বা টেক্সট পেস্ট করুন:")

        generate_btn = st.button("✨ কুইজ তৈরি করো")
        st.markdown('</div>', unsafe_allow_html=True)

    if generate_btn:
        if not api_key:
            st.error("প্রথমে এপিআই কি (API Key) সেট করুন!")
        elif not extracted_content and not uploaded_image:
            st.error("⚠️ কোনো ফাইল বা টেক্সট ইনপুট দিন!")
        else:
            with st.spinner("🔄 ঢাবি স্ট্যান্ডার্ড প্রশ্ন ও অপশন তৈরি হচ্ছে..."):
                try:
                    model = genai.GenerativeModel('gemini-3.6-flash')
                    prompt = f"""
                    তুমি ঢাকা বিশ্ববিদ্যালয় ভর্তি পরীক্ষার একজন এক্সপার্ট প্রশ্ন প্রণেতা। নিচের কন্টেন্ট থেকে ঠিক {num_questions} টি উচ্চমানের বহুনির্বাচনী প্রশ্ন (MCQ) তৈরি করো `{subject}` বিষয়ের জন্য।
                    অবশ্যই নিচের ফরম্যাটে একটি নিখুঁত JSON Array আউটপুট দেবে (অন্য কোনো অতিরিক্ত লেখা বা markdown ট্যাগ যেমন ```json দেওয়া যাবে না, শুধু র ডেটা):
                    [
                      {{
                        "question": "প্রশ্ন এখানে লিখবে?",
                        "options": ["অপশন ক", "অপশন খ", "অপশন গ", "অপশন ঘ"],
                        "correct_answer": "সঠিক অপশনটি (যেমন অপশন ক এর পুরো টেক্সট)",
                        "explanation": "কেন এই উত্তর সঠিক তার বিস্তারিত ব্যাখ্যা"
                      }}
                    ]
                    """
                    if uploaded_image:
                        response = model.generate_content([prompt, uploaded_image])
                    else:
                        response = model.generate_content([prompt + "\n\nকন্টেন্ট:\n" + extracted_content])
                    
                    clean_text = response.text.strip().replace("```json", "").replace("```", "").strip()
                    st.session_state.quiz_questions = json.loads(clean_text)
                    st.success("🎉 কুইজ সফলভাবে তৈরি হয়েছে! নিচে প্র্যাকটিস শুরু করো 👇")
                except Exception as e:
                    st.error(f"ত্রুটি দেখা দিয়েছে: {e}")

    # Interactive Quiz Section
    if st.session_state.quiz_questions:
        st.markdown("---")
        st.subheader("✍️ লাইভ কুইজ টেস্ট:")
        
        with st.form("quiz_form"):
            user_answers = {}
            for i, q in enumerate(st.session_state.quiz_questions):
                st.markdown(f"**প্রশ্ন {i+1}: {q['question']}**")
                user_answers[i] = st.radio(f"উত্তর নির্বাচন করো #{i+1}", q['options'], key=f"q_{i}", index=None)
                st.markdown("---")
            
            submit_quiz = st.form_submit_button("📋 সাবমিট ও ফলাফল দেখাও")
            
            if submit_quiz:
                correct_count = 0
                total = len(st.session_state.quiz_questions)
                session_mistakes = []
                
                for i, q in enumerate(st.session_state.quiz_questions):
                    ans = user_answers.get(i)
                    if ans == q['correct_answer']:
                        correct_count += 1
                    else:
                        session_mistakes.append({
                            "subject": subject,
                            "question": q['question'],
                            "your_answer": ans if ans else "উত্তর দাওনি",
                            "correct_answer": q['correct_answer'],
                            "explanation": q['explanation']
                        })
                
                # Update Stats & Growth Tracker
                st.session_state.stats["total_attempted"] += total
                st.session_state.stats["total_correct"] += correct_count
                st.session_state.mistakes.extend(session_mistakes)
                
                accuracy = (correct_count / total) * 100
                st.session_state.stats["history"].append(accuracy)
                
                st.balloons()
                st.success(f"🎯 আপনার স্কোর: {correct_count} / {total} (সঠিকতার হার: {accuracy:.1f}%)")
                
                # Show Explanations for Mistakes
                if session_mistakes:
                    st.warning("⚠️ যেসব প্রশ্ন ভুল হয়েছে সেগুলোর সঠিক উত্তর ও ব্যাখ্যা নিচে দেওয়া হলো:")
                    for m in session_mistakes:
                        st.markdown(f"""
                        - **প্রশ্ন:** {m['question']}
                        - **আপনার উত্তর:** <span style="color:red">{m['your_answer']}</span>
                        - **সঠিক উত্তর:** <span style="color:green">{m['correct_answer']}</span>
                        - **ব্যাখ্যা:** {m['explanation']}
                        """, unsafe_allow_html=True)

with tab2:
    st.subheader("📊 আপনার পড়াশোনার গ্রোথ ও পারফরম্যান্স")
    stats = st.session_state.stats
    total_att = stats["total_attempted"]
    total_corr = stats["total_correct"]
    overall_acc = (total_corr / total_att * 100) if total_att > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("মোট কুইজ প্রশ্ন এটেন্ড", total_att)
    with col2:
        st.metric("সঠিক উত্তর", total_corr)
    with col3:
        st.metric("গ্রোথ / একুরেসি রেট", f"{overall_acc:.1f}%")
    
    if stats["history"]:
        st.markdown("#### 📈 পারফরম্যান্স গ্রোথ ট্রেন্ড:")
        st.line_chart(stats["history"])
        st.info("💡 টিপস: গ্রাফ ওপরের দিকে উঠলে বুঝবে তোমার প্রস্তুতি ভালো হচ্ছে!")
    else:
        st.info("প্রথমে 'কুইজ জেনারেট ও প্র্যাকটিস' ট্যাব থেকে অন্তত একটি কুইজ সাবমিট করো, তাহলে এখানে গ্রোথ দেখতে পাবে।")

with tab3:
    st.subheader("❌ ভুল সংশোধন ও নোটবুক (Mistakes Archive)")
    if st.session_state.mistakes:
        st.markdown(f"মোট ভুলের সংখ্যা: **{len(st.session_state.mistakes)} টি**")
        if st.button("🗑️ ভুলের তালিকা রিসেট করো"):
            st.session_state.mistakes = []
            st.rerun()
            
        for idx, m in enumerate(st.session_state.mistakes):
            with st.expander(f"ভুল #{idx+1}: {m['question'][:50]}..."):
                st.write(f"📚 বিষয়: {m['subject']}")
                st.write(f"❌ তোমার উত্তর: {m['your_answer']}")
                st.write(f"✅ সঠিক উত্তর: {m['correct_answer']}")
                st.info(f"💡 ব্যাখ্যা: {m['explanation']}")
    else:
        st.success("অভিনন্দন! তোমার কোনো ভুল রেকর্ড করা হয়নি। কুইজ প্র্যাকটিস করলে ভুলগুলো এখানে জমা হবে।")
            
