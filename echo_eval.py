#!/usr/bin/env python3
"""
ECHO Eval Script — LLM-as-Judge edition
Runs prompts directly against Gemini and scores outputs vs. Austin's ideal outputs.
Bypasses n8n entirely — ~15 second feedback loop for prompt iteration.

Usage:
  python3 echo_eval.py                    # run eval, scores + inline diff for failures
  python3 echo_eval.py --all              # show inline diff for ALL artifacts (pass + fail)
  python3 echo_eval.py --suggest          # also suggest prompt edits for low-scoring artifacts
  python3 echo_eval.py --artifact email   # eval only one artifact key
"""

import json
import re
import argparse
import google.generativeai as genai

# ── Config ───────────────────────────────────────────────────────────────────
import os, pathlib
_env = pathlib.Path("/Users/austinhollsnd/Desktop/workflows/.env")
if _env.exists():
    for _line in _env.read_text().splitlines():
        if "=" in _line and not _line.startswith("#"):
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())
GEMINI_API_KEY   = os.environ["GEMINI_API_KEY"]
ASSESSMENT_MODEL = "gemini-2.0-flash"
ARTIFACT_MODEL   = "gemini-2.0-flash-lite"
JUDGE_MODEL      = "gemini-2.0-flash"
DEAL_DATE        = "2026-01-21"
IDEALS_FILE      = "/Users/austinhollsnd/Desktop/workflows/velentium_ideals.json"
WORKFLOW_FILE    = "/Users/austinhollsnd/Desktop/workflows/ECHOv4.json"

