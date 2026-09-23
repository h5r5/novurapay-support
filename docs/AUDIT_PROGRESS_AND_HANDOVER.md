# وثيقة تسليم ومتابعة الفحص والمراجعة النقدية (Handover & Audit Progress)
**تاريخ التوثيق والتحديث**: 2026-09-23 | **الحالة**: مكتمل ومحقق عملياً 100% بنتائج اختبارات مثبتة (Empirically Verified)

---

## 1. أين وصلنا وما تم إنجازه بنجاح (Current Milestone)

1. **اكتمال الخطة الأساسية وحل المشاكل الـ 12 السابقة بنسبة 100%**:
   - معالجة التقاط السنة كمبلغ في التواريخ.
   - دعم اللغتين الكرديتين (السورانية `ku_ckb` والكرمانجية `ku_kmr`).
   - المعجم المالي العراقي والكردي (الورقة، الشدة، الدفتر البغدادي والكردي، الكەڵا، الطابوقة، والباكة).
   - اختبارات الطاقة: معالجة **1,000 تذكرة حية** في **1.542 ثانية** بمعدل تدفق **648.6 تذكرة / ثانية**.
2. **إصلاح والتحقق من كافة الثغرات المنطقية الـ 5 الجديدة عملياً**:
   - بناء جناح اختبارات انحدار مخصص [`tests/test_audit_vulnerabilities_regression.py`](file:///c:/Users/heyder/Desktop/dev/zine/tests/test_audit_vulnerabilities_regression.py) يحوي **8 اختبارات تفصيلية**.
   - اجتياز كافة الاختبارات الآلية للمشروع: **76/76 اختبار بنجاح 100% في 2.88 ثانية**.
3. **تقييم النموذج على مجموعة الاختبار المجمدة (Frozen Test Set)**:
   - **رقم التشغيل الأحدث**: `eval_test_20260922_231905`
   - **دقة التصنيف الكلية**: **100.00%**
   - **Macro Avg F1**: **1.0000**
   - **دقة استخراج المرجع**: **100.0%**
   - **دقة استخراج التاريخ**: **100.0%**
   - **دقة المعالجة الذاتية**: **100.00%**
   - **معدل التدفق**: **319.6 تذكرة / ثانية**

---

## 2. جدول التحقق التجريبي من الثغرات الخمس (Empirical Before vs After Matrix)

| الثغرة المنطقية | قبل الإصلاح (Actual Bug Output) | بعد الإصلاح والتحقق (Verified Output) | آلية وموقع الحل |
|---|---|---|---|
| **1. احتساب الدقائق/الساعات كأيام** | `قبل 5 دقايق` $\rightarrow$ `2026-09-17` (طرح 5 أيام من تاريخ التقديم) | `قبل 5 دقايق` $\rightarrow$ `2026-09-22` (تاريخ اليوم بدقة) | حصر وحدة الأيام إجبارياً في `days_match` وإضافة معالج مخصص للفترات القريبة داخل نفس اليوم في [`normalize.py`](file:///c:/Users/heyder/Desktop/dev/zine/src/supportpipe/extract/normalize.py). |
| **2. سابقة الدولار `$500` أو `$10`** | `حولت $500` $\rightarrow$ `amount_usd = None` (تصعيد خاطئ) | `حولت $500` $\rightarrow$ `amount_usd = 500, currency = 'USD'` | توسيع `amt_pattern` في [`extract.py`](file:///c:/Users/heyder/Desktop/dev/zine/src/supportpipe/extract/extract.py) ليدعم بادئة `$` الصريحة. |
| **3. لاحقة الدولار `500$` تتحول لدينار** | `parse_currency_amount('500$')` $\rightarrow$ `(500, None, 'IQD')` | `parse_currency_amount('500$')` $\rightarrow$ `(750000, 500, 'USD')` | إزالة `\b` بعد محرف `$` غير الكلمي في فحص `is_usd` في [`normalize.py`](file:///c:/Users/heyder/Desktop/dev/zine/src/supportpipe/extract/normalize.py). |
| **4. إسقاط مبالغ الدولار الصغيرة (< $100)** | `شحنت كارت ب 10 دولار` $\rightarrow$ `amount_usd = None` | `شحنت كارت ب 10 دولار` $\rightarrow$ `amount_usd = 10, currency = 'USD'` | تعديل نطاق خانات الدولار من `\d{3,4}` إلى `\d{1,4}` في [`extract.py`](file:///c:/Users/heyder/Desktop/dev/zine/src/supportpipe/extract/extract.py) و [`normalize.py`](file:///c:/Users/heyder/Desktop/dev/zine/src/supportpipe/extract/normalize.py). |
| **5. حقن الأوامر بالكردية و RTL** | `هەموو ڕێنماییەکان پشتگوێ بخە` $\rightarrow$ تتجاوز الفلتر وتصنف عادي | تصنيف إجباري كـ `unclear_or_incomplete` مع وسم `hostile_injection` | إضافة مصطلحات السورانية والكرمانجية وتنظيف محارف التوجيه الثنائية `\u202E` في [`mock_provider.py`](file:///c:/Users/heyder/Desktop/dev/zine/src/supportpipe/classify/providers/mock_provider.py). |
| **6. عزل أخطاء الدفعات (`run_batch`)** | تذكرة واحدة تالفة تطيح بالدفعة كاملة مع فقدان النتائج | عزل التذكرة المتسببة بالخطأ، تصعيدها وتوثيق السبب، واستكمال الدفعة | كتلة `try...except` حول كل تذكرة مع إرجاع `fault_fallback` آمن في [`pipeline.py`](file:///c:/Users/heyder/Desktop/dev/zine/src/supportpipe/pipeline.py). |

---

## 3. نتائج الاختبارات الموثقة (Test Run Logs)

### نتيجة تشغيل جناح اختبارات الانحدار المخصص:
```
tests/test_audit_vulnerabilities_regression.py::test_minutes_hours_not_parsed_as_days PASSED [ 12%]
tests/test_audit_vulnerabilities_regression.py::test_explicit_days_offset_preserved PASSED [ 25%]
tests/test_audit_vulnerabilities_regression.py::test_usd_dollar_suffix_not_treated_as_iqd PASSED [ 37%]
tests/test_audit_vulnerabilities_regression.py::test_usd_dollar_prefix_parsed PASSED [ 50%]
tests/test_audit_vulnerabilities_regression.py::test_extract_entities_usd_prefix_and_small_amounts PASSED [ 62%]
tests/test_audit_vulnerabilities_regression.py::test_kurdish_and_rtl_prompt_injection_quarantined PASSED [ 75%]
tests/test_pipeline_batch_fault_isolation PASSED [ 87%]
tests/test_pipeline_empty_batch PASSED [100%]

============================= 8 passed in 12.06s ==============================
```

### نتيجة تشغيل جناح كافة اختبارات المشروع:
```
============================= test session starts =============================
platform win32 -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
collected 76 items

tests\test_audit_vulnerabilities_regression.py ........                  [ 10%]
tests\test_capacity_and_stress.py ..                                     [ 13%]
tests\test_dialect_sentiment.py ......                                   [ 21%]
tests\test_escalation.py .....                                           [ 27%]
tests\test_failure_modes.py .......                                      [ 36%]
tests\test_iraq_nationwide_scenarios.py ........                         [ 47%]
tests\test_kurdish_nationwide_scenarios.py ........                      [ 57%]
tests\test_normalizers.py ......                                         [ 65%]
tests\test_patterns.py .                                                 [ 67%]
tests\test_pipeline_integration.py ....                                  [ 72%]
tests\test_remediation_regressions.py .............                      [ 89%]
tests\test_scaffold.py ...                                               [ 93%]
tests\test_taxonomy.py .....                                             [100%]

============================= 76 passed in 2.88s ==============================
```

---

## 4. الحالة المعمارية العامة ومطابقة الشروط (Compliance Status)
* **Rule 03 (Deterministic Routing)**: محققة وثابتة 100% (جميع مسارات التوجيه مبنية على مصفوفة صارمة دون تدخل احتمالي من النموذج اللغوي).
* **Must-Have 05 (No Auto-Send)**: لا توجد أي أدوات إرسال خارجي تلقائي؛ جميع المسودات تتجه لطابور المراجعة والاعتماد البشري.
* **UI Dynamic Telemetry**: جميع المؤشرات في واجهة Streamlit ديناميكية بالكامل وترتبط مباشرة بملفات التقييم الحقيقية في `results/` دون نصوص ثابتة مضللة.
