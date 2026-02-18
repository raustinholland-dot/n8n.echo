# Deal Path MCP Server

An MCP (Model Context Protocol) server that exposes the Deal Path V2 hybrid 2-agent system via standardized tools.

## Architecture

```
MCP Client (Claude, etc.)
    ↓
MCP Server (this file)
    ↓
Assessment Engine → Artifact Engine
    ↓
Deal Memory (JSON files)
```

## Installation

1. **Install dependencies:**
   ```bash
   cd /Users/austinhollsnd/Desktop/DEAL_PATH_BUILD2
   pip install -r requirements.txt
   ```

2. **Configure MCP client:**

   The server is already configured in your MCP config at:
   `/Users/austinhollsnd/.gemini/antigravity/mcp_config.json`

   ```json
   "dealpath": {
       "command": "python3",
       "args": ["/Users/austinhollsnd/Desktop/DEAL_PATH_BUILD2/mcp_server.py"],
       "env": {
           "PYTHONPATH": "/Users/austinhollsnd/Desktop/DEAL_PATH_BUILD2"
       }
   }
   ```

3. **Restart your MCP client** (Claude Code, etc.) to load the new server.

## Available Tools

### 1. `process_deal_input`

Process a deal input (transcript, email, Teams message) through both engines.

**Parameters:**
- `content` (required): Raw content (transcript, email body, etc.)
- `deal_slug` (optional): Deal identifier (auto-generated if not provided)
- `input_type` (optional): Type of input (`call_transcript`, `email`, `teams_message`, or `auto`)
- `date` (optional): Date of interaction (YYYY-MM-DD, defaults to today)
- `source_filename` (optional): Original filename for reference

**Example:**
```json
{
  "content": "Call transcript here...",
  "input_type": "call_transcript",
  "date": "2026-02-16"
}
```

**What it does:**
1. Runs Assessment Engine to calculate P2V2C2 scores and CAS stage
2. Runs Artifact Engine to generate all required outputs
3. Saves everything to deal memory
4. Returns complete assessment + artifacts

### 2. `get_deal_status`

Get current status of a deal including P2V2C2 scores, CAS stage, and momentum.

**Parameters:**
- `deal_slug` (required): Deal identifier

**Example:**
```json
{
  "deal_slug": "partnership-healthplan"
}
```

### 3. `list_deals`

List all deals in memory with their current status.

**Parameters:** None

**Returns:** List of all deals with CAS stages, P2V2C2 totals, and momentum.

### 4. `get_deal_artifacts`

Get generated artifacts for a specific deal and date.

**Parameters:**
- `deal_slug` (required): Deal identifier
- `date` (optional): Date (YYYY-MM-DD), defaults to latest

**Example:**
```json
{
  "deal_slug": "partnership-healthplan",
  "date": "2026-02-16"
}
```

## Deal Memory Structure

All deals are stored in: `/Users/austinhollsnd/Desktop/DEAL_PATH_BUILD2/deals/`

```
deals/
├── partnership-healthplan/
│   ├── conversation_history.json  # All interactions
│   ├── current_state.json         # Latest P2V2C2 & CAS
│   └── artifacts/
│       ├── 2026-02-10_outputs.json
│       └── 2026-02-17_outputs.json
└── american-medical/
    └── ...
```

### File Formats

**conversation_history.json:**
```json
{
  "deal_slug": "partnership-healthplan",
  "opportunity_name": "Partnership HealthPlan - Add-on",
  "interactions": [
    {
      "turn_id": 1,
      "timestamp": "2026-02-10T10:00:00Z",
      "input_type": "call_transcript",
      "date": "2026-02-10",
      "assessment": { /* P2V2C2 scores, CAS, evidence */ },
      "artifacts_generated": ["call_summary", "client_email", ...]
    }
  ]
}
```

**current_state.json:**
```json
{
  "deal_slug": "partnership-healthplan",
  "date": "2026-02-10",
  "p2v2c2_assessment": { /* scores, evidence, momentum */ },
  "cas_assessment": { /* current stage, VOs completed */ },
  "highlights": [ /* strategic insights */ ]
}
```

**artifacts/YYYY-MM-DD_outputs.json:**
```json
{
  "artifacts": {
    "call_summary": "...",
    "salesforce_dap": "...",
    "salesforce_p2v2c2": "...",
    "client_email": "...",
    "internal_message": "..."
  },
  "orchestration_logic": {
    "current_cas": "2B",
    "next_cas_target": "3A",
    "artifacts_generated": [...],
    "artifacts_skipped": [...]
  }
}
```

## Usage Examples

### Example 1: Process a discovery call transcript

```python
# Via MCP client (Claude Code, etc.)
Use the process_deal_input tool:
{
  "content": "Austin: Thanks for joining today...",
  "input_type": "call_transcript",
  "date": "2026-02-16",
  "source_filename": "partnership_discovery_2026_02_16.txt"
}
```

### Example 2: Check deal status

```python
Use the get_deal_status tool:
{
  "deal_slug": "partnership-healthplan"
}
```

### Example 3: List all active deals

```python
Use the list_deals tool with no parameters
```

## Testing

Test the MCP server directly:

```bash
cd /Users/austinhollsnd/Desktop/DEAL_PATH_BUILD2

# Test with a sample transcript
python3 mcp_server.py
```

Or test via Claude Code once configured.

## Troubleshooting

### "MCP SDK not installed"
```bash
pip install mcp
```

### "GOOGLE_API_KEY not found"
Make sure `.env` file exists with:
```
GOOGLE_API_KEY=your_key_here
```

### "Assessment Engine error"
Check that the `skills/` directory exists with all required knowledge files:
- `skills/methodology/p2v2c2_rubric.md`
- `skills/methodology/cas_state_machine.md`
- `skills/methodology/role_definitions.md`
- `skills/compliance/clearwater_sales_process.md`
- `skills/compliance/ppmg_strategic_nuances.md`
- `skills/messaging/austin_email_style.md`
- `skills/messaging/cas_artifact_mapping.md`
- `skills/messaging/salesforce_formatting.md`

## Performance

- **Processing time:** ~5 seconds total (2-3s assessment + 2-3s artifacts)
- **Cost:** ~$0.07 per input (at 20 inputs/day = ~$26/year)
- **Reliability:** High (deterministic scoring with temperature=0.0)

## Architecture Alignment

This MCP server follows the architecture defined in `ARCHITECTURE.md`:

✅ Hybrid 2-Agent approach (Assessment + Artifact engines)
✅ Deterministic P2V2C2 scoring (temperature=0.0)
✅ CAS-to-artifact mapping
✅ Deal memory persistence
✅ <5 second processing time

## Next Steps

After the MCP server is running:

1. ✅ Test with real transcript data
2. ⏳ Add more specialized artifacts (approach documents, proposals, etc.)
3. ⏳ Implement learning loop (capture user edits for improvement)
4. ⏳ Add caching for repeated queries
5. ⏳ Parallelize artifact generation if needed

## Support

For issues or questions:
- Check `ARCHITECTURE.md` for design decisions
- Review `agents/assessment_engine.py` and `agents/artifact_engine.py` for engine logic
- See conversation history in deal memory for debugging
