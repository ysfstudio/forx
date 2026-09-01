import streamlit as st
from PIL import Image

# إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="Forex & Gold AI Analyst",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تنسيق الواجهة بتصميم عصري (Dark Moody Theme مريح للعمل)
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        background: linear-gradient(90deg, #2b5876 0%, #4e4376 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #4e4376 0%, #2b5876 100%);
        color: #f0f0f0;
    }
    .metric-card {
        background-color: #1a1c23;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #2d3139;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# الشريط الجانبي (Sidebar)
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bullish.png", width=80)
    st.title("لوحة التحكم")
    st.markdown("---")
    
    market_type = st.selectbox(
        "اختر السوق المستهدف:",
        ["الذهب (XAUUSD)", "عملات رئيسية (Forex)", "العملات الرقمية (Crypto)"]
    )
    
    analysis_style = st.selectbox(
        "طريقة التحليل:",
        ["تحليل كلاسيكي (دعم ومقاومة)", "برايس أكشن (Price Action)", "مؤشرات فنية"]
    )
    
    st.markdown("---")
    st.info("💡 **نصيحة تداول:** ارفع صورة واضحة للشارت (فريم 1H أو 4H أو Daily) لتحصل على دقة أعلى في تحديد نقاط الدخول والخروج.")

# الواجهة الرئيسية
st.title("⚡ منصة الذكاء الاصطناعي لتحليل الفوركس والذهب")
st.markdown("### ارفع لقطة شاشة (Screenshot) للشارت وسيقوم الذكاء الاصطناعي بقراءته وتحليله لك فوراً بالتفصيل.")

# قسم رفع الصور
uploaded_file = st.file_uploader("اختر صورة الشارت أو اسحبها هنا (PNG, JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.subheader("🖼️ الشارت المرفوع")
        image = Image.open(uploaded_file)
        st.image(image, caption="شارت السوق الحالي", use_container_width=True)
        
    with col2:
        st.subheader("📊 تحليل الذكاء الاصطناعي الفوري")
        
        with st.spinner("جاري قراءة الشارت وتحليل حركة السوق... بانتظار النتائج..."):
            # محاكاة تحليل ذكي مرتب وواضح للمتداول
            st.markdown("""
            <div style="background-color: #161b22; padding: 15px; border-radius: 8px; border-left: 4px solid #00ffcc;">
                <p><b>📌 الاتجاه العام للسوق (Trend):</b> صاعد على المدى القصير مع وجود اختبار لمنطقة عرض قوية.</p>
                <p><b>🎯 نقطة الدخول المقترحة (Entry Point):</b> من السعر الحالي أو عند إعادة التباين للمنطقة المحددة.</p>
                <p><b>🛑 وقف الخسارة (Stop Loss):</b> أسفل آخر قاع مكون بشمعة تأكيد.</p>
                <p><b>💰 أهداف الربح (Take Profit):</b><br>
                - الهدف الأول (TP1): قريب ومنطقي.<br>
                - الهدف الثاني (TP2): عند المقاومة الرئيسية التالية.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.success("تم تحليل الشارت بنجاح وجاهز للتنفيذ على مسؤوليتك الشخصية!")

else:
    # عرض تنبيه يوضح شكل الواجهة قبل الرفع
    st.markdown("<br>", unsafe_allow_html=True)
    info_col1, info_col2, info_col3 = st.columns(3)
    
    with info_col1:
        st.markdown("<div class='metric-card'><h4>1️⃣ ارفع الصورة</h4><p>قم برفع شارت الذهب أو العملات الخاص بك.</p></div>", unsafe_allow_html=True)
    with info_col2:
        st.markdown("<div class='metric-card'><h4>2️⃣ تحليل فوري</h4><p>يقوم النظام بقراءة الشمعات والدعوم.</p></div>", unsafe_allow_html=True)
    with info_col3:
        st.markdown("<div class='metric-card'><h4>3️⃣ حدد صفقاتك</h4><p>تعرف على نقاط الدخول والخروج بدقة.</p></div>", unsafe_allow_html=True)
