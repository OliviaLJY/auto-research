import csv
import json
import re
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "derived"
OUT.mkdir(parents=True, exist_ok=True)

SHARDS = [
    RAW / "sciagent_shards" / "scibench_gemma_broadcast.jsonl.zst",
    RAW / "sciagent_shards" / "scibench_gpt_broadcast.jsonl.zst",
    RAW / "sciagent_shards" / "labbench_gemma_broadcast.jsonl.zst",
    RAW / "sciagent_shards" / "labbench_gpt_broadcast.jsonl.zst",
]


def jsonable(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "tolist"):
        return jsonable(value.tolist())
    if hasattr(value, "item"):
        try:
            return jsonable(value.item())
        except (TypeError, ValueError):
            pass
    if isinstance(value, dict):
        return {k: jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    return str(value)


con = duckdb.connect()
meta = con.execute(
    """
    select trajectory_uid, benchmark_id, protocol_id, actor_model_id,
           evaluator_model_id, message_count, total_tokens, final_correct,
           problem_uid, raw_trace_path, raw_trace_row
    from read_parquet(?)
    """,
    [str(RAW / "sciagent_trajectories.parquet")],
).fetchdf()
meta_by_id = {row.trajectory_uid: row for row in meta.itertuples(index=False)}

records = []
for shard in SHARDS:
    rows = con.execute(
        "select * from read_json_auto(?, format='newline_delimited', compression='zstd')",
        [str(shard)],
    ).fetchdf()
    for row in rows.itertuples(index=False):
        item = {name: jsonable(getattr(row, name)) for name in rows.columns}
        item["local_shard"] = shard.name
        records.append(item)

records.sort(
    key=lambda r: (
        r["local_shard"],
        -(int(meta_by_id[r["trajectory_uid"]].message_count or 0)),
        r["trajectory_uid"],
    )
)

selected = []
for shard in sorted({r["local_shard"] for r in records}):
    group = [r for r in records if r["local_shard"] == shard]
    selected.extend(group[:5])

with (OUT / "sciagent_long20.jsonl").open("w", encoding="utf-8") as handle:
    for item in selected:
        handle.write(json.dumps(item, ensure_ascii=False) + "\n")

inventory_fields = [
    "trajectory_uid",
    "source",
    "benchmark_id",
    "protocol_id",
    "actor_model_id",
    "message_count",
    "event_count",
    "total_tokens",
    "final_correct",
    "problem_uid",
    "local_shard",
    "public_url",
    "selection_note",
]
inventory_rows = []
for item in selected:
    m = meta_by_id[item["trajectory_uid"]]
    inventory_rows.append(
        {
            "trajectory_uid": item["trajectory_uid"],
            "source": "SciAgentTrace",
            "benchmark_id": m.benchmark_id,
            "protocol_id": m.protocol_id,
            "actor_model_id": m.actor_model_id,
            "message_count": int(m.message_count),
            "event_count": len(item.get("events") or []),
            "total_tokens": "" if m.total_tokens is None else int(m.total_tokens),
            "final_correct": m.final_correct,
            "problem_uid": m.problem_uid,
            "local_shard": item["local_shard"],
            "public_url": "https://huggingface.co/datasets/AgentsSci/scientific-agent-protocol-traces",
            "selection_note": "Top-5 message_count within a balanced benchmark/model broadcast shard",
        }
    )

with (OUT / "trajectory_inventory.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=inventory_fields)
    writer.writeheader()
    writer.writerows(inventory_rows)

# AutoSapiens idea campaigns are external-validity trajectories. The repository
# contains 21 idea-level campaigns; five have locally downloaded handoff text.
tree = json.loads((RAW / "autosapiens_tree.json").read_text(encoding="utf-8"))
idea_ids = sorted(
    {
        match.group(1)
        for entry in tree["tree"]
        if (match := re.fullmatch(r"runs/(idea\d{3})/idea\.md", entry["path"]))
    }
)
with (OUT / "autosapiens_campaign_inventory.csv").open("w", newline="", encoding="utf-8") as handle:
    fields = ["campaign_id", "source", "public_url", "downloaded_for_annotation", "trajectory_unit"]
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    for idea_id in idea_ids:
        writer.writerow(
            {
                "campaign_id": idea_id,
                "source": "AutoSapiens / MultiAgentAutoResearch",
                "public_url": f"https://github.com/yanghangAI/autosapiens/tree/main/runs/{idea_id}",
                "downloaded_for_annotation": idea_id in {"idea001", "idea014", "idea015", "idea018", "idea021"},
                "trajectory_unit": "Architect idea -> Designer design -> Reviewer review -> Builder/code review -> experiment result",
            }
        )

print(f"selected SciAgentTrace trajectories: {len(selected)}")
print(f"inventoried AutoSapiens campaigns: {len(idea_ids)}")
