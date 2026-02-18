#!/usr/bin/env python3
"""
ECHO Eval Script
Runs prompts directly against Gemini and scores outputs vs. ideal.
Bypasses n8n entirely — ~10 second feedback loop for prompt iteration.

Usage:
  python3 echo_eval.py                    # run eval, print scored report
  python3 echo_eval.py --show-output      # also print full generated text
  python3 echo_eval.py --artifact email   # eval only one artifact
"""

import json
import sys
import re
import argparse
import google.generativeai as genai

# ── Config ──────────────────────────────────────────────────────────────────
GEMINI_API_KEY = "AIzaSyBdCH67ed-TLBQZHLMRKUCh9K0tTsdfAZ0"
ASSESSMENT_MODEL = "gemini-2.0-flash"
ARTIFACT_MODEL   = "gemini-2.0-flash-lite"
DEAL_DATE        = "2026-01-21"

# ── Transcript ───────────────────────────────────────────────────────────────
TRANSCRIPT = """See below transcript for the Velentium call. MSS deal that Sandy (who I replaced on the PPM team) started on and they went another direction, but came back. This is the first call for this new opportunity. "Hey. Good afternoon. How are you?  Oh, it's UK in the background. What's up, you gay? How are you, man?  I am In person live. We all in H town? Yep.  Yep. We finally got the UK to make the trip down here. And he brought a bunch of bad weather wind.  I mean, it's funny. It's funny we've been on, you know, our life is on these calls and these meetings. And whenever we're talking to the Southeast, everybody's talking about the weather that's coming.  And then when we talk to like Chicago in New York, they're like, oh, that's so cute of you guys to be worried about this. about like a couple of inches of snow. But such is it, that Listen, it's like I'm in Atlanta and, you know, we, my wife woke up this morning. It was like, are you concerned?  I'm like, I mean, they like, make you think that the sky is following. But you guys know it. I grew up in Houston, and like, like everybody loves to talk about hurricanes.  As soon as there's one in the Caribbean, like, everybody's, like, tracking on what's's really good website. There's those guys, that do the storm tracking, Space City. Do you ever, you ever look at their emails?  They actually do really good work on hurricane tracking and stuff like that. They're based out of Houston. Next time hurricane comes, I'll go take a look at it.  I'll drop you their link. I'll drop you the website. All right...  Well, I don't even know if or at Richmond is Adam joining or should we just. Yeah, I't. Yeah, I didn't think so ever.  I think Adam honestly just suggested us to reconnect with you guys and, you know, I'll let you've met Richmond, right or wrong? Have you not? I think just over email.  So it's nice to meet you guys. I'm, um. I'm on David's team.  I've fused on private equity strategy, so I've been working a lot with Adam. I joined about a year ago. So a lot of yearall's conversations were already kind of in flight at that point.  But yes, over the last gosh, probably six months in earnest, I've been working more so with Adam and kind of more so across the portfolio. So it's good to connect recall. I know we exchanged some emails throughout the year as well, but nice to meet you all. wise you too, yeah.  In Austin, you can do an intro. Yeah, and my name's Austin Holland. I work on the PPM team alongside David and Richmond. and I joined seven months ago.  So, I think you guys have been in touch with Sandy before on some occasions. So I'm kind of stepping in for Sandy now. So, yeah, good, good to talk to you guys and look forward to getting up to speed.  Yeah, so, I mean, we were just tracking you ads to migration projects that were going on and I think Adam suggested us check in and, you know, if that's really all this is, how can we be helpful? Where do things stand, you know, specifically man security services, but we can also zoom out and take a broader perspective on kind of what's on your compliance, what's on your cybersecurity roadmap. And is there anything that we need to talk through or think through with you or can be of support to you?  So throwing spaghetti on the wall here, where we're at is, we feel things are pretty stable from just the security environment, if you will. We have our MSP, obviously, in place. Things are going reasonably well there.  However, I think there's an opportunity here where we sort of bifurcate and make sure that the fox isn't gardening a hen house. Yep. And I think it would be nice to explore options there.  The current MSP, like most MSPs are really good at level one support. And we actually have a person on site, which has been good for our company. This is one of the reasons we went to this MSP a couple of years ago is that we were able to arrange for a solution where we have a person on site.  And so that's been good for us as an organization. And things seem fairly stable. Also, last year, we got our together with this MSP and a contractor that they secured, we got our ISO 27001 certification.  We need to keep that maintained, obviously, going forward. And so I think for us, there's an opportunity to explore on one level, hey, what services can we split off this current arrangement that we have? Recognizing their core competency is going to be the level one support and some of the level two or more project-based activities that we're handling, like, you know, they're doing the installation of a new dedicated internet circuit and redoing the Wi-Fi points.  I mean, these are all things that they're doing here being local, conveniently physical access is really good. I think that's where they're going to have the leg up, if you will. But things that back in, SOC, security compliance, ISO ongoing ISO 27001 compliance.  Those are things that they don't need to be physical here for. So I think we, there's an opportunity to explore where can we put that over to Clearwater and you take on that responsibility. And they continue to do the day-to-day hands on keyboard local IT support. So that's kind of where our head is. And we want to make sure we get a proposal and see what the pricing looks like for that. And then we're going to talk to you guys and probably one or two other vendors about this and see if we can make something work, going into our renewal discussions with our current MSP. Travis: also, also what we wanted was to have the scoping on the security services to make sure we cover everything. And so to your point, when we went through the ISO 27001, we had a contractor they kind of subcontracted to come in and do the assessment. So what we want to make sure is that when we split this off, we cover everything and we have a clean line. So there's no ambiguity about what Clearwater is responsible for and what the existing MSP is responsible for. Travis: we actually have kind of a spreadsheet or a table that we've started to build that delineates what we're thinking, the areas of responsibility. Austin: and that's perfect. Yeah, that's exactly, that's the kind of output we're going to need to do our work. UK: perfect. So going into our renewal discussions, I want to be able to hand something to Clearwater, this is the scope, this is what we want you to be responsible for. And then the remaining items stay with the MSP. Richmond: so when do those renewal discussions happen with the MSP? Travis: June. June of this year. So we'll actually we should have renewed already. We've been in a month to month right now. Richmond: oh, wow, okay. And just as background, just out of curiosity, is there a different MSP you're talking to in addition to Clearwater, or just Clearwater at this point? Travis: two or three potentially UK:  probably two or three. So what counts does Clearwater need to be able to scope this? Austin: we need device counts. Users, servers, endpoints. And then for a split, we've been building these split models where we detail, here's what Clearwater is going to own, here's what stays with the client, here's what we can work together on. UK: there's also some cloud infrastructure too. Azure? Travis: yes. UK: and then Fortigate. Travis: Fortigate firewalls. And we also have a couple of PCs that we're going to be decommissioning. Yeah, we can send you guys a, we can send you over the device list along with the spreadsheet on the areas of responsibility. Austin: great. So just so we have a realistic view, I probably won't be able to get back to you guys until after my trip tomorrow. I have a flight tomorrow morning. I'll try to review it this week when I can. And then sometime next week, I'd like to get back to you guys with sort of a revised proposal based on those updated counts. Richmond: Travis, UK, it's great to reconnect. I don't think we've spoken in a while. I don't think we've spoken since Sandy. Austin: I think Sandy left about a year ago. Richmond: yeah, so it's been a while.  But Austin's done a great job getting up to speed. I think what I took away is you really understand your situation. And it actually makes our job very easy. And just again, this is Austin's deal, but I just wanted to be here for the first call. And there's good energy around this. This can come together very quickly if you want it to. Travis: UK tell them a little bit about what's on the horizon from a business perspective. UK: yeah, we're growing a bit. We've had an acquisition that came through recently. We're also involved in some real estate development. We're diversifying a little bit. Travis: so yeah that's kind of a broad overview. And then on the IT security front, we're kind of continuing to add some new employees as things grow. So it's an active environment right now for us."
"""

