---
name: engineering-improve
description: "Iterative improvement over a verified baseline. A/B comparison, cross-model code review, and structured experiment tracking. Use when user says \"改进\", \"improve\", \"优化\", \"A/B对比\", \"engineering improve\", or has a verified baseline ready for modification."
argument-hint: [improvement-direction-or-requirement]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent, Skill, mcp__codex__codex, mcp__codex__codex-reply
---

# Engineering Improvement

Improve baseline for: **$ARGUMENTS**

## Goal

Take a verified baseline from `/engineering-repro` and iteratively improve it through structured experimentation: propose changes, implement, run A/B comparisons, review results, and decide whether to keep or discard each change.

## Constants

- **MAX_IMPROVEMENT_ROUNDS = 6** — Maximum improvement iterations before forcing a decision.
- **CODE_REVIEW = true** — Cross-model review of each improvement before running. Uses Codex MCP.
- **HUMAN_CHECKPOINT = false** — When `true`, pause after each round's A/B results for user approval. When `false`, auto-accept improvements that meet criteria.
- **IMPROVEMENT_THRESHOLD = 0.01** — Minimum relative improvement to accept a change (1%). Prevent noise from being accepted as progress.
- **REGRESSION_TOLERANCE = 0.005** — Maximum acceptable regression on non-target metrics (0.5%).
- **COMPACT = false** — When `true`, append results to `EXPERIMENT_LOG.md` for session recovery.

> Override: `/engineering-improve "reduce latency" — max rounds: 10, human checkpoint: true, threshold: 0.02`

## Inputs

1. **Verified baseline** from `/engineering-repro`:
   - `repro-logs/REPRO_TRACKER.md` — baseline metrics
   - Baseline checkpoint and run command
   - `repro-logs/REPRO_PLAN.md` — understanding of the method
2. **`FROZEN_SPEC.md`** — experiment fairness lock (REQUIRED)
3. **Improvement direction** from `$ARGUMENTS` or requirement document
4. **AUCTOR.md** — GPU config, compute budget, constraints

If no verified baseline exists, warn the user and suggest running `/engineering-repro` first.

**If `FROZEN_SPEC.md` does not exist, REFUSE to proceed.** The frozen spec is the fairness guarantee — without it, improvement results cannot be trusted.

## Files This Skill Maintains

```text
improve-logs/
  IMPROVE_PLAN.md              # Improvement hypotheses and priority
  IMPROVE_TRACKER.md           # Per-round A/B results
  IMPROVE_LOG.md               # Detailed log of each attempt
  ACCEPTED_CHANGES.md          # Cumulative list of accepted improvements
```

## Workflow

### Phase 1: Analyze Baseline and Generate Hypotheses

1. Read baseline results and method understanding from `repro-logs/`
2. Read improvement direction from arguments or requirement
3. Generate ranked improvement hypotheses:

```markdown
# Improvement Plan

## Baseline
- Method: [name]
- Key metric: [metric] = [value]
- Secondary metrics: [list]

## Improvement Hypotheses (ranked by expected impact)

### H1: [title] — Expected: +X%
- **What**: [description of the change]
- **Why**: [reasoning — paper insight, known technique, engineering intuition]
- **Risk**: [what could go wrong]
- **Effort**: [LOW / MEDIUM / HIGH]
- **Priority**: MUST-TRY

### H2: [title] — Expected: +Y%
...
```

4. Write to `improve-logs/IMPROVE_PLAN.md`

### Phase 1.5: Frozen Spec Compliance Check

Before ANY experiment, read `FROZEN_SPEC.md` and enforce:

| Section | Policy | On Violation |
|---------|--------|-------------|
| **Data Preparation** | FROZEN — no changes allowed | HALT and warn user |
| **Evaluation Protocol** | FROZEN — no changes allowed | HALT and warn user |
| **Data Augmentation** | NEEDS_USER_APPROVAL | Ask user; if approved, document as deliberate variable and re-run baseline with same augmentation for fair comparison |

**Before each round**, verify:
1. Training data is identical to `FROZEN_SPEC.md` (same files, same preprocessing)
2. Evaluation script/command matches `FROZEN_SPEC.md` exactly
3. Evaluation set (test split) is unchanged
4. No data leakage (test data not used in training/validation)

If a proposed hypothesis requires changing frozen items (e.g., "try a different dataset" or "use a different metric"), this is NOT an improvement — it is a new reproduction target. Redirect the user to `/engineering-repro` with a new `REPRO_TARGET.md`.

**Allowed modifications** (from `FROZEN_SPEC.md`):
- Feature extraction parameters
- Model architecture
- Training algorithm / optimizer / scheduler
- Hyperparameters
- Loss function
- Regularization

### Phase 2: Improvement Loop (repeat up to MAX_IMPROVEMENT_ROUNDS)

For each hypothesis (highest priority first):

#### 2.1: Implement the Change

- Create a new experiment branch or config variant
- Implement the proposed modification
- Keep the change isolated — one hypothesis per round
- **Verify the change does NOT touch any FROZEN items**

#### 2.2: Code Review (if CODE_REVIEW = true)

Send the diff to Codex MCP:

