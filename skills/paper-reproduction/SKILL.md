---
name: paper-reproduction
description: "Reproduce a paper from the paper itself or a paper plus repo. Search for official code, recursively trace upstream base models until open-source code is found, then set up the environment, prepare data, modify code, and run the reproduction. Use when user says \"复现论文\", \"reproduce paper\", \"paper reproduction\", \"有论文没代码\", or wants a minimal paper-to-code workflow."
argument-hint: [paper-url-pdf-or-title]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent, Skill, mcp__codex__codex, mcp__codex__codex-reply
---

# Paper Reproduction

Reproduce paper: **$ARGUMENTS**

## Goal

This skill is the narrow path for one job only:

1. take a target paper
2. find usable code
3. if no official code exists, recursively backtrack to the nearest open-source base repo
4. set up environment and data
5. patch the code until the paper can be run
6. launch and monitor reproduction experiments

Use this instead of stitching together the full ARIS research pipeline when the task is simply: **"here is a paper, reproduce it."**

## Minimal Inputs

Prefer these inputs, in order:

1. `PAPER_REPRO_TARGET.md` at project root
2. a paper PDF path
3. an arXiv URL
4. a paper title plus venue/year

If `PAPER_REPRO_TARGET.md` does not exist, create it from `templates/PAPER_REPRO_TARGET_TEMPLATE.md` when available. If the template file is not present in the current project, recreate the same structure inline from the user's request.

## Files This Skill Should Maintain

Create and update these files:

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

The `repro-logs/` files capture paper-specific reverse engineering. The `refine-logs/` files are the handoff into `experiment-bridge`.

## Workflow

### Phase 1: Freeze the Reproduction Target

Read the paper and write `PAPER_REPRO_TARGET.md` with:

- exact paper identity
- what must be reproduced: table, figure, metric, or claim
- acceptable tolerance vs reported numbers
- compute limit and hardware constraint
- whether "official code only" is required, or upstream base repos are allowed

Do not proceed with a vague target like "reproduce the whole paper" if the paper has multiple claims. Break it into a primary target and optional secondary targets.

### Phase 2: Find Code in Descending Preference Order

Search in this order:

1. paper abstract page, project page, appendix, supplementary material
2. authors' GitHub or lab repos
3. benchmark or dataset leaderboards mentioned by the paper
4. cited implementation repos for the immediate parent method
5. open-source repos for the paper's backbone / base model / trainer

Prefer repos that match the paper on:

- task
- dataset and split
- backbone family
- framework
- evaluation protocol
- license and accessibility

Record every serious candidate in `repro-logs/REPO_LINEAGE.md`.

### Phase 3: Recursive Base-Repo Backtracking

If no official implementation exists, recursively move upward through the method lineage until a usable open-source base is found.

Use this backtracking order:

1. **Paper method repo** — exact paper implementation
2. **Immediate parent method repo** — the method this paper extends
3. **Base model repo** — backbone, pretrained model, or trainer stack
4. **Benchmark harness repo** — task-specific training and evaluation pipeline

At each level:

- identify what the paper adds on top of that layer
- search for open-source repos implementing that layer
- rank candidates by architectural overlap and data / metric compatibility
- stop at the nearest repo that covers most of the pipeline and leaves a patchable gap

Never silently jump to an unrelated repo just because it is popular. If the lineage becomes speculative, write that explicitly in `repro-logs/ASSUMPTIONS.md`.

### Phase 4: Write the Reverse-Engineering Plan

Write `repro-logs/PAPER_REPRO_PLAN.md` using `templates/PAPER_REPRO_PLAN_TEMPLATE.md` when available. If the template file is missing, recreate the same sections inline.

The plan must answer:

- what repo was selected and why
- what the paper changes relative to that repo
- what environment is needed
- what data preparation is needed
- what code modules must be added or modified
- what metrics and tables will verify success

Also write `repro-logs/REPRO_TRACKER.md` with compact execution rows:

```markdown
| ID | Stage | Goal | Artifact | Status | Notes |
|----|-------|------|----------|--------|-------|
| R0 | repo  | select base repo | REPO_LINEAGE.md | DONE | ... |
```

### Phase 5: Prepare Environment and Data

After the base repo is chosen:

1. clone it into `base_repo/` unless the user provided an existing repo
2. inspect `README`, requirements, setup scripts, entrypoints, and configs
3. write down the exact environment commands in `repro-logs/PAPER_REPRO_PLAN.md`
4. implement missing dataset download / preprocessing scripts if needed
5. ensure there is a deterministic eval path and parseable outputs

Before modifying model code, make sure the baseline repo can at least boot, import, and run a tiny sanity pass.

### Phase 6: Patch the Gap from Repo to Paper

Implement the smallest change set that closes the gap between the selected repo and the paper:

- architecture deltas
- loss terms
- training schedule
- data preprocessing differences
- inference / decoding changes
- metric computation

For every missing paper detail:

- infer the most defensible choice from the paper and upstream repo
- log it in `repro-logs/ASSUMPTIONS.md`
- keep the change isolated and reviewable

### Phase 7: Convert to Executable Experiment Plan

Once the code path is clear, generate:

- `refine-logs/EXPERIMENT_PLAN.md`
- `refine-logs/EXPERIMENT_TRACKER.md`

Map the reproduction into this run ladder:

1. `M0` sanity: repo boots, one tiny run, metric file emitted
2. `M1` baseline: upstream repo reproduces its own baseline or a close paper baseline
3. `M2` paper patch: paper-specific modifications enabled
4. `M3` reproduction: target table / metric / figure rerun
5. `M4` gap analysis: if numbers miss, run ablations on likely causes

Then hand off to `/experiment-bridge` for implementation cleanup and deployment, or reuse the same milestone structure directly if already in execution mode.

### Phase 8: Run, Monitor, and Judge Reproduction

Use:

- `/experiment-bridge` when the execution plan still needs structured implementation
- `/run-experiment` to launch runs
- `/monitor-experiment` to pull results
- `/training-check` when W&B is configured

Classify the final outcome as one of:

- **REPRODUCED** — target metrics are within the agreed tolerance
- **PARTIAL** — the core trend holds but absolute numbers miss
- **BLOCKED** — missing details, missing data, or missing compute prevent a fair attempt
- **NEGATIVE** — the paper claim does not hold under the reconstructed setup

Write the verdict and raw numbers back into `repro-logs/PAPER_REPRO_PLAN.md` and `repro-logs/REPRO_TRACKER.md`.

## Key Rules

- Prefer the nearest valid upstream repo, not the easiest repo.
- Always separate **paper facts** from **our reconstruction assumptions**.
- Reproduce the paper's metric and split before adding extra improvements.
- Never claim "reproduced" without raw numbers and the exact run command.
- If no code exists anywhere in the lineage, stop after producing the reverse-engineering plan and state the blocker clearly.

## Minimal Stack

If the user only wants paper reproduction, the practical stack is:

- `paper-reproduction`
- `experiment-bridge`
- `run-experiment`
- `monitor-experiment`
- `training-check` (optional)
- `arxiv` / `research-lit` only when paper lookup is incomplete
