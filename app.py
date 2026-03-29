import streamlit as st
from groq import Groq
import pyperclip
import random
import os

# ---------- API (SECURE WAY) ----------
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("⚠️ API Key not found. Please set GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# ---------- Session State ----------
if "tweets" not in st.session_state:
    st.session_state.tweets = None

if "voice" not in st.session_state:
    st.session_state.voice = None

# ---------- Page ----------
st.set_page_config(
    page_title="BrandVoice AI Tweet Studio",
    page_icon="💖",
    layout="wide"
)

# ---------- Styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

html, body, [class*="css"] {
font-family:'Poppins',sans-serif;
}

.stApp{
background:
radial-gradient(circle at 20% 20%, #ffe4e6 0%, transparent 35%),
radial-gradient(circle at 80% 80%, #e0e7ff 0%, transparent 35%),
linear-gradient(120deg,#f8fbff,#ffffff,#eef5ff);
}

.main-title{
text-align:center;
font-size:48px;
font-weight:700;
margin-top:20px;
background:linear-gradient(90deg,#ff4d6d,#4361ee);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
}

.subtitle{
text-align:center;
font-size:18px;
color:#6b7280;
margin-bottom:30px;
}

.voice-box{
background:white;
padding:24px;
border-radius:16px;
border-left:6px solid #ff4d6d;
margin-bottom:25px;
box-shadow:0 6px 18px rgba(0,0,0,0.08);
}

.tweet-card{
background:white;
padding:20px;
border-radius:16px;
margin-bottom:18px;
box-shadow:0 6px 20px rgba(0,0,0,0.08);
border-left:5px solid #06d6a0;
}

.stButton>button{
border-radius:10px;
background:#4361ee;
color:white;
border:none;
padding:8px 16px;
font-weight:600;
}
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("""
<div class="main-title">💖 BrandVoice AI Tweet Studio</div>
<div class="subtitle">Because every brand deserves tweets with personality ❤️</div>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.header("Brand Information")

brand = st.sidebar.text_input("Brand Name")
industry = st.sidebar.text_input("Industry / Category")

campaign = st.sidebar.selectbox(
    "Campaign Objective",
    ["Engagement", "Promotion", "Brand Awareness"]
)

product = st.sidebar.text_area("Describe the Product")

generate = st.sidebar.button("Generate Tweets")
regen = st.sidebar.button("Generate New Tweets")

# ---------- Tone Detection ----------
def detect_tone_badge(text):
    text = text.lower()

    if "humor" in text or "funny" in text:
        return "😂 Humorous"
    if "premium" in text:
        return "💎 Premium"
    if "motivational" in text:
        return "🔥 Motivational"
    if "friendly" in text:
        return "😊 Friendly"

    return "✨ Neutral"

# ---------- Brand Voice ----------
def analyze_brand_voice(brand, industry, product):
    prompt = f"""
Analyze the brand voice.

Brand: {brand}
Industry: {industry}
Product: {product}

Identify:
- Brand tone
- Target audience
- Content themes
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    except Exception:
        st.error("❌ Error analyzing brand voice. Check API key or internet.")
        return None

# ---------- Tweet Generator ----------
def generate_ai_tweets(brand, industry, campaign, product):
    prompt = f"""
You are a social media strategist.

Brand: {brand}
Industry: {industry}
Product: {product}
Campaign: {campaign}

Generate EXACTLY 10 tweets.

Rules:
- Each tweet on new line
- No numbering
- Short and engaging
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    except Exception:
        st.error("❌ Error generating tweets. Check API key.")
        return None

# ---------- Generate ----------
if generate:
    if brand == "":
        st.warning("Please enter a brand name")
    else:
        with st.spinner("Analyzing brand voice..."):
            st.session_state.voice = analyze_brand_voice(brand, industry, product)

        with st.spinner("Generating tweets..."):
            st.session_state.tweets = generate_ai_tweets(brand, industry, campaign, product)

# ---------- Regenerate ----------
if regen and st.session_state.voice:
    with st.spinner("Generating new tweets..."):
        st.session_state.tweets = generate_ai_tweets(brand, industry, campaign, product)

# ---------- Show Voice ----------
if st.session_state.voice:
    tone = detect_tone_badge(st.session_state.voice)

    st.markdown(f"""
<div class="voice-box">
<b>💓 Brand Voice Analysis</b><br><br>
<b>Detected Tone:</b> {tone}<br><br>
{st.session_state.voice}
</div>
""", unsafe_allow_html=True)

# ---------- Tweets ----------
if st.session_state.tweets:
    st.subheader("✍️ Generated Tweets")

    tweet_list = [t.strip() for t in st.session_state.tweets.split("\n") if t.strip()]
    tweet_list = tweet_list[:10]

    for i, tweet in enumerate(tweet_list):
        trending = random.choice([True, False, False])
        badge = ""

        if trending:
            badge = "<span style='background:#fee2e2;color:#b91c1c;padding:4px 10px;border-radius:8px;font-size:12px;'>🔥 Trending</span>"

        col1, col2 = st.columns([9, 1])

        with col1:
            st.markdown(f"""
<div class="tweet-card">
<b>Tweet {i+1}</b> {badge}
<br><br>
{tweet}
</div>
""", unsafe_allow_html=True)

        with col2:
            if st.button("📑", key=f"copy_{i}"):
                pyperclip.copy(tweet)
                st.toast("Tweet copied!")