# ── Ideal Outputs (from Austin's RLHF edits) ────────────────────────────────
IDEALS = {
    "pain_evidence": "Pain (4/5) - High. Explicit concern regarding the \"fox guarding the hen house\" with their current MSP.",
    "power_evidence": "Power (4/5) - Travis and UK are the primary stakeholders and are driving the \"bifurcation\" strategy.",
    "vision_evidence": "Vision (5/5) - Very Strong. Client has an existing spreadsheet/table defining exactly where Clearwater takes responsibility vs. the MSP.",
    "value_evidence": "Value (4/5) - Clear value in Clearwater's ability to handle back-end Azure security and ISO maintenance.",
    "change_evidence": "Change (5/5) - High. Client is actively seeking to split services before their June MSP renewal.",
    "control_evidence": "Control (3/5) - Relationship is being rebuilt after a hiatus; we need to move fast to match their renewal timeline.",
    "client_follow_up_email": """Travis and UK,

Thanks again for the time today. Your framing of the \"fox guarding the hen house\" dynamic with your current MSP made the opportunity very clear — that separation of duties is exactly where Clearwater adds value.

We heard you on the scope: back-end Azure security, SOC, and ongoing ISO 27001 maintenance, cleanly separated from the MSP's day-to-day local IT support. The spreadsheet you're building on areas of responsibility is exactly the input we need to build a proper split model.

As discussed, our next steps are as follows:

- You'll send over the device list and the areas-of-responsibility spreadsheet
- Austin will revise the proposal with updated counts (endpoints, servers, users, Azure/cloud infrastructure, Fortigate firewalls)
- We'll reconnect the week of [next week date] to walk through the revised proposal before your June renewal discussions

We look forward to speaking with you again.

Best,
Austin""",
    "salesforce_block_1_dap": """2026-01-21 - Qualify - Problem validation [COMPLETED]
2026-01-28 - Scoping/Pricing - Revised proposal with updated counts [IN PROGRESS]
2026-02-04 - Approach Presentation [PLANNED]
2026-02-11 - Co-Create [PLANNED]
2026-02-18 - Go/No-Go [PLANNED]
2026-02-25 - Budget Approval [PLANNED]
2026-03-04 - MSA/SOW [PLANNED]
2026-03-11 - Redlines [PLANNED]
2026-03-18 - DocuSign [PLANNED]
2026-03-25 - Contract Execution [PLANNED]
2026-04-01 - Kickoff [PLANNED]

Current State: Velentium uses an existing MSP for full IT stack (L1 support, SOC, security compliance, ISO 27001). On-site MSP resource. Recently completed Azure migration. Fortigate firewalls. ISO 27001 certified.
Future State: Clearwater owns back-end security, SOC, compliance, ISO 27001 maintenance. MSP retains L1/L2 support and physical on-site services. Clean delineation via client's responsibility spreadsheet.
Risks: 2-3 competing vendors; incumbent MSP renewal pressure in June; relationship gap since Sandy left.
Next Step: Receive device list + responsibility spreadsheet from Travis/UK.""",
    "internal_message_pricing": """Hey Steve,

Had a discovery call with Velentium — new MSS opportunity. They want to bifurcate security services from their MSP. Clearwater would own: back-end Azure security, SOC, security compliance, ISO 27001 maintenance. MSP keeps: L1 support, on-site resource, physical/project work.

They're sending over a device list. Counts mentioned:
- Endpoints (exact count TBD — list incoming)
- Servers (TBD)
- Users (TBD)
- Cloud infrastructure: Azure
- Firewalls: Fortigate
- A few PCs being decommissioned (can exclude)

June renewal deadline with current MSP — we need to move fast. 2-3 vendors in play.

Please price out the bifurcated model (Clearwater owns SOC/compliance/ISO, MSP retains helpdesk) once we get the device list. Will forward it as soon as it arrives.""",
    "exec_recap_forwardable": """Austin, Richmond, and David K. engaged with Travis and UK at Velentium to discuss a Managed Security Services opportunity. Velentium, having completed an Azure migration and achieved ISO 27001 certification, is looking to bifurcate their IT operations — separating back-end security, SOC, and compliance work from their current MSP's day-to-day L1 support and physical services.

The client's framing was sharp: they want to make sure "the fox isn't guarding the hen house." They have an existing spreadsheet delineating areas of responsibility and are prepared to hand it to us as the scope document. June is the MSP renewal deadline; they're currently month-to-month. Two to three vendors are being considered.

Richmond noted the relationship gap since Sandy left (~1 year) and that Austin has done well getting up to speed. Next step is receipt of their device list and responsibility matrix, followed by a revised proposal from Austin the following week.""",
}

