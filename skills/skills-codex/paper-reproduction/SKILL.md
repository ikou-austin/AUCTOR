---
name: paper-reproduction
description: "Reproduce a paper from the paper itself or a paper plus repo. Search for official code, recursively trace upstream base models until open-source code is found, then set up the environment, prepare data, modify code, and run the reproduction. Use when user says \"复现论文\", \"reproduce paper\", \"paper reproduction\", \"有论文没代码\", or wants a minimal paper-to-code workflow."
---

# Paper Reproduction

Reproduce paper: **$ARGUMENTS**

## Goal

Use this skill when the user wants one narrow pipeline:

1. provide a paper
2. find official code or the nearest usable upstream repo
3. backtrack through parent methods until open-source code exists
4. prepare environment and data
5. patch the repo into the paper's method
6. run the reproduction

This is the minimal alternative to the full research workflow.

## Required Files

Maintain:

```text
PAPER_REPRO_TARGET.md
repro-logs/
  PAPER_REPRO_PLAN.md
  REPO_LINEAGE.md
  REPRO_TRACKER.md
  ASSUMPTIONS.md
refine-logs/
  EXPERIMENT_PLAN.md
  EXPERIMENT_TRACKER.md
```

If `PAPER_REPRO_TARGET.md` is missing, create it from `templates/PAPER_REPRO_TARGET_TEMPLATE.md` when available. If that template file is not present in the current project, recreate the same structure inline.

## Workflow

### Phase 1: Freeze the Reproduction Target

Read the paper and define:

- exact paper identity
- target table / figure / metric to reproduce
- tolerance vs paper numbers
- compute budget
- whether upstream repos are allowed

Write this to `PAPER_REPRO_TARGET.md`.

### Phase 2: Search for Code

Check in order:

1. paper page and supplementary material
2. authors' repos
3. benchmark or dataset repos
4. immediate parent method repos
5. backbone / base model repos

Record candidates and decisions in `repro-logs/REPO_LINEAGE.md`.

### Phase 3: Recursive Upstream Backtracking

If no official repo exists, recursively move up:

1. exact paper implementation
2. parent method
3. base model / trainer
4. benchmark harness

Stop at the nearest repo that covers most of the task, data, and evaluation pipeline.

If the lineage becomes speculative, log that in `repro-logs/ASSUMPTIONS.md`.

### Phase 4: Write the Reproduction Plan

Write `repro-logs/PAPER_REPRO_PLAN.md` from `templates/PAPER_REPRO_PLAN_TEMPLATE.md` when available. If that template file is missing, recreate the same sections inline.

The plan must specify:

- selected base repo and why
- repo-to-paper deltas
- environment setup
- data preparation
- code patch list
- verification milestones

Also write a compact `repro-logs/REPRO_TRACKER.md`.

### Phase 5: Prepare Repo, Environment, and Data

Clone the chosen repo into `base_repo/` unless one already exists.

Then:

- inspect setup instructions and entrypoints
- document exact environment commands
- add missing data preprocessing scripts if needed
- ensure a deterministic metric path and parseable outputs
- boot the baseline repo before major code edits

### Phase 6: Implement the Paper Delta

Patch only what the paper adds:

- modules
- losses
- training schedule
- preprocessing
- inference or decoding
- metrics

Log every non-explicit paper detail in `repro-logs/ASSUMPTIONS.md`.

### Phase 7: Convert to Execution Milestones

Generate:

- `refine-logs/EXPERIMENT_PLAN.md`
- `refine-logs/EXPERIMENT_TRACKER.md`

Use this ladder:

1. `M0` sanity
2. `M1` upstream baseline
3. `M2` paper patch enabled
4. `M3` target reproduction
5. `M4` miss analysis if needed

Then use `/experiment-bridge`, `/run-experiment`, and `/monitor-experiment` to execute.

### Phase 8: Judge the Outcome

Classify the result:

- `REPRODUCED`
- `PARTIAL`
- `BLOCKED`
- `NEGATIVE`

Always report raw numbers, tolerance, and exact run commands.

## Key Rules

- Prefer the nearest valid upstream repo, not the most famous repo.
- Separate paper facts from reconstruction assumptions.
- Reproduce the original metric and split first.
- Do not claim success without raw numbers.
