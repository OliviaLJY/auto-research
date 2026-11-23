# AutoResearch trajectory transparency

This repository studies when multi-agent research trajectories become difficult for an external
human auditor to understand, and which communication structures make the hidden state recoverable.

The first pilot does **not** support the simple claim that longer trajectories monotonically become
more pronominal or less readable. Across 20 long Broadcast trajectories (5,329 retained events and
658,928 lexical tokens), the late-minus-early change in referential terms had a median of -0.008 per
1,000 words: 10 trajectories increased and 10 decreased.

The qualitative evidence points to more specific mechanisms:

1. **Protocol-induced opacity.** Compact entries such as `C5 revise B` require the orchestration
   schema and surrounding events. The same `C5` slot can be reused for different candidate values.
2. **Content drift under apparent coordination.** Agents can preserve fields such as `Candidate
   under review` and `Review Position` while the review text becomes unrelated to the task.
3. **Evidence opacity.** A decision or candidate update may remain visible after the supporting
   observation or experiment has disappeared.
4. **Recoverable cross-artifact references.** Stable paths plus local restatement of metrics and
   configuration make file-based research handoffs substantially easier to audit.

The defensible pilot claim is:

> Public multi-agent scientific traces contain protocol-dependent shorthand, identifier reuse,
> and episodes of severe content drift. Structured research handoffs with stable paths and repeated
> specifications appear easier to audit. A monotonic increase in lexical opacity with trajectory
> length is not established by this pilot.

## Repository map

- [`reports/pilot_findings.md`](reports/pilot_findings.md): full pilot findings and limitations.
- [`reports/trajectory_cases.md`](reports/trajectory_cases.md): four report-ready trajectory cases
  with stable IDs, event sequences, and faithful interpretations.
- [`reports/decoder_examples.md`](reports/decoder_examples.md): compact before-and-after decoder examples.
- [`prompts/decoder_prompt.md`](prompts/decoder_prompt.md): evidence-grounded decoder baseline and JSON schema.
- [`protocols/study_protocol.md`](protocols/study_protocol.md): next human-comprehension study.
- [`data/derived/`](data/derived): annotations, inventories, aggregate metrics, and pilot results.
- [`figures/opacity_over_time.png`](figures/opacity_over_time.png): descriptive lexical-proxy figure.
- [`scripts/`](scripts): corpus construction, proxy analysis, and pilot annotation scripts.

## Most useful cases

- `traj_853d36af4c6b3b9b5955`: a 289-event LAB-Bench Broadcast trace in which `C5` is repeatedly
  reused for A, B, and D candidate states.
- `traj_c0130827235174b989eb`: an OmniMath Broadcast trace in which all peer reviews drift to
  summer driving safety and gaslighting while candidate `14` remains under review.
- `traj_8710af6e0bb6034c84a4`: a clear SciBench Broadcast control in which every reviewer locally
  restates the ideal-gas evidence for `51.4 bar`.
- AutoSapiens `idea021`: a file-based handoff that points to `runs/idea015/design004/code/` and
  restates the 98.92 mm weighted MPJPE and two-decoder architecture.

See [`reports/trajectory_cases.md`](reports/trajectory_cases.md) for the event-level evidence.

## Reproduction

The scripts expect public source files under `data/raw/` and write generated artifacts to
`data/derived/` and `figures/`. Raw data and large generated event-level files are intentionally
excluded from Git.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/build_corpus.py
python scripts/analyze_opacity.py
python scripts/build_annotations.py
```

Required public sources:

- [SciAgentTrace](https://huggingface.co/datasets/AgentsSci/scientific-agent-protocol-traces)
- [AutoSapiens](https://github.com/yanghangAI/autosapiens)
- [MultiAgentAutoResearch](https://github.com/yanghangAI/MultiAgentAutoResearch)

The external GPT, DeepSeek, and GLM decoder comparison has not been run yet. The prompt and scoring
contract are included so that all models can be evaluated with the same context and output schema.