# ── Rubrics (pass/fail checks per artifact) ──────────────────────────────────
RUBRICS = {
    "pain_evidence": [
        ("Format: '[Dim] (X/5) - [Intensity]. [Summary]'", lambda t: bool(re.match(r'Pain \(\d/5\) - \w+\.', t))),
        ("Mentions 'fox' or conflict of interest", lambda t: "fox" in t.lower() or "conflict" in t.lower()),
        ("Score is 4/5", lambda t: "4/5" in t),
    ],
    "power_evidence": [
        ("Mentions Travis and UK", lambda t: "travis" in t.lower() and "uk" in t.lower()),
        ("Score is 4/5", lambda t: "4/5" in t),
    ],
    "vision_evidence": [
        ("Score is 5/5", lambda t: "5/5" in t),
        ("Mentions spreadsheet or table of responsibilities", lambda t: "spreadsheet" in t.lower() or "table" in t.lower() or "delineat" in t.lower()),
    ],
    "value_evidence": [
        ("Score is 4/5", lambda t: "4/5" in t),
        ("Mentions Azure or ISO", lambda t: "azure" in t.lower() or "iso" in t.lower()),
    ],
    "change_evidence": [
        ("Score is 5/5", lambda t: "5/5" in t),
        ("Mentions June renewal", lambda t: "june" in t.lower() or "renewal" in t.lower()),
    ],
    "control_evidence": [
        ("Score is 3/5", lambda t: "3/5" in t),
        ("Mentions rebuilding relationship or hiatus", lambda t: "hiatus" in t.lower() or "rebuilt" in t.lower() or "rebuild" in t.lower() or "sandy" in t.lower() or "gap" in t.lower()),
    ],
    "client_follow_up_email": [
        ("Starts with 'Travis and UK,' (not Richmond, not 'Hi')", lambda t: t.strip().startswith("Travis and UK")),
        ("No filler openers (no 'Thanks again for the productive')", lambda t: "productive call" not in t.lower()),
        ("No 'Hi' opener", lambda t: not t.strip().lower().startswith("hi")),
        ("Mentions 'fox' or specific call detail", lambda t: "fox" in t.lower() or "hen house" in t.lower() or "bifurcat" in t.lower()),
        ("Closes with 'We look forward to speaking with you again.'", lambda t: "we look forward to speaking with you again" in t.lower()),
        ("Closes with 'Best,\\nAustin'", lambda t: "best,\naustin" in t.lower() or "best,\r\naustin" in t.lower()),
        ("No subject line in body", lambda t: not t.strip().lower().startswith("subject:")),
        ("Mentions specific tech (Azure, Fortigate, ISO)", lambda t: any(x in t.lower() for x in ["azure", "fortigate", "iso 27001", "fortigate"])),
    ],
    "salesforce_block_1_dap": [
        ("No 2024 dates", lambda t: "2024" not in t),
        ("No 2025 dates", lambda t: "2025" not in t),
        ("First completed date is 2026-01-21 or similar 2026 date", lambda t: bool(re.search(r'2026-\d{2}-\d{2}.*COMPLETED', t))),
        ("Includes full path to close (MSA/SOW, DocuSign, Kickoff)", lambda t: "msa" in t.lower() and "docusign" in t.lower() and "kickoff" in t.lower()),
        ("Mentions June or renewal deadline", lambda t: "june" in t.lower() or "renewal" in t.lower()),
        ("Mentions Fortigate or Azure in current/future state", lambda t: "fortigate" in t.lower() or "azure" in t.lower()),
    ],
    "internal_message_pricing": [
        ("Addressed to Steve", lambda t: "steve" in t.lower()),
        ("Mentions specific tech: Azure", lambda t: "azure" in t.lower()),
        ("Mentions specific tech: Fortigate", lambda t: "fortigate" in t.lower()),
        ("Mentions June or renewal urgency", lambda t: "june" in t.lower() or "renewal" in t.lower()),
        ("Specific ask (not just 'provide pricing')", lambda t: "price out" in t.lower() or "pricing for" in t.lower() or "calculate" in t.lower() or "model" in t.lower()),
        ("Mentions bifurcated model or split", lambda t: "bifurcat" in t.lower() or "split" in t.lower()),
    ],
    "exec_recap_forwardable": [
        ("Names all Clearwater participants (Austin, Richmond)", lambda t: "austin" in t.lower() and "richmond" in t.lower()),
        ("Names all client participants (Travis, UK)", lambda t: "travis" in t.lower() and "uk" in t.lower()),
        ("Uses client's own language/quotes ('fox' or 'hen house')", lambda t: "fox" in t.lower() or "hen house" in t.lower()),
        ("No bullet points", lambda t: "- " not in t and "* " not in t),
        ("Mentions June renewal", lambda t: "june" in t.lower()),
        ("Mentions Sandy (relationship gap)", lambda t: "sandy" in t.lower()),
    ],
}

