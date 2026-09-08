import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from PIL import Image

st.set_page_config(page_title="Varsity Admission Quiz Generator", page_icon="🎓", layout="centered")

# API Configuration
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else None

if not api_key:
    st.warning("দয়া করে Streamlit Secrets-এ আপনার Gemini API Key যুক্ত করুন। (Manage app -> Settings -> Secrets)")
else:
    genai.configure(api_key=api_key)

st.title("🎓 ভার্সিটি ভর্তি পরীক্ষা কুইজ জেনারেটর")
st.markdown("যেকোনো **PDF, স্ক্রিনশট, ছবি বা টেক্সট** আপলোড করে ঢাকা বিশ্ববিদ্যালয় ভর্তি পরীক্ষার আদলে কঠিন ও মানসম্মত কুইজ তৈরি করুন।")

# Subject & Qty Selection
subject = st.selectbox("বিষয় নির্বাচন করো:", ["বাংলা", "ইংরেজি", "সাধারণ জ্ঞান", "বিজ্ঞান ও অন্যান্য"])
num_questions = st.number_input("প্রশ্নের সংখ্যা (৫ থেকে ৫০০ পর্যন্ত):", min_value=5, max_value=500, value=20)

# Input options
upload_type = st.radio("ইনপুট মাধ্যম বেছে নাও:", ["ফাইল বা ছবি আপলোড (PDF/Image)", "সরাসরি টেক্সট পেস্ট"])

extracted_content = None
uploaded_image = None

if upload_type == "ফাইল বা ছবি আপলোড (PDF/Image)":
    uploaded_file = st.file_uploader("পিডিএফ বা স্ক্রিনশট আপলোড করো", type=["pdf", "png", "jpg", "jpeg"])
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            extracted_content = "".join([page.extract_text() or "" for page in reader.pages])
            st.success("পিডিএফ সফলভাবে পড়া হয়েছে!")
        else:
            uploaded_image = Image.open(uploaded_file)
            st.success("ছবি সফলভাবে আপলোড হয়েছে!")
else:
    extracted_content = st.text_area("এখানে তোমার পড়ার টপিক বা টেক্সট পেস্ট করো:")

if st.button("🚀 কুইজ তৈরি করো"):
    if not api_key:
        st.error("প্রথমে Streamlit Secrets-এ এপিআই কি (API Key) যুক্ত করুন!")
    elif not extracted_content and not uploaded_image:
        st.error("দয়া করে কোনো ফাইল, ছবি বা টেক্সট ইনপুট দাও!")
    else:
        with st.spinner("ঢাকা বিশ্ববিদ্যালয় ভর্তি পরীক্ষার আদলে প্রশ্ন তৈরি হচ্ছে... (বড় সাইজের কুইজের জন্য একটু সময় লাগতে পারে)"):
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            তুমি ঢাকা বিশ্ববিদ্যালয় ভর্তি পরীক্ষার একজন প্রশ্ন প্রণেতা। নিচের কন্টেন্ট থেকে ঠিক {num_questions} টি উচ্চমানের বহুনির্বাচনী প্রশ্ন (MCQ) তৈরি করো `{subject}` বিষয়ের জন্য। 
            প্রশ্নগুলো স্ট্যান্ডার্ড ভার্সিটি ভর্তি পরীক্ষার মতো কঠিন ও ট্রিকি হতে হবে।
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
                st.subheader("📝 তোমার কুইজ সেট:")
                st.write(response.text)
            except Exception as e:
                st.error(f"ত্রুটি দেখা দিয়েছে: {e}")
