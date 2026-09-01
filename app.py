# -*- coding: utf-8 -*-
"""
منصة تحليل الذهب والفوركس - النسخة المجانية بالكامل
=====================================================
هذه النسخة لا تحتاج أي مفتاح مدفوع. تعتمد على:
- بيانات سعر حقيقية من Twelve Data (خطة مجانية - Free Tier)
- تحليل فني بقواعد برمجية (RSI, MACD, Moving Averages, دعوم/مقاومات)
  بدون أي نموذج ذكاء اصطناعي مدفوع.

تنبيه: هذا التطبيق لأغراض تعليمية وتحليلية فقط، وليس توصية استثمارية.
التداول بالفوركس والذهب ينطوي على مخاطر عالية.
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import plotly.graph_objects as go


# =========================================================
# 1. إعدادات الصفحة
# =========================================================
st.set_page_config(
    page_title="Gold & Forex Free Analyzer",
    page_icon="🥇",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# 2. تصميم الواجهة (Custom CSS)
# =========================================================
def inject_custom_css():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #0e1117 0%, #131722 100%);
            color: #d1d4dc;
        }
        h1, h2, h3 { font-family: 'Segoe UI', sans-serif; color: #f5c542; }
        .metric-card {
            background-color: #1e222d;
            border: 1px solid #2a2e39;
            border-radius: 14px;
            padding: 18px 22px;
            margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.35);
        }
        .metric-card h4 { color: #9aa0aa; margin: 0 0 6px 0; font-size: 14px; font-weight: 500; }
        .metric-card .value { font-size: 22px; font-weight: 700; }
        .bullish { color: #26a69a; }
        .bearish { color: #ef5350; }
        .neutral { color: #f5c542; }
        section[data-testid="stSidebar"] { background-color: #131722; border-right: 1px solid #2a2e39; }
        .stButton>button {
            background-color: #f5c542; color: #0e1117; font-weight: 700;
            border-radius: 10px; border: none; padding: 0.6em 1.2em;
        }
        .stButton>button:hover { background-color: #ffd766; color: #0e1117; }
        .disclaimer-box {
            background-color: #241f14; border: 1px solid #f5c542;
            border-radius: 10px; padding: 10px 16px; font-size: 13px; color: #f5c542;
        }
        .news-item {
            background-color: #1e222d; border-radius: 10px; padding: 12px 16px;
            margin-bottom: 10px; border-left: 4px solid #f5c542;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 3. الحالة العامة
# =========================================================
def init_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []
    if "td_api_key" not in st.session_state:
        st.session_state.td_api_key = ""


# =========================================================
# 4. جلب بيانات السعر من Twelve Data (مجاني)
# =========================================================
@st.cache_data(ttl=60, show_spinner=False)
def fetch_price_data(api_key: str, symbol: str, interval: str, output_size: int = 200):
    """
    يجلب بيانات الشموع (OHLC) من Twelve Data.
    خطة Free Tier تكفي لهذا الاستخدام (800 طلب/يوم تقريباً).
    """
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": output_size,
        "apikey": api_key,
        "order": "ASC",
    }
    r = requests.get(url, params=params, timeout=15)
    data = r.json()

    if "values" not in data:
        raise RuntimeError(data.get("message", "تعذر جلب البيانات. تأكد من صحة المفتاح والرمز."))

    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)
    df = df.sort_values("datetime").reset_index(drop=True)
    return df


# =========================================================
# 5. حساب المؤشرات الفنية يدوياً (بدون مكتبات مدفوعة)
# =========================================================
def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # المتوسطات المتحركة
    df["sma20"] = df["close"].rolling(20).mean()
    df["sma50"] = df["close"].rolling(50).mean()

    # RSI (14)
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi14"] = 100 - (100 / (1 + rs))

    # MACD (12, 26, 9)
    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]

    # ATR (14) لتقدير التذبذب (يُستخدم لتحديد SL/TP تقريبياً)
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["atr14"] = tr.rolling(14).mean()

    return df


# =========================================================
# 6. تحديد الدعوم والمقاومات (Pivot بسيط)
# =========================================================
def find_support_resistance(df: pd.DataFrame, lookback: int = 40):
    recent = df.tail(lookback)
    resistance = recent["high"].max()
    support = recent["low"].min()
    return round(support, 2), round(resistance, 2)


# =========================================================
# 7. محرك التحليل القائم على القواعد (بدون ذكاء اصطناعي مدفوع)
# =========================================================
def rule_based_analysis(df: pd.DataFrame) -> dict:
    last = df.iloc[-1]
    price = last["close"]

    # تحديد الاتجاه العام بناءً على المتوسطات المتحركة
    if pd.notna(last["sma20"]) and pd.notna(last["sma50"]):
        if last["sma20"] > last["sma50"] and price > last["sma20"]:
            trend = "صاعد"
        elif last["sma20"] < last["sma50"] and price < last["sma20"]:
            trend = "هابط"
        else:
            trend = "عرضي"
    else:
        trend = "غير كافٍ من البيانات"

    # حالة RSI
    rsi = last["rsi14"]
    if pd.isna(rsi):
        rsi_state = "غير متوفر"
    elif rsi >= 70:
        rsi_state = "تشبع شرائي (Overbought)"
    elif rsi <= 30:
        rsi_state = "تشبع بيعي (Oversold)"
    else:
        rsi_state = "منطقة متوازنة"

    # إشارة MACD
    if pd.notna(last["macd"]) and pd.notna(last["macd_signal"]):
        macd_signal_text = "تقاطع إيجابي (زخم صاعد)" if last["macd"] > last["macd_signal"] else "تقاطع سلبي (زخم هابط)"
    else:
        macd_signal_text = "غير متوفر"

    support, resistance = find_support_resistance(df)
    atr = last["atr14"] if pd.notna(last["atr14"]) else 0

    # اقتراح تعليمي لنقاط الدخول/الهدف/الوقف بناءً على ATR (تقريبي وليس دقيق)
    if trend == "صاعد":
        entry = round(price, 2)
        tp = round(price + atr * 2, 2)
        sl = round(price - atr * 1, 2)
    elif trend == "هابط":
        entry = round(price, 2)
        tp = round(price - atr * 2, 2)
        sl = round(price + atr * 1, 2)
    else:
        entry, tp, sl = None, None, None

    summary_parts = [
        f"السعر الحالي {round(price, 2)}.",
        f"الاتجاه العام حسب المتوسطات المتحركة (SMA20/SMA50): {trend}.",
        f"مؤشر RSI عند {round(rsi, 1) if pd.notna(rsi) else 'غير متوفر'} ({rsi_state}).",
        f"مؤشر MACD يشير إلى: {macd_signal_text}.",
        f"أقرب دعم ملحوظ عند {support}، وأقرب مقاومة عند {resistance}.",
    ]

    return {
        "price": round(price, 2),
        "trend": trend,
        "rsi": round(rsi, 1) if pd.notna(rsi) else None,
        "rsi_state": rsi_state,
        "macd_signal_text": macd_signal_text,
        "support": support,
        "resistance": resistance,
        "entry": entry,
        "take_profit": tp,
        "stop_loss": sl,
        "summary": " ".join(summary_parts),
        "timestamp": df.iloc[-1]["datetime"],
    }


def trend_css_class(trend: str) -> str:
    if "صاعد" in trend:
        return "bullish"
    if "هابط" in trend:
        return "bearish"
    return "neutral"


# =========================================================
# 8. رسم الشارت (Plotly - مجاني بالكامل)
# =========================================================
def plot_chart(df: pd.DataFrame, symbol: str):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df["datetime"], open=df["open"], high=df["high"],
        low=df["low"], close=df["close"], name=symbol,
        increasing_line_color="#26a69a", decreasing_line_color="#ef5350",
    ))
    fig.add_trace(go.Scatter(x=df["datetime"], y=df["sma20"], line=dict(color="#f5c542", width=1.3), name="SMA 20"))
    fig.add_trace(go.Scatter(x=df["datetime"], y=df["sma50"], line=dict(color="#3d5afe", width=1.3), name="SMA 50"))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        height=500,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


# =========================================================
# 9. الأخبار (اختياري - NewsAPI المجاني)
# =========================================================
def fetch_market_news(news_api_key: str, query: str = "XAUUSD OR gold OR forex"):
    if not news_api_key:
        return None, "لم يتم إدخال مفتاح NewsAPI، لذلك لا يمكن جلب الأخبار الحية (اختياري)."
    url = "https://newsapi.org/v2/everything"
    params = {"q": query, "sortBy": "publishedAt", "language": "en", "pageSize": 8, "apiKey": news_api_key}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json().get("articles", []), None
    except Exception as e:
        return None, f"تعذر جلب الأخبار: {e}"


# =========================================================
# 10. الشريط الجانبي
# =========================================================
def render_sidebar():
    with st.sidebar:
        st.markdown("## ⚙️ الإعدادات")

        st.session_state.td_api_key = st.text_input(
            "مفتاح Twelve Data API (مجاني)",
            value=st.session_state.td_api_key,
            type="password",
            help="سجل حساب مجاني من twelvedata.com واحصل على مفتاح API بدون بطاقة ائتمان.",
        )
        st.caption("🔗 احصل على مفتاحك من: twelvedata.com/pricing (اختر Free)")

        symbol = st.selectbox(
            "الرمز (Symbol)",
            ["XAU/USD", "EUR/USD", "GBP/USD", "USD/JPY"],
            index=0,
        )

        interval = st.selectbox(
            "الإطار الزمني",
            ["5min", "15min", "1h", "4h", "1day"],
            index=2,
        )

        news_api_key = st.text_input(
            "مفتاح NewsAPI (اختياري ومجاني)",
            type="password",
            help="من newsapi.org - للأخبار الحية فقط.",
        )

        st.markdown("---")
        st.markdown("### 🕒 سجل التحليلات")
        if not st.session_state.history:
            st.caption("لا يوجد تحليلات محفوظة بعد.")
        else:
            for item in reversed(st.session_state.history[-10:]):
                with st.expander(f"{item['time']} — {item['trend']}"):
                    st.write(item["summary"])

        st.markdown("---")
        st.markdown(
            '<div class="disclaimer-box">⚠️ هذا التطبيق مجاني بالكامل ويعتمد على '
            "تحليل فني بقواعد برمجية، وليس توصية استثمارية.</div>",
            unsafe_allow_html=True,
        )

    return symbol, interval, news_api_key


# =========================================================
# 11. تبويب التحليل الرئيسي
# =========================================================
def render_analysis_tab(symbol: str, interval: str):
    st.subheader(f"📊 تحليل {symbol} المباشر (مجاني بالكامل)")

    if not st.session_state.td_api_key:
        st.info("أدخل مفتاح Twelve Data المجاني في الشريط الجانبي للبدء. التسجيل مجاني بالكامل بدون بطاقة ائتمان.")
        return

    if st.button("🔄 جلب البيانات وتحليلها الآن", use_container_width=True):
        with st.spinner("جاري جلب البيانات وتحليلها..."):
            try:
                df = fetch_price_data(st.session_state.td_api_key, symbol, interval)
                df = compute_indicators(df)
                result = rule_based_analysis(df)
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
                return

        st.session_state.history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "trend": result["trend"],
            "summary": result["summary"],
        })

        st.plotly_chart(plot_chart(df, symbol), use_container_width=True)
        render_result(result)


def render_result(result: dict):
    css_class = trend_css_class(result["trend"])

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card"><h4>السعر الحالي</h4>
        <div class="value">{result['price']}</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card"><h4>الاتجاه العام</h4>
        <div class="value {css_class}">{result['trend']}</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card"><h4>RSI (14)</h4>
        <div class="value">{result['rsi']} - {result['rsi_state']}</div></div>""", unsafe_allow_html=True)

    st.markdown(f"**📉 إشارة MACD:** {result['macd_signal_text']}")

    c4, c5 = st.columns(2)
    c4.metric("أقرب دعم", result["support"])
    c5.metric("أقرب مقاومة", result["resistance"])

    st.markdown("#### 🎯 نقاط تعليمية تقريبية (بناءً على ATR)")
    c6, c7, c8 = st.columns(3)
    c6.metric("نقطة الدخول", result["entry"] or "غير متاح (سوق عرضي)")
    c7.metric("هدف الربح (TP)", result["take_profit"] or "—")
    c8.metric("وقف الخسارة (SL)", result["stop_loss"] or "—")

    st.markdown("#### 📝 الملخص")
    st.write(result["summary"])

    st.markdown(
        '<div class="disclaimer-box">⚠️ هذا التحليل آلي بقواعد فنية بسيطة، وليس توصية تداول. '
        "الأسواق المالية عالية المخاطر، استشر مختصاً مرخصاً قبل اتخاذ أي قرار.</div>",
        unsafe_allow_html=True,
    )


