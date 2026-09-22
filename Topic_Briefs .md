## **Agentic AI Challenge Iraq: Topic Briefs** 

**DRAFT FOR REVIEW  |  17/09/2026** 

Six topics. Pick one. Each brief tells you the problem, what to build, what your submission must include, what is out of scope, what data you will need, and what a strong result looks like. Read the rules that apply to every topic first. 

**The six topics at a glance** 

|**#**|**Topic**|**In one line**|
|---|---|---|
|01|**Fraud & Scam Protection Agent**|Catches the risky moment and talks the user out of the scam, in their own<br>words.|
|02|**SME & Merchant Assistant**|Gives a small merchant the numbers they never had time to work out.|
|03|**AI Loan Officer**|Takes a loan application from first contact to a complete, explained file for<br>a human decision.|
|04|**Bill Pay & Transfer Agent**|Turns "pay my electricity bill" into a completed, confirmed transaction.|
|05|**KYC Document Agent**|Reads the documents, checks them against each other, and knows when<br>to hand over to a person.|
|06|**Support Pipeline Automation**|A back-office pipeline that classifies, routes and pre-drafts support tickets<br>so people spend their time on the hard ones.|



### **Rules for every topic** 













**Leverage what LLMs can do.** Every topic is about using and deploying foundation models: prompting, retrieval, tool use, agents and evaluation. The question each brief asks is how far you can take a modern model on a real problem. 

- **Simulate your data with an LLM.** No real customer records, identity documents or transaction histories, yours or anyone else’s. Use a model to generate the transactions, tickets, profiles or documents your brief needs. Give it the structure and the edge cases you want, generate more than you need, check a sample by hand, and hold part back for testing. 

- **Build a test set.** Every brief asks for a held-out set your system was not tuned on, and for your results on it. A demo without numbers is a demo, not evidence. 

- **Iraqi Arabic is the default.** Users in these briefs speak and type in dialect. Show how your system handles that. 

- **Disclose everything you used.** Models, tools, libraries, data sources and AI coding assistants. Using AI to build is expected. Hiding it is not. 

- **Simple and reliable beats complex.** A focused system that works will score above an ambitious architecture that does not. 

### **How projects are judged** 

Complexity alone does not score. Weights for the build and demo round: 

|**Dimension**|**Weight**|**What judges look for**|
|---|---|---|
|Working prototype and reliability|**25%**|Does it run live on input the judges supply, and does it hold up?|
|Technical judgment and architecture|**20%**|Right tool for the job, sensible failure handling, no unjustified<br>complexity|
|Problem and impact|**20%**|A real user, a real problem, evidence you spoke to someone|
|Grounding, security and responsibility|**15%**|Outputs traceable to data, safe failure, privacy handled|
|Evaluation evidence|**15%**|A held-out test set and honest results on it|
|Demo clarity|**5%**|Judges understand what it does in the first minute|





**Before scoring, every submission must clear four checks** 

- A repository with commit history spanning the build period. 

- A live run on judge-supplied input. 

- Full disclosure of models, tools and data. 

- At least three documented failure modes with how you handle them. 

# **01   Fraud & Scam Protection Agent** 

_Catches the risky moment and talks the user out of the scam, in their own words._ 



#### **The problem** 

Wallet users in Iraq are targeted by social-engineering scams: fake agents calling for an OTP, prize messages that need a "processing fee", urgent requests to move money to a "safe" account. The money is usually gone before anyone at ZainCash can react. Detection after the fact is too late. The intervention has to happen at the moment the user is about to act. 



#### **What you build** 

An agent with two layers. A detection layer watches transaction activity for known risk signals (first transfer to a new recipient, unusual amount or time, a rapid sequence of transfers, patterns that match a known scam script). A coaching layer steps in before the transaction completes and talks to the user in Iraqi Arabic: what looks wrong, why, and what a scammer would typically say next. The user can proceed or cancel. Every intervention and outcome is logged. 



#### **Must have** 

- **Intervenes before the transaction completes** , not after. 

- Explains the specific risk in **plain Iraqi Arabic** , with no jargon. 

- **Lets the user proceed** if they choose, and records that choice. 

- Detection uses **clear rules or simple statistics** that a reviewer can read and understand. 



#### **Out of scope** 

Blocking transactions without the user’s consent. Detection should rest on rules and thresholds a reviewer can read; the model’s job is the coaching. 



#### **Data** 

Use an LLM to generate synthetic transaction histories for at least 20 users, with scam scenarios planted in some of them, from a structure you define. Research real Iraqi scam patterns and turn them into a written catalogue your detection layer uses. **No real customer data** . 



#### **What a strong submission shows** 

- **Low false positives** . An agent that interrupts honest transactions gets switched off by the user within a week. 

