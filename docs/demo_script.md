# Demo script (3 minutes)

The point to land: launchpad is a consulting firm that keeps the founder in charge and tells the truth, including "don't launch this".

## Before you start
- Ollama running with the model already pulled; `streamlit run app/ui.py` (or `docker compose up`) open at http://localhost:8501.
- A second browser tab with the committed demo outputs open: `outputs/phase1_gate_evidence.md`, the weak-brief files (`*_weak.md`), `payment_test_log.md` and `decision_log.json`.
- On a CPU-only laptop one step takes minutes, so the live run shows the start and the committed run shows the rest. Say so.

## 0:00-0:20 The problem and the promise
"Founders get confident-sounding AI advice with no sources and no brakes. launchpad is an open-source consulting firm: six firm agents plus the client's own departments, every claim sourced or labelled ASSUMPTION, and the founder approves every step. Free: a local open-weight model, $0 per run."

## 0:20-1:00 Live: a new brief
1. Paste the brief you were given into the form and press **Start engagement**.
2. The engagement manager asks follow-up questions (product format, audience, a 90-day learning goal). Answer them.
3. If the brief is an excluded product (crypto, health or legal advice, physical goods), it stops right here with the reason. That is a feature: show it.
4. Otherwise step 1.1 starts researching. Leave it running and switch tabs.

## 1:00-2:15 The committed run: what a full engagement looks like
1. **Step file** (`phase1_step1_idea_and_industry.md`): conclusion first, niches scored by the calculator (the model never does the maths), the departments' pushback, the claims ledger with URLs or ASSUMPTION.
2. **Evidence gate** (`phase1_gate_evidence.md`): the go / pivot / stop rule, decided in code.
3. **Demand test (2.2)**: the founder locks the waitlist target before any results exist; it cannot be changed afterwards.
4. **Approval inbox**: agents can only propose (publish, send, hire). Approving creates a one-time token in the UI, and the action is only written to `outputs/` as MOCKED.
5. **STOP cases**: the strong brief pauses at the demand gate (`phase2_gate_final_recommendation.md`) because no real waitlist result exists yet, and the system will not invent one; the weak brief (`*_weak.md`) pivots once at the evidence gate before reaching the same STOP; the crypto brief (`*_excluded.md`) is refused at intake.

## 2:15-2:45 Back to the live run
Show the first checkpoint if it has arrived: approve / edit / redo with feedback / stop.

## 2:45-3:00 Close
"Apache-2.0, `docker compose up`, no keys, $0 per run. Phases 1-2 and the pricing step are live; the other steps of 3-6 are labelled MOCKED; payments run only against a MOCKED provider, and refunds need the founder. It will never promise income, fake reviews or urgency, or act without the founder."
