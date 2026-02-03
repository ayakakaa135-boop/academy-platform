# تقرير تحليل مشاكل النشر لمشروع Academy Platform

## المقدمة

تمت مراجعة مشروع `academy-platform` لتحديد الأسباب المحتملة لفشل عملية النشر (deployment). تم التركيز على ملفات الإعداد والتكوين الرئيسية مثل `render.yaml`، `build.sh`، `requirements.txt`، `pyproject.toml`، و`config/settings.py`.

## المشاكل المكتشفة والحلول المقترحة

### 1. عدم تطابق إصدار Python

**المشكلة:**

وجد أن ملف `pyproject.toml` يحدد متطلب `requires-python = ">=3.13"`، بينما كان ملف `render.yaml` يستخدم `PYTHON_VERSION: "3.11.0"`، وملف `runtime.txt` كان يحدد `python-3.12.3`. أدى هذا التضارب إلى فشل تثبيت التبعيات، حيث أن `django==6.0.1` يتطلب Python بإصدار `3.12` أو أعلى.

**الحل:**

تم تحديث إصدار Python في كل من `render.yaml` و`runtime.txt` ليصبح `3.13.0` ليتوافق مع المتطلبات المحددة في `pyproject.toml`.

### 2. عدم وجود `dj-database-url` في التبعيات

**المشكلة:**

كان ملف `config/settings.py` يستخدم `dj_database_url.config` لتكوين قاعدة البيانات، ولكن الحزمة `dj-database-url` لم تكن مدرجة ضمن التبعيات في `requirements.txt` أو `pyproject.toml`.

**الحل:**

تمت إضافة `dj-database-url==2.3.0` إلى ملفي `requirements.txt` و`pyproject.toml` لضمان توفر الحزمة أثناء عملية النشر.

### 3. تكوين قاعدة البيانات غير الأمثل

**المشكلة:**

كان تكوين قاعدة البيانات في `config/settings.py` يستخدم متغيرات بيئة منفصلة (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`) بدلاً من استخدام `DATABASE_URL` الموحد الذي توفره منصات النشر مثل Render.

**الحل:**

تم تعديل قسم `DATABASES` في `config/settings.py` لاستخدام `dj_database_url.config` مع متغير البيئة `DATABASE_URL`، مما يجعل التكوين أكثر مرونة وتوافقًا مع بيئات النشر السحابية.

### 4. تكوين الملفات الثابتة (Static Files) غير الصحيح

**المشكلة:**

كان إعداد `STATICFILES_STORAGE` في `config/settings.py` يستخدم الطريقة القديمة لتحديد تخزين الملفات الثابتة، والتي قد لا تكون متوافقة مع إصدارات Django الحديثة (4.x وما فوق) التي تفضل استخدام قاموس `STORAGES`.

**الحل:**

تم تحديث `config/settings.py` لاستخدام قاموس `STORAGES` لتحديد `staticfiles`، مما يضمن التوافق مع إصدار Django الحالي واستخدام `whitenoise.storage.CompressedManifestStaticFilesStorage` بشكل صحيح.

### 5. عدم وجود `CSRF_TRUSTED_ORIGINS` في بيئة الإنتاج

**المشكلة:**

في بيئات الإنتاج، من الضروري تحديد `CSRF_TRUSTED_ORIGINS` لمنع هجمات تزوير الطلبات عبر المواقع (CSRF). لم يكن هذا الإعداد موجودًا في `config/settings.py`.

**الحل:**

تمت إضافة `CSRF_TRUSTED_ORIGINS` إلى `config/settings.py` مع تحديد النطاق الخاص بمنصة Render (`https://academy-platform.onrender.com`) لضمان الأمان في بيئة الإنتاج.

### 6. صلاحيات ملف `build.sh`

**المشكلة:**

قد لا يكون ملف `build.sh` قابلاً للتنفيذ بشكل افتراضي على بعض أنظمة النشر، مما يؤدي إلى فشل خطوة البناء.

**الحل:**

تم التأكد من أن ملف `build.sh` يمتلك صلاحيات التنفيذ باستخدام الأمر `chmod +x /home/ubuntu/academy-platform/build.sh`.

## التوصيات النهائية

بعد تطبيق هذه التعديلات، يجب أن يكون المشروع جاهزًا للنشر على منصة Render بشكل صحيح. يُنصح دائمًا بمراجعة سجلات النشر (deployment logs) بعناية بعد كل محاولة نشر لتحديد أي مشاكل أخرى قد تظهر.

---
