# Gemma autoresearch: empirical and causal analysis

Snapshot: 2026-10-02T03:09:34-07:00

The strongest claim is a fixed-train improvement from the overall tool-assisted ledger-construction pipeline. Prompts and evidence are treated together for the main research update; isolating individual tool effects is not required to report that gain. Adaptive train selection does not establish generalization to a fresh population. Cross-model results are not a controlled model-size experiment.

## Closest matched 12B comparisons

| Change | Before LDS | After LDS | Delta | Same evaluator source? |
| --- | ---: | ---: | ---: | --- |
| Reorganize factual constraint evidence | 0.5767 | 0.6070 | +0.0303 | True |
| Add a second factual verification pass | 0.5767 | 0.5211 | -0.0556 | True |
| Separate identity, money roles and restrictions | 0.5024 | 0.5228 | +0.0204 | True |
| Append decision/constraint evidence T34 | 0.5024 | 0.5101 | +0.0077 | False |

### Reorganize factual constraint evidence
Same T32+T36 stages and evaluator source. A bundle of prompt edits improved this fixed train set; individual clauses and transfer remain unidentified.
Matched verdict changes: 21 corrected, 17 worsened.

### Add a second factual verification pass
Same first-pass prompt, evidence stages and evaluator source. This specific second-pass design reduced train LDS; it does not show that every two-pass design fails.
Matched verdict changes: 18 corrected, 19 worsened.

### Separate identity, money roles and restrictions
Same T32+T33 stages and evaluator source. The prompt bundle improved train LDS while changing construct recovery and false flags.
Matched verdict changes: 21 corrected, 17 worsened.

### Append decision/constraint evidence T34
Prompt text and existing stages match, but evaluator source hashes differ. The +0.0077 is a confounded comparison, not an isolated T34 effect.
Matched verdict changes: 21 corrected, 23 worsened.

## Current 12B Calendar comparison
The no-tools baseline scored 0.3024 LDS-v2 and candidate candidate_5ba0cbec37e8 scored 0.3411 across the same 96 cases (+0.0387).
Balanced accuracy: 0.5104 → 0.5729. Construct macro-F1: 0.0943 → 0.1094.

## Uncertainty
{
  "draws": 4000,
  "seed": 20261002,
  "unit": "Matched malicious/benign pair, resampled within task \u00d7 ground-truth construct strata.",
  "limitation": "Exploratory percentile intervals conditional on already selected configurations. They do not correct adaptive selection, measure inference repeatability or establish out-of-domain effects."
}

Exploratory 95% paired bootstrap intervals for ledger baseline → selected best:
{
  "31B_train": {
    "delta": 0.0692,
    "interval95": [
      0.0284,
      0.1103
    ],
    "verdict_corrected": 15,
    "verdict_worsened": 11,
    "n": 144,
    "pairs": 72
  },
  "31B_calendar": {
    "delta": 0.0047,
    "interval95": [
      -0.0464,
      0.0552
    ],
    "verdict_corrected": 4,
    "verdict_worsened": 8,
    "n": 96,
    "pairs": 48
  },
  "12B_train": {
    "delta": 0.2048,
    "interval95": [
      0.1398,
      0.2706
    ],
    "verdict_corrected": 32,
    "verdict_worsened": 8,
    "n": 144,
    "pairs": 72
  },
  "12B_calendar": {
    "delta": 0.0387,
    "interval95": [
      -0.0395,
      0.1197
    ],
    "verdict_corrected": 24,
    "verdict_worsened": 18,
    "n": 96,
    "pairs": 48
  }
}

## Decisions and proposed experiments
1. Freeze candidate selection before evaluating a genuinely untouched task or dataset; report per-task scores and all promoted candidates without selecting on Calendar.
2. Repeat matched runs and assess screen ranking on a larger predeclared screen.

## Reproducibility
See snapshot.json for all exported aggregate metrics, complete candidate score tables, source paths and SHA-256 hashes. Private case text and per-case predictions are not exported.