# ── Prompts (pulled from ECHOv4.json) ────────────────────────────────────────
def load_prompts():
    with open("/Users/austinhollsnd/Desktop/workflows/ECHOv4.json") as f:
        wf = json.load(f)
    prompts = {}
    for n in wf["nodes"]:
        if n["name"] == "Assessment Engine (Agent 1)":
            prompts["assessment"] = n["parameters"]["options"]["systemMessage"]
        if n["name"] == "Artifact Engine (Agent 2)":
            prompts["artifact"] = n["parameters"]["options"]["systemMessage"]
    return prompts

# ── Run Gemini ────────────────────────────────────────────────────────────────
def run_gemini(model_name, system_prompt, user_input, temperature=0):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_prompt,
        generation_config={"temperature": temperature, "response_mime_type": "application/json"},
    )
    resp = model.generate_content(user_input)
    return json.loads(resp.text)

# ── Score ─────────────────────────────────────────────────────────────────────
def score_artifact(key, generated_text):
    checks = RUBRICS.get(key, [])
    results = []
    for label, fn in checks:
        try:
            passed = fn(generated_text)
        except Exception:
            passed = False
        results.append((label, passed))
    return results

def print_score(key, generated, results, show_output=False, show_ideal=False):
    passed = sum(1 for _, p in results if p)
    total = len(results)
    icon = "✓" if passed == total else ("~" if passed >= total * 0.7 else "✗")
    print(f"\n{icon} {key.upper()} [{passed}/{total}]")
    for label, ok in results:
        print(f"   {'PASS' if ok else 'FAIL'} — {label}")
    if show_output:
        print(f"\n   --- GENERATED ---\n{generated}\n")
    if show_ideal and key in IDEALS:
        print(f"\n   --- IDEAL ---\n{IDEALS[key]}\n")

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--show-output", action="store_true")
    parser.add_argument("--show-ideal", action="store_true")
    parser.add_argument("--artifact", default=None, help="Only eval one artifact key")
    args = parser.parse_args()

    print("Loading prompts from ECHOv4.json...")
    prompts = load_prompts()

    # Step 1: Run Assessment Engine
    print("Running Assessment Engine (Gemini 2.0 Flash)...")
    assessment_input = json.dumps({
        "deal_slug": "velentium-2026-02-18",
        "input_type": "transcript",
        "date": DEAL_DATE,
        "account_name": "Velentium",
        "content": TRANSCRIPT,
        "_noDealsFound": True,
        "_contextSource": "new_opportunity",
    })
    # Strip n8n template expressions from system prompt for direct use
    assessment_system = re.sub(r'=\{.*?\}', '', prompts["assessment"])
    assessment_out = run_gemini(ASSESSMENT_MODEL, assessment_system, assessment_input, temperature=0)
    print(f"Assessment done. CAS: {assessment_out.get('cas_current','?')} | P2V2C2: {assessment_out.get('p2v2c2_total', sum(assessment_out.get('p2v2c2_scores',{}).get(k,{}).get('score',0) for k in ['pain','power','vision','value','change','control']))}")

    # Step 2: Run Artifact Engine
    print("Running Artifact Engine (Gemini 2.0 Flash Lite)...")
    artifact_system = prompts["artifact"]
    # Replace n8n expression for assessment context with actual data
    artifact_system = re.sub(
        r'\{\{\s*JSON\.stringify\(\$\([\'"]Assessment Engine \(Agent 1\)[\'"]\)\.item\.json.*?\)\s*\}\}',
        json.dumps(assessment_out, indent=2),
        artifact_system
    )
    artifact_out = run_gemini(ARTIFACT_MODEL, artifact_system, assessment_input, temperature=0.3)

    artifacts = artifact_out.get("artifacts", artifact_out)

    # Step 3: Score
    print("\n" + "="*60)
    print("ECHO EVAL REPORT — Velentium 2026-01-21")
    print("="*60)

    all_passed = all_total = 0
    keys_to_eval = [args.artifact] if args.artifact else list(RUBRICS.keys())

    for key in keys_to_eval:
        # Map artifact keys to evidence keys
        gen_key = key
        if key.endswith("_evidence"):
            dim = key.replace("_evidence", "")
            gen_key = f"salesforce_{dim}_description"

        generated = artifacts.get(gen_key) or artifacts.get(key) or ""
        results = score_artifact(key, generated)
        print_score(key, generated, results, args.show_output, args.show_ideal)
        all_passed += sum(1 for _, p in results if p)
        all_total += len(results)

    print("\n" + "="*60)
    pct = int(100 * all_passed / all_total) if all_total else 0
    print(f"TOTAL: {all_passed}/{all_total} checks passed ({pct}%)")
    if pct == 100:
        print("All checks passed — ready to push to n8n.")
    elif pct >= 70:
        print("Mostly passing — review FAILs above before pushing.")
    else:
        print("Significant failures — prompt needs work.")
    print("="*60)

if __name__ == "__main__":
    main()
