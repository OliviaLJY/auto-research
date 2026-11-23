import csv
import json
import math
import re
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived"
FIGURES = ROOT / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|C\d+|[0-9]+(?:\.[0-9]+)?")
REFERENTIAL = {
    "it", "its", "itself", "this", "that", "these", "those", "they", "them",
    "their", "theirs", "former", "latter", "same", "previous", "above", "below",
    "here", "there", "such", "one", "ones",
}
VAGUE_PHRASES = [
    "the candidate", "this answer", "that answer", "the result", "this result",
    "the approach", "this approach", "previous answer", "previous attempt",
    "the issue", "this issue", "the method", "this method",
]
SHORTHAND_RE = re.compile(r"\bC\d+\b|\b(?:approve|revise|select_for_review)\b", re.I)


def metrics(text):
    words = WORD_RE.findall(text)
    lower = [w.lower() for w in words]
    n = max(1, len(words))
    ref = sum(w in REFERENTIAL for w in lower)
    vague = sum(text.lower().count(p) for p in VAGUE_PHRASES)
    shorthand = len(SHORTHAND_RE.findall(text))
    acronyms = len(re.findall(r"\b[A-Z]{2,8}\b", text))
    return {
        "words": len(words),
        "referential_count": ref,
        "referential_per_1k": 1000 * ref / n,
        "vague_np_count": vague,
        "vague_np_per_1k": 1000 * vague / n,
        "candidate_shorthand_count": shorthand,
        "candidate_shorthand_per_1k": 1000 * shorthand / n,
        "acronym_count": acronyms,
        "acronym_per_1k": 1000 * acronyms / n,
    }


trajectories = [json.loads(line) for line in (OUT / "sciagent_long20.jsonl").read_text(encoding="utf-8").splitlines()]
event_rows = []
for traj in trajectories:
    events = traj.get("events") or []
    retained = [e for e in events if e.get("content") and e.get("type") in {"message", "summary"}]
    for idx, event in enumerate(retained):
        row = {
            "trajectory_uid": traj["trajectory_uid"],
            "benchmark_id": traj["benchmark_id"],
            "actor_model_id": traj["actor_model_id"],
            "event_index": idx,
            "event_count": len(retained),
            "normalized_position": idx / max(1, len(retained) - 1),
            "decile": min(9, int(10 * idx / max(1, len(retained)))),
            "event_type": event.get("type"),
            "sender": event.get("sender"),
            "stage": event.get("stage"),
            "content": event.get("content"),
        }
        row.update(metrics(row["content"]))
        event_rows.append(row)

