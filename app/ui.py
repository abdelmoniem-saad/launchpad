"""Streamlit founder console: brief form, engagement view per step, claims with sources, approval
inbox, gate screen, decision log and company blueprint.

Run: streamlit run app/ui.py   (Docker: http://localhost:8501)
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402
from langgraph.checkpoint.sqlite import SqliteSaver  # noqa: E402
from langgraph.types import Command  # noqa: E402

from app import approval, config, orchestrator  # noqa: E402
from app import decision_log as dl  # noqa: E402
from app.phases import PHASE_NAMES, STEPS  # noqa: E402

st.set_page_config(page_title="launchpad", layout="wide")
OUT = os.environ.get("OUTPUT_DIR", "outputs")


@st.cache_resource
def graph():
    path = Path(os.environ.get("STATE_DIR", "data")) / "engagements.sqlite"
    path.parent.mkdir(parents=True, exist_ok=True)
    return orchestrator.build(SqliteSaver(sqlite3.connect(path, check_same_thread=False)))


def cfg():
    return {"configurable": {"thread_id": st.session_state["thread"]}, "recursion_limit": 400}


def run(inp):
    with st.spinner("The firm is working on this step (local model; this can take a few minutes)..."):
        graph().invoke(inp, cfg())
    st.rerun()


def badge(live: bool) -> str:
    return ":green[LIVE]" if live else ":orange[MOCKED]"


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.title("launchpad")
    st.caption("An open-source AI consulting firm for founders. You approve every step.")
    st.write(f"Model: `{config.model_name()}`")
    st.markdown("**What is live and what is mocked**")
    for s in STEPS:
        st.markdown(f"{badge(s['live'])} {s['id']} {s['title']}")
    if "thread" in st.session_state and st.button("New engagement"):
        del st.session_state["thread"]
        st.rerun()

# ------------------------------------------------------------------ brief form
if "thread" not in st.session_state:
    st.header("Brief")
    with st.form("brief"):
        idea = st.text_area("Your idea (a digital product)")
        customer = st.text_input("Target customer")
        market = st.text_input("Market / region (optional)", placeholder="e.g. Egypt / MENA")
        c1, c2 = st.columns(2)
        budget = c1.number_input("Budget (USD)", min_value=0.0, value=0.0, step=50.0)
        hours = c2.number_input("Hours per week", min_value=0.0, value=0.0, step=1.0)
        skills = st.text_input("Your skills")
        values = st.text_input("Your values (optional)")
        out = st.text_input("Output folder", value=OUT)
        fast = st.checkbox("Fast mode (one department panel per step, fewer model calls)", value=True)
        if st.form_submit_button("Start engagement"):
            st.session_state["thread"] = uuid.uuid4().hex
            st.session_state["out"] = out
            run({"brief": {"idea": idea, "target_customer": customer, "market": market, "budget_usd": budget or None,
                           "hours_per_week": hours or None, "skills": skills, "values": values},
                 "run_dir": out, "fast_mode": fast})
    st.stop()

snap = graph().get_state(cfg())
state = snap.values
interrupts = [i.value for i in (snap.interrupts or [])]
tab_step, tab_inbox, tab_claims, tab_log, tab_blueprint = st.tabs(
    ["Engagement", "Approval inbox", "Claims ledger", "Decision log", "Company blueprint"])

# ------------------------------------------------------------------ engagement / checkpoint
with tab_step:
    if not interrupts:
        st.header(f"Engagement {state.get('status', '').upper()}")
        if state.get("stop_reason"):
            st.error(state["stop_reason"])
        for g in state.get("gate_history", []):
            st.write(f"Step {g['step']}: **{g['outcome'].upper()}** - {'; '.join(g['reasons'])}")
        if state.get("cost"):
            st.json(state["cost"])
    else:
        p = interrupts[0]
        if p["type"] == "brief_interview":
            st.header("A few questions before we start")
            with st.form("interview"):
                answers = {}
                for q in p["questions"]:
                    label = q["question"] + ("" if q["required"] else " (optional)")
                    if q.get("options"):
                        answers[q["field"]] = st.radio(label, q["options"], index=None, key="q_" + q["field"])
                    else:
                        answers[q["field"]] = st.text_input(label, key="q_" + q["field"])
                if st.form_submit_button("Continue"):
                    run(Command(resume=answers))
        elif p["type"] == "enter_results":
            st.header("Step 2.4: enter your demand-test result")
            t = p.get("threshold") or {}
            st.info(f"Locked target: **{t.get('target')} {t.get('metric')}** in {t.get('days')} days. "
                    "Enter the real number you got. The system never invents signups.")
            with st.form("results"):
                actual = st.text_input("Actual result (leave blank if the test has not run yet)")
                if st.form_submit_button("Submit result"):
                    run(Command(resume={"actual": actual}))
        else:
            step = next(s for s in STEPS if s["id"] == p["step"])
            st.header(f"Phase {step['phase']} {PHASE_NAMES[step['phase']]} - step {p['step']}: {p['title']}")
            st.markdown(badge(p.get("live")))
            rep = p.get("report") or {}
            st.subheader("Conclusion")
            st.write(rep.get("conclusion", ""))
            for kp in rep.get("key_points", []):
                ids = ", ".join(kp.get("claim_ids") or [])
                st.markdown(f"- {kp.get('text')} `{kp.get('label')}`{' ' + ids if ids else ''}")
            if rep.get("recommendation"):
                st.markdown(f"**Strategy architect recommends: {rep['recommendation'].upper()}** - {rep.get('rationale', '')}")
            for d in rep.get("open_disagreements", []):
                st.warning(d)
            if p.get("departments"):
                st.subheader("Departments")
                st.table([{"department": k, **{x: v.get(x, "") for x in ("position", "pushback", "tradeoff")}}
                          for k, v in p["departments"].items()])
            if p.get("quant"):
                with st.expander("Calculator results"):
                    st.json(p["quant"])
            with st.expander("Full work"):
                st.json(p.get("work") or {})
            for f in p.get("flags") or []:
                st.warning(f)
            if p.get("pending_actions"):
                st.info("This step proposed actions. Review them in the Approval inbox tab (MOCKED: nothing is really sent or posted).")
            target = None
            if p.get("proposed_threshold"):
                t = p["proposed_threshold"]
                st.subheader("Lock the demand threshold before any results exist")
                st.caption(t.get("basis", ""))
                target = st.number_input(f"Target {t['metric']} in {t['days']} days", min_value=1, value=max(1, int(t["target"])))
            st.subheader("Your decision")
            feedback = st.text_area("Feedback (for redo) or your edited conclusion (for edit)")
            c1, c2, c3, c4 = st.columns(4)
            extra = {"threshold_target": target} if target else {}
            if c1.button("Approve" + (" and lock threshold" if target else ""), type="primary"):
                run(Command(resume={"decision": "approve", **extra}))
            if c2.button("Edit"):
                run(Command(resume={"decision": "edit", "edited_conclusion": feedback, **extra}))
            if c3.button("Redo with feedback"):
                run(Command(resume={"decision": "redo", "feedback": feedback}))
            if c4.button("Stop"):
                run(Command(resume={"decision": "stop"}))

# ------------------------------------------------------------------ approval inbox
with tab_inbox:
    st.header("Approval inbox")
    st.caption("Agents can only propose. Approving creates a one-time token here, in the UI, and the MOCKED action runs once.")
    run_dir = state.get("run_dir", st.session_state.get("out", OUT))
    for a in approval.list_actions(run_dir):
        with st.container(border=True):
            st.markdown(f"**{a['type'].upper()}** ({a['id']}, step {a['step']}) - {a['reason']} - status `{a['status']}` :orange[MOCKED]")
            st.code(json.dumps(a["payload"].get("draft"), indent=2, ensure_ascii=False)[:2000])
            if a["status"] == "pending":
                c1, c2 = st.columns(2)
                if c1.button("Approve", key="ap" + a["id"]):
                    token = approval.founder_approve(a["id"])
                    st.success(f"Executed (MOCKED): {approval.execute(a['id'], token)}")
                if c2.button("Reject", key="rj" + a["id"]):
                    approval.founder_reject(a["id"])
                    st.rerun()

# ------------------------------------------------------------------ claims, log, blueprint
with tab_claims:
    st.header("Claims ledger")
    st.dataframe([{k: c.get(k) for k in ("id", "step", "type", "text", "source_url")} for c in state.get("claims", [])],
                 use_container_width=True)
with tab_log:
    st.header("Decision log")
    st.dataframe(dl.entries()[-200:][::-1], use_container_width=True)
with tab_blueprint:
    st.header("Company blueprint (step 2.5)")
    if state.get("blueprint"):
        st.json(state["blueprint"])
    else:
        st.write("Not reached yet.")