# ── Transcript ────────────────────────────────────────────────────────────────
TRANSCRIPT = """See below transcript for the Velentium call. MSS deal that Sandy (who I replaced on the PPM team) started on and they went another direction, but came back. This is the first call for this new opportunity. "Hey. Good afternoon. How are you?  Oh, it's UK in the background. What's up, you gay? How are you, man?  I am In person live. We all in H town? Yep.  Yep. We finally got the UK to make the trip down here. And he brought a bunch of bad weather wind.  I mean, it's funny. It's funny we've been on, you know, our life is on these calls and these meetings. And whenever we're talking to the Southeast, everybody's talking about the weather that's coming.  And then when we talk to like Chicago in New York, they're like, oh, that's so cute of you guys to be worried about this. about like a couple of inches of snow. But such is it, that Listen, it's like I'm in Atlanta and, you know, we, my wife woke up this morning. It was like, are you concerned?  I'm like, I mean, they like, make you think that the sky is following. But you guys know it. I grew up in Houston, and like, like everybody loves to talk about hurricanes.  As soon as there's one in the Caribbean, like, everybody's, like, tracking on what's's really good website. There's those guys, that do the storm tracking, Space City. Do you ever, you ever look at their emails?  They actually do really good work on hurricane tracking and stuff like that. They're based out of Houston. Next time hurricane comes, I'll go take a look at it.  I'll drop you their link. I'll drop you the website. All right...  Well, I don't even know if or at Richmond is Adam joining or should we just. Yeah, I't. Yeah, I didn't think so ever.  I think Adam honestly just suggested us to reconnect with you guys and, you know, I'll let you've met Richmond, right or wrong? Have you not? I think just over email.  So it's nice to meet you guys. I'm, um. I'm on David's team.  I've fused on private equity strategy, so I've been working a lot with Adam. I joined about a year ago. So a lot of yearall's conversations were already kind of in flight at that point.  But yes, over the last gosh, probably six months in earnest, I've been working more so with Adam and kind of more so across the portfolio. So it's good to connect recall. I know we exchanged some emails throughout the year as well, but nice to meet you all. wise you too, yeah.  In Austin, you can do an intro. Yeah, and my name's Austin Holland. I work on the PPM team alongside David and Richmond. and I joined seven months ago.  So, I think you guys have been in touch with Sandy before on some occasions. So I'm kind of stepping in for Sandy now. So, yeah, good, good to talk to you guys and look forward to getting up to speed.  Yeah, so, I mean, we were just tracking you ads to migration projects that were going on and I think Adam suggested us check in and, you know, if that's really all this is, how can we be helpful? Where do things stand, you know, specifically man security services, but we can also zoom out and take a broader perspective on kind of what's on your compliance, what's on your cybersecurity roadmap. And is there anything that we need to talk through or think through with you or can be of support to you?  So throwing spaghetti on the wall here, where we're at is, we feel things are pretty stable from just the security environment, if you will. We have our MSP, obviously, in place. Things are going reasonably well there.  However, I think there's an opportunity here where we sort of bifurcate and make sure that the fox isn't gardening a hen house. Yep. And I think it would be nice to explore options there.  The current MSP, like most MSPs are really good at level one support. And we actually have a person on site, which has been good for our company. This is one of the reasons we went to this MSP a couple of years ago is that we were able to arrange for a solution where we have a person on site.  And so that's been good for us as an organization. And things seem fairly stable. Also, last year, we got our together with this MSP and a contractor that they secured, we got our ISO 27001 certification.  We need to keep that maintained, obviously, going forward. And so I think for us, there's an opportunity to explore on one level, hey, what services can we split off this current arrangement that we have? Recognizing their core competency is going to the level one support and some of the level two or more project-based activities that we're handling, like, you know, they're doing the installation of a new dedicated internet circuit and redoing the Wi-Fi points.  I mean, these are all things that they're doing here being local, conveniently physical access is really good. I think that's where they're going to have the leg up, if you will. But things that back in, SOC, security compliance, ISO ongoing ISO 27001 compliance.  Those are things that they don't need to be physical here for. So I think we, there's an opportunity to explore where can we put that over to Clearwater and you take on that responsibility. And they continue to do the day-to-day hands on keyboard local IT support. So that's kind of where our head is. And we want to make sure we get a proposal and see what the pricing looks like for that. And then we're going to talk to you guys and probably one or two other vendors about this and see if we can make something work, going into our renewal discussions with our current MSP. Travis: also, also what we wanted was to have the scoping on the security services to make sure we cover everything. And so to your point, when we went through the ISO 27001, we had a contractor they kind of subcontracted to come in and do the assessment. So what we want to make sure is that when we split this off, we cover everything and we have a clean line. So there's no ambiguity about what Clearwater is responsible for and what the existing MSP is responsible for. Travis: we actually have kind of a spreadsheet or a table that we've started to build that delineates what we're thinking, the areas of responsibility. Austin: and that's perfect. Yeah, that's exactly, that's the kind of output we're going to need to do our work. UK: perfect. So going into our renewal discussions, I want to be able to hand something to Clearwater, this is the scope, this is what we want you to be responsible for. And then the remaining items stay with the MSP. Richmond: so when do those renewal discussions happen with the MSP? Travis: June. June of this year. So we'll actually we should have renewed already. We've been in a month to month right now. Richmond: oh, wow, okay. And just as background, just out of curiosity, is there a different MSP you're talking to in addition to Clearwater, or just Clearwater at this point? Travis: two or three potentially UK:  probably two or three. So what counts does Clearwater need to be able to scope this? Austin: we need device counts. Users, servers, endpoints. And then for a split, we've been building these split models where we detail, here's what Clearwater is going to own, here's what stays with the client, here's what we can work together on. UK: there's also some cloud infrastructure too. Azure? Travis: yes. UK: and then Fortigate. Travis: Fortigate firewalls. And we also have a couple of PCs that we're going to be decommissioning. Yeah, we can send you guys a, we can send you over the device list along with the spreadsheet on the areas of responsibility. Austin: great. So just so we have a realistic view, I probably won't be able to get back to you guys until after my trip tomorrow. I have a flight tomorrow morning. I'll try to review it this week when I can. And then sometime next week, I'd like to get back to you guys with sort of a revised proposal based on those updated counts. Richmond: Travis, UK, it's great to reconnect. I don't think we've spoken in a while. I don't think we've spoken since Sandy. Austin: I think Sandy left about a year ago. Richmond: yeah, so it's been a while.  But Austin's done a great job getting up to speed. I think what I took away is you really understand your situation. And it actually makes our job very easy. And just again, this is Austin's deal, but I just wanted to be here for the first call. And there's good energy around this. This can come together very quickly if you want it to. Travis: UK tell them a little bit about what's on the horizon from a business perspective. UK: yeah, we're growing a bit. We've had an acquisition that came through recently. We're also involved in some real estate development. We're diversifying a little bit. Travis: so yeah that's kind of a broad overview. And then on the IT security front, we're kind of continuing to add some new employees as things grow. So it's an active environment right now for us."
"""

