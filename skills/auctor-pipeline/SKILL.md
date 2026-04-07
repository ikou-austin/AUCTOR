---
name: auctor-pipeline
description: "Full AUCTOR engineering pipeline: reproduction → improvement → deployment → reporting → feedback loop. Use when user says \"全流程\", \"auctor pipeline\", \"end to end\", \"从复现到落地\", \"full pipeline\", or wants the complete automated engineering lifecycle."
argument-hint: [paper-or-requirement]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent, Skill, mcp__codex__codex, mcp__codex__codex-reply
---

# AUCTOR Pipeline: Reproduction → Improvement → Deployment → Report

End-to-end engineering workflow for: **$ARGUMENTS**

## Constants

- **AUTO_PROCEED = false** — When `true`, gates auto-proceed after presenting results. When `false` (default), wait for user confirmation at each gate.
- **SKIP_DEPLOY = false** — When `true`, skip the deployment stage (useful for research-only tasks).
- **SKIP_IMPROVE = false** — When `true`, skip improvement and go directly to deployment after reproduction.
- **MAX_RETRIES = 5** — Passed to `/engineering-repro`.
- **MAX_IMPROVEMENT_ROUNDS = 6** — Passed to `/engineering-improve`.
- **CODE_REVIEW = true** — Passed to all stages.
- **HUMAN_CHECKPOINT = false** — Passed to `/engineering-improve`. When `true`, pause after each A/B comparison.
- **PUSH_FEISHU = true** — Passed to `/engineering-report`.
- **REPORT_AUDIENCE = "mixed"** — Passed to `/engineering-report`.

> Override: `/auctor-pipeline "paper.pdf" — auto proceed: true, skip deploy: true, human checkpoint: true`

## Overview

```
Stage 1                    Stage 2                Stage 3               Stage 4
/engineering-repro    →   /engineering-improve  → /engineering-deploy → /engineering-report
├── find code/data        ├── hypothesize          ├── export model       ├── collect all logs
├── setup env             ├── implement            ├── optimize           ├── generate charts
├── reproduce baseline    ├── A/B compare          ├── benchmark          ├── write report
├── failure loop          ├── accept/reject        ├── integration test   ├── push feishu
└── verify metrics        └── track cumulative     └── verify deploy      └── feedback loop
                                                                               ↓
                                                                          Stage 2 (re-entry)
```

## Pipeline State

Maintain `AUCTOR.md` in project root as the pipeline dashboard:

```markdown
# AUCTOR Pipeline Status

## Project
- Requirement: [description]
- Paper: [title, if applicable]
- Started: [date]

## Pipeline Status
- Stage: [repro / improve / deploy / report / feedback]
- Current skill: [active skill name]
- Last update: [timestamp]

## Configuration
- GPU: [server/device info]
- Compute budget: [hours]
- WandB: [project name, if configured]

## Stage Results
- Reproduction: [REPRODUCED / PARTIAL / IN_PROGRESS / BLOCKED]
- Improvement: [+X% / IN_PROGRESS / SKIPPED]
- Deployment: [DEPLOYED / STAGING / IN_PROGRESS / SKIPPED]
- Report: [DELIVERED / IN_PROGRESS / PENDING]
```

## Pipeline Stages

### Stage 1: Engineering Reproduction

```
/engineering-repro "$ARGUMENTS" — max retries: $MAX_RETRIES, code review: $CODE_REVIEW
```

Update `AUCTOR.md`: Stage = repro.

**Gate 1 — Reproduction Checkpoint:**

```
Stage 1 complete:
- Target: [paper/method]
- Status: [REPRODUCED / PARTIAL / ACCEPTED_WITH_GAP]
- Key metric: [name] = [value] (target: [target])
- Attempts: [N]

Options:
→ "continue" — proceed to improvement
→ "accept gap" — accept current baseline despite gap, proceed
→ "retry with hints" — provide additional context for more reproduction attempts
→ "stop" — end pipeline, generate report of what we have
```

If REPRODUCED or user accepts → proceed.
If BLOCKED and human provides hints → re-enter Stage 1.
If user stops → jump to Stage 4 (report what we have).

If AUTO_PROCEED = true: auto-proceed after 30 seconds if REPRODUCED. If PARTIAL/BLOCKED, always wait for human.

### Stage 2: Engineering Improvement (unless SKIP_IMPROVE = true)

Read improvement direction from:
1. User's explicit instructions (from Gate 1 response)
2. `$ARGUMENTS` if it contains improvement keywords
3. Generic: "improve [primary metric] while maintaining [secondary metrics]"

