# Deal Path V2 - ECHO Portal Roadmap

## Phase 1: Core Processing Engine (Manual Workflows)
**Timeline:** 2-3 weeks
**Goal:** Autonomous deal engine that processes inputs and generates all artifacts

### Deliverables:
1. ✅ **Assessment Engine (Agent 1)**
   - P2V2C2 deterministic scoring (temperature=0.0)
   - CAS progression logic
   - Input classification (transcript/email/Teams/meeting)
   - Deal memory integration

2. ✅ **Artifact Engine (Agent 2)**
   - CAS-to-artifact mapping
   - Generate: DAP, P2V2C2 blocks, client emails, internal messages, call summaries
   - Plain text outputs (copy-paste ready)

3. ✅ **Gmail Polling (1-minute interval)**
   - Intake email: dealpath@[yourdomain].com
   - Process forwarded emails/attachments
   - Store raw inputs

4. ✅ **Deal Memory Storage**
   - `/deals/[deal_slug]/conversation_history.json`
   - `/deals/[deal_slug]/current_state.json`
   - `/deals/[deal_slug]/artifacts/[date]_outputs.json`

5. ✅ **ECHO Portal (Review UI)**
   - Task-oriented progressive disclosure
   - "Copy to Clipboard" buttons for each artifact
   - Manual copy-paste to Salesforce/Outlook/Teams
   - Deal ledger view

6. ✅ **Outlook Rules Documentation**
   - Email forwarding rules
   - Meeting invite forwarding
   - Teams message forwarding

### Success Criteria:
- P2V2C2 scores match manual assessment ≥95%
- Same input + history = same output 100%
- Processing time <5 seconds
- All outputs plain text (no formatting issues)

---

## Phase 2: Integration & Automation
**Timeline:** 4-6 weeks after Phase 1
**Goal:** Reduce manual steps, add direct posting capabilities

### Deliverables:
1. ⏳ **Automatic Voice Memo Recording**
   - **Scheduled Calls:** Microsoft Graph API reads Outlook calendar → auto-start/stop recording
   - **Ad-hoc Calls:** Teams activity monitor detects when call starts → auto-start recording
   - Monitor Teams.app microphone/camera usage as call indicator
   - Auto-stop recording when call ends (scheduled time or mic released)
   - Seamless integration with existing Voice Memo watcher
   - **Result:** Every Teams call (scheduled or not) is captured automatically

2. ⏳ **Microsoft Graph API Integration**
   - Direct Teams message posting (no copy-paste)
   - Outlook calendar reading
   - Meeting metadata extraction

3. ⏳ **Salesforce API (if IT approved)**
   - Direct DAP updates
   - P2V2C2 field updates
   - Opportunity notes appending
   - **Fallback:** Continue manual copy-paste

4. ⏳ **Daily Prep Agent**
   - Read Outlook calendar 2-3 days ahead
   - Generate meeting prep materials
   - Pre-populate context for upcoming calls

5. ⏳ **Enhanced Deal Ledger**
   - Visual timeline of all interactions
   - P2V2C2 trend graphs
   - CAS progression tracker

6. ⏳ **Cloud Deployment (Always-On)**
   - Deploy Gmail poller to Google Cloud Run/Compute Engine
   - Migrate deal memory to Cloud Storage
   - Secure credential management (Secret Manager)
   - ~$5-10/month for 24/7 availability
   - **Result:** System runs even when traveling/Mac is off

### Success Criteria:
- Voice Memo recordings start/stop automatically based on calendar
- 80% reduction in manual copy-paste actions
- Teams messages posted directly from ECHO
- Calendar-aware prep materials generated automatically
- System available 24/7 regardless of Mac status

---

## Phase 3: Learning Loop
**Timeline:** Ongoing after Phase 2
**Goal:** System learns from user edits and improves over time

### Deliverables:
1. ✅ **Edit Capture System**
   - Track all user edits to generated artifacts
   - Categorize edits: tone, content, structure, facts
   - Store edit patterns

2. ✅ **Pattern Recognition**
   - Identify recurring edit types
   - Detect client-specific preferences
   - Adjust generator prompts dynamically

3. ✅ **A/B Testing Framework**
   - Test prompt variations
   - Measure edit rates
   - Roll out improvements incrementally

4. ✅ **Feedback Loop UI**
   - "This was helpful/not helpful" buttons
   - Quick edit categorization
   - Suggested improvements from system

### Success Criteria:
- Edit rate decreases 30% within 3 months
- Client-specific tone adjustments automatic
- User satisfaction >85%

---

## Phase 4: Scale & Optimization
**Timeline:** 6+ months after Phase 3
**Goal:** Handle full team usage, optimize for speed/cost

### Deliverables:
1. ✅ **Multi-User Support**
   - Multiple AEs using same system
   - Deal assignment/routing
   - Shared knowledge pool

2. ✅ **Performance Optimization**
   - Parallelize artifact generation
   - Add caching for repeated queries
   - Reduce processing time to <3 seconds

3. ✅ **Advanced Analytics**
   - Time-to-5VO trends
   - TCV optimization insights
   - Win/loss pattern analysis

4. ✅ **Knowledge Base Expansion**
   - Industry-specific modules (healthcare, finance, etc.)
   - Client vertical patterns
   - Competitive intelligence integration

### Success Criteria:
- Support 5+ AEs simultaneously
- Processing time <3 seconds
- Average time-to-5VO reduced 25%
- TCV increased or maintained

---

## Phase 1 Detail: Data Flow (LOCKED)

### INPUT → PROCESSING → OUTPUT → STORAGE

**INPUT (Plain Text):**
- Call transcripts (.txt, pasted, or extracted from .vtt)
- Emails (forwarded as attachment)
- Teams messages (forwarded or pasted)
- Meeting invites (forwarded)

**PROCESSING (JSON - Internal Only):**
```json
{
  "deal_slug": "partnership-healthplan",
  "p2v2c2_assessment": { /* Agent 1 output */ },
  "cas_assessment": { /* Agent 1 output */ },
  "artifacts": { /* Agent 2 output */ }
}
```

**OUTPUT (Plain Text - Copy-Paste Ready):**
1. Salesforce Block 1: DAP + Current/Future State
2. Salesforce Block 2: P2V2C2 Scoring
3. Client Follow-Up Email
4. Internal Team Update
5. Call Summary
6. Teams Message (if applicable)

**STORAGE (JSON Files):**
```
/deals/partnership-healthplan/
  ├── conversation_history.json
  ├── current_state.json
  └── artifacts/2026-02-10_outputs.json
```

**ECHO Portal Interaction (Phase 1):**
1. User drops transcript into ECHO or email auto-polls
2. System processes (~5 seconds)
3. ECHO displays all artifacts with "Copy" buttons
4. User clicks "Copy" → pastes into Salesforce/Outlook/Teams
5. User edits as needed, sends/saves
6. (Future: User marks "Sent" → system stores final version)

---

## Current Status: Phase 1 - Near Complete

**Completed:**
- ✅ Assessment Engine with P2V2C2 rubric
- ✅ Artifact Engine (5 outputs)
- ✅ Gmail polling (60s interval)
- ✅ Voice Memo watcher with Gemini 2.0 transcription
- ✅ Deal memory storage
- ✅ Documentation (Gmail, Outlook, Voice Memos)

**Remaining:**
- ⏳ ECHO Portal UI (review/copy buttons)
- ⏳ End-to-end testing with real data

**Phase 2 Preview:**
- Calendar-triggered Voice Memo automation (top priority)
