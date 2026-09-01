# 🥇 Gold & Forex AI Analyzer

منصة تحليل ذكية لأسواق الذهب (XAUUSD) والفوركس، تعتمد على رفع صور الشارتات
وتحليلها عبر Claude Vision API، مع واجهة Streamlit احترافية.

> ⚠️ **تنبيه**: هذا التطبيق لأغراض تعليمية وتحليلية فقط، وليس توصية استثمارية.
> التداول بالفوركس والذهب ينطوي على مخاطر عالية.

---

## 1. المتطلبات

- Python 3.9 أو أحدث
- مفتاح Anthropic API (من [console.anthropic.com](https://console.anthropic.com))
- (اختياري) مفتاح NewsAPI مجاني من [newsapi.org](https://newsapi.org) لتفعيل تبويب الأخبار

---

## 2. التثبيت والتشغيل محلياً

```bash
# 1. إنشاء بيئة افتراضية (اختياري لكن مستحسن)
python -m venv venv
source venv/bin/activate        # على ويندوز: venv\Scripts\activate

# 2. تثبيت المكتبات
pip install -r requirements.txt

# 3. تشغيل التطبيق
streamlit run app.py
```

بعدها سيفتح المتصفح تلقائياً على:
```
http://localhost:8501
```

أدخل مفتاح Anthropic API في الشريط الجانبي، وابدأ برفع صور الشارتات.

---

## 3. رفع المشروع إلى GitHub

```bash
# داخل مجلد المشروع
git init
git add .
git commit -m "Initial commit: Gold & Forex AI Analyzer"

# أنشئ مستودع فارغ على GitHub أولاً، ثم:
git remote add origin https://github.com/USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

> استبدل `USERNAME` و `REPO_NAME` باسم حسابك واسم المستودع الذي أنشأته.

### ملاحظة أمان مهمة
لا تضع مفتاح API الخاص بك مباشرة في الكود أو ترفعه على GitHub.
المفتاح يُدخل من المستخدم مباشرة داخل واجهة التطبيق (Session فقط ولا يُحفظ).
إذا رغبت باستخدام متغيرات بيئة بدلاً من ذلك، أضف ملف `.env` وأضفه إلى `.gitignore`.

---

## 4. هيكل الملفات

```
gold_ai_app/
├── app.py              # التطبيق الرئيسي
├── requirements.txt    # المكتبات المطلوبة
└── README.md           # هذا الملف
```

---

## 5. الميزات

- 📊 رفع صورة شارت وتحليلها بالذكاء الاصطناعي (اتجاه، دعوم، مقاومات، نموذج فني)
- 🎯 نقاط دخول/هدف/وقف خسارة تعليمية تقريبية
- 📰 تبويب أخبار مباشرة (اختياري عبر NewsAPI)
- 🗂️ سجل لكل التحليلات السابقة خلال الجلسة
- 🎨 واجهة داكنة احترافية شبيهة بمنصات التداول

---

## 6. تطوير مستقبلي مقترح

- ربط بيانات سعر حية عبر API مثل TwelveData أو Alpha Vantage
- حفظ السجل بشكل دائم عبر قاعدة بيانات بدلاً من session_state
- دعم تحليل عدة أطر زمنية بصورة واحدة (Multi-timeframe)
