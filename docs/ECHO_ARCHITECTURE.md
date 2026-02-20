# ECHO Architecture — Canonical Design
Version: 2.0
Status: Documented, ready to implement

---

## Core Principle

The database is the single source of truth for every deal. No agent passes data to another agent directly. Every agent reads from and writes to the deal record. Adding a new agent never requires rewiring existing agents.

---

## Two-Agent Architecture

### Agent 1 — ECHO Intelligence Engine
**Input:** Raw deal input (transcript, email, notes) + full prior deal record from PostgreSQL

**Three tasks in sequence:**
1. **Evidence Extraction** — reads the input, produces a structured speaker-attributed evidence document. Verbatim quotes only. No interpretation, no scoring. Every claim attributed to a named speaker.
2. **P2V2C2 Scoring** — reads the evidence document it just produced. Scores each dimension by finding the highest rubric level directly supported by named evidence. Must cite the specific rubric line and speaker. Cannot score a level it cannot cite.
3. **Phase 1 Salesforce Artifacts** — produces all Salesforce copy-paste blocks: close date, stage, CAS, forecast category, DAP block, risks, next step, all six P2V2C2 evidence descriptions.

**Writes to DB:** Evidence document + scores + Phase 1 artifacts + full deal state

**Output schema:**
```json
{
  "evidence": {
    "participants": [],
    "pain_quotes": [],
    "power_signals": [],
    "vision_signals": [],
    "value_signals": [],
    "change_signals": [],
    "control_signals": [],
    "services_mentioned": [],
    "next_steps_mentioned": []
  },
  "salesforce": {
    "close_date": "",
    "stage": "",
    "cas": "",
    "forecast_category": "",
    "salesforce_block_1_dap": "",
    "risks": "",
    "next_step": "",
    "pain_score": 0, "pain_evidence": "",
    "power_score": 0, "power_evidence": "",
    "vision_score": 0, "vision_evidence": "",
    "value_score": 0, "value_evidence": "",
    "change_score": 0, "change_evidence": "",
    "control_score": 0, "control_evidence": ""
  }
}
```

---

### Agent 2 — ECHO Artifact Engine
**Input:** Full deal record from PostgreSQL (evidence document, scores, Phase 1 artifacts, deal history) — NOT from Agent 1 directly

**One task:** Generate Phase 2 narrative artifacts

**Writes to DB:** Phase 2 artifacts appended to same deal record

**Output schema:**
```json
{
  "narratives": {
    "call_summary": "",
    "highlights": "",
    "action_items": "",
    "p2v2c2_scoring": "",
    "internal_actions": "",
    "services_narrative": "",
    "general_narrative": "",
    "anecdotes": "",
    "internal_team_update": ""
  }
}
```

---

### Any Future Agent
Reads the full deal record from DB. Has access to raw evidence, scores, all artifacts, full history. No dependency on any other agent's output chain. No rewiring required.

---

## What the DB Record Contains After Each Run
- Raw evidence document (speaker-attributed, verbatim)
- P2V2C2 scores with rubric citations
- Phase 1 Salesforce artifacts (7 fields + 12 P2V2C2 score/evidence pairs)
- Phase 2 narrative artifacts (9 fields)
- Full deal history (every prior run appended, delta-flagged)

---

## Knowledge Base Design

| Content | Location | Reason |
|---------|----------|--------|
| P2V2C2 rubric table | Hardcoded in Agent 1 system prompt | Needed on every call, small, must never miss |
| Role definitions (PC, PES, ES, DM, Champion) | Hardcoded in Agent 1 system prompt | Same reason |
| CPS stage definitions | DDA_Constitution.md in vector store | Referenced but not needed verbatim every time |
| Clearwater service catalog | Vector store (n8n_vectors) | Long, changes, only relevant portions needed |
| DAP structure | DDA_Constitution.md in vector store | Referenced contextually |

---

## P2V2C2 Rubric (embed directly in Agent 1 prompt)

