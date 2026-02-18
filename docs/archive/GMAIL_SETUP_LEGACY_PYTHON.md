# Gmail Polling Setup Guide

## Overview
The Gmail poller checks **austinhollsnd@gmail.com** every 1 minute, processes emails through the Deal Path pipeline (Assessment Engine → Artifact Engine), and stores results in deal memory.

## Quick Start

### 1. First-Time Authentication

Gmail OAuth credentials are already configured. Just run the poller:

```bash
cd /Users/austinhollsnd/Desktop/DEAL_PATH_BUILD2
.venv/bin/python agents/gmail_poller.py
```

This will:
1. Open browser for Google OAuth consent
2. Sign in with **austinhollsnd@gmail.com**
3. Authorize "Deal Path Intake" to access Gmail
4. Save token to `token.json` (used for future runs)

**Security Note:** `token.json` contains access credentials - do NOT commit to version control.

### 2. Forward Emails to Intake

**Method 1: Manual Forwarding**
- Forward call transcripts, Teams messages, meeting notes to austinhollsnd@gmail.com
- Format: Forward as attachment if possible (preserves metadata)

**Method 2: Outlook Auto-Forward Rules** (See OUTLOOK_RULES.md - coming next)
- Set up rules to auto-forward specific emails from Outlook to Gmail

### 3. Running the Poller

**Foreground (testing):**
```bash
.venv/bin/python agents/gmail_poller.py
```

**Background (production - Mac):**
```bash
nohup .venv/bin/python agents/gmail_poller.py > gmail_poller.log 2>&1 &
```

**Stop background process:**
```bash
ps aux | grep gmail_poller
kill <PID>
```

## How It Works

### Email Processing Flow

```
1. Gmail Poller checks austinhollsnd@gmail.com for unread emails (every 60s)
   ↓
2. Extract email content (body, attachments, subject)
   ↓
3. Classify input type (transcript/email/Teams/meeting)
   ↓
4. Run Assessment Engine
   - Calculate P2V2C2 scores (deterministic, temperature=0.0)
   - Determine CAS stage
   - Extract facts
   ↓
5. Run Artifact Engine
   - Generate DAP, P2V2C2 blocks, emails, summaries
   ↓
6. Store results in /deals/[deal_slug]/
   - conversation_history.json
   - current_state.json
   - artifacts/[timestamp]_outputs.json
   ↓
7. Mark email as read
```

### Deal Memory Structure

```
/deals/
├── partnership-healthplan-2026-02-10/
│   ├── conversation_history.json
│   ├── current_state.json
│   └── artifacts/
│       ├── 2026-02-10_14-30-15_outputs.json
│       └── 2026-02-17_09-15-42_outputs.json
└── american-medical-2026-02-12/
    └── ...
```

## Email Format Guidelines

### For Call Transcripts
**Subject:** `Call Transcript - [Client Name] - [Date]`
**Body:** Paste transcript directly or attach as `.txt` file

### For Teams Messages
**Subject:** `Teams Message - [Channel/Client Name]`
**Body:** Copy-paste Teams conversation

### For Meeting Notes
**Subject:** `Meeting Notes - [Client Name] - [Topic]`
**Body:** Meeting notes or calendar invite forwarded

## Troubleshooting

### "Token expired" error
- Delete `token.json`
- Run poller again to re-authenticate

### "No new emails" but I forwarded something
- Check Gmail inbox directly
- Ensure email is unread
- Check spam folder

### Poller crashes
- Check error logs: `tail -f gmail_poller.log`
- Verify API quotas: [Google Cloud Console](https://console.cloud.google.com/apis/dashboard)

## Cost & Quotas

- **Gmail API:** Free tier = 1,000,000,000 quota units/day
- **Poll every 60 seconds:** ~43,200 polls/month = ~1.3M quota units/month
- **Well within free tier**

## Next Steps

1. Run poller for first time to authenticate
2. Set up Outlook auto-forward rules
3. Test with real call transcript
4. Build ECHO Portal UI for reviewing outputs
