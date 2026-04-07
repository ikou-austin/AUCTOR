---
name: engineering-repro
description: "Engineering reproduction: from paper/requirement to verified baseline. Handles code-available and paper-only paths, automatic failure diagnosis loop, and human escalation. Use when user says \"复现\", \"reproduce\", \"engineering repro\", \"跑通baseline\", \"复现论文\", or wants to reproduce a paper/method on a target dataset."
argument-hint: [paper-url-or-requirement-description]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent, Skill, mcp__codex__codex, mcp__codex__codex-reply
---

# Engineering Reproduction

Reproduce and verify: **$ARGUMENTS**

## Goal

Take a paper, method description, or engineering requirement and turn it into a verified, running baseline with reproducible benchmark numbers. This skill handles the messy reality of reproduction: missing code, incompatible datasets, broken environments, and unclear paper details.

## Constants

- **MAX_RETRIES = 5** — Maximum fix-and-retry cycles before escalating to human.
- **BENCHMARK_TOLERANCE = 0.02** — Acceptable relative deviation from reported numbers (2%). Override per metric in `REPRO_TARGET.md`.
- **AUTO_ESCALATE = true** — When `true`, automatically sends Feishu notification on escalation. When `false`, only writes the stuck report.
- **CODE_REVIEW = true** — Cross-model review of implemented code before running. Uses Codex MCP.
- **SANITY_FIRST = true** — Run a minimal sanity check before full reproduction.

> Override: `/engineering-repro "paper.pdf" — max retries: 8, tolerance: 0.05, code review: false`

## Inputs (in preference order)

1. `REPRO_TARGET.md` at project root (best — pre-filled target spec)
2. A paper PDF path or arXiv URL
3. A requirement document describing the method to reproduce
4. A paper title + venue/year + brief description

If `REPRO_TARGET.md` does not exist, create it from `templates/PAPER_REPRO_TARGET_TEMPLATE.md` when available. If the template is not present, generate the same structure inline.

## Files This Skill Maintains

```text
REPRO_TARGET.md              # Frozen reproduction target (what to reproduce)
repro-logs/
  REPRO_RESOURCES.md         # Collected resources (code, data, models)
  REPRO_PLAN.md              # Reverse-engineering plan
  REPO_LINEAGE.md            # Code search trail and ancestry
  ASSUMPTIONS.md             # Paper facts vs our reconstruction guesses
  REPRO_TRACKER.md           # Milestone execution table
  REPRO_LOG.md               # Per-attempt failure analysis and fix log
  REPRO_STUCK_REPORT.md      # Generated on escalation (human intervention request)
```

## Workflow

### Phase 1: Freeze the Reproduction Target

Read the paper/requirement and write `REPRO_TARGET.md`:

- Exact paper identity (title, authors, venue, year, URL)
- What must be reproduced: specific table, figure, metric, or claim
- Target numbers and acceptable tolerance per metric
- Compute budget and hardware constraints
- Dataset requirements (name, version, splits)
- Whether official code is required or upstream base repos are acceptable

Rules:
- Do NOT accept a vague target like "reproduce the whole paper". Break into primary target (one table/metric) and optional secondary targets.
- If the requirement comes from an engineering need (not a paper), still formalize it as a `REPRO_TARGET.md` with clear success criteria.

### Phase 2: Resource Collection

Search for and document all reproduction resources in `repro-logs/REPRO_RESOURCES.md`.

#### 2a: Code Search (descending preference)

1. Paper abstract page, project page, appendix, supplementary material
2. Authors' GitHub / lab repos
3. Benchmark/dataset leaderboards mentioned by the paper
4. Cited implementation repos for the immediate parent method
5. Open-source repos for the backbone / base model / trainer

Record every candidate in `repro-logs/REPO_LINEAGE.md` with:
- URL, stars, last commit date, license
- Architectural overlap with target paper
- Data/metric compatibility assessment
- Known issues (from GitHub Issues, README caveats)

#### 2b: Dataset Search

1. Official dataset links from the paper
2. Dataset hosting platforms (HuggingFace, Kaggle, OpenDataLab, ModelScope)
3. Alternative datasets if official is unavailable (document the deviation)

For each dataset, record: URL, size, format, license, preprocessing requirements.

#### 2c: Backbone / Pretrained Model Search

1. Official pretrained weights from the paper
2. HuggingFace / ModelScope model hubs
3. Upstream repo's pretrained checkpoints

For each model, record: URL, framework, input format, expected performance.

### Phase 3: Determine Reproduction Path

Based on Phase 2 results, classify into one of two paths:

```
Path A: Code Available
  - Official repo or high-quality community implementation found
  - Proceed to environment setup and direct reproduction

Path B: Paper Only (no usable code)
  - No code, or code is unusable (wrong framework, broken, license issue)
  - Need to find backbone and implement from paper description
```

