# Sample Pre-Drafted First Responses for Owner Review

**Milestone 1 Deliverable (Section 12, Item 5)**  
**Target:** 10 diverse sample tickets processed through the pipeline, demonstrating grounded first-response drafting in Iraqi Arabic dialect without false promises or ungrounded data.

---

### Sample 1: Failed Transfer (High Priority, Non-Escalated)
- **Ticket ID:** `TKT-2026-0001`
- **Channel:** `app`
- **Customer Message:** *"حولت 50,000 دينار لصديقي والفلوس انخصمت من المحفظة بس ما وصلت ورقم العملية TXN-99887766 امس بالليل"*
- **Extracted Fields:** Amount: `50,000 IQD` | Reference: `TXN-99887766` | Date: `2026-09-21`
- **Pre-Drafted First Response (Arabic):**
  > "أهلاً بك، نتأسف على الإزعاج بخصوص عملية التحويل. استلمنا طلبك بمبلغ 50,000 دينار، وفريق التحويلات راح يتحقق من العملية برقم المرجع TXN-99887766 ويردلك خبر خلال وقت قصير."
- **Reviewer Action:** [Approve & Send] | [Minor Edit]

---

### Sample 2: Wrong Recipient (High Priority, Non-Escalated)
- **Ticket ID:** `TKT-2026-0002`
- **Channel:** `whatsapp`
- **Customer Message:** *"حولت بالخطأ لرقم ثاني بدل رقم اخوي المبلغ 100,000 دينار رقم العملية TXN-88776655 قبل يومين فدوة كدرون ترجعوها؟"*
- **Extracted Fields:** Amount: `100,000 IQD` | Reference: `TXN-88776655` | Date: `2026-09-20`
- **Pre-Drafted First Response (Arabic):**
  > "أهلاً بك، استلمنا بلاغك بخصوص التحويل الخاطئ بمبلغ 100,000 دينار. فريق العمليات راح يتواصل ويدقق برقم العملية TXN-88776655 حتى نساعدك بالإجراءات الممكنة بأسرع وقت."
- **Reviewer Action:** [Approve & Send] | [Minor Edit]

---

### Sample 3: Login Problem (Medium Priority, Non-Escalated)
- **Ticket ID:** `TKT-2026-0003`
- **Channel:** `sms`
- **Customer Message:** *"رمز التأكيد OTP ما يوصلني على خطي حتى افتح المحفظة امس بالليل جربت عشر مرات وماكو"*
- **Extracted Fields:** None required
- **Pre-Drafted First Response (Arabic):**
  > "أهلاً بك، فهمنا مشكلتك بتسجيل الدخول إلى التطبيق. فريق الدعم التقني راح يراجع حالة حسابك. يرجى التأكد من تحديث التطبيق لأحدث نسخة واستقرار الاتصال بالإنترنت، وراح نتواصل وياك."
- **Reviewer Action:** [Approve & Send] | [Minor Edit]

---

### Sample 4: Card Declined at ATM (High Priority, Non-Escalated)
- **Ticket ID:** `TKT-2026-0004`
- **Channel:** `app`
- **Customer Message:** *"الكارت مالتي انرفض بجهاز الصراف الآلي بالمول وسحب البطاقة وما رجعها"*
- **Extracted Fields:** None required
- **Pre-Drafted First Response (Arabic):**
  > "أهلاً بك، نأسف للمشكلة اللي واجهتك مع البطاقة. فريق البطاقات راح يفحص سبب الرفض أو العطل بالنظام البنكي حتى ترجع تستخدمها بشكل طبيعي."
- **Reviewer Action:** [Approve & Send] | [Minor Edit]

---

