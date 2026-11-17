"""Action gateway: the only way anything is published, sent, spent, signed, hired or contacted.

Agents can only *propose* an ActionProposal {type, payload, reason}; it is stored as `pending`.
It executes only with a one-time token that is created when the founder clicks Approve in the UI
(or types `approve` in the CLI). The token is created and consumed in UI code and never passes
through a model, so no prompt can trigger an action. Execution is MOCKED: the approved draft is
written to outputs/ with a MOCKED label; nothing is actually posted, sent, charged or contacted.
"""
from __future__ import annotations

import json
import os
import secrets
import sqlite3
import uuid
from pathlib import Path

from app import decision_log as dl

ACTION_TYPES = ("publish", "send", "spend", "sign", "hire", "contact", "refund")


class ApprovalRequired(Exception):
    pass


def _db() -> sqlite3.Connection:
    path = Path(os.environ.get("STATE_DIR", "data")) / "actions.sqlite"
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute("""CREATE TABLE IF NOT EXISTS actions (id TEXT PRIMARY KEY, run_dir TEXT, step TEXT,
                   type TEXT, payload TEXT, reason TEXT, status TEXT, token TEXT)""")
    return con


def propose(run_dir: str, step: str, type_: str, payload: dict, reason: str, agent: str) -> str:
    if type_ not in ACTION_TYPES:
        raise ValueError(f"unknown action type {type_}")
    aid = f"act_{uuid.uuid4().hex[:8]}"
    with _db() as con:
        con.execute("INSERT INTO actions VALUES (?,?,?,?,?,?,?,NULL)",
                    (aid, run_dir, step, type_, json.dumps(payload, ensure_ascii=False), reason, "pending"))
    dl.log(agent, f"propose_action {type_} ({aid}) step {step}: pending founder approval")
    return aid


def list_actions(run_dir: str | None = None, status: str | None = None) -> list[dict]:
    q, args = "SELECT id, run_dir, step, type, payload, reason, status FROM actions WHERE 1=1", []
    if run_dir:
        q += " AND run_dir=?"
        args.append(run_dir)
    if status:
        q += " AND status=?"
        args.append(status)
    with _db() as con:
        rows = con.execute(q, args).fetchall()
    keys = ("id", "run_dir", "step", "type", "payload", "reason", "status")
    return [{**dict(zip(keys, r)), "payload": json.loads(r[4])} for r in rows]


def founder_approve(action_id: str) -> str:
    """Called only from UI/CLI code when the founder approves. Returns a one-time token."""
    token = secrets.token_urlsafe(16)
    with _db() as con:
        con.execute("UPDATE actions SET token=?, status='approved' WHERE id=? AND status='pending'",
                    (token, action_id))
    return token


def founder_reject(action_id: str) -> None:
    with _db() as con:
        con.execute("UPDATE actions SET status='rejected', token=NULL WHERE id=? AND status='pending'", (action_id,))
    dl.log("governance.action_gateway", f"founder_reject {action_id}: not executed")


def execute(action_id: str, token: str | None) -> Path:
    """Run an approved action exactly once (MOCKED). Raises ApprovalRequired without a valid token."""
    with _db() as con:
        row = con.execute("SELECT run_dir, step, type, payload, status, token FROM actions WHERE id=?",
                          (action_id,)).fetchone()
        if not row or row[4] != "approved" or not token or not secrets.compare_digest(row[5] or "", token):
            dl.log("governance.action_gateway", f"blocked_execute {action_id}: no valid founder token")
            raise ApprovalRequired(action_id)
        con.execute("UPDATE actions SET status='executed', token=NULL WHERE id=?", (action_id,))
    run_dir, step, type_, payload = row[0], row[1], row[2], json.loads(row[3])
    phase, num = step.split(".")
    out = Path(run_dir) / f"phase{phase}_step{num}_action_{type_}_{action_id}_MOCKED.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(f"**{k}:** {v}" if not isinstance(v, (dict, list)) else f"**{k}:**\n```json\n{json.dumps(v, indent=2, ensure_ascii=False)}\n```"
                     for k, v in payload.items())
    out.write_text(f"# MOCKED {type_} action {action_id} (step {step})\n\n"
                   f"Founder approved. MOCKED: nothing was actually {type_}ed or contacted; this file is the record.\n\n{body}\n",
                   "utf-8")
    dl.log("governance.action_gateway", f"execute_mocked {type_} {action_id}", approved_by="founder", mocked=True)
    return out