```
/engineering-improve "[direction]" — max rounds: $MAX_IMPROVEMENT_ROUNDS, code review: $CODE_REVIEW, human checkpoint: $HUMAN_CHECKPOINT
```

Update `AUCTOR.md`: Stage = improve.

**Gate 2 — Improvement Checkpoint:**

```
Stage 2 complete:
- Baseline: [metric] = [original]
- Improved: [metric] = [improved] (+[delta]%)
- Rounds: [N], Accepted changes: [M]
- Top improvements: [list]

Options:
→ "deploy" — proceed to deployment with current best
→ "keep improving" — continue with new hypotheses [specify direction]
→ "revert to round N" — go back to a specific accepted state
→ "stop" — end pipeline, generate report
```

If AUTO_PROCEED = true and improvement > 0: auto-proceed to deploy after 30 seconds.

### Stage 3: Engineering Deployment (unless SKIP_DEPLOY = true)

```
/engineering-deploy "$ARGUMENTS"
```

Update `AUCTOR.md`: Stage = deploy.

**Gate 3 — Deployment Checkpoint:**

```
Stage 3 complete:
- Model exported: [format]
- Accuracy: [original] → [exported] (delta: [X])
- Latency: [p50]ms / [p99]ms
- Integration tests: [pass rate]

Options:
→ "report" — generate final report
→ "optimize more" — continue performance optimization
→ "stop" — end pipeline
```

### Stage 4: Engineering Report

```
/engineering-report "$ARGUMENTS" — audience: $REPORT_AUDIENCE, push feishu: $PUSH_FEISHU
```

Update `AUCTOR.md`: Stage = report.

### Stage 5: Feedback Loop

After the report is delivered, the pipeline enters standby for feedback:

```
AUCTOR Pipeline complete. Report delivered.

Awaiting stakeholder feedback:
→ "modify [aspect]" — re-enter improvement stage with specific direction
→ "redeploy" — re-enter deployment with updated model
→ "new target" — start a new reproduction target
→ "update report" — regenerate report with additional context
→ "done" — archive and close
```

When feedback arrives:
1. Parse the feedback type
2. Route to the appropriate stage:
   - Improvement feedback → Stage 2 (re-entry)
   - Deployment feedback → Stage 3 (re-entry)
   - New target → Stage 1 (fresh start)
   - Report update → Stage 4 (regenerate)
3. After the stage completes, auto-generate an updated report (Stage 4)
4. Return to feedback standby

Update `AUCTOR.md` with each re-entry.

## Session Recovery

If the pipeline is interrupted (context compaction, crash, etc.):

1. Read `AUCTOR.md` for current stage and status
2. Read the appropriate `*-logs/` directory for detailed state
3. Resume from the current stage's last checkpoint
4. Log: "AUCTOR Pipeline recovered. Resuming at Stage [N]: [name]."

## Key Rules

- **Gates are mandatory.** Never skip a gate unless AUTO_PROCEED is true AND the result is clearly positive.
- **Report at any stage.** If the user asks for a report mid-pipeline, generate one with available data and resume.
- **Fail gracefully.** If any stage fails irrecoverably, generate a report of everything up to that point.
- **Budget tracking.** Maintain running GPU-hour total in `AUCTOR.md`. Warn at 80% of budget.
- **Don't loop forever.** Each stage has its own max iterations. Respect them.
- **AUCTOR.md is the source of truth.** Update it after every significant state change.

## Typical Timeline

| Stage | Duration | Can run unattended? |
|-------|----------|---------------------|
| 1. Reproduction | 30min - 4hrs (depends on retries) | Yes if AUTO_PROCEED=true |
| 2. Improvement | 1-8hrs (depends on rounds) | Yes if HUMAN_CHECKPOINT=false |
| 3. Deployment | 30min - 2hrs | Yes |
| 4. Report | 5-15min | Yes |
| 5. Feedback | Async (human dependent) | N/A |

**Overnight mode**: Set `AUTO_PROCEED=true`, `HUMAN_CHECKPOINT=false`, launch before sleep. Wake up to a report with verified reproduction, iterative improvements, and deployment-ready artifacts.

## Entry Points

The pipeline supports starting from any stage:

```
/auctor-pipeline "full requirement"              ← start from Stage 1
/engineering-repro "just reproduce this"          ← Stage 1 only
/engineering-improve "improve latency"            ← Stage 2 only (needs existing baseline)
/engineering-deploy "deploy to production"        ← Stage 3 only (needs improved model)
/engineering-report "Q2 summary"                  ← Stage 4 only (needs any logs)
```