Write the decision and rationale to `repro-logs/REPRO_PLAN.md`.

### Phase 4A: Code-Available Path

#### 4A.1: Environment Setup

1. Clone the repository
2. Inspect README, requirements, Dockerfiles, setup scripts
3. Resolve dependency conflicts:
   - Pin Python version to match repo's CI or README
   - Handle CUDA version mismatches
   - Fix deprecated API calls if needed
4. Document exact environment commands in `repro-logs/REPRO_PLAN.md`

#### 4A.2: Data Preparation

1. Download/prepare dataset per repo instructions
2. Verify data format matches what the code expects
3. Check train/val/test splits match the paper
4. If dataset version differs from paper, document in `repro-logs/ASSUMPTIONS.md`

#### 4A.3: Sanity Run (if SANITY_FIRST = true)

Before full training, run a minimal sanity check:
- Tiny subset of data (1-2 batches)
- Verify: imports work, data loads, forward pass runs, loss computes, backward pass works, metrics emit
- Check GPU memory usage is within bounds

If sanity fails → enter Phase 5 (Failure Loop) immediately.

#### 4A.4: Full Reproduction Run

1. Run training/inference with paper's hyperparameters
2. Log all metrics (wandb if configured in AUCTOR.md)
3. Compare results against `REPRO_TARGET.md` benchmarks
4. If within BENCHMARK_TOLERANCE → Phase 6 (Success)
5. If outside tolerance → Phase 5 (Failure Loop)

### Phase 4B: Paper-Only Path

#### 4B.1: Recursive Base-Repo Backtracking

If no official implementation exists, move upward through the method lineage until a usable open-source base is found:

1. **Paper method repo** — exact paper implementation
2. **Immediate parent method repo** — the method this paper extends
3. **Base model repo** — backbone, pretrained model, trainer stack
4. **Benchmark harness repo** — task-specific training/eval pipeline

At each level:
- Identify what the paper adds on top of that layer
- Search for open-source repos implementing that layer
- Rank by architectural overlap and data/metric compatibility
- Stop at the nearest repo that covers most of the pipeline with a patchable gap

Never jump to an unrelated repo just because it is popular. If the lineage is speculative, write that in `repro-logs/ASSUMPTIONS.md`.

#### 4B.2: Implement from Paper

On top of the selected backbone/base:

1. Implement architecture changes described in the paper
2. Implement loss functions / training procedures
3. Implement data preprocessing pipeline
4. Implement evaluation metrics matching the paper

For every missing detail:
- Infer the most defensible choice from the paper + upstream code
- Log it in `repro-logs/ASSUMPTIONS.md`
- Keep changes isolated and reviewable

#### 4B.3: Cross-Model Code Review (if CODE_REVIEW = true)

Send implementation to external reviewer via Codex MCP:

```
mcp__codex__codex:
  config: {"model_reasoning_effort": "xhigh"}
  prompt: |
    Review this implementation of [paper title] based on [backbone repo].

    ## Paper method summary:
    [key method details]

    ## Implementation:
    [paste code]

    Check for:
    1. Does the code correctly implement the method described in the paper?
    2. Are architecture changes correct (dimensions, operations, connections)?
    3. Is the loss function implemented correctly?
    4. Is evaluation using dataset ground truth (NOT another model's output)?
    5. Any potential issues (OOM, numerical instability, shape mismatches)?

    For each issue: CRITICAL / MAJOR / MINOR and the exact fix.
```

Fix CRITICAL issues before proceeding. Max 2 review rounds.

If Codex MCP is unavailable, skip silently and proceed.

#### 4B.4: Run Reproduction

Same as 4A.3 (sanity) → 4A.4 (full run).

### Phase 5: Failure Diagnosis Loop

**Triggered when**: benchmark metrics deviate beyond BENCHMARK_TOLERANCE, or runtime errors prevent completion.

For each retry (up to MAX_RETRIES):

#### 5.1: Analyze Failure

Classify the failure into one of these categories:

| Category | Symptoms | Typical Fix |
|----------|----------|-------------|
| **Environment** | ImportError, CUDA mismatch, version conflict | Pin versions, install missing deps, switch CUDA |
| **Data** | Shape mismatch, wrong splits, missing files | Re-download, reformat, check preprocessing |
| **Code Bug** | NaN loss, wrong dimensions, logic error | Debug, fix implementation, check paper details |
| **Hyperparameter** | Converges but wrong numbers, unstable training | Adjust LR, batch size, epochs, scheduler |
| **Paper Ambiguity** | Multiple valid interpretations, missing details | Try alternatives, check cited works, contact authors |
| **Resource** | OOM, disk full, timeout | Reduce batch, gradient checkpointing, bigger machine |

