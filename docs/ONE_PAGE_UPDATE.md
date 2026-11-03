# NovuraPay SupportPipe: One-Page Project Update (MVP Stage)

**Agentic AI Challenge Iraq — Topic 06: Support Pipeline Automation**  
**Participant:** Haider Ali | **Repository:** [github.com/h5r5/novurapay-support](https://github.com/h5r5/novurapay-support)  
**Date:** November 2026 | **Target Deadline:** Final MVP Submission (Nov 17, 2026)  
**Consultancy Session:** Sunday, Nov 8, 2026 (5:20 PM – 5:40 PM Baghdad Time)

---

## 1. Executive Summary & Core Hypothesis
Support inquiries for Iraqi digital wallets (simulated as *NovuraPay*) arrive with heavy dialect variance, emotional slang, provincial currency units (*دفتر، شدة، ورقة، طابوقة*), and complex multi-issue complaints. Traditional conversational chatbots hallucinate financial promises and risk severe compliance violations.

**SupportPipe is an enterprise back-office batch pipeline, not a chatbot.** It uses a deterministic **Tri-Engine Hybrid Architecture** with **Zero Outbound Auto-Send Policy**: no message ever reaches a customer without explicit human supervisor approval.

---

## 2. What Works (Empirically Verified & Shipped)
* **Automated Regression Suite:** **223/223 tests passing** (unit, trilingual, capacity, failure mode, and hybrid consensus).
* **Deep Dialect Extraction:** Instant (~0.5ms) regex and dialect sanitization extracting 11-digit Iraqi phone numbers, masked PII (`07xx****xxx` with strict LTR visual layout), provincial currency units, and calendar-accurate relative dates (*"صارلي شهر"*, *"قبل اولت البارحة"*).
* **Multi-Issue Ticket Resolution:** Composite tickets combining operational app faults and financial transfer disputes (*"التطبيق علق وانخصم المبلغ وما وصل"*) are automatically decomposed, routed with multi-intent detection, and pre-drafted for human sign-off.
* **Calibrated Safety Gate (Failure Mode Resilience):**
  * **100/100 resilience** against prompt injections, Unicode direction overrides (BiDi attacks), and gibberish text.
  * Deterministic routing via closed `routing_table.yaml` prevents hallucinated operational departments.
* **Dual-Interface Operations Cockpit:**
  * High-speed Native Web Cockpit ([`supportpipe-dashboardv2.html`](file:///C:/Users/heyder/Desktop/dev/zine/supportpipe-dashboardv2.html)) driven by FastAPI REST backend ([`server.py`](file:///C:/Users/heyder/Desktop/dev/zine/src/supportpipe/server.py)).
  * Live Multi-Model comparison playground (Mock V13, Google Gemini 2.5 Flash, Groq Llama 3.3, TypeSafe Jev 1.13) with quota protection and discrepancy tracking.
* **Continuous Blind Stress Testing:** Evaluated across **19 unseen stress rounds (3,822 tickets)**, achieving **74.91% blind accuracy** (Wilson 95% CI: [73.51%, 76.26%]), with recent rounds stabilizing between **83%–88%**.

---

## 3. What Does Not Work Yet (Honest Disclosures & Known Gaps)
* **Kurdish Dialect Coverage:** While Kurdish Sorani and Kurmanji dialect dictionaries and normalizers are active, the synthetic fine-tuning corpus has fewer Kurdish samples (14% of corpus) compared to Iraqi Arabic (86%).
* **Cloud Audit Latency:** Google Gemini 2.5 Flash live calls take 8–12 seconds depending on cloud API round-trip. While local triage completes in ~0.5ms, real-time multi-model side-by-side evaluation requires visual loading feedback.
* **REST Polling vs SSE Streaming:** Currently, draft responses load on completion rather than streaming token-by-token via Server-Sent Events (SSE).

---

## 4. What Comes Next (Roadmap Before Final Submission: Nov 17)
1. **Server-Sent Events (SSE) Streaming:** Introduce token-by-token streaming in the web cockpit to eliminate perceived latency during live judge demonstrations.
2. **Kurdish Dataset Expansion:** Generate 300 additional synthetic Kurdish support tickets covering Erbil and Sulaymaniyah telecom and merchant payment scenarios.
3. **Automated Benchmark Harness for Judges:** Deliver a zero-dependency CLI command (`supportpipe test-live --file <judge_tickets.jsonl>`) that prints an audit report in under 5 seconds.
4. **Final High-Efficiency Video Pitch:** Produce a concise (<3 min, <10MB) walkthrough of the tri-engine consensus, multi-issue handling, and supervisor review loop.

---

## 5. Specific Questions for the Nov 8 Mentor Session
1. **Evaluation Criteria on Discrepancy Learning:** How do judges value offline self-correcting rules (`Candidate Rule #14`) versus pure model accuracy?
2. **Kurdish Dialect Weighting:** In the live evaluation set, what is the expected proportion of Kurdish vs Iraqi Arabic tickets?
3. **Judge Input Formats:** Will the live test run during the finals provide structured JSONL files or unstructured raw strings entered into the UI?