```
mcp__codex__codex:
  config: {"model_reasoning_effort": "xhigh"}
  prompt: |
    Review this improvement to [method].

    ## Baseline method:
    [summary]

    ## Proposed change:
    [diff or new code]

    ## Expected effect:
    [from hypothesis]

    Check:
    1. Is the change correctly implemented?
    2. Could it introduce regressions on other metrics?
    3. Any bugs or numerical issues?
    4. Is evaluation still fair (same ground truth, same splits)?
```

Fix CRITICAL issues. Skip if Codex unavailable.

#### 2.3: Run A/B Comparison

Run both baseline and improved version:
- Same dataset, same splits, same seeds (multiple seeds if possible)
- Same evaluation protocol
- Save results as JSON/CSV for comparison

If experiment needs GPU:
```
/run-experiment [improved version command]
```

#### 2.4: Evaluate Results

Compare improved vs baseline:

```markdown
## Round N: [Hypothesis title]

| Metric | Baseline | Improved | Delta | Significant? |
|--------|----------|----------|-------|--------------|
| [primary] | X.XX | Y.YY | +Z.ZZ (+W%) | Yes/No |
| [secondary] | ... | ... | ... | ... |

- Seeds tested: [list]
- Variance: [if multi-seed]
```

Decision criteria:
- **ACCEPT**: Primary metric improves >= IMPROVEMENT_THRESHOLD AND no secondary metric regresses > REGRESSION_TOLERANCE
- **REJECT**: Primary metric does not improve, or secondary metrics regress unacceptably
- **INCONCLUSIVE**: Improvement is within noise range — try more seeds or larger test set

#### 2.5: Decision

**If HUMAN_CHECKPOINT = true**: Present results and wait for user decision.

**If HUMAN_CHECKPOINT = false**: Auto-decide based on criteria above.

On ACCEPT:
- Merge improvement into the current best
- Update `improve-logs/ACCEPTED_CHANGES.md`
- The improved version becomes the new baseline for subsequent rounds

On REJECT:
- Revert the change
- Log why it failed in `improve-logs/IMPROVE_LOG.md`
- Move to next hypothesis

#### 2.6: Document Round

Append to `improve-logs/IMPROVE_TRACKER.md`:

```markdown
| Round | Hypothesis | Delta | Decision | Cumulative |
|-------|-----------|-------|----------|------------|
| 1 | H1: [title] | +2.3% | ACCEPT | +2.3% |
| 2 | H2: [title] | -0.1% | REJECT | +2.3% |
```

Append to `improve-logs/IMPROVE_LOG.md`:

```markdown
## Round N — [Hypothesis title] — [ACCEPT/REJECT]

### Change
[what was modified]

### Results
[A/B comparison table]

### Analysis
[why it worked or didn't]

### Decision
[ACCEPT/REJECT with reasoning]
```

When COMPACT = true, also append to `EXPERIMENT_LOG.md`.

### Phase 3: Termination

When loop ends (max rounds, all hypotheses tested, or user stops):

1. Write improvement summary:

```
Engineering Improvement complete:
- Baseline: [metric] = [original value]
- Final: [metric] = [improved value]
- Total improvement: +[delta] (+[percent]%)
- Rounds: [N], Accepted: [M], Rejected: [K]
- Accepted changes: [list]
- Checkpoint: [path to best model]
- Next step: /engineering-deploy "[method]"
```

2. Update `improve-logs/ACCEPTED_CHANGES.md` with final cumulative summary

3. The improved checkpoint is ready for `/engineering-deploy`

### Phase 4: Re-entry from Feedback

When called after `/engineering-report` with user/stakeholder feedback:

1. Read feedback from the report or user message
2. Generate new improvement hypotheses based on feedback
3. Append to `improve-logs/IMPROVE_PLAN.md`
4. Resume Phase 2 loop with the new hypotheses

## Key Rules

- **FROZEN_SPEC.md is law.** Data preparation and evaluation protocol are locked after reproduction. Violating this invalidates all improvement results. No exceptions without explicit user approval + re-baselining.
- **One change per round.** Never stack multiple hypotheses in a single A/B test.
- **Fair comparison.** Same data, same splits, same seeds, same evaluation. Always. This is enforced by FROZEN_SPEC.md.
- **Track everything.** Every round must be logged, even rejected ones.
- **No cherry-picking.** Report all seeds, not just the best one.
- **Budget awareness.** Track GPU-hours against AUCTOR.md budget.
- **Reuse baseline infrastructure.** Don't rewrite training code — modify configs and minimal code.
- **Ground truth.** Evaluation must use dataset ground truth, never another model's output.
- **Augmentation is a gray area.** Changing data augmentation (noise/reverb/speed for speech, crop/flip for vision) may be legitimate but MUST be flagged to the user and the baseline MUST be re-run with the same augmentation for fair comparison.

## Composing with Other Skills

```
/engineering-repro "paper or requirement"    ← get verified baseline
/engineering-improve "[direction]"           ← you are here
/engineering-deploy "[method]"               ← deploy improved model
/engineering-report                          ← generate improvement report
/auctor-pipeline "requirement"               ← full end-to-end flow
```
