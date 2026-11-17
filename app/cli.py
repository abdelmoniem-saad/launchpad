"""Command-line founder console (same graph as the Streamlit UI).

  python -m app.cli --brief briefs/<name>.json [--out outputs] [--fresh-log] [--full]

At every checkpoint the founder types approve / edit / redo / stop. Proposed actions are listed
and only run (MOCKED) when the founder types `approve` for that action here.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from pathlib import Path

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from app import approval, orchestrator
from app import decision_log as dl


def ask(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


def show_checkpoint(p: dict) -> None:
    print("\n" + "=" * 72)
    print(f"STEP {p['step']} {'(LIVE)' if p.get('live') else '(MOCKED)'}: {p['title']}")
    print("-" * 72)
    rep = p.get("report") or {}
    print("CONCLUSION:", rep.get("conclusion", ""))
    for kp in rep.get("key_points", []):
        print(f"  - {kp.get('text', '')} [{kp.get('label')}{': ' + ', '.join(kp.get('claim_ids') or []) if kp.get('claim_ids') else ''}]")
    if rep.get("recommendation"):
        print(f"Architect recommends: {rep['recommendation'].upper()} - {rep.get('rationale', '')}")
    for d, pos in (p.get("departments") or {}).items():
        if pos.get("pushback"):
            print(f"  dept.{d} pushback: {pos['pushback']}")
    for f in p.get("flags") or []:
        print(f"  FLAG: {f}")
    if p.get("proposed_threshold"):
        t = p["proposed_threshold"]
        print(f"Proposed demand threshold: {t['target']} {t['metric']} in {t['days']} days ({t['basis']})")
    print(f"Full report: {p.get('file')}")


def handle_actions(run_dir: str) -> None:
    for a in approval.list_actions(run_dir, "pending"):
        draft = json.dumps(a["payload"].get("draft"), ensure_ascii=False)[:600]
        print(f"\nACTION {a['id']} ({a['type']}, MOCKED): {a['reason']}\n  {draft}")
        if ask("  Type 'approve' to run it (MOCKED), anything else rejects: ").lower() == "approve":
            token = approval.founder_approve(a["id"])  # token stays in this process, never reaches a model
            print("  ->", approval.execute(a["id"], token))
        else:
            approval.founder_reject(a["id"])


def answer(payload: dict, run_dir: str) -> dict:
    kind = payload.get("type")
    if kind == "brief_interview":
        print("\n" + payload["question"])
        return {f: ask(f"  {f}: ") for f in payload["missing"]}
    if kind == "enter_results":
        print("\n" + payload["question"])
        return {"actual": ask("  actual: ")}
    show_checkpoint(payload)
    handle_actions(run_dir)
    while True:
        d = ask("\nDecision [approve / edit / redo / stop]: ").lower()
        if d in orchestrator.DECISIONS:
            break
    resp = {"decision": d}
    if d == "edit":
        resp["edited_conclusion"] = ask("New conclusion: ")
    if d == "redo":
        resp["feedback"] = ask("Feedback for the redo: ")
    if d in ("approve", "edit") and payload.get("proposed_threshold"):
        t = ask(f"Lock threshold target (Enter keeps {payload['proposed_threshold']['target']}): ")
        if t:
            resp["threshold_target"] = t
    return resp


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--brief", required=True)
    ap.add_argument("--out", default=os.environ.get("OUTPUT_DIR", "outputs"))
    ap.add_argument("--fresh-log", action="store_true")
    ap.add_argument("--full", action="store_true", help="full mode: parallel department reviews + negotiation")
    args = ap.parse_args(argv)
    if args.fresh_log:
        dl.reset()
    brief = json.loads(Path(args.brief).read_text("utf-8"))
    graph = orchestrator.build(InMemorySaver())
    cfg = {"configurable": {"thread_id": uuid.uuid4().hex}, "recursion_limit": 400}
    result = graph.invoke({"brief": brief, "run_dir": args.out, "fast_mode": not args.full}, cfg)
    while result.get("__interrupt__"):
        payload = result["__interrupt__"][0].value
        result = graph.invoke(Command(resume=answer(payload, args.out)), cfg)
    print("\nENGAGEMENT", result.get("status", "").upper(), "-", result.get("stop_reason", ""))
    print(json.dumps(result.get("cost", {}), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
