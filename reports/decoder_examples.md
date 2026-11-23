# Decoder examples from the pilot corpus

## Example 1: protocol shorthand and identifier reuse

Original event:

```text
C5 revise \boxed{B}
```

Faithful expansion:

> The protocol's candidate-memory entry labeled `C5` records a revision whose proposed
> answer is option B. This event alone does not explain why B was proposed and does not show
> that B is correct.

Required warning: `C5` is reused at other points for different candidate values and actions.
It is therefore a local protocol slot, not a stable semantic name. Recoverability is medium
unless the decoder is given the surrounding candidate-review events.

## Example 2: content drift with a visible candidate

Original peer-review event:

```text
Candidate under review: \boxed{14}
Review Position: needs_revision
Peer Review: I understand you're looking for information about the history of “gaslighting”...
```

Faithful expansion:

> The peer-review step marks candidate 14 as needing revision, but the supplied review text is
> unrelated to the arithmetic problem. No task-relevant reason for revision can be recovered
> from this event.

This must be labeled `content_drift`; a decoder must not invent a mathematical criticism.

## Example 3: cross-artifact AutoResearch reference

Original phrase:

```text
the two-decoder SOTA / runs/idea015/design004/code/
```

Faithful expansion, when `idea021/idea.md` is in context:

> The referenced starting point is AutoSapiens idea015/design004: a four-layer coarse decoder
> followed by an independent two-layer refinement decoder, combined with LLRD, continuous
> square-root-spaced depth positional encoding, and a 384-dimensional wide head. Its reported
> validation weighted MPJPE is 98.92 mm.

The exact path makes this reference highly recoverable. Without the referenced artifact or its
restatement in `idea021/idea.md`, the decoder should leave the implementation details unresolved.