- A test set with labeled scam and non-scam scenarios, and the **precision and recall** you achieved on it. 

- Coaching that **sounds like a person from Iraq** , not a translated bank notice. 



**Stretch, if you have time:** A training mode that simulates a scam attempt so a user can practise recognising one safely. 

# **02   SME & Merchant Assistant** 

_Gives a small merchant the numbers they never had time to work out._ 



#### **The problem** 

Small merchants in Iraq run their business on cash, a notebook and WhatsApp. Most cannot say what their margin was last week, when cash will run short, or which customer payments have not arrived. They are not short of transactions. They are short of anyone turning those transactions into answers. 



#### **What you build** 

An assistant for a single small merchant. It ingests their transactions (from a wallet export, a CSV, or photos of receipts), keeps a simple ledger, answers questions in Iraqi Arabic ("how much did I make this week", "who still owes me"), flags payments that have not reconciled, and produces a 30-day cash-flow projection from the ledger with a plain explanation of what drives it. 



#### **Must have** 

- Every number it states is **traceable to the underlying transactions** . No estimates presented as facts. 

- **Answers in Iraqi Arabic** and handles dialect in the questions it receives. 

- **Flags unreconciled or unusual payments** with a reason. 



#### **Out of scope** 

Tax filing, formal accounting compliance, and integration with real accounting software. The projection is arithmetic on the ledger, explained by the model. This is a working assistant for the merchant, not an accounting product. 

- Produces a **weekly summary** a merchant would actually read. 



#### **Data** 

Use an LLM to generate a realistic synthetic ledger for one merchant: at least three months of daily sales, supplier payments and customer credit, with a few **deliberate anomalies** you specify. Include some handwritten or photographed receipts if you attempt receipt capture. 



#### **What a strong submission shows** 

- The projection is **explained, not just charted** . The merchant should understand why next month looks tight. 

- A test set of questions with known correct answers, and how often the assistant got the number **exactly right** . 

- Design choices that fit a merchant with a phone and **ten spare minutes a day** . 

**Stretch, if you have time:** Supplier reorder suggestions based on sales pace, drafted as a message the merchant approves before it sends. 

# **03   AI Loan Officer** 

_Takes a loan application from first contact to a complete, explained file for a human decision._ 



#### **The problem** 

Applying for small credit in Iraq is opaque. Applicants do not know what documents are needed, submit incomplete files, wait, and get rejected without an explanation they can act on. On the other side, loan officers spend most of their time chasing paperwork rather than assessing. 



#### **What you build** 

An agent that runs the application end to end, up to the decision. It gathers the required information and documents through conversation in Iraqi Arabic, checks the file for completeness and internal consistency, tests it against a written set of eligibility rules, and computes indicators from wallet history (transaction regularity, inflow stability) as inputs for a human underwriter. It then explains to the applicant, in plain language, what they qualify to apply for, what is missing, and what would strengthen their application. The final decision stays with a person. 



#### **Must have** 

- The eligibility rules are **written down, visible in the demo** , and applied consistently. 

- The agent **never issues an approve or decline** . It prepares and explains; a human decides. 



#### **Out of scope** 

Making the credit decision. Any indicator you compute from alternative data must be explainable in one sentence and presented as an input, not a verdict. 

- Every flag or shortfall is explained to the applicant in **words they can act on** . 

- Incomplete applications are handled gracefully, with a **clear list of what is still needed** . 



#### **Data** 

Use an LLM to generate synthetic applicant profiles with matching wallet histories, at least 15, spanning strong, weak and borderline cases. Write your own **eligibility rulebook** and include it in your submission. 



**What a strong submission shows** 

- **Transparency** . A judge can see exactly why the agent flagged what it flagged. 

- **Awareness of fairness** . Show you thought about which signals could disadvantage someone unfairly, and what you did about it. 

- A test set of applications with **expected outcomes** for completeness and eligibility checks, and your accuracy on it. 

**Stretch, if you have time:** A view for the human underwriter that summarises the file in one screen with the indicators and the open questions. 

# **04   Bill Pay & Transfer Agent** 

_Turns "pay my electricity bill" into a completed, confirmed transaction._ 



#### **The problem** 

Paying a bill or sending money in a wallet app takes many taps and several screens. Users who are less comfortable with smartphones abandon the flow or make mistakes. A single sentence, spoken or typed, should be enough. 



#### **What you build** 

An agent that takes a natural-language request in Iraqi Arabic ("pay my electricity bill", "send 50,000 to Ahmed"), works out the intent, gathers anything missing (which Ahmed, which biller, which amount), shows a clear confirmation, executes against a mock wallet API, and reports the result. When something goes wrong, it fails safely and says so. 