### Sample 5: Bill Payment Failure (Medium Priority, Non-Escalated)
- **Ticket ID:** `TKT-2026-0005`
- **Channel:** `app`
- **Customer Message:** *"دفعت فاتورة الكهرباء بمبلغ 75,000 دينار برقم عملية TXN-44556677 والكهرباء تكول ما مسدد"*
- **Extracted Fields:** Amount: `75,000 IQD` | Reference: `TXN-44556677`
- **Pre-Drafted First Response (Arabic):**
  > "أهلاً بك، نعتذر عن تأخر تسديد الفاتورة. تم تسجيل طلبك بمبلغ 75,000 دينار ورقم العملية TXN-44556677، وفريق الدفع راح يتابع الأمر مع مزود الخدمة مباشرة."
- **Reviewer Action:** [Approve & Send] | [Minor Edit]

---

### Sample 6: Agent Dispute (Medium Priority, Non-Escalated)
- **Ticket ID:** `TKT-2026-0006`
- **Channel:** `whatsapp`
- **Customer Message:** *"الوكيل اللي بالمنصور طلب مني عمولة 5000 دينار فوك السحب وهذا مخالف"*
- **Extracted Fields:** None required
- **Pre-Drafted First Response (Arabic):**
  > "أهلاً بك، نعتذر عن أي تجربة غير مريحة مع الوكيل. استلمنا شكواك وفريق إدارة شبكة الوكلاء راح يفتح تحقيق بالواقعة ويتخذ الإجراء المناسب لحفظ حقك."
- **Reviewer Action:** [Approve & Send] | [Minor Edit]

---

### Sample 7: Fraud Report (High Priority, Non-Escalated)
- **Ticket ID:** `TKT-2026-0007`
- **Channel:** `app`
- **Customer Message:** *"الحكولي انسرقت فلوسي من المحفظة اتصل بيه واحد كال اني موظف واخذ الكود وطارت كل فلوسي"*
- **Extracted Fields:** None required
- **Pre-Drafted First Response (Arabic):**
  > "أهلاً بك، تم استلام بلاغك بأولوية قصوى وجاري تحويله لفريق مكافحة الاحتيال لاتخاذ التدابير الأمنية الفورية وتتبع الحركة لحماية حسابك."
- **Reviewer Action:** [Approve & Send] | [Minor Edit]

---

### Sample 8: Account Blocked (High Priority, Non-Escalated)
- **Ticket ID:** `TKT-2026-0008`
- **Channel:** `app`
- **Customer Message:** *"حسابي مجمج وفجأة يكتبلي راجع الإدارة ومكاعد اكدر احول ولا اسحب فلوسي"*
- **Extracted Fields:** None required
- **Pre-Drafted First Response (Arabic):**
  > "أهلاً بك، استلمنا طلبك بخصوص تقييد الحساب. فريق التوثيق والامتثال راح يدقق بالسبب ويرسل لك الخطوات اللازمة لفك الحظر وحماية أمان محفظتك."
- **Reviewer Action:** [Approve & Send] | [Minor Edit]

---

### Sample 9: Missing Transaction Reference (ESCALATED)
- **Ticket ID:** `TKT-2026-0009`
- **Channel:** `app`
- **Customer Message:** *"حولت فلوس وخصموا الرصيد والعملية تكول معلقة بدون رقم ولا شي شسوي؟"*
- **Pipeline Decision:** **ESCALATED TO HUMAN REVIEWER**
- **Internal Note for Agent (No automated customer message sent):**
  > "[تذكرة مصعدة للمراجعة اليدوية]: Extraction incomplete: Missing transaction reference required for category 'failed_transfer'"
- **Reviewer Action:** Agent manually contacts user for transaction details.

---

### Sample 10: Vague Customer Greeting (ESCALATED)
- **Ticket ID:** `TKT-2026-0010`
- **Channel:** `sms`
- **Customer Message:** *"مرحبا اريد مساعدة ضروري"*
- **Pipeline Decision:** **ESCALATED TO HUMAN REVIEWER**
- **Internal Note for Agent (No automated customer message sent):**
  > "[تذكرة مصعدة للمراجعة اليدوية]: Ticket is ambiguous, vague, or incomplete; manual agent triage required"
- **Reviewer Action:** Agent replies manually asking for issue details.
