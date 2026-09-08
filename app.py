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