# ── Artifact key → generated output key mapping ──────────────────────────────
ARTIFACT_KEY_MAP = {
    "pain_evidence":            "salesforce_pain_description",
    "power_evidence":           "salesforce_power_description",
    "vision_evidence":          "salesforce_vision_description",
    "value_evidence":           "salesforce_value_description",
    "change_evidence":          "salesforce_change_description",
    "control_evidence":         "salesforce_control_description",
    "client_follow_up_email":   "client_follow_up_email",
    "salesforce_block_1_dap":   "salesforce_block_1_dap",
    "internal_message_pricing": "internal_message_pricing",
    "exec_recap_forwardable":   "exec_recap_forwardable",
}

# ── Load ideals ───────────────────────────────────────────────────────────────
def load_ideals():
    with open(IDEALS_FILE) as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith("_")}

# ── Load prompts ──────────────────────────────────────────────────────────────
def load_prompts():
    with open(WORKFLOW_FILE) as f:
        wf = json.load(f)
    prompts = {}
    for n in wf["nodes"]:
        if n["name"] == "Assessment Engine (Agent 1)":
            prompts["assessment"] = n["parameters"]["options"]["systemMessage"]
        if n["name"] == "Artifact Engine (Agent 2)":
            prompts["artifact"] = n["parameters"]["options"]["systemMessage"]
    return prompts

# ── Run Gemini ────────────────────────────────────────────────────────────────
def run_gemini(model_name, system_prompt, user_input, temperature=0, json_mode=True):
    genai.configure(api_key=GEMINI_API_KEY)
    config = {"temperature": temperature}
    if json_mode:
        config["response_mime_type"] = "application/json"
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_prompt,
        generation_config=config,
    )
    resp = model.generate_content(user_input)
    if json_mode:
        return json.loads(resp.text)
    return resp.text

# ── LLM Judge ─────────────────────────────────────────────────────────────────
JUDGE_SYSTEM = """You are an expert sales operations judge evaluating AI-generated sales artifacts.

You will be given:
1. An artifact key (what type of artifact this is)
2. The generated output from the AI
3. The ideal/gold-standard output written by the human

Score the generated output from 1-5 against the ideal:
5 = Matches ideal in substance, tone, format, and specificity. No meaningful gaps.
4 = Very close. Minor differences in wording or one small detail missing.
3 = Captures the main idea but misses important specifics, format issues, or tone problems.
2 = Partially correct but missing key content or has significant format/tone problems.
1 = Substantially wrong, missing core content, or fundamentally different from ideal.

Return JSON: {"score": <1-5>, "reasoning": "<1-2 sentences explaining the score and what specifically is missing or wrong>"}

Be strict. A 5 means it could replace the ideal with no edits. A 4 means you'd make one small tweak."""

def judge_artifact(key, generated, ideal):
    result = run_gemini(JUDGE_MODEL, JUDGE_SYSTEM, json.dumps({
        "artifact_key": key,
        "generated": generated,
        "ideal": ideal,
    }), temperature=0)
    return result.get("score", 0), result.get("reasoning", "")

# ── Prompt Suggestion ─────────────────────────────────────────────────────────
SUGGEST_SYSTEM = """You are an expert prompt engineer for AI sales automation.

You will be given:
1. An artifact key (what type of artifact)
2. The current prompt used to generate it
3. The generated output (what the AI produced)
4. The ideal output (what it should have produced)
5. The judge's reasoning for the low score

Suggest a SPECIFIC, CONCRETE change to the prompt that would fix the gap.
Focus on the single most impactful change. Be precise — quote exact text to add/change/move in the prompt.

Return JSON: {"suggestion": "<specific prompt edit>"}"""

def suggest_prompt_edit(key, prompt_excerpt, generated, ideal, reasoning):
    result = run_gemini(JUDGE_MODEL, SUGGEST_SYSTEM, json.dumps({
        "artifact_key": key,
        "prompt_excerpt": prompt_excerpt[:2000],
        "generated": generated,
        "ideal": ideal,
        "judge_reasoning": reasoning,
    }), temperature=0.3)
    return result.get("suggestion", "No suggestion generated.")

# ── Print inline diff ─────────────────────────────────────────────────────────
def print_inline_diff(key, score, reasoning, generated, ideal):
    icon = "✓" if score >= 4 else ("~" if score == 3 else "✗")
    print(f"\n{icon} {key.upper()} — {score}/5")
    print(f"   {reasoning}")
    # Truncate long fields to keep terminal readable
    max_chars = 600
    gen_display  = generated[:max_chars] + ("..." if len(generated) > max_chars else "")
    ideal_display = ideal[:max_chars]    + ("..." if len(ideal) > max_chars else "")
    print(f"\n   GENERATED:\n{_indent(gen_display)}")
    print(f"\n   IDEAL:\n{_indent(ideal_display)}")

