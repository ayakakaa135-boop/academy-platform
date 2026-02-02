# 🎓 الأكاديمية التعليمية | Academy Platform

<div align="center">

![Django](https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![HTMX](https://img.shields.io/badge/HTMX-1.9-3366CC?style=for-the-badge&logo=htmx&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**منصة تعليمية متكاملة مع دعم كامل للعربية والإنجليزية**

**Full-Featured Learning Management System with Arabic & English Support**

[المميزات](#-المميزات) • [التثبيت](#-التثبيت) • [الاستخدام](#-الاستخدام) • [التوثيق](#-التوثيق) • [المساهمة](#-المساهمة)

</div>

---

## 📋 جدول المحتويات

- [نظرة عامة](#-نظرة-عامة)
- [المميزات الرئيسية](#-المميزات-الرئيسية)
- [التقنيات المستخدمة](#️-التقنيات-المستخدمة)
- [البنية التحتية](#-البنية-التحتية)
- [التثبيت السريع](#-التثبيت-السريع)
- [الإعداد](#️-الإعداد)
- [الاستخدام](#-الاستخدام)
- [HTMX API](#-htmx-api)
- [التوثيق](#-التوثيق)
- [الأداء](#-الأداء)
- [المساهمة](#-المساهمة)
- [الترخيص](#-الترخيص)

---

## 🌟 نظرة عامة

**الأكاديمية التعليمية** هي منصة تعليمية شاملة ومتطورة مبنية باستخدام Django، توفر تجربة تعلم حديثة وتفاعلية مع واجهة مستخدم احترافية ودعم كامل للغتين العربية والإنجليزية.

### ✨ لماذا هذه المنصة؟

- 🚀 **أداء فائق** - مبنية بأحدث التقنيات والممارسات
- 🎨 **تصميم عصري** - واجهة احترافية مع خطوط عربية جميلة
- 🌐 **متعددة اللغات** - RTL/LTR تلقائي مع دعم كامل
- 📱 **متجاوبة بالكامل** - تعمل بسلاسة على جميع الأجهزة
- 💳 **دفع آمن** - تكامل احترافي مع Stripe
- ⚡ **تفاعلية** - تجربة سلسة بدون إعادة تحميل باستخدام HTMX
- 📧 **رسائل احترافية** - قوالب بريد HTML فاخرة

---

## 🎯 المميزات الرئيسية

### 🎓 نظام إدارة الدورات

<details>
<summary><b>انقر للتوسيع</b></summary>

- ✅ **دورات غير محدودة** مع تصنيفات وفئات متعددة
- ✅ **مستويات صعوبة** (مبتدئ، متوسط، متقدم)
- ✅ **دروس فيديو** - دعم YouTube, Vimeo, ملفات محلية
- ✅ **دروس تجريبية مجانية** لجذب الطلاب
- ✅ **ترتيب الدروس** بسهولة
- ✅ **محرر نصوص غني** (TinyMCE)
- ✅ **تتبع التقدم** تلقائياً
- ✅ **شهادات إتمام** (قريباً)

</details>

### 👥 إدارة المستخدمين المتقدمة

<details>
<summary><b>انقر للتوسيع</b></summary>

- ✅ **مصادقة محسّنة** باستخدام Django Allauth
- ✅ **التحقق من البريد الإلكتروني** إلزامي
- ✅ **إعادة تعيين كلمة المرور** آمنة
- ✅ **ملفات شخصية كاملة** مع صور
- ✅ **لوحة تحكم شخصية** للمستخدم
- ✅ **تتبع التقدم والإنجازات**
- ✅ **سجل الدفعات والفواتير**
- ✅ **إشعارات بريد إلكتروني** ذكية

</details>

### 💬 التفاعل والمجتمع

<details>
<summary><b>انقر للتوسيع</b></summary>

- ✅ **نظام تعليقات متقدم** مع HTMX
- ✅ **ردود متداخلة** (Nested Replies)
- ✅ **نظام تقييمات ⭐** تفاعلي
- ✅ **مراجعات الدورات** من الطلاب
- ✅ **إضافة/حذف فوري** بدون reload
- ✅ **تصفية وبحث** ديناميكي

</details>

### 💳 نظام دفع احترافي

<details>
<summary><b>انقر للتوسيع</b></summary>

- ✅ **تكامل Stripe كامل** مع Webhooks
- ✅ **دفع آمن ومشفر** PCI compliant
- ✅ **فواتير تلقائية** بعد كل دفعة
- ✅ **تأكيد بريد HTML** فاخر
- ✅ **سجل معاملات شامل**
- ✅ **دعم استرجاع المبالغ**
- ✅ **عملات متعددة** (قريباً)

</details>

### 📝 مدونة تعليمية

<details>
<summary><b>انقر للتوسيع</b></summary>

- ✅ **مقالات غير محدودة**
- ✅ **تصنيفات ووسوم**
- ✅ **نظام تعليقات**
- ✅ **محرر غني** TinyMCE
- ✅ **SEO محسّن**
- ✅ **مشاركة اجتماعية**

</details>

### 🎨 تصميم وتجربة استخدام استثنائية

<details>
<summary><b>انقر للتوسيع</b></summary>

- ✅ **خطوط عربية احترافية** (Cairo, Tajawal, IBM Plex)
- ✅ **نظام ألوان متناسق** مع 20+ لون
- ✅ **انتقالات سلسة** (transitions)
- ✅ **تأثيرات Hover** متقدمة
- ✅ **Animations احترافية** Animate.css
- ✅ **Dark Mode Support**
- ✅ **RTL/LTR تلقائي**
- ✅ **800+ سطر CSS** مخصص

</details>

### ⚡ تفاعلية متقدمة (HTMX)

<details>
<summary><b>انقر للتوسيع</b></summary>

- ✅ **بحث مباشر** (Live Search) مع debounce
- ✅ **تصفية ديناميكية** للدورات
- ✅ **إضافة تعليقات** بدون reload
- ✅ **تقييمات فورية** ⭐
- ✅ **تحديث التقدم** تلقائياً
- ✅ **Infinite Scroll**
- ✅ **معاينة سريعة** للدورات في Modal
- ✅ **15+ ميزة تفاعلية**

</details>

### 📧 قوالب بريد إلكتروني فاخرة

<details>
<summary><b>انقر للتوسيع</b></summary>

- ✅ **8 قوالب HTML** احترافية
- ✅ **تصميم Responsive** للموبايل
- ✅ **Gradient وألوان** جذابة
- ✅ **بريد ترحيبي** عند التسجيل
- ✅ **تأكيد الشراء** مع تفاصيل كاملة
- ✅ **إشعارات أمان** (تسجيل دخول، تغيير كلمة مرور)
- ✅ **تذكيرات** ذكية
- ✅ **Footer احترافي** مع روابط

</details>

---

## 🛠️ التقنيات المستخدمة

### Backend Stack

| التقنية | الإصدار | الاستخدام |
|---------|---------|-----------|
| ![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white) | 3.11+ | لغة البرمجة |
| ![Django](https://img.shields.io/badge/Django-5.0-092E20?logo=django&logoColor=white) | 5.0+ | Web Framework |
| ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-316192?logo=postgresql&logoColor=white) | 14+ | قاعدة البيانات |
| ![Supabase](https://img.shields.io/badge/Supabase-Latest-3ECF8E?logo=supabase&logoColor=white) | Latest | Database Cloud |
| Django Allauth | 0.57+ | المصادقة |
| Stripe Python | 7.0+ | الدفع |
| Pillow | 10.0+ | الصور |
| TinyMCE | 4.0+ | المحرر |

### Frontend Stack

| التقنية | الإصدار | الاستخدام |
|---------|---------|-----------|
| ![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white) | 5.3 | CSS Framework |
| ![HTMX](https://img.shields.io/badge/HTMX-1.9-3366CC?logo=htmx&logoColor=white) | 1.9 | التفاعلية |
| Alpine.js | 3.x | State Management |
| Font Awesome | 6.4 | الأيقونات |
| Animate.css | 4.1 | الحركات |
| Google Fonts | - | الخطوط |

### DevOps & Tools

- **Gunicorn** - WSGI Server
- **Whitenoise** - Static Files
- **uv** - Package Manager
- **Git** - Version Control

---

## 📁 البنية التحتية

```
academy_project/
│
├── 📂 config/                    # إعدادات Django
│   ├── settings.py               # ✅ الإعدادات الرئيسية
│   ├── urls.py                   # ✅ المسارات
│   └── wsgi.py                   # ✅ WSGI
│
├── 📂 users/                     # تطبيق المستخدمين
│   ├── models.py                 # ✅ CustomUser
│   ├── views.py                  # ✅ Profile, Dashboard
│   ├── forms.py                  # ✅ نماذج المستخدم
│   └── signals.py                # ✅ إشعارات البريد
│
├── 📂 courses/                   # تطبيق الدورات
│   ├── models.py                 # ✅ 8 Models
│   ├── views.py                  # ✅ واجهات عادية
│   ├── htmx_views.py             # ✅ 10 HTMX Views
│   ├── forms.py                  # ✅ النماذج
│   └── admin.py                  # ✅ لوحة إدارة محسّنة
│
├── 📂 blog/                      # تطبيق المدونة
│   ├── models.py                 # ✅ Post, Category
│   ├── views.py                  # ✅ قائمة وتفاصيل
│   └── forms.py                  # ✅ نماذج التعليقات
│
├── 📂 payments/                  # تطبيق المدفوعات
│   ├── models.py                 # ✅ Payment
│   ├── views.py                  # ✅ Stripe Integration
│   └── signals.py                # ✅ إشعارات الدفع
│
├── 📂 templates/                 # 30+ قالب HTML
│   ├── base.html                 # ✅ القالب الأساسي
│   ├── 📂 courses/               # ✅ 6 قوالب + partials
│   ├── 📂 users/                 # ✅ 2 قوالب
│   ├── 📂 blog/                  # ✅ 3 قوالب
│   ├── 📂 payments/              # ✅ 3 قوالب
│   ├── 📂 account/               # ✅ 7 قوالب مصادقة
│   │   └── 📂 email/             # ✅ 4 قوالب بريد
│   └── 📂 emails/                # ✅ 4 رسائل إضافية
│
├── 📂 static/                    # ملفات ثابتة
│   ├── 📂 css/
│   │   └── custom.css            # ✅ 800+ سطر
│   └── 📂 js/
│       └── enhancements.js       # ✅ تحسينات JS
│
├── 📂 media/                     # رفع الملفات
│
├── 📄 pyproject.toml             # ✅ التبعيات
├── 📄 setup.sh                   # ✅ سكريبت تثبيت
├── 📄 .env.example               # ✅ مثال للبيئة
├── 📄 manage.py                  # ✅ Django CLI
└── 📄 README.md                  # ✅ هذا الملف
```

### 📊 الإحصائيات

- **4 تطبيقات Django**
- **14 نموذج قاعدة بيانات**
- **30+ قالب HTML**
- **34 ملف Python**
- **5000+ سطر كود**
- **11 ملف توثيق**

---

## 🚀 التثبيت السريع

### المتطلبات

- Python 3.11+
- PostgreSQL 14+
- Git

### خطوات التثبيت

```bash
# 1️⃣ استنساخ المشروع
git clone https://github.com/yourusername/academy-platform.git
cd academy-platform

# 2️⃣ بيئة افتراضية
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3️⃣ تثبيت التبعيات (سريع مع uv)
pip install uv
uv pip install -e .

# 4️⃣ نسخ المتغيرات
cp .env.example .env

# 5️⃣ تحديث .env
nano .env  # أضف بياناتك

# 6️⃣ تشغيل المشروع
chmod +x setup.sh
./setup.sh
```

### التثبيت اليدوي

```bash
# قاعدة البيانات
createdb academy_db

# الهجرات
python manage.py makemigrations
python manage.py migrate

# مستخدم مدير
python manage.py createsuperuser

# ملفات ثابتة
python manage.py collectstatic --noinput

# تشغيل
python manage.py runserver
```

**الموقع:** `http://localhost:8000`  
**الإدارة:** `http://localhost:8000/admin`

---

## ⚙️ الإعداد

### ملف .env

```bash
# Django
SECRET_KEY=your-super-secret-key-here-change-this
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Supabase أو محلي)
DATABASE_URL=postgresql://user:pass@host:port/db

# Email (Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=Academy <noreply@academy.com>

# Stripe
STRIPE_PUBLIC_KEY=pk_test_xxxxx
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# Site
SITE_URL=http://localhost:8000

# Language
LANGUAGE_CODE=ar  # ar أو en
```

### Stripe Setup

1. [Stripe Dashboard](https://dashboard.stripe.com)
2. احصل على API Keys
3. أضفها في `.env`
4. اختبر: `4242 4242 4242 4242`

### Email Setup

**للتطوير:**
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**للإنتاج (Gmail):**
1. [App Password](https://myaccount.google.com/apppasswords)
2. استخدمه في `.env`

---

## 💻 الاستخدام

### تشغيل الخادم

```bash
python manage.py runserver
```

### لوحة الإدارة

```
URL: http://localhost:8000/admin
```

### إنشاء دورة

1. اذهب للإدارة
2. Courses → Add
3. املأ البيانات
4. أضف دروس
5. انشر!

### الاختبارات

```bash
# جميع الاختبارات
python manage.py test

# تطبيق محدد
python manage.py test courses

# مع Coverage
coverage run --source='.' manage.py test
coverage report
```

---

## 🔌 HTMX API

### Endpoints

| Endpoint | Method | الوصف |
|----------|--------|-------|
| `/htmx/courses/` | GET | قائمة دورات ديناميكية |
| `/htmx/search/` | GET | بحث مباشر |
| `/htmx/lesson/{id}/comment/` | POST | إضافة تعليق |
| `/htmx/comment/{id}/delete/` | DELETE | حذف تعليق |
| `/htmx/course/{slug}/review/` | POST | إضافة تقييم |
| `/htmx/lesson/{id}/progress/` | POST | تحديث التقدم |
| `/htmx/course/{slug}/preview/` | GET | معاينة دورة |

### مثال استخدام

```html
<!-- بحث مباشر -->
<input type="text" 
       hx-get="/htmx/search/"
       hx-trigger="keyup changed delay:500ms"
       hx-target="#results">

<!-- إضافة تعليق -->
<form hx-post="/htmx/lesson/1/comment/"
      hx-target="#comments"
      hx-swap="afterbegin">
    <textarea name="content"></textarea>
    <button>إرسال</button>
</form>
```

---

## 📚 التوثيق

| الملف | الوصف |
|------|-------|
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | دليل التثبيت الشامل |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | النشر على السيرفرات |
| [HTMX_INTEGRATION.md](HTMX_INTEGRATION.md) | دليل HTMX |
| [HTMX_COMPLETE_GUIDE.md](HTMX_COMPLETE_GUIDE.md) | الدليل الكامل |
| [DESIGN_UX_IMPROVEMENTS.md](DESIGN_UX_IMPROVEMENTS.md) | التصميم والـ UX |
| [EMAIL_TEMPLATES_IMPROVEMENTS.md](EMAIL_TEMPLATES_IMPROVEMENTS.md) | قوالب البريد |
| [ACCOUNT_TEMPLATES.md](ACCOUNT_TEMPLATES.md) | قوالب المصادقة |

---

## ⚡ الأداء

### معايير

| المقياس | القيمة |
|---------|--------|
| Page Load | < 2s |
| Time to Interactive | < 3s |
| First Paint | < 1s |
| Lighthouse | 90+ |

### التحسينات

- ✅ Lazy Loading
- ✅ CSS/JS Minification
- ✅ Smart Caching
- ✅ CDN
- ✅ DB Indexing
- ✅ Query Optimization
- ✅ HTMX (90% less data)

---

## 🤝 المساهمة

نرحب بمساهماتك! 🎉

### الخطوات

1. Fork المشروع
2. أنشئ فرع: `git checkout -b feature/amazing`
3. Commit: `git commit -m 'Add feature'`
4. Push: `git push origin feature/amazing`
5. افتح Pull Request

### الإرشادات

- اتبع PEP 8
- أضف اختبارات
- وثّق التغييرات
- رسائل commit واضحة

---

## 🐛 المشاكل

وجدت مشكلة؟ [افتح Issue](https://github.com/yourusername/academy/issues)

---

## 📞 الدعم

- 📧 Email: support@academy.com
- 💬 Discord: [Join](https://discord.gg/academy)
- 🐦 Twitter: [@academy](https://twitter.com/academy)

---

## 📄 الترخيص

MIT License - انظر [LICENSE](LICENSE)

---

## 🙏 شكر

- [Django](https://djangoproject.com)
- [Bootstrap](https://getbootstrap.com)
- [HTMX](https://htmx.org)
- [Stripe](https://stripe.com)

---

<div align="center">

**إذا أعجبك المشروع، أعطه ⭐**

[![GitHub stars](https://img.shields.io/github/stars/yourusername/academy?style=social)](https://github.com/ayakakaa135-boop/academy/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/academy?style=social)](https://github.com/ayakakaa135-boop/academy/network/members)

[⬆ العودة للأعلى](#-الأكاديمية-التعليمية--academy-platform)

</div>