#### **Must have** 

- Nothing executes without an **explicit confirmation step** the user can read and understand. 

- Ambiguity is resolved by **asking, not guessing** . Two contacts named Ahmed means a question, not a coin flip. 



#### **Out of scope** 

Connecting to real payment systems. You build and run a mock wallet API with contacts, billers, balances and transaction history. The agent talks to that. 

- Retries **never cause a double payment** . Show how you prevent it. 

- Clear, **honest failure messages** when a payment cannot go through. 



#### **Data** 

Your mock wallet: users, contacts (including duplicates and similar names), billers, balances and history, generated with an LLM from a schema you define. Plus a test set of at least 50 requests in Iraqi dialect, including **ambiguous and malformed** ones, generated the same way and then edited by hand for realism. 



#### **What a strong submission shows** 

- The confirmation step is **designed, not bolted on** . It shows the right information at the right moment. 

- Edge cases are **handled deliberately** : insufficient balance, unknown contact, a request that is really two requests. 

- Your test set results, including how it behaves on requests that **should not go through** . 



**Stretch, if you have time:** Voice input. The same agent driven by spoken Iraqi Arabic. 

# **05   KYC Document Agent** 

_Reads the documents, checks them against each other, and knows when to hand over to a person._ 



#### **The problem** 

Onboarding a customer or merchant needs photos of an ID, a business license and a tax card. Reviewers check them by hand, which is slow and inconsistent. The photos are often blurry, tilted or partially covered, and the documents are in Arabic script with handwriting on some of them. 



#### **What you build** 

An agent that takes the document photos, extracts the relevant fields from each using a multimodal model, validates them (expiry dates, formats, and whether the name and details match across documents), attaches a confidence to every field, and either passes the file or routes it to a human with a short summary of what needs checking and why. 



#### **Must have** 

- A **confidence score for every extracted field** , and a threshold below which the field goes to a human. 

- **Cross-document checks** : the name on the license matches the name on the ID, and so on. 



#### **Out of scope** 

Face matching, liveness checks and forgery detection. This brief is about reading and validating, not authenticating identity. 

- It **never fills in a field it could not read** . Blank and flagged beats invented. 

- A **clear exception path** with a human-readable summary for the reviewer. 



#### **Data** 

Create sample documents yourself from templates, with fictional names and numbers generated by an LLM. **Photograph them badly on purpose** : poor light, angles, glare, partial coverage. **Do not use real identity documents** , yours or anyone else’s. 



**What a strong submission shows** 

- Extraction accuracy on a **held-out set** of documents you did not tune on. 

- **Calibrated confidence** : when the agent says 90%, it should be right about 90% of the time. 

- Sensible behaviour on the **worst photos** , which is where manual review actually spends its time. 



**Stretch, if you have time:** Guidance back to the user at capture time: "the corner is cut off, retake the photo". 

# **06   Support Pipeline Automation** 

_A back-office pipeline that classifies, routes and pre-drafts support tickets so people spend their time on the hard ones._ 



#### **The problem** 

Support requests arrive in Iraqi dialect through the app and messaging channels. Agents read each one, work out what it is about, find the transaction, and route or answer it. Most of that work is repetitive, and the queue grows faster than the team. 



#### **What you build** 

A batch pipeline, not a chatbot. It runs over a queue of tickets and, for each one, uses an LLM to classify the issue, set a priority, extracts structured details (transaction reference, amount, date), routes it to the right team, and drafts a first response for a human agent to approve or edit. Anything it is unsure about is escalated with a note. 



#### **Must have** 

- Runs as a **pipeline over a batch of tickets** , with a summary of what it did. 

- Every classification **carries a confidence** , and low-confidence tickets are escalated rather than guessed. 



#### **Out of scope** 

A customer-facing chatbot. Classification and extraction are done with the LLM. This brief is about the work behind the queue, not the conversation with the customer. 

- Drafted responses are **never sent automatically** . A human approves. 

- Measured on a **labeled test set** the pipeline was not tuned on. 



#### **Data** 

Generate a synthetic ticket set of at least 200 messages in Iraqi dialect with an LLM, covering the common support categories (failed transfer, wrong recipient, login problem, agent dispute, card issue, and so on), with labels for category, priority and the details to extract. Read a sample to make sure it sounds like real customers. **Hold part back for testing** . 



**What a strong submission shows** 

- **Classification accuracy and extraction accuracy** on the **held-out set** , with the confusion cases discussed. 

- Draft responses that a support agent would **actually send with minor edits** . 

- A clear view of **throughput** : how many tickets it handled, how many it escalated, and why. 

**Stretch, if you have time:** A weekly pattern report: which issues are rising, and which are likely caused by the same underlying problem. 

