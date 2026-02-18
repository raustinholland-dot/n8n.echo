# ECHO — Design Principles & MVP Definition

> This document captures the foundational thinking behind ECHO, written by Austin Holland during the early design phase. It serves as the north star for all build decisions.

---

## Project Goal

Build ECHO: an autonomous, self-updating, and dynamic deal engine with 3 guiding principles:

1. **Recalculate deal health** with each input of new information using objective metrics and the P2V2C2 sales methodology framework, while maintaining all relevant historical context.
2. **Generate all necessary outputs** (artifacts — DAPs, follow-ups, strategic coordination emails, internal meeting agendas, pricing messages, etc.) to move a deal from its current CAS to 5VO — Contract Signed.
3. **Achieve 5VO in the shortest time possible for the largest TCV possible.**

---

## The "Coke Machine" Protocol

For every input:
- Evaluate all 15 ledger elements internally
- **Display ONLY** the specific output requested or the immediate next-step draft
- Total suppression of the full ledger is the mandatory default
- Provide a "Full Ledger Audit" only when explicitly requested

---

## Governance & Logic Rules

- **Sequential Lock:** Activity n+1 cannot be validated until VO(n) is confirmed
- **The Power Mandate:** Transitioning to Stage 3 (Prove) requires a confirmed connection between identified Pain and the Executive Sponsor
- **The Power Ceiling:** If Power is scored 2 or lower, Overall Deal Health cannot exceed 30%
- **Truth Conflict:** If user input overrides the rubric or logic, the engine must challenge the user, seek to understand the deviation, and flag the resulting strategic risk
- **The 48-Hour Rule:** Final Approach Document drafts must be submitted to internal approvers at least 48 hours before the client presentation
- **Pre-Proposal Gate:** Cannot email an AD with pricing (CAS 3D) until a Validation Meeting (3C) has occurred

---

## P2V2C2 Scoring Highlights

- **Pain:** Moves to 5 only when the Executive Sponsor agrees the pain is great enough to change
- **Power:** Moves to 3 only after meeting the Executive Sponsor
- **Vision:** Remains at 2 until specific "Success Criteria" or "Proof Criteria" are documented and agreed upon
- **Control:** A score of 4 or 5 requires documented confirmation that the ES has agreed to and is executing on the Dual Action Plan (DAP) timeline

---

## Velocity Decay Thresholds

| Activity | Threshold |
|---|---|
| Pricing (Internal) | 24-hour follow-up |
| Scoping/Approval (Internal) | 48-hour flag as risk |
| Post-Call Email (Client) | 24-hour re-engagement |
| Stall Alert | 7 days inactivity = -10 point health deduction |

---

## Standard DAP Timeline Milestones

```
[Date] - Initial Discovery [STATUS]
[Date] - Define Current State and Desired Future State [STATUS]
[Date] - Co-Create Session [STATUS]
[Date] - Present Draft Approach [STATUS]
[Date] - Present Updated Approach based on feedback [STATUS]
[Date] - Go / No Go Decision [STATUS]
[Date] - Submit for Budget Approval [STATUS]
[Date] - Send MSA/SOW [STATUS]
[Date] - [Client Name] Initial Review of MSA/SOW & Redlines [STATUS]
[Date] - Call to Review Redlines [STATUS]
[Date] - Finalize Redlines and Launch DocuSign [STATUS]
[Date] - Execute Contract [STATUS]
[Date] - Initial Engagement Meeting / Project Start [STATUS]
[Date] - Final Report Delivered to [Client Name] [STATUS]
```

---

## 15 Ledger Elements (Internal Evaluation)

```
date_updated, opportunity_name, cas, salesforce_block_1_dap,
last_activity, p2v2c2_reasoning, salesforce_block_2_p2v2c2,
client_follow_up_email, internal_message_scoping,
internal_message_pricing, ad_gap_analysis, meeting_prep,
proactive_strategy, strategic_simulation, products_pricing
```

---

## Origin Story

ECHO evolved from "Call Notes" — a Google Gemini Gem originally built to structure call transcripts into Salesforce-ready formats. After proving it could recalculate deal health months later from a single new transcript input, it was renamed "Deal Path" and expanded to guide the full sales cycle. The core insight: the same model that processes a first call can maintain full deal context indefinitely, draft nuanced relational responses, and reference specific quotes from past transcripts to drive strategic points home. ECHO is the n8n-based, PostgreSQL-backed evolution of that proof of concept — built to run at scale across all deals simultaneously.