#### 5.2: Apply Fix

- Fix exactly ONE suspected cause per retry (isolate variables)
- Document in `repro-logs/REPRO_LOG.md`:

```markdown
## Attempt N (timestamp)
- **Failure category**: [category]
- **Symptom**: [what went wrong]
- **Diagnosis**: [why we think this is the cause]
- **Fix applied**: [what we changed]
- **Files modified**: [list]
- **Result**: [PENDING — will be filled after re-run]
```

#### 5.3: Re-run and Evaluate

- Run the reproduction again with the fix
- Compare against target benchmarks
- Update `REPRO_LOG.md` with the result
- If within tolerance → Phase 6 (Success)
- If still failing → back to 5.1 with the new information

#### 5.4: Escalation (after MAX_RETRIES exhausted)

Generate `repro-logs/REPRO_STUCK_REPORT.md`:

```markdown
# Reproduction Stuck Report

## Target
[from REPRO_TARGET.md]

## Attempts Summary
| # | Category | Fix | Result | Gap |
|---|----------|-----|--------|-----|
| 1 | Environment | Fixed CUDA 11.8→12.1 | Runtime error resolved | - |
| 2 | Data | Re-downloaded dataset v2 | Metrics still 5% off | 5% |
| ... | ... | ... | ... | ... |

## Current Best Result
- Metric: X.XX (target: Y.YY, gap: Z%)
- Run command: `python train.py --config ...`
- Checkpoint: `checkpoints/best_attempt_N.pt`

## Root Cause Analysis
[Best guess at why reproduction is failing]

## Recommended Human Actions
1. [Most likely fix that requires human judgment]
2. [Alternative approach]
3. [External resource needed]

## Decision Needed
- [ ] Continue with more attempts (provide hints below)
- [ ] Accept current best result as baseline (gap: Z%)
- [ ] Abandon this reproduction target
- [ ] Try alternative paper/method

## Human Hints (fill in if continuing)
[Space for human to provide additional context, correct assumptions, etc.]
```

If AUTO_ESCALATE = true and Feishu is configured:
- Send notification via `/feishu-notify` with summary and link to stuck report
- Wait for human response

If human provides hints → restart from Phase 5.1 with new information, reset retry counter to MAX_RETRIES/2 (give a few more attempts with the new hints).

### Phase 6: Success — Freeze Baseline

When reproduction succeeds (metrics within tolerance):

1. **Record verified results** in `repro-logs/REPRO_TRACKER.md`:

```markdown
| ID | Stage | Goal | Metric | Target | Actual | Status |
|----|-------|------|--------|--------|--------|--------|
| R0 | repo  | find base code | - | - | [repo URL] | DONE |
| R1 | env   | setup environment | - | - | Python 3.10, CUDA 12.1 | DONE |
| R2 | data  | prepare dataset | - | - | [dataset, N samples] | DONE |
| R3 | repro | reproduce benchmark | [metric] | [target] | [actual] | REPRODUCED |
```

2. **Save baseline artifacts**:
   - Best checkpoint path
   - Exact run command
   - Environment snapshot (pip freeze or conda env export)
   - Config file used

3. **Update `REPRO_TARGET.md`** with final verdict: REPRODUCED / PARTIAL / ACCEPTED_WITH_GAP

4. **Handoff**: The verified baseline is now ready for `/engineering-improve`.

```
Reproduction complete:
- Target: [paper/method]
- Status: REPRODUCED
- Metric: [name] = [value] (target: [target], tolerance: [tol])
- Attempts: [N] (including [M] fix cycles)
- Baseline checkpoint: [path]
- Next step: /engineering-improve "[method]"
```

## Key Rules

- **Large file handling**: If the Write tool fails due to file size, retry using Bash to write in chunks. Do not ask permission.
- **One fix per retry.** Changing multiple things at once makes diagnosis impossible.
- **Paper facts vs assumptions.** Always separate in `ASSUMPTIONS.md`. Never present an assumption as a paper fact.
- **Ground truth evaluation.** ALWAYS compare against dataset ground truth labels, NEVER against another model's output.
- **Don't fabricate results.** If reproduction fails, report it honestly.
- **Budget awareness.** Track GPU-hours. Warn if approaching limits from AUCTOR.md.
- **Reuse existing code.** Scan the project before writing new scripts. Extend, don't duplicate.
- **Determinism.** Fix random seeds. Log seeds in run commands.

## Composing with Other Skills

```
/engineering-repro "paper or requirement"    ← you are here
/engineering-improve "[method]"              ← after baseline is verified
/engineering-deploy "[method]"               ← after improvement is validated
/engineering-report                          ← generate reports at any stage
/auctor-pipeline "requirement"               ← full end-to-end flow
```
