import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "derived"
OUT.mkdir(parents=True, exist_ok=True)

REFERENTIAL = {
    "it", "its", "this", "that", "these", "those", "they", "them", "their",
    "same", "previous", "above", "below", "former", "latter", "here", "there",
}


def refs(text):
    words = re.findall(r"[A-Za-z]+", text.lower())
    return ";".join(sorted(set(words) & REFERENTIAL))


def abbreviations(text):
    items = re.findall(r"\b(?:[A-Z]{2,8}|C\d+)\b", text)
    return ";".join(dict.fromkeys(items[:20]))


rows = []


def add_row(case_id, turn, sender, stage, text, *, unit="message", omitted="none observed",
            backtrack=0, recoverability="high", note="", onset=False):
    rows.append(
        {
            "case_id": case_id,
            "turn": turn,
            "unit": unit,
            "sender": sender,
            "stage": stage,
            "text_excerpt": re.sub(r"\s+", " ", text).strip()[:700],
            "referential_terms": refs(text),
            "abbreviations_or_shorthand": abbreviations(text),
            "omitted_or_hidden_premise": omitted,
            "opacity_onset": onset,
            "estimated_backtrack_turns": backtrack,
            "recoverability": recoverability,
            "analyst_note": note,
        }
    )


# Three message-level scientific-agent cases.
sample_specs = [
    ("SCIBENCH_BROADCAST_CLEAR", "scibench__broadcast.jsonl"),
    ("LABBENCH_PER_CLEAR", "labbench__per.jsonl"),
    ("OMNIMATH_BROADCAST_DRIFT", "omnimath2__broadcast.jsonl"),
]
for case_id, filename in sample_specs:
    messages = []
    for line in (RAW / "sciagent_samples" / filename).read_text(encoding="utf-8").splitlines():
        obj = json.loads(line)
        if obj.get("type") == "message":
            messages.append(obj["message"])
    for i, msg in enumerate(messages, start=1):
        content = msg.get("content", "")
        omitted = "none observed"
        backtrack = 0
        rec = "high"
        note = "Key quantities and candidate answer are restated locally."
        onset = False
        if case_id == "LABBENCH_PER_CLEAR":
            note = "Role handoff is explicit; Planner, Executor, and Reviewer each restate the operative evidence."
        if case_id == "OMNIMATH_BROADCAST_DRIFT" and 4 <= i <= 33:
            omitted = "review text switches to unrelated safety/history content; intended arithmetic-review rationale is missing"
            backtrack = i - 1
            rec = "medium" if i in {10, 18, 26} else "low"
            onset = i == 4
            note = (
                "The candidate value remains visible, but the peer-review content is unrelated. "
                "Recovery requires returning to the original problem or a later Mira correction."
            )
        add_row(
            case_id, i, msg.get("sender", msg.get("role", "unknown")),
            msg.get("stage", "prompt"), content, omitted=omitted,
            backtrack=backtrack, recoverability=rec, note=note, onset=onset,
        )


# Two file-handoff AutoResearch campaigns. Each artifact is treated as one turn.
for idea_id in ["idea001", "idea015"]:
    base = RAW / "autosapiens_selected" / "runs" / idea_id
    ordered = [base / "idea.md"]
    for design_dir in sorted(p for p in base.glob("design*" ) if p.is_dir()):
        ordered.extend([design_dir / "design.md", design_dir / "review.md", design_dir / "code_review.md"])
    ordered.extend([base / "review_log.md", base / "code_review_log.md"])
    ordered = [p for p in ordered if p.exists()]
    for i, file in enumerate(ordered, start=1):
        text = file.read_text(encoding="utf-8", errors="replace")
        rel = file.relative_to(base).as_posix()
        sender = "Architect" if rel == "idea.md" or rel.endswith("review.md") else "Designer/Builder"
        if rel.endswith("code_review.md"):
            sender = "Reviewer"
        omitted = "none observed"
        backtrack = 0
        note = "Structured artifact names the source idea/design and restates the implementation or review target."
        if idea_id == "idea015" and rel != "idea.md":
            omitted = "full definition of the inherited 'SOTA triple combo' is externalized to idea014/design003"
            backtrack = 1
            note = (
                "The handoff is readable because it gives an exact path and usually restates hyperparameters, "
                "but a fully independent audit still requires opening the referenced predecessor artifact."
            )
        add_row(
            f"AUTOSAPIENS_{idea_id.upper()}", i, sender, rel, text,
            unit="artifact_handoff", omitted=omitted, backtrack=backtrack,
            recoverability="high", note=note,
        )


fields = list(rows[0])
with (OUT / "pilot_annotations.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"annotation rows: {len(rows)} across {len(set(r['case_id'] for r in rows))} cases")