def _indent(text, prefix="   "):
    return "\n".join(prefix + line for line in text.splitlines())

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all",      action="store_true", help="Show inline diff for all artifacts (not just failures)")
    parser.add_argument("--suggest",  action="store_true", help="Suggest prompt edits for low-scoring artifacts")
    parser.add_argument("--artifact", default=None,        help="Only eval one artifact key")
    args = parser.parse_args()

    print("Loading ideals and prompts...")
    ideals  = load_ideals()
    prompts = load_prompts()

    # Step 1: Assessment Engine
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
    assessment_system = re.sub(r'=\{.*?\}', '', prompts["assessment"])
    assessment_out    = run_gemini(ASSESSMENT_MODEL, assessment_system, assessment_input, temperature=0)
    p2v2c2_total = sum(
        assessment_out.get("p2v2c2_scores", {}).get(k, {}).get("score", 0)
        for k in ["pain", "power", "vision", "value", "change", "control"]
    )
    print(f"Assessment done. CAS: {assessment_out.get('cas_current','?')} | P2V2C2 total: {p2v2c2_total}")

    # Step 2: Artifact Engine
    print("Running Artifact Engine (Gemini 2.0 Flash Lite)...")
    artifact_system = re.sub(
        r'\{\{\s*JSON\.stringify\(\$\([\'"]Assessment Engine \(Agent 1\)[\'"]\)\.item\.json.*?\)\s*\}\}',
        json.dumps(assessment_out, indent=2),
        prompts["artifact"],
    )
    artifact_out = run_gemini(ARTIFACT_MODEL, artifact_system, assessment_input, temperature=0.3)
    artifacts    = artifact_out.get("artifacts", artifact_out)

    # Step 3: Judge each artifact
    print("\n" + "=" * 60)
    print("ECHO EVAL REPORT — Velentium 2026-01-21")
    print("=" * 60)

    keys_to_eval = [args.artifact] if args.artifact else list(ARTIFACT_KEY_MAP.keys())
    scores     = {}
    reasonings = {}
    generateds = {}

    for key in keys_to_eval:
        gen_key   = ARTIFACT_KEY_MAP.get(key, key)
        generated = artifacts.get(gen_key) or artifacts.get(key) or ""
        ideal     = ideals.get(key, "")
        generateds[key] = generated

        if not ideal:
            print(f"\n? {key.upper()} — no ideal defined, skipping")
            continue
        if not generated:
            print(f"\n✗ {key.upper()} — no output generated")
            scores[key]     = 0
            reasonings[key] = "No output was generated."
            continue

        score, reasoning  = judge_artifact(key, generated, ideal)
        scores[key]       = score
        reasonings[key]   = reasoning

        # Always show score + reasoning
        # Show inline diff for failures, or all if --all
        if args.all or score < 4:
            print_inline_diff(key, score, reasoning, generated, ideal)
        else:
            icon = "✓"
            print(f"\n{icon} {key.upper()} — {score}/5")
            print(f"   {reasoning}")

    # Step 4: Summary
    print("\n" + "=" * 60)
    scored_keys = [k for k in keys_to_eval if k in scores]
    if scored_keys:
        avg     = sum(scores[k] for k in scored_keys) / len(scored_keys)
        failing = [k for k in scored_keys if scores[k] < 4]
        print(f"AVERAGE SCORE: {avg:.1f}/5.0  ({len(scored_keys)} artifacts judged)")
        if failing:
            print(f"BELOW 4/5:     {', '.join(failing)}")
        else:
            print("All artifacts scored 4/5 or higher.")
    print("=" * 60)

    # Step 5: Prompt suggestions
    if args.suggest and scored_keys:
        failing = [k for k in scored_keys if scores[k] < 4]
        if not failing:
            print("\nNo failing artifacts — nothing to suggest.")
        else:
            print(f"\nPROMPT SUGGESTIONS")
            print("=" * 60)
            evidence_keys = {k for k in failing if k.endswith("_evidence")}
            for key in failing:
                prompt_src = prompts["assessment"] if key in evidence_keys else prompts["artifact"]
                suggestion = suggest_prompt_edit(
                    key, prompt_src,
                    generateds.get(key, ""),
                    ideals.get(key, ""),
                    reasonings.get(key, ""),
                )
                print(f"\n[{key.upper()}] score: {scores[key]}/5")
                print(f"  {suggestion}")
            print("=" * 60)

if __name__ == "__main__":
    main()
