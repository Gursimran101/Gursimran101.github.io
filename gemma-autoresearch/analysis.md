# Gemma autoresearch: empirical and causal analysis

Snapshot: 2026-10-09T23:01:59-07:00

The searched tool-assisted ledger-construction pipeline attained higher train LDS than the no-tools reference. Prompts and evidence are treated together for the main research update; isolating individual tool effects is not required to report that result. The selected 12B configuration also scored higher than the no-tools ledger on the same 96 Calendar cases. Adaptive train selection does not establish generalization to a fresh population. Cross-model results are not a controlled model-size experiment.

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

## 12B Calendar comparison
The no-tools ledger scored 0.3024 LDS-v2 and the search winner scored 0.3411 across the same 96 cases (+0.0387).
Balanced accuracy: 0.5104 → 0.5729. Construct macro-F1: 0.0943 → 0.1094.
All 37 full-train-promoted candidates were evaluated on Calendar. 34 scored above the ledger baseline; 23 scored above the train winner. The highest Calendar score was 0.4208 from a candidate with train LDS-v2 0.5180. That maximum was identified after evaluating all promoted candidates, so it is exploratory post-selection evidence, not the preselected train-winner result.

## Haiku construction → Gemma 31B reader
The completed Haiku-constructor search improved train LDS-v2 from 0.5485 to 0.5809 (+0.0324), and Calendar from 0.4064 to 0.4687 (+0.0623). All predictions were made by the frozen Gemma 31B reader after factual-only ledger sanitization. These are separate from the earlier proxy that scored Haiku's own verdicts and construct labels.
The progress plot includes the two inherited configurations plus all six completed continuation candidates. The original seed and first factual-tool train scores survive as exact scalars in the saved transcript; their raw train run directories were removed during an earlier cleanup. Calendar has complete baseline and winner artifacts.

## Astra consultations
Five completed consultations: one in 31B and four in 12B. Astra reviewed train-side artifacts and proposed experiments between evaluations. The source-paired 31B comparison variant and the small 12B evidence-window improvement followed its advice; most 12B follow-up arms lost. This supports usefulness for diagnosis and experimental steering, but does not measure Astra's isolated effect.
- 31B, Sep 25, 10:50 PM Pacific: After four rounds without improvement: diagnose construct errors and choose one concrete experiment. Show both literal values and their sources in comparisons; preserve the existing evidence graph. A source-paired prompt variant scored 0.5729 versus the previous 0.5393 best. Useful steering; Astra's contribution was not isolated.
- 12B, Sep 29, 08:29 PM Pacific: Early errors: why were identity and restriction violations being confused? Separate identity, amount provenance, action purpose and execution status. Provided a concrete representation diagnosis and experiments; its individual contribution was not isolated.
- 12B, Oct 05, 12:27 AM Pacific: At the 0.6070 plateau: investigate false positives and contradictory provenance. Prioritize a deterministic identity table and preserve source-to-action links. Identity-table and wording variants were tested but remained below the incumbent.
- 12B, Oct 06, 12:04 AM Pacific: After four stalled rounds: request distinct mechanisms rather than more identity evidence. Sparse comparisons, verbatim request replay, symmetric factual coverage and a bounded rewrite. All four follow-up arms fell short of the incumbent on screen or full train.
- 12B, Oct 06, 01:11 PM Pacific: After five stalled rounds: reassess missing restrictions and evidence length. Specification-first decomposition, source-linked counts, outcome cards and shorter evidence windows. The shorter-window arm became the train best: 0.6070 → 0.6087. Other evaluated arms lost; a further shortening also lost.

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
    "delta": 0.2065,
    "interval95": [
      0.1424,
      0.2701
    ],
    "verdict_corrected": 35,
    "verdict_worsened": 10,
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
