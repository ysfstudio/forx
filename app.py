# -*- coding: utf-8 -*-
"""
منصة الذكاء الاصطناعي لتحليل أسواق الفوركس والذهب (XAUUSD)
============================================================
تطبيق Streamlit يسمح للمستخدم برفع صورة شارت (Chart Screenshot)
ويقوم بتحليلها عبر Claude Vision API لاستخراج:
- الاتجاه العام للسوق
- مستويات الدعم والمقاومة
- نقاط الدخول والخروج المقترحة (Entry / TP / SL)
كما يحتوي على قسم أخبار مباشرة وسجل للتحليلات السابقة.

تنبيه مهم: هذا التطبيق لأغراض تعليمية وتحليلية فقط،
ولا يُعتبر توصية استثمارية أو مالية بأي شكل من الأشكال.
القرار النهائي للتداول يقع بالكامل على مسؤولية المستخدم.
"""

import streamlit as st
import base64
import json
import io
import re
from datetime import datetime

import requests
from PIL import Image

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None


# =========================================================
# 1. إعدادات الصفحة العامة
# =========================================================
st.set_page_config(
    page_title="Gold & Forex AI Analyzer",
    page_icon="🥇",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# 2. تصميم الواجهة (Custom CSS) - وضع داكن احترافي شبيه بمنصات التداول
# =========================================================
def inject_custom_css():
    st.markdown(
        """
        <style>
        /* الخلفية العامة */
        .stApp {
            background: linear-gradient(180deg, #0e1117 0%, #131722 100%);
            color: #d1d4dc;
        }

        /* العناوين الرئيسية */
        h1, h2, h3 {
            font-family: 'Segoe UI', sans-serif;
            color: #f5c542;
        }

        /* البطاقات (Cards) */
        .metric-card {
            background-color: #1e222d;
            border: 1px solid #2a2e39;
            border-radius: 14px;
            padding: 18px 22px;
            margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.35);
        }
        .metric-card h4 {
            color: #9aa0aa;
            margin: 0 0 6px 0;
            font-size: 14px;
            font-weight: 500;
        }
        .metric-card .value {
            font-size: 22px;
            font-weight: 700;
        }
        .bullish { color: #26a69a; }
        .bearish { color: #ef5350; }
        .neutral { color: #f5c542; }

        /* شريط جانبي */
        section[data-testid="stSidebar"] {
            background-color: #131722;
            border-right: 1px solid #2a2e39;
        }

        /* أزرار */
        .stButton>button {
            background-color: #f5c542;
            color: #0e1117;
            font-weight: 700;
            border-radius: 10px;
            border: none;
            padding: 0.6em 1.2em;
        }
        .stButton>button:hover {
            background-color: #ffd766;
            color: #0e1117;
        }

        /* صندوق التنبيه */
        .disclaimer-box {
            background-color: #241f14;
            border: 1px solid #f5c542;
            border-radius: 10px;
            padding: 10px 16px;
            font-size: 13px;
            color: #f5c542;
        }

        /* عناصر الأخبار */
        .news-item {
            background-color: #1e222d;
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 10px;
            border-left: 4px solid #f5c542;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 3. الحالة العامة (Session State)
# =========================================================
def init_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []  # كل تحليل سابق يُحفظ هنا
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""


# =========================================================
# 4. أدوات مساعدة (Helper Functions)
# =========================================================
def image_to_base64(uploaded_file) -> tuple[str, str]:
    """تحويل الصورة المرفوعة إلى base64 + تحديد نوعها (media_type)."""
    image = Image.open(uploaded_file)
    if image.mode != "RGB":
        image = image.convert("RGB")

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=92)
    img_bytes = buffer.getvalue()
    b64_str = base64.b64encode(img_bytes).decode("utf-8")
    return b64_str, "image/jpeg"


def build_analysis_prompt() -> str:
    """صياغة تعليمات دقيقة لنموذج الذكاء الاصطناعي حتى يرجع تحليل منظم بصيغة JSON."""
    return """
أنت محلل فني محترف متخصص بأسواق الفوركس والذهب (XAUUSD).
سيتم تزويدك بصورة شارت (رسم بياني للسعر). حلل الصورة بعناية وأرجع تحليلاً
تعليمياً منظماً بصيغة JSON فقط، بدون أي نص إضافي خارج JSON، بالمفاتيح التالية:

{
  "trend": "صاعد" أو "هابط" أو "عرضي",
  "trend_confidence": رقم من 0 إلى 100 يمثل مدى وضوح الاتجاه في الصورة,
  "support_levels": [قائمة بمستويات الدعم التقريبية كأرقام أو أوصاف نصية],
  "resistance_levels": [قائمة بمستويات المقاومة التقريبية],
  "pattern_detected": "اسم النموذج الفني إن وجد (مثل مثلث، رأس وكتفين...) أو null",
  "suggested_entry": "منطقة دخول تعليمية تقريبية أو null إذا لم تكن الصورة واضحة كفاية",
  "suggested_take_profit": "هدف ربح تعليمي تقريبي أو null",
  "suggested_stop_loss": "مستوى وقف خسارة تعليمي تقريبي أو null",
  "risk_reward_note": "ملاحظة مختصرة عن نسبة المخاطرة إلى العائد",
  "summary": "ملخص عام لحالة السوق كما تظهر في الصورة في 3-4 جمل",
  "confidence_level": "منخفضة أو متوسطة أو عالية - مدى ثقتك بالتحليل بناءً على وضوح الصورة"
}

ملاحظات إلزامية:
- لا تعتبر هذا التحليل توصية استثمارية قطعية، بل قراءة تعليمية لما تظهره الصورة فقط.
- إذا كانت الصورة غير واضحة أو لا تحتوي على شارت فعلي، اذكر ذلك في summary وأرجع null للحقول غير المؤكدة.
- التزم حصراً بصيغة JSON صحيحة القابلة للتحليل مباشرة.
"""


def call_claude_vision(api_key: str, b64_image: str, media_type: str) -> dict:
    """استدعاء Claude Vision API لتحليل صورة الشارت وإرجاع النتيجة كقاموس Python."""
    if Anthropic is None:
        raise RuntimeError("مكتبة anthropic غير مثبتة. ثبّتها عبر: pip install anthropic")

    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1200,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": b64_image,
                        },
                    },
                    {"type": "text", "text": build_analysis_prompt()},
                ],
            }
        ],
    )

    raw_text = "".join(
        block.text for block in response.content if getattr(block, "type", "") == "text"
    )

    # تنظيف أي رموز Markdown محتملة حول الـ JSON
    cleaned = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "trend": "غير معروف",
            "trend_confidence": 0,
            "support_levels": [],
            "resistance_levels": [],
            "pattern_detected": None,
            "suggested_entry": None,
            "suggested_take_profit": None,
            "suggested_stop_loss": None,
            "risk_reward_note": "تعذر تحليل استجابة النموذج بصيغة منظمة.",
            "summary": raw_text[:600],
            "confidence_level": "منخفضة",
        }


def trend_css_class(trend: str) -> str:
    if "صاعد" in trend:
        return "bullish"
    if "هابط" in trend:
        return "bearish"
    return "neutral"


def fetch_market_news(news_api_key: str, query: str = "XAUUSD OR gold OR forex"):
    """
    جلب أخبار مرتبطة بالسوق عبر NewsAPI (اختياري، يحتاج مفتاح من newsapi.org).
    إذا لم يتوفر مفتاح، يتم إرجاع رسالة توضيحية بدلاً من بيانات وهمية.
    """
    if not news_api_key:
        return None, "لم يتم إدخال مفتاح NewsAPI في الشريط الجانبي، لذلك لا يمكن جلب الأخبار الحية."

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 8,
        "apiKey": news_api_key,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("articles", []), None
    except Exception as e:
        return None, f"تعذر جلب الأخبار: {e}"


# =========================================================
# 5. الشريط الجانبي (Sidebar)
# =========================================================
def render_sidebar():
    with st.sidebar:
        st.markdown("## ⚙️ الإعدادات")

        st.session_state.api_key = st.text_input(
            "مفتاح Anthropic API",
            value=st.session_state.api_key,
            type="password",
            help="يُستخدم للاتصال بنموذج Claude لتحليل الصور. لا يتم حفظه أو إرساله لأي جهة أخرى.",
        )

        news_api_key = st.text_input(
            "مفتاح NewsAPI (اختياري)",
            type="password",
            help="للحصول على أخبار حية عن الذهب والفوركس من newsapi.org",
        )

        st.markdown("---")
        st.markdown("### 🕒 سجل التحليلات السابقة")

        if not st.session_state.history:
            st.caption("لا يوجد تحليلات محفوظة بعد.")
        else:
            for i, item in enumerate(reversed(st.session_state.history[-10:])):
                with st.expander(f"{item['time']} — {item['trend']}"):
                    st.write(item["summary"])

        st.markdown("---")
        st.markdown(
            '<div class="disclaimer-box">⚠️ هذا التطبيق لأغراض تعليمية فقط '
            "ولا يمثل نصيحة مالية أو استثمارية.</div>",
            unsafe_allow_html=True,
        )

    return news_api_key


# =========================================================
# 6. تبويب تحليل الشارت
# =========================================================
def render_chart_analysis_tab():
    st.subheader("📊 تحليل الشارت بالذكاء الاصطناعي")
    st.write("ارفع لقطة شاشة لشارت الذهب (XAUUSD) أو أي زوج فوركس، وسيقوم النظام بتحليلها خطوة بخطوة.")

    uploaded_file = st.file_uploader(
        "اختر صورة الشارت (PNG / JPG)", type=["png", "jpg", "jpeg"]
    )

    col_img, col_btn = st.columns([2, 1])

    if uploaded_file:
        with col_img:
            st.image(uploaded_file, caption="الصورة المرفوعة", use_container_width=True)

    with col_btn:
        analyze_clicked = st.button("🔍 تحليل الشارت الآن", use_container_width=True)

    if analyze_clicked:
        if not uploaded_file:
            st.warning("الرجاء رفع صورة الشارت أولاً.")
            return
        if not st.session_state.api_key:
            st.error("الرجاء إدخال مفتاح Anthropic API في الشريط الجانبي أولاً.")
            return

        with st.spinner("جاري تحليل الشارت... قد يستغرق ذلك بضع ثوانٍ ⏳"):
            try:
                b64_image, media_type = image_to_base64(uploaded_file)
                result = call_claude_vision(st.session_state.api_key, b64_image, media_type)
            except Exception as e:
                st.error(f"حدث خطأ أثناء التحليل: {e}")
                return

        # حفظ في السجل
        st.session_state.history.append(
            {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "trend": result.get("trend", "غير معروف"),
                "summary": result.get("summary", ""),
            }
        )

        render_analysis_result(result)


def render_analysis_result(result: dict):
    st.markdown("### 🧭 نتيجة التحليل")

    trend = result.get("trend", "غير معروف")
    css_class = trend_css_class(trend)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""<div class="metric-card"><h4>الاتجاه العام</h4>
            <div class="value {css_class}">{trend}</div></div>""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""<div class="metric-card"><h4>مستوى الثقة بالنموذج المرصود</h4>
            <div class="value">{result.get('trend_confidence', 0)}%</div></div>""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""<div class="metric-card"><h4>درجة ثقة التحليل</h4>
            <div class="value">{result.get('confidence_level', 'غير محدد')}</div></div>""",
            unsafe_allow_html=True,
        )

    st.markdown("#### 📌 مستويات الدعم والمقاومة")
    c4, c5 = st.columns(2)
    with c4:
        st.markdown("**الدعوم:**")
        supports = result.get("support_levels") or ["لا يوجد بيانات كافية"]
        for s in supports:
            st.write(f"- {s}")
    with c5:
        st.markdown("**المقاومات:**")
        resistances = result.get("resistance_levels") or ["لا يوجد بيانات كافية"]
        for r in resistances:
            st.write(f"- {r}")

    if result.get("pattern_detected"):
        st.info(f"🔺 نموذج فني محتمل: **{result['pattern_detected']}**")

    st.markdown("#### 🎯 نقاط تعليمية للدخول والخروج (تقريبية)")
    c6, c7, c8 = st.columns(3)
    c6.metric("نقطة الدخول المقترحة", result.get("suggested_entry") or "غير متوفر")
    c7.metric("هدف الربح (TP)", result.get("suggested_take_profit") or "غير متوفر")
    c8.metric("وقف الخسارة (SL)", result.get("suggested_stop_loss") or "غير متوفر")

    if result.get("risk_reward_note"):
        st.caption(f"ℹ️ {result['risk_reward_note']}")

    st.markdown("#### 📝 الملخص العام")
    st.write(result.get("summary", "لا يوجد ملخص متاح."))

    st.markdown(
        '<div class="disclaimer-box">⚠️ هذه القراءة تعليمية بناءً على الصورة المرفوعة فقط، '
        "وليست توصية تداول. الأسواق المالية عالية المخاطر ويجب استشارة مختص مرخّص قبل اتخاذ أي قرار.</div>",
        unsafe_allow_html=True,
    )


# =========================================================
# 7. تبويب الأخبار المباشرة
# =========================================================
def render_news_tab(news_api_key: str):
    st.subheader("📰 أخبار السوق المباشرة")
    st.write("آخر الأخبار المرتبطة بالذهب والفوركس (تحتاج مفتاح NewsAPI مجاني من newsapi.org).")

    if st.button("🔄 تحديث الأخبار"):
        articles, error = fetch_market_news(news_api_key)

        if error:
            st.warning(error)
        elif not articles:
            st.info("لا توجد أخبار حالياً.")
        else:
            for a in articles:
                title = a.get("title", "بدون عنوان")
                source = a.get("source", {}).get("name", "مصدر غير معروف")
                published = a.get("publishedAt", "")[:16].replace("T", " ")
                url = a.get("url", "#")
                st.markdown(
                    f"""<div class="news-item">
                    <b>{title}</b><br>
                    <small>{source} • {published}</small><br>
                    <a href="{url}" target="_blank">قراءة المزيد ↗</a>
                    </div>""",
                    unsafe_allow_html=True,
                )
    else:
        st.caption("اضغط \"تحديث الأخبار\" لجلب آخر المستجدات.")


# =========================================================
# 8. تبويب سجل التحليلات
# =========================================================
def render_history_tab():
    st.subheader("🗂️ سجل التحليلات الكامل")

    if not st.session_state.history:
        st.info("لم يتم إجراء أي تحليل بعد. ابدأ من تبويب \"تحليل الشارت\".")
        return

    for i, item in enumerate(reversed(st.session_state.history)):
        with st.expander(f"{item['time']} — الاتجاه: {item['trend']}"):
            st.write(item["summary"])

    if st.button("🗑️ مسح السجل بالكامل"):
        st.session_state.history = []
        st.rerun()


# =========================================================
# 9. نقطة الدخول الرئيسية
# =========================================================
def main():
    inject_custom_css()
    init_session_state()

    st.title("🥇 Gold & Forex AI Analyzer")
    st.caption("منصة تحليل ذكية لأسواق الذهب والفوركس عبر تحليل صور الشارتات بالذكاء الاصطناعي")

    news_api_key = render_sidebar()

    tab1, tab2, tab3 = st.tabs(["📊 تحليل الشارت", "📰 الأخبار المباشرة", "🗂️ السجل"])

    with tab1:
        render_chart_analysis_tab()
    with tab2:
        render_news_tab(news_api_key)
    with tab3:
        render_history_tab()


if __name__ == "__main__":
    main()