# =========================================================
# 12. تبويب الأخبار
# =========================================================
def render_news_tab(news_api_key: str):
    st.subheader("📰 أخبار السوق المباشرة")
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
                    f"""<div class="news-item"><b>{title}</b><br>
                    <small>{source} • {published}</small><br>
                    <a href="{url}" target="_blank">قراءة المزيد ↗</a></div>""",
                    unsafe_allow_html=True,
                )
    else:
        st.caption('اضغط "تحديث الأخبار" لجلب آخر المستجدات (اختياري - يحتاج مفتاح NewsAPI).')


# =========================================================
# 13. تبويب السجل
# =========================================================
def render_history_tab():
    st.subheader("🗂️ سجل التحليلات")
    if not st.session_state.history:
        st.info('لم يتم إجراء أي تحليل بعد. ابدأ من تبويب "التحليل".')
        return
    for item in reversed(st.session_state.history):
        with st.expander(f"{item['time']} — الاتجاه: {item['trend']}"):
            st.write(item["summary"])
    if st.button("🗑️ مسح السجل"):
        st.session_state.history = []
        st.rerun()


# =========================================================
# 14. نقطة الدخول
# =========================================================
def main():
    inject_custom_css()
    init_session_state()

    st.title("🥇 Gold & Forex Free Analyzer")
    st.caption("تحليل فني مجاني بالكامل لأسواق الذهب والفوركس، يعتمد على بيانات حقيقية وقواعد برمجية بدون أي تكلفة.")

    symbol, interval, news_api_key = render_sidebar()

    tab1, tab2, tab3 = st.tabs(["📊 التحليل", "📰 الأخبار", "🗂️ السجل"])
    with tab1:
        render_analysis_tab(symbol, interval)
    with tab2:
        render_news_tab(news_api_key)
    with tab3:
        render_history_tab()


if __name__ == "__main__":
    main()
