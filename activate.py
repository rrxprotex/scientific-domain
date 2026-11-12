#!/usr/bin/env python3
"""Deterministic activation gate for the scientific-domain skill.

Given a task/prompt, decide ACTIVATE / SKIP / ABSTAIN and nominate a domain.
This is a HEURISTIC NOMINATION, never a verdict about the task. In hook mode it
is completely silent unless it fires, so it costs nothing on ordinary prompts.

Pure stdlib, no network, no API key. Works in any harness: Claude Code hooks,
OpenCode, WorkBuddy, or a plain shell.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("domain", HERE / "domain.py")
domain = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(domain)

POSITIVE = [
    r"\b(analy[sz]e|analy[sz]is|examin|research|study|investigat|literature|theor|concept|terminolog|evidence|claim|hypothes|scientific|classif|relate|connect|cite|ground|audit notes|review notes)\b",
    r"\b(why does|how does|what is known about|which theory|what term|compare theories)\b",
    r"analiz|incele|araştır|teori|kuram|kavram|terim|kanıt|iddia|hipotez|mekanizma|ilişkilendir|literatür|bilimsel|sınıflandır|karşılaştır|kaynak|bilgi çıkar|nasıl çalışır",
    # es / pt / it / fr
    r"anal[iy]s|examin|investig|recherch|te[oó]r|th[eé]or|hip[oó]tes|hypoth[eè]s|concept|terminol|[ée]videnc|literat|clasifi|clasif|compar|relacion|revendic",
    # de
    r"analys|untersuch|forsch|theori|konzept|terminolog|evidenz|hypothese|behaupt|klassifi|literatur|vergleich",
    # ru
    r"анализ|исследован|теори|концепт|терминолог|гипотез|утвержд|классифиц|литератур|сопостав|сравн|доказат",
]
NEGATIVE = [
    r"\b(fix (a )?typo|renam|commit|push|pull|install|uninstall|run tests|update dependenc|format|lint|revert|merge branch)\b",
    r"\b(write (a )?(poem|story)|compos(e|ing) a poem|generat(e|ing) a poem)\b",
    r"yazı hatası|commit at|push at|testleri çalıştır|kurulum yap|şiir yaz|hikaye yaz|hikâye yaz",
    r"^\s*what (time|day|date|is the weather)\b",
    # de
    r"tippfehler|fehler (korrigieren|beheben)|umbenennen|installieren|deinstallieren|erstell einen commit",
    # es / fr / pt / it
    r"corrige.*(falta|faute|erro|typo)|faute de frappe|renombr|renommer|d[ée]sinstal|git commit",
    # ru
    r"опечатк|переименов|установ(ить|ка)|удалить (файл|папк)|коммит",
]
GREETING = re.compile(
    r"^\s*(hi|hello|hey|merhaba|selam|thanks|thank you|teşekkür|günaydın|iyi günler|"
    r"hola|buenos d[íi]as|bonjour|bonsoir|merci|guten (tag|morgen)|hallo|danke|ciao|ol[áa]|"
    r"gracias|obrigado|привет|здравствуйте|добрый (день|утро|вечер)|спасибо|مرحبا)\b", re.I)
SIMPLE_WHAT = re.compile(r"^\s*(what|who|when|where|which|ne|kim|ne zaman|nerede)\b", re.I)

CLAIM_LIMIT = ("Heuristic nomination only: this decision does not establish that the "
               "skill improved any outcome, and it is not a verdict about the task.")


def decision(choice, dom, reason, signals, route=None):
    out = {
        "decision": choice,
        "domain": dom,
        "ontology": (route or {}).get("ontology"),
        "route_status": (route or {}).get("status"),
        "reason": reason,
        "signals": signals,
        "claim_limit": CLAIM_LIMIT,
    }
    return out


def classify(text):
    t = str(text or "").strip()
    low = t.lower()
    if not t:
        return decision("ABSTAIN", None, "empty prompt", [])
    pos = [p for p in POSITIVE if re.search(p, low)]
    neg = [p for p in NEGATIVE if re.search(p, low)]
    # A greeting only wins when there is NO knowledge-work signal; "merhaba,
    # bu şarkıyı analiz et" is a knowledge task, not a greeting.
    if GREETING.match(low) and not pos:
        return decision("SKIP", None, "greeting or thanks", [])
    words = t.split()
    if len(words) < 3:
        return decision("ABSTAIN", None, "prompt too short to classify", [])
    if neg and not pos:
        return decision("SKIP", None, "matched a negative trigger", neg)
    if len(words) <= 9 and SIMPLE_WHAT.match(low) and not pos:
        return decision("SKIP", None, "short factual lookup", [])
    if not pos:
        return decision("ABSTAIN", None, "no knowledge-work signal", [])
    route = domain.route_text(t)
    return decision("ACTIVATE", route["domain"], f"knowledge-work signal; {route['reason']}",
                    pos[:4], route)


def run_hook() -> int:
    """Claude Code UserPromptSubmit shape. Silent on SKIP/ABSTAIN."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        payload = {}
    text = payload.get("prompt") or payload.get("message") or ""
    d = classify(text)
    if d["decision"] != "ACTIVATE":
        return 0
    context = (
        f"scientific-domain available. {d['reason']}. "
        f"Proposed domain={d['domain']} (route={d['route_status']}); ontology={d['ontology']}. "
        f"This is a PROPOSAL: confirm it first (`python domain.py use --ontology {d['domain']}`) "
        f"or pass --ontology explicitly; until then only the generic vocabulary applies. "
        f"Run `python domain.py terms` before naming any concept, and `add`/`check` "
        f"before asserting a knowledge claim. {d['claim_limit']}"
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }, ensure_ascii=False))
    return 0


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--text", help="task/prompt text")
    parser.add_argument("--stdin", action="store_true", help="read plain task text from stdin")
    parser.add_argument("--hook", action="store_true",
                        help="Claude Code UserPromptSubmit mode: JSON on stdin, silent unless ACTIVATE")
    args = parser.parse_args(argv)
    if args.hook:
        return run_hook()
    text = sys.stdin.read() if args.stdin else (args.text or "")
    print(json.dumps(classify(text), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
