# ECHO Workflows

n8n automation workflows for the ECHO deal intelligence system.

## Active Workflow

### ECHOv4.json
**n8n ID:** `RlnZGOaKU4ee7D6M`
**Instance:** `http://localhost:5678`

End-to-end sales deal assessment pipeline using P2V2C2 methodology.

#### Flow
1. **Gmail Trigger** — polls every minute for emails from `austin.holland@clearwatersecurity.com`
2. **Input Classifier** — extracts deal slug, input type, participants
3. **Load Deal Memory** — looks up existing deal in PostgreSQL
4. **Assessment Engine (Gemini 2.0 Flash)** — scores deal across P2V2C2 (6 dimensions, 0–5 each, max 30) and assigns CAS
5. **Artifact Engine (Gemini 2.0 Flash Lite)** — generates Salesforce DAP block, P2V2C2 descriptions, client follow-up email, exec recap, internal pricing message
6. **Format for PostgreSQL** — builds pre-escaped SQL strings
7. **Send Review Notification Email** — emails Austin with portal link + artifact preview
8. **Wait for Review (Editing Portal)** — pauses execution at `http://localhost:5678/form-waiting/{executionId}`, pre-fills all artifact fields for review/edit
9. **Merge Edited Artifacts** — merges form edits with AI originals (blank = keep original)
10. **Save Artifacts** → **Save Evidence** → **Save History** — writes to PostgreSQL with `approved = true`
11. **Save Artifact Feedback** — records original vs. edited per field in `artifacts_feedback` for RLHF
12. **Gmail — Final Email** — sends approved artifacts to Austin

#### Key Constraints
- n8n 2.8.3 does NOT support a Webhook trigger + Wait(form) node in the same workflow
- The MCP webhook trigger was removed for this reason — trigger via Gmail only
- Form pre-population uses expressions referencing `Format for PostgreSQL` node

#### CAS Format
`[1-5][A-B]: [short description]`
e.g. `2B: Qualify - Problem validation`

#### P2V2C2 Description Format
`[Dimension] ([score]/5) - [Intensity]. [One-sentence summary.]`
e.g. `Pain (4/5) - High. Client flags conflict of interest with current MSP.`

---

## Database

**DB:** `echo_deals` (PostgreSQL@15 via Homebrew)
**Credential in n8n:** `ECHO PostgreSQL`

### Tables
| Table | Purpose |
|---|---|
| `deals` | One row per deal slug — CAS, P2V2C2 scores, account info |
| `artifacts` | Generated artifact text per deal run |
| `artifacts_feedback` | RLHF data — original vs. edited output per field |
| `p2v2c2_evidence` | Evidence text per dimension per run |
| `deal_history` | Audit log of every input processed |
| `action_plans` | Extracted action items |

---

## Deployment

1. Start PostgreSQL: `brew services start postgresql@15`
2. Start n8n in Docker Desktop
3. Import workflow via n8n UI or API:
   ```bash
   curl -X PUT http://localhost:5678/api/v1/workflows/RlnZGOaKU4ee7D6M \
     -H "X-N8N-API-KEY: <key>" \
     -H "Content-Type: application/json" \
     -d @ECHOv4.json
   ```
4. Activate the workflow in n8n UI

---

## Git Workflow — How to Push Changes to GitHub

**Do NOT use n8n's built-in source control.** It requires Docker reconfiguration and a separate deploy key — it's fragile and unnecessary.

Instead, use manual git push from the VS Code terminal. Run this from `/Users/austinhollsnd/Desktop/workflows/` after any change:

```bash
git add ECHOv4.json && git commit -m "describe what changed" && git push
```

### When to push:
- After any prompt changes to the Assessment Engine or Artifact Engine
- After any structural workflow changes (new nodes, connections, etc.)
- After testing confirms the change is working

### How workflow changes are made:
1. Edit `ECHOv4.json` locally (via Claude or directly)
2. Push to n8n via the API curl command above
3. Push to GitHub via the git commands above

### API key location:
The n8n API key is stored in the n8n SQLite DB. Retrieve it with:
```bash
sqlite3 ~/.n8n/database.sqlite "SELECT apiKey, label FROM user_api_keys LIMIT 5;"
```

### SSH key:
GitHub access uses the SSH key at `~/.ssh/github_echo`. This is already configured — `git push` works without any password.

---

## Archive

- **ECHOv3.json** — previous version, single-agent, no human-in-the-loop editing portal
