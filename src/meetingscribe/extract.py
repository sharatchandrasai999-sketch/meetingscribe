"""Extract action items and a summary from a plain-text transcript.

Everything here is heuristic string matching — no model, no API call:

- A line is an action item if it contains action language ("will",
  "needs to", "need to", "TODO", "action:", "follow up", "assign") or a
  due-date phrase ("by Friday", "by 2026-11-12", ...).
- The owner is the first capitalized name at the start of the line
  (e.g. "Sarah will ..." -> Sarah), or the name after "assign to".
  Lines that name nobody get owner "Unassigned".
- A due date is the raw matched date phrase: YYYY-MM-DD, "March 5",
  "by Friday", or "next Monday". It is kept as written, not parsed
  into a real date.
- The summary is extractive: the first three sentences of the
  transcript, in order. Nothing is generated or paraphrased.
"""

from __future__ import annotations

import re

ACTION_WORDS = (
    "will",
    "needs to",
    "need to",
    "todo",
    "action:",
    "follow up",
    "assign",
)

_WEEKDAYS = "Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday"
_MONTHS = (
    "January|February|March|April|May|June|July|August|September|October|November|December"
)

DATE_PATTERNS = [
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),  # 2026-11-12
    re.compile(rf"\b(?:{_MONTHS}) \d{{1,2}}(?:st|nd|rd|th)?\b"),  # March 5
    re.compile(rf"\bby (?:next )?({_WEEKDAYS})\b", re.IGNORECASE),  # by Friday
    re.compile(rf"\bnext ({_WEEKDAYS})\b", re.IGNORECASE),  # next Monday
]

_NAME = r"[A-Z][a-z]+(?: [A-Z][a-z]+)?"
_OWNER_AT_START = re.compile(rf"^({_NAME})\b")
_ASSIGN_TO = re.compile(rf"\bassign(?:ed|s|ing)? to ({_NAME})\b", re.IGNORECASE)
# Words that are capitalized at a line start but are not names.
_NOT_NAMES = {"The", "This", "That", "We", "I", "It", "Our", "Next", "Please", "Action", "Todo"}

_PREFIX = re.compile(r"^\s*(?:[-*•]\s*)?(?:TODO|ACTION)\s*:\s*", re.IGNORECASE)
_SENTENCE = re.compile(r"[^.!?\n]+[.!?]")


def find_due(line: str) -> str | None:
    """Return the raw date phrase in ``line``, or None if there is none."""
    for pattern in DATE_PATTERNS:
        match = pattern.search(line)
        if match:
            return match.group(0)
    return None


def _is_action(line: str) -> bool:
    lowered = line.lower()
    if any(word in lowered for word in ACTION_WORDS):
        return True
    # A bare date ("next Tuesday") is not an action on its own; only a
    # "by <date>" deadline makes a line an action item.
    return "by " in lowered and find_due(line) is not None


def find_owner(line: str) -> str:
    """Best-guess owner: a name at the line start, or after "assign to"."""
    match = _ASSIGN_TO.search(line)
    if match:
        return match.group(1)
    cleaned = _PREFIX.sub("", line).strip()
    match = _OWNER_AT_START.match(cleaned)
    if match and match.group(1) not in _NOT_NAMES:
        return match.group(1)
    return "Unassigned"


def extract_action_items(text: str) -> list[dict]:
    """Return [{"owner", "task", "due"}] for every action line in ``text``."""
    items = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or not _is_action(line):
            continue
        task = _PREFIX.sub("", line).strip()
        items.append(
            {"owner": find_owner(line), "task": task, "due": find_due(line)}
        )
    return items


def summarize(text: str, n_sentences: int = 3) -> str:
    """Extractive summary: the first ``n_sentences`` sentences, in order."""
    sentences = [s.strip() for s in _SENTENCE.findall(text)]
    return " ".join(sentences[:n_sentences])


def parse_transcript(text: str) -> dict:
    """Return {"summary": ..., "action_items": [...]} for a transcript."""
    return {"summary": summarize(text), "action_items": extract_action_items(text)}
