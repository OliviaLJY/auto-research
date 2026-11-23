# Making AutoResearch Legible: first pilot report

Date: 2026-11-23

## Outcome first

The pilot establishes a usable corpus and a sharper hypothesis, but it does **not** yet support
the simple claim that long multi-agent trajectories monotonically become more pronominal or
less readable.

Across 20 long Broadcast Deliberation trajectories—5,329 message/summary events and 658,928
lexical tokens—the median late-minus-early change in referential terms was essentially zero
(-0.008 per 1,000 words): 10 trajectories increased and 10 decreased. Vague noun phrases
increased in 12 of 20 trajectories, while candidate-memory shorthand decreased in 12 of 20.
These are descriptive lexical proxies, not comprehension measurements.

The qualitative audit instead found three more precise mechanisms:

1. **Protocol-induced opacity.** Compact state entries such as `C5 revise \boxed{B}` are useful
   to the orchestrator but opaque without the protocol schema. The same `C5` slot is reused for
   different values and actions, creating identifier collisions.
2. **Content drift under apparent coordination.** In one public Broadcast trajectory, all three
   peers repeatedly produced unrelated text about gaslighting or summer safety while continuing
   to mark the visible candidate `14` as needing revision. The group retained superficial
   coordination while losing task-relevant review content.
3. **Cross-artifact dependence.** AutoResearch handoffs use references such as
   `idea014/design003` and “SOTA triple combo.” These references are recoverable when exact paths
   and configuration restatements are present, but not from the phrase alone.

The strongest revised research question is therefore:

> Which communication and memory mechanisms make multi-agent research trajectories opaque to
> an external auditor, and when do structured handoffs prevent that opacity?

## Corpus assembled

### Core long-dialogue sample

The core sample contains 20 of the longest public Broadcast Deliberation trajectories from four
balanced SciAgentTrace shards:

- SciBench × Gemma 4 31B: five;
- SciBench × GPT-OSS 120B: five;
- LAB-Bench × Gemma 4 31B: five;
- LAB-Bench × GPT-OSS 120B: five.

Each shard contributes its five highest-message-count trajectories. The selected records contain
205–311 retained message/summary events and include candidate proposals, peer review, candidate
memory, evaluation, and retries. Selection details and stable IDs are in
`trajectory_inventory.csv`.

### Real AutoResearch external-validity set

The AutoSapiens repository exposes 21 idea-level campaigns created by a role-specialized
MultiAgentAutoResearch workflow. Each campaign is a file-based trajectory:

```text
Architect idea → Designer design → Reviewer review → Builder/code review → experiment result
```

All 21 campaigns are inventoried. Five campaigns—idea001, idea014, idea015, idea018, and
idea021—were downloaded for close inspection. These artifacts are genuine autonomous ML
experimentation, but they are structured handoffs rather than raw Agent-to-Agent chat.

### Sources inspected but not treated as core multi-agent dialogue

- RIDAR: 420 autonomous-research trajectories; the inspected 945-event trace had no sub-agent
  IDs and was therefore kept as a possible single-agent control.
- Autonomous Research Agents: five fully archived research runs with logs, plans, experiments,
  and papers; useful for auditability research but not a raw multi-agent dialogue corpus.
- MultiAgentAutoResearch framework repository: useful for role and memory design; its example
  runs live in the separate AutoSapiens repository.

## Pilot annotation

`pilot_annotations.csv` contains 76 audited units across five cases:

| Case | Units | Result |
|---|---:|---|
| SciBench Broadcast clear control | 8 messages | Candidate and evidence are restated locally. |
| LAB-Bench Planner–Executor–Reviewer | 6 messages | Explicit role handoff; little backtracking needed. |
| OmniMath Broadcast drift | 35 messages | Opacity begins at peer-review turn 4; 27 units have low recoverability. |
| AutoSapiens idea001 | 12 artifacts | Exact design references and detailed restatement keep handoffs legible. |
| AutoSapiens idea015 | 15 artifacts | Inherited baseline requires one cross-artifact lookup, but paths and hyperparameters are explicit. |

This is an analyst pilot used to refine the scheme. It is not independent human ground truth.

## What the first figure says

`opacity_over_time.png` plots four lexical proxies by trajectory-position decile. Pooled curves
show small upward slopes for referential terms, vague noun phrases, and uppercase acronyms, but
the per-trajectory early/late comparison is heterogeneous. The aggregate slope is partly driven
by stage composition: later protocol phases contain different templates and scientific content.

Therefore, the current figure should be presented as a diagnostic, not evidence for the main
hypothesis. The next figure must use validated referent resolution and human comprehension.

## A better decomposition of “opacity”

The pilot suggests separating at least four constructs:

- **Referential opacity:** a surface form cannot be linked to a unique entity or earlier claim.
- **State opacity:** compact protocol state is readable only with hidden orchestration rules.
- **Evidence opacity:** a decision is visible, but its supporting observation or experiment is
  missing.
- **Semantic drift:** messages remain syntactically coordinated but become unrelated to the
  actual task.

These should not be collapsed into a single score until each measure predicts human
comprehension or intervention accuracy.

## Minimal decoder baseline

`decoder_prompt.md` implements a model-agnostic, evidence-grounded decoder. It requires:

- a faithful expanded message;
- surface-form-to-referent mappings;
- recovered implicit premises;
- evidence event IDs for every recovery;
- calibrated confidence;
- unresolved alternatives;
- warnings for identifier collisions, content drift, corrupted text, and protocol state that
  is not proof.

The crucial baseline behavior is abstention. For the drift case, the correct output is not a
plausible mathematical review; it is “the relevant rationale is missing.”

The prompt has not yet been executed on GPT, DeepSeek, and GLM because this workspace has no
configured provider credentials or endpoints. Running the same prompt at temperature zero is
the next engineering step; the comparison protocol is already specified.

## Recommended next seven days

1. Add 20 AutoResearch raw-chat trajectories. Public structured artifacts are not sufficient to
   test spontaneous shorthand between research agents. If raw sessions are unavailable, run the
   public MultiAgentAutoResearch workflow and preserve parent and sub-agent JSONL logs.
2. Independently annotate 24 excerpts with two researchers. Measure first opacity onset,
   antecedent identity, evidence span, backtrack distance, and recoverability.
3. Run the decoder prompt on GPT, DeepSeek, and GLM with identical context windows. Score
   evidence overlap and unsupported recovery, not fluency.
4. Compare unstructured Broadcast, explicit PER handoffs, and file-based AutoSapiens handoffs.
   This is the most promising causal variable exposed by the pilot.
5. Replace pronoun counts with task-based comprehension: current objective, active candidate,
   reason for change, supporting evidence, and appropriate human intervention.

## Claim that is currently defensible

> Public multi-agent scientific traces contain recoverable but protocol-dependent shorthand,
> identifier reuse, and episodes of severe content drift. Structured research handoffs with
> stable paths and repeated specifications appear substantially easier to audit. A monotonic
> increase in lexical opacity with trajectory length is not established by this pilot.

That claim is narrower than the starting intuition, but it is testable and less vulnerable to a
reviewer asking whether “opacity” is merely a count of pronouns.

## Public sources

- SciAgentTrace: https://huggingface.co/datasets/AgentsSci/scientific-agent-protocol-traces
- AutoSapiens: https://github.com/yanghangAI/autosapiens
- MultiAgentAutoResearch: https://github.com/yanghangAI/MultiAgentAutoResearch
- RIDAR: https://huggingface.co/datasets/THU-KEG/RIDAR
- Autonomous Research Agents: https://github.com/kofujimura/autonomous-research-agents
