"""Founder approval. Nothing is published, sent, spent or signed without an explicit approve.

Every outbound action goes through `require_approval`. Without a founder "approve",
it raises `ApprovalRejected` and the action does not happen. Non-interactive runs
(no TTY) reject by default.
"""
from __future__ import annotations

import sys
from typing import Callable

Approver = Callable[[str, str], bool]


class ApprovalRejected(Exception):
    pass


def cli_approver(action: str, summary: str) -> bool:
    if not sys.stdin or not sys.stdin.isatty():
        print(f"[approval] no interactive founder available; rejecting '{action}'.")
        return False
    print("\n" + "=" * 60)
    print(f"FOUNDER APPROVAL NEEDED: {action}")
    print("-" * 60)
    print(summary)
    print("=" * 60)
    answer = input("Type 'approve' to continue, anything else rejects: ").strip().lower()
    return answer == "approve"


def reject_all(action: str, summary: str) -> bool:
    return False


def require_approval(action: str, summary: str, approver: Approver, log, agent: str = "approval") -> str:
    """Ask the founder. Returns "founder" on approve; raises ApprovalRejected otherwise."""
    approved = bool(approver(action, summary))
    log.append(agent, f"founder_{'approve' if approved else 'reject'}:{action}",
               approved_by="founder" if approved else None,
               outcome="approved" if approved else "rejected")
    if not approved:
        raise ApprovalRejected(action)
    return "founder"
