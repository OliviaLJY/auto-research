# Concrete trajectory cases

These cases are selected to separate four phenomena that are easily conflated by a single
"opacity" score: protocol state compression, semantic drift, local evidence repetition, and
recoverable cross-artifact reference.

Quoted text is shortened only where the omitted passage does not change the reported mechanism.
The stable trajectory IDs and event numbers are retained so the excerpts can be checked against
the public source data.

## Case 1  Reused protocol state in one trajectory

**Trajectory:** `traj_853d36af4c6b3b9b5955`
**Source:** LAB-Bench Broadcast
**Task:** identify the longest ORF and the amino acid at position 48
**Scale:** 289 events
**Outcome:** final answer did not pass

Events 39 to 45 show how a short protocol record depends on adjacent review content:

| Event | Sender and stage | Trace excerpt |
|---:|---|---|
| 39 | system, candidate memory | `C5 approve A` |
| 40 | Rowan, peer review | Candidate A is approved after another ORF enumeration. |
| 41 | system, candidate memory | `C5 revise B` |
| 42 | Talia, peer review | Candidate A; propose correction; longest ORF begins at 235; codon 48 is `GGC`; propose B. |
| 43 | system, update | `Candidate updated from A to B` |
| 44 | system, protocol | Previous candidate A; current candidate for further review B; selection is not proof. |
| 45 | system, candidate memory | `C5 select_revision B` |

Event 41 alone does not reveal whether `C5` is an entity, a candidate identifier, or a protocol
slot. With event 42, a faithful expansion is possible:

> Candidate-memory slot C5 records Talia's proposal to revise the current candidate from A to B.
> Her stated basis is a recalculation of the ORF start and the 48th codon. B remains a peer
> suggestion, not a verified result.

`C5` is not stable even within this trajectory. Later events include:

- event 62: `C5 revise D`;
- event 64: `C5 revise B`;
- event 68: `C5 select_revision D`;
- event 71: `C5 revise D`;
- event 73: `C5 revise B`.

**Finding.** This is state opacity and identifier reuse, not ordinary pronoun ambiguity. A decoder
must treat `C5` as a mutable protocol slot and use nearby evidence rather than merge every `C5`
record into one stable candidate.

## Case 2  Semantic drift with intact coordination fields

**Trajectory:** `traj_c0130827235174b989eb`
**Source:** OmniMath Broadcast
**Task:** calculate `(3,1) ∇ (4,2)` where `(a,b) ∇ (c,d) = ac + bd`

The task answer is `3×4 + 1×2 = 14`. The candidate remains visible while the review content drifts:

| Message | Sender and stage | Trace excerpt |
|---:|---|---|
| 1 | user, prompt | Calculate the defined operation. |
| 2 | Mira, discussion | `3×4 + 1×2 = 14`; candidate answer 14. |
| 3 | system, candidate review | Candidate 14 from Mira is under group review. |
| 4 | Mira, approval | Candidate 14; needs revision; review explains the "100 deadliest days of summer" and road safety. |
| 5 | Rowan, approval | Candidate 14; needs revision; another summer-driving-safety response. |
| 6 | Talia, approval | Candidate 14; needs revision; more teen-driver and road-safety content. |
| 7-9 | Mira, Rowan, Talia | Candidate 14; needs revision; all three reviews switch to the history of gaslighting. |
| 10 | Mira, discussion | Re-establishes `3×4 + 1×2 = 14`; candidate answer 14. |
| final | system and evaluator | Submit 14; evaluation signal PASS. |

The coordination protocol remains active: the candidate field, review-position field, retries, and
submission all continue. What disappears is the task-relevant reason for revision.

A faithful decoder should report:

- candidate 14 is supported by message 2;
- review messages 4 to 9 are unrelated to the arithmetic task;
- no task-relevant reason for `needs_revision` can be recovered from those messages.

It should **not** invent a plausible mathematical criticism. In the 35-unit pilot annotation,
opacity begins at message 4 and 27 units are marked low-recoverability.

**Finding.** Protocol conformance is not evidence of semantic coordination. A system may continue
to advance the workflow after the review channel has lost task-relevant content.

## Case 3  Evidence repetition as a transparency control

**Trajectory:** `traj_8710af6e0bb6034c84a4`
**Source:** SciBench Broadcast
**Task:** ideal-gas pressure for 10.0 mol ethane in 4.860 dm³ at 27°C

| Message | Sender | Locally restated evidence |
|---:|---|---|
| 2 | Mira | Lists `n`, `V`, `T`; applies `P=nRT/V`; obtains about 51.4 bar. |
| 4 | Mira | Repeats the formula and inputs; obtains 51.37 bar; rounds to 51.4 bar; approves. |
| 5 | Rowan | Uses `R=0.0831446 L bar K⁻¹ mol⁻¹`; independently obtains 51.415 bar; approves. |
| 6 | Talia | Recomputes in SI units and converts Pa to bar; obtains 51.433 bar; approves. |
| 7-8 | system and evaluator | Submit 51.4 bar; evaluation signal PASS. |

Any review message contains the current candidate, formula, inputs, conversion, and conclusion. An
external reader does not have to return to the original proposal to verify the approval.

**Finding.** More tokens do not necessarily imply less transparency. Here, repeated evidence
reduces backtracking and creates local verifiability. Communication cost and audit benefit should be
measured separately.

## Case 4  Recoverable file-based research handoff

**Campaign:** AutoSapiens `idea021`
**Reference:** `runs/idea015/design004/code/`

The phrase "two-decoder SOTA" is compressed, but the handoff includes a stable path and restates
the inherited result:

- weighted MPJPE: **98.92 mm**;
- LLRD with gamma 0.90;
- continuous square-root-spaced depth positional encoding;
- hidden dimension 384;
- four-layer coarse decoder;
- independent two-layer refinement decoder.

Following the path to `idea015/design004/design.md` recovers the exact two-pass design and loss:
pass 1 uses the four-layer decoder, pass 2 uses the independent two-layer refinement decoder, and
the supervised objective is `0.5 L(J1) + 1.0 L(J2)`.

The `idea021` handoff also preserves the reason for the next experiment: `idea019` tested anatomical
priors on a weaker shared-decoder baseline, so the priors should be retested on the stronger
two-decoder baseline.

**Finding.** Structured external memory does not eliminate compression. It turns compressed terms
into traceable references. Stable entity paths, current metrics, inherited configuration, and the
reason for change are promising transparency requirements for research-agent handoffs.

## Cross-case implication

| Case | Current candidate visible | Supporting reason visible | Mechanism |
|---|---|---|---|
| Reused C5 state | Partly | Only in adjacent events | Protocol compression and identifier reuse |
| OmniMath drift | Yes, 14 | No | Workflow continues after semantic drift |
| Ideal-gas Broadcast | Yes, 51.4 bar | Repeated locally | Evidence repetition improves auditability |
| AutoSapiens handoff | Yes, current baseline | Recoverable through path and restatement | Stable references and specification fields |

These cases motivate task-based evaluation: can an external reader identify the current objective,
active candidate, reason for change, supporting evidence, and appropriate intervention point? Word
counts and pronoun frequency are useful diagnostics, but they do not answer those questions.