| Score | Pain | Power | Vision | Value | Change | Control |
|-------|------|-------|--------|-------|--------|---------|
| 0 | No knowledge of pain | No idea who is power | No idea of needs | Benefits unknown | No one committed | Buying process unknown |
| 1 | PC shared their situation | Indication of a PES | Begun to define needs | Believe situation causes pain | PC open to change | C described process as C knows it |
| 2 | PC admitted pain | Champion agreed to take to PES | Mapped capabilities to needs | Defined cost of pain | PC confirmed PES will meet | Met with a PES |
| 3 | PC indicated pain of PES | Met with PES | Agreed to proof criteria | Believe solution addresses pain | PES agreed need to change | Pain admitted & vision created for ES |
| 4 | PES admitted pain | PES agreed to DAP | ES agreed to vision of improved future state | ES shared benefits with DM | ES chosen Clearwater to lead change | ES agreed to DAP |
| 5 | ES agreed pain great enough to change | DAP steps on schedule | ES painting vision to others | DM agreed to financial terms | ES convinced DM must change | DAP complete |

**Role definitions:**
- PC = Potential Champion
- PES = Potential Executive Sponsor
- C = Champion
- ES = Executive Sponsor
- DM = Decision Maker

---

## Review Portal — 28 Fields

**Phase 1 — Salesforce (19 fields):**
close_date, stage, cas, forecast_category, salesforce_block_1_dap, risks, next_step,
pain_score, pain_evidence, power_score, power_evidence, vision_score, vision_evidence,
value_score, value_evidence, change_score, change_evidence, control_score, control_evidence

**Phase 2 — Narratives (9 fields):**
call_summary, highlights, action_items, p2v2c2_scoring, internal_actions,
services_narrative, general_narrative, anecdotes, internal_team_update

---

## Current System State (pre-implementation)

- **Workflow:** ECHOv4 - PostgreSQL_TESTING (ID: RlnZGOaKU4ee7D6M)
- **n8n:** v2.8.3, Docker container 'n8n', port 5678
- **DB:** PostgreSQL echo_deals, local, user=austinhollsnd
- **Vector store:** n8n_vectors, 64 chunks, pgvector 0.8.0
- **Current agents:** 1 (ECHO Engine — single pass, to be split)
- **Node count:** 25
- **Credentials:** ECHO OpenAI API (fIeGh1UabUL1CBma), ECHO PostgreSQL (ZMNqF3gUEXvNCjht), Gmail ECHO (KcxcROH9oa3L7IUB)
- **Model:** gpt-4o, temperature 0
- **Embeddings:** text-embedding-3-small, 1536 dimensions
- **Review portal:** echo_portal.py, port 5679
- **Key files:**
  - ECHOv4.json — workflow source
  - docs/ECHO_ARCHITECTURE.md — this file
  - docs/knowledge/DDA_Constitution.md — sales process rules
  - docs/knowledge/DDA_OutputPatterns.md — output formatting patterns
  - docs/knowledge/DDA_Services_OneLiners.md — service catalog one-liners
  - GEM Documents/ECHO GEM_DESCRIPTION_INSTRUCTIONS.txt — original system prompt source

---

## Context Transfer Prompt

Use this to resume work in a new session:

```
ECHO ARCHITECTURE CONTEXT — SESSION HANDOFF

PROJECT: ECHO — AI-powered deal intelligence system for Austin Holland,
Clearwater Security, PPM team.

NEXT TASK: Split the current single ECHO Engine node into two agents:
  Agent 1 (ECHO Intelligence Engine): evidence extraction + P2V2C2 scoring + Phase 1 Salesforce artifacts
  Agent 2 (ECHO Artifact Engine): Phase 2 narrative artifacts, reads from DB not from Agent 1

See /Users/austinhollsnd/Desktop/workflows/docs/ECHO_ARCHITECTURE.md for:
- Full architecture spec
- Agent output schemas
- P2V2C2 rubric to hardcode in Agent 1 prompt
- Complete field list for review portal
- Current system state and credentials

Key implementation notes:
- P2V2C2 rubric must be hardcoded in Agent 1 system prompt, NOT in vector store
- Agent 1 must do evidence extraction as a separate internal step before scoring
- Agent 1 must cite specific rubric line + speaker name for each score
- Agent 2 reads from PostgreSQL deal record, not from Agent 1 output directly
- Format for PostgreSQL node reads from Agent 1 only for Phase 1 fields
- A second Format/Save node will handle Agent 2 Phase 2 fields
- Review portal Wait form already has all 28 fields configured correctly
- Workflow ID: RlnZGOaKU4ee7D6M
- All credentials already configured in n8n
```
