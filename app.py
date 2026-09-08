import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from PIL import Image

# Page Configuration
st.set_page_config(
    page_title="Varsity Quiz Pro - ঢাবি স্ট্যান্ডার্ড", 
    page_icon="🎓", 
    layout="centered"
)

# Custom CSS for Animations, Glassmorphism & Gorgeous UI
st.markdown("""
    <style>
    /* Global Styling & Smooth Fade In Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #311042 100%);
        color: #f8fafc;
        animation: fadeIn 0.8s ease-out;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
        animation: fadeIn 0.6s ease-out;
    }

    /* Gradient Title Effect */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 5px;
        animation: fadeIn 0.5s ease-out;
    }

    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 30px;
    }

    /* Custom Animated Button */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        font-size: 1.1rem;
        font-weight: 700;
        padding: 14px 28px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
        transition: all 0.3s ease;
        cursor: pointer;
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(168, 85, 247, 0.6);
        background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%);
    }

    /* Quiz Output Card Styling */
    .quiz-box {
        background: rgba(15, 23, 42, 0.7);
        border-left: 5px solid #818cf8;
        padding: 20px;
        border-radius: 10px;
        margin-top: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# API Configuration
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else None

if not api_key:
    st.warning("⚠️ দয়া করে Streamlit Secrets-এ আপনার Gemini API Key যুক্ত করুন। (Manage app -> Settings -> Secrets)")
else:
    genai.configure(api_key=api_key)

# Header Section
st.markdown('<div class="main-title">🎓 Varsity Quiz Master</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">ঢাকা বিশ্ববিদ্যালয় ভর্তি পরীক্ষার স্ট্যান্ডার্ডে আনলিমিটেড কুইজ জেনারেটর</div>', unsafe_allow_html=True)

# Main Form Container with Glassmorphism
with st.container():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        subject = st.selectbox("📚 বিষয় নির্বাচন করো:", ["বাংলা", "ইংরেজি", "সাধারণ জ্ঞান", "বিজ্ঞান ও আইসিটি"])
    with col2:
        num_questions = st.number_input("🔢 প্রশ্নের সংখ্যা (৫-৫০০):", min_value=5, max_value=500, value=15)

    upload_type = st.radio("📥 ইনপুট মাধ্যম বেছে নাও:", ["ফাইল বা স্ক্রিনশট আপলোড (PDF/Image)", "সরাসরি টেক্সট পেস্ট"])

    extracted_content = None
    uploaded_image = None

    if upload_type == "ফাইল বা স্ক্রিনশট আপলোড (PDF/Image)":
        uploaded_file = st.file_uploader("আপনার পিডিএফ বা ছবি ড্রপ করুন", type=["pdf", "png", "jpg", "jpeg"])
        if uploaded_file is not None:
            if uploaded_file.type == "application/pdf":
                reader = PdfReader(uploaded_file)
                extracted_content = "".join([page.extract_text() or "" for page in reader.pages])
                st.success("✅ পিডিএফ সফলভাবে রিড করা হয়েছে!")
            else:
                uploaded_image = Image.open(uploaded_file)
                st.success("✅ ছবি সফলভাবে আপলোড হয়েছে!")
    else:
        extracted_content = st.text_area("✍️ এখানে আপনার পড়ার টপিক বা টেক্সট পেস্ট করুন:")

    st.markdown('</div>', unsafe_allow_html=True)

# Action Button
if st.button("🚀 এক্সক্লুসিভ কুইজ তৈরি করো"):
    if not api_key:
        st.error("প্রথমে Streamlit Secrets-এ এপিআই কি (API Key) যুক্ত করুন!")
    elif not extracted_content and not uploaded_image:
        st.error("⚠️ দয়া করে কোনো ফাইল, ছবি বা টেক্সট ইনপুট দিন!")
    else:
        with st.spinner("✨ ঢাবি ভর্তি পরীক্ষার আদলে কঠিন ও ট্রিকি প্রশ্ন তৈরি হচ্ছে... একটু অপেক্ষা করুন..."):
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            prompt = f"""
            তুমি ঢাকা বিশ্ববিদ্যালয় ভর্তি পরীক্ষার একজন এক্সপার্ট প্রশ্ন প্রণেতা। নিচের কন্টেন্ট থেকে ঠিক {num_questions} টি উচ্চমানের বহুনির্বাচনী প্রশ্ন (MCQ) তৈরি করো `{subject}` বিষয়ের জন্য। 
            প্রশ্নগুলো স্ট্যান্ডার্ড ভার্সিটি ভর্তি পরীক্ষার মতো কঠিন, স্ট্যান্ডার্ড ও ট্রিকি হতে হবে।
            প্রতিটি প্রশ্নের ৪টি অপশন (ক, খ, গ, ঘ) থাকবে। 
            উত্তরগুলো নিচের ফরম্যাটে বাংলায় সুন্দরভাবে সাজিয়ে আউটপুট দাও:
            
            প্রশ্ন ১: [প্রশ্ন]
            ক) ... খ) ... গ) ... ঘ) ...
            সঠিক উত্তর: [সঠিক অপশন]
            ব্যাখ্যা: [কেন এই উত্তর সঠিক তার বিস্তারিত ব্যাখ্যা]
            ---
            """
            
            try:
                if uploaded_image:
                    response = model.generate_content([prompt, uploaded_image])
                else:
                    response = model.generate_content([prompt + "\n\nকন্টেন্ট:\n" + extracted_content])
                    
                st.markdown("---")
                st.markdown("### 📝 তোমার কুইজ সেট:")
                st.markdown(f'<div class="quiz-box">{response.text}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ ত্রুটি দেখা দিয়েছে: {e}")
                