fields = list(event_rows[0])
with (OUT / "event_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(event_rows)

summary_rows = []
for decile in range(10):
    rows = [r for r in event_rows if r["decile"] == decile]
    total_words = sum(r["words"] for r in rows) or 1
    summary_rows.append(
        {
            "decile": decile + 1,
            "normalized_midpoint": (decile + 0.5) / 10,
            "events": len(rows),
            "words": total_words,
            "referential_per_1k": 1000 * sum(r["referential_count"] for r in rows) / total_words,
            "vague_np_per_1k": 1000 * sum(r["vague_np_count"] for r in rows) / total_words,
            "candidate_shorthand_per_1k": 1000 * sum(r["candidate_shorthand_count"] for r in rows) / total_words,
            "acronym_per_1k": 1000 * sum(r["acronym_count"] for r in rows) / total_words,
        }
    )

with (OUT / "position_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0]))
    writer.writeheader()
    writer.writerows(summary_rows)

change_rows = []
metric_counts = [
    ("referential_count", "referential_delta_per_1k"),
    ("vague_np_count", "vague_np_delta_per_1k"),
    ("candidate_shorthand_count", "candidate_shorthand_delta_per_1k"),
    ("acronym_count", "acronym_delta_per_1k"),
]
for trajectory_uid in sorted({r["trajectory_uid"] for r in event_rows}):
    rows = [r for r in event_rows if r["trajectory_uid"] == trajectory_uid]
    early = [r for r in rows if r["normalized_position"] < 0.5]
    late = [r for r in rows if r["normalized_position"] >= 0.5]
    out = {
        "trajectory_uid": trajectory_uid,
        "benchmark_id": rows[0]["benchmark_id"],
        "actor_model_id": rows[0]["actor_model_id"],
        "events": len(rows),
    }
    for count_key, delta_key in metric_counts:
        early_rate = 1000 * sum(r[count_key] for r in early) / max(1, sum(r["words"] for r in early))
        late_rate = 1000 * sum(r[count_key] for r in late) / max(1, sum(r["words"] for r in late))
        out[delta_key] = late_rate - early_rate
    change_rows.append(out)

with (OUT / "trajectory_change.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(change_rows[0]))
    writer.writeheader()
    writer.writerows(change_rows)

x = np.array([r["normalized_midpoint"] for r in summary_rows])
slopes = {}
for key in ["referential_per_1k", "vague_np_per_1k", "candidate_shorthand_per_1k", "acronym_per_1k"]:
    y = np.array([r[key] for r in summary_rows])
    slopes[key] = float(np.polyfit(x, y, 1)[0])

series = [
    ("referential_per_1k", "Referential terms / 1k words"),
    ("vague_np_per_1k", "Vague noun phrases / 1k words"),
    ("candidate_shorthand_per_1k", "Candidate-memory shorthand / 1k words"),
    ("acronym_per_1k", "Uppercase acronyms / 1k words"),
]
result = {
    "trajectory_count": len(trajectories),
    "event_count": len(event_rows),
    "word_count": sum(r["words"] for r in event_rows),
    "linear_slope_per_normalized_trajectory": slopes,
    "late_minus_early_summary": {
        delta_key: {
            "median": float(np.median([r[delta_key] for r in change_rows])),
            "positive_trajectories": sum(r[delta_key] > 0 for r in change_rows),
            "negative_trajectories": sum(r[delta_key] < 0 for r in change_rows),
        }
        for _, delta_key in metric_counts
    },
    "warning": "These are lexical proxies, not validated human-comprehension or coreference measures.",
}
(OUT / "pilot_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

# Dependency-light chart rendering with Pillow.
canvas = Image.new("RGB", (1600, 1000), "white")
draw = ImageDraw.Draw(canvas)
font = ImageFont.load_default()
draw.text((40, 25), "Pilot opacity proxies across 20 long broadcast trajectories", fill="#111827", font=font)
colors = ["#2563eb", "#dc2626", "#059669", "#7c3aed"]
for panel, ((key, title), color) in enumerate(zip(series, colors)):
    col, row = panel % 2, panel // 2
    left, top = 70 + col * 780, 90 + row * 440
    width, height = 680, 340
    yvals = [float(r[key]) for r in summary_rows]
    ymax = max(yvals) * 1.1 or 1.0
    draw.rectangle((left, top, left + width, top + height), outline="#9ca3af", width=2)
    draw.text((left, top - 25), title, fill="#111827", font=font)
    points = []
    for i, value in enumerate(yvals):
        px = left + 20 + i * (width - 40) / 9
        py = top + height - 20 - value / ymax * (height - 40)
        points.append((px, py))
        draw.ellipse((px - 5, py - 5, px + 5, py + 5), fill=color)
        draw.text((px - 4, top + height + 8), str(i + 1), fill="#4b5563", font=font)
    draw.line(points, fill=color, width=4)
    draw.text((left, top + height + 28), "trajectory position decile", fill="#4b5563", font=font)
    draw.text((left + width - 80, top + 6), f"max {ymax / 1.1:.2f}", fill="#6b7280", font=font)
canvas.save(FIGURES / "opacity_over_time.png")
print(json.dumps(result, indent=2))
