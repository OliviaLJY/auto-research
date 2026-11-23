# Next human study: comprehension, not prettiness

## Design

Use a within-subject comparison with three conditions:

1. original trajectory excerpt;
2. fluent summary baseline;
3. evidence-grounded decoder output.

Sample 24 excerpts: eight clear controls, eight shorthand/reference cases, and eight drift or
irrecoverable cases. Balance early, middle, and late trajectory positions. Randomize condition
order and prevent the same participant from seeing the same excerpt twice.

## Questions per excerpt

- What problem is the group solving?
- What candidate or implementation is currently under review?
- What changed relative to the previous step?
- Why was the change proposed?
- Is the change supported by evidence, only suggested by a peer, or unresolved?
- Where should a human intervene?

Record answer correctness, reading time, confidence, and evidence-event selection.

## Primary outcomes

- comprehension accuracy;
- calibrated confidence;
- time to answer;
- unsupported inference rate;
- correct identification of “cannot be recovered.”

The last outcome is essential: a decoder that always produces an explanation may look helpful
while reducing reliability.

## Annotation procedure

Two annotators independently mark referents, omitted premises, evidence spans, first opacity
onset, required backtrack distance, and recoverability. Adjudicate disagreements and report
agreement separately for detection, referent identity, and recoverability. The current
`pilot_annotations.csv` is an analyst pilot, not independent human ground truth.
