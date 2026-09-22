# ADR-0002: Batch Pipeline vs. Open-Ended Agent Loop

## Status
Accepted

## Context
The competition brief specifies Topic 06 as "Support Pipeline Automation" and explicitly mandates:
> "A batch pipeline, not a chatbot. It runs over a queue of tickets and, for each one, uses an LLM to classify the issue, set a priority, extracts structured details (transaction reference, amount, date), routes it to the right team, and drafts a first response for a human agent to approve or edit."

The judging criteria heavily reward "Technical judgment and architecture (no unjustified complexity)" and "Working prototype and reliability (runs live on judge-supplied input, holds up)".

## Options Considered
1. **Open-Ended Agent Framework (ReAct loop, AutoGen, CrewAI, LangGraph)**:
   - Dynamic tool-use loop where an LLM decides what tools to call in free-form steps.
   - High latency, non-deterministic execution paths, high token cost, vulnerability to infinite loops or tool hallucinations, difficult to benchmark cleanly on a batch of 300+ tickets.
2. **Fixed Typed Sequential Pipeline (Chosen)**:
   - Linear, structured stages:
     `Ingest -> Validate -> Classify (LLM) -> Extract (LLM) -> Normalize (Code) -> Route (Code) -> Escalate Check (Code) -> Draft (LLM) -> Review Queue`.
   - Each stage receives typed Pydantic models and produces strictly validated output.
   - Deterministic escalation gates protect downstream stages if confidence is low.

## Decision
We implement a typed, deterministic pipeline rather than an autonomous conversational agent loop.

## Rationale
- **Predictability & Reliability:** A batch of 100 tickets takes a predictable amount of time, with clear latency budgets per stage.
- **Auditable Failure Modes:** If extraction fails or confidence is low, the pipeline immediately halts downstream drafting and escalates with a structured reason note.
- **Judge Alignment:** The challenge rubric penalizes unjustified complexity. A clean, resilient batch architecture directly answers the brief while maintaining 100% testability.
