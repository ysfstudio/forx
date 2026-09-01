# 🥇 Gold & Forex Free Analyzer

نسخة **مجانية بالكامل** من منصة تحليل الذهب والفوركس. لا تحتاج أي مفتاح مدفوع.

## كيف تشتغل؟
- تجيب بيانات السعر الحقيقية (شموع OHLC) من **Twelve Data** (خطة مجانية).
- تحسب المؤشرات الفنية (RSI, MACD, SMA20/50, ATR) بكود بايثون عادي.
- تحدد الاتجاه والدعوم/المقاومات ونقاط دخول/هدف/وقف تقريبية بقواعد برمجية بسيطة —
  **بدون أي نموذج ذكاء اصطناعي مدفوع**.

> ⚠️ تعليمي فقط، وليس توصية استثمارية.

---

## 1. المفتاح المطلوب (مجاني 100%)

اذهب إلى: https://twelvedata.com/pricing
اختر **Free Plan** → سجل بالبريد الإلكتروني (بدون بطاقة ائتمان) → انسخ الـ API Key.

الخطة المجانية تعطيك تقريباً 800 طلب/يوم و 8 طلبات/دقيقة، تكفي بسهولة للاستخدام الشخصي.

(اختياري) مفتاح NewsAPI مجاني من https://newsapi.org لتفعيل تبويب الأخبار.

---

## 2. التشغيل محلياً

```bash
python -m venv venv
source venv/bin/activate        # ويندوز: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

يفتح المتصفح على `http://localhost:8501`. الصق مفتاح Twelve Data بالشريط الجانبي واضغط
"جلب البيانات وتحليلها الآن".

---

## 3. رفع المشروع إلى GitHub

```bash
git init
git add .
git commit -m "Initial commit: Gold & Forex Free Analyzer"
git remote add origin https://github.com/USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

---

## 4. نشر مجاني أونلاين (اختياري)

تكدر تنشر الموقع مجاناً بالكامل عبر **Streamlit Community Cloud**:
1. ارفع الكود لمستودع GitHub (خطوة 3).
2. روح لـ https://share.streamlit.io وسجل دخول بحساب GitHub.
3. اختر المستودع وملف `app.py` واضغط Deploy.
4. المفاتيح (API Keys) تُدخل من المستخدم مباشرة داخل الواجهة، فما تحتاج تحطها بإعدادات النشر.

---

## ملاحظات
- الأسعار المعروضة تجريبية/تعليمية بحسب دقة مصدر البيانات المجاني، وقد تختلف قليلاً عن منصة الوسيط (Broker) الخاص بيك.
- التحليل قائم على قواعد فنية بسيطة (Moving Averages, RSI, MACD, ATR) — مو ذكاء اصطناعي توليدي.
