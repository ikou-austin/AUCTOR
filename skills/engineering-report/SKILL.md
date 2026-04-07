---
name: engineering-report
description: "Auto-generate engineering reports from workflow logs. Collects metrics, generates comparison tables/charts, writes structured reports, and pushes to Feishu. Use when user says \"汇报\", \"report\", \"写报告\", \"生成汇报\", \"engineering report\", or wants a summary of reproduction/improvement/deployment work."
argument-hint: [report-scope-or-audience]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent, Skill, mcp__codex__codex, mcp__codex__codex-reply
---

# Engineering Report

Generate report for: **$ARGUMENTS**

## Goal

Automatically collect results from all AUCTOR workflow stages and generate a structured report suitable for stakeholder review. Supports incremental reports (any stage) and final comprehensive reports.

## Constants

- **REPORT_FORMAT = "markdown"** — Output format: markdown, html, or latex.
- **PUSH_FEISHU = true** — Auto-push report summary to Feishu when complete.
- **INCLUDE_CHARTS = true** — Generate comparison charts using Python matplotlib.
- **AUDIENCE = "technical"** — Report style: "technical" (full details), "executive" (summary only), "mixed" (summary + appendix).
- **LANGUAGE = "zh-CN"** — Report language: zh-CN, en.

> Override: `/engineering-report "Q2 model update" — audience: executive, language: en, push feishu: true`

## Inputs

This skill reads from all AUCTOR workflow log directories. All are optional — the report adapts to whatever is available.

```text
REPRO_TARGET.md                        # What was being reproduced
AUCTOR.md                              # Project context
repro-logs/                            # From /engineering-repro
  REPRO_TRACKER.md, REPRO_LOG.md, REPRO_PLAN.md, ASSUMPTIONS.md
improve-logs/                          # From /engineering-improve
  IMPROVE_TRACKER.md, IMPROVE_LOG.md, ACCEPTED_CHANGES.md
deploy-logs/                           # From /engineering-deploy
  DEPLOY_TRACKER.md, PERF_BENCHMARK.md, EXPORT_REPORT.md
```

## Files This Skill Maintains

```text
reports/
  REPORT_[date]_[scope].md             # Main report document
  figures/                             # Generated charts and tables
    comparison_chart.png
    improvement_trend.png
    deployment_metrics.png
```

## Workflow

### Phase 1: Collect Data

Scan for available log files and extract structured data:

1. **Reproduction data** (from `repro-logs/`):
   - Target vs actual metrics
   - Number of attempts, failure categories
   - Time spent, compute used

2. **Improvement data** (from `improve-logs/`):
   - Per-round A/B results
   - Accepted vs rejected changes
   - Cumulative improvement trajectory

3. **Deployment data** (from `deploy-logs/`):
   - Export accuracy validation
   - Performance benchmarks (latency, throughput, memory)
   - Integration test results

### Phase 2: Generate Visualizations (if INCLUDE_CHARTS = true)

Generate charts using Python + matplotlib:

1. **Improvement trajectory** — line chart showing metric progression across rounds
2. **A/B comparison** — grouped bar chart of baseline vs improved for each metric
3. **Deployment performance** — bar chart of latency/throughput across export formats
4. **Failure analysis** — pie chart of failure categories during reproduction (if applicable)

Save to `reports/figures/`.

### Phase 3: Write Report

Adapt report structure to AUDIENCE:

#### Technical Report (audience = "technical")

```markdown
# Engineering Report: [Scope]

**Date**: [date]
**Author**: AUCTOR (automated)
**Project**: [from AUCTOR.md]

## 1. Executive Summary
[2-3 sentences: what was done, key result, status]

## 2. Reproduction
### 2.1 Target
[from REPRO_TARGET.md]
### 2.2 Process
[attempts, key decisions, challenges]
### 2.3 Results
[target vs actual metrics table]
### 2.4 Assumptions Made
[from ASSUMPTIONS.md — what was inferred vs stated in paper]

## 3. Improvement
### 3.1 Improvement Hypotheses
[from IMPROVE_PLAN.md]
### 3.2 A/B Results
[per-round comparison table]
### 3.3 Accepted Changes
[what worked and by how much]
### 3.4 Rejected Changes
[what didn't work and why — equally important]
### 3.5 Cumulative Improvement
[chart: improvement trajectory]

## 4. Deployment
### 4.1 Export Validation
[accuracy before/after export]
### 4.2 Performance
[latency, throughput, memory table and chart]
### 4.3 Integration Tests
[pass/fail summary]

## 5. Resource Usage
- Total GPU-hours: [X]
- Wall-clock time: [Y]
- Attempts: [reproduction] + [improvement rounds] + [deployment iterations]

## 6. Open Issues & Risks
[any unresolved problems, known limitations, risks]

## 7. Recommendations
[next steps, future improvements, maintenance notes]

## Appendix
### A. Detailed Reproduction Log
[from REPRO_LOG.md]
### B. Full A/B Comparison Data
[raw numbers]
### C. Deployment Artifacts
[paths to exported models, configs, scripts]
```

#### Executive Report (audience = "executive")

Condensed version — sections 1, 2.3, 3.5, 4.2, 5, 7 only. No appendix. Charts only.

#### Mixed Report (audience = "mixed")

Executive summary up front, full technical details in collapsible appendix sections.

### Phase 4: Stakeholder Feedback Integration

If the report is generated mid-workflow (not final), include a feedback section:

```markdown
## Feedback Requested

Please review the above results and provide direction:

- [ ] **Continue improving**: [specify direction or accept current trajectory]
- [ ] **Change approach**: [specify new direction]
- [ ] **Deploy current version**: [accept current metrics]
- [ ] **Abandon and pivot**: [specify new target]

Respond via Feishu or update this section directly.
```

### Phase 5: Push to Feishu (if PUSH_FEISHU = true)

If Feishu is configured (`~/.claude/feishu.json` exists):

1. Format a condensed summary for Feishu message:
   - One-line status: [REPRODUCED/IMPROVED/DEPLOYED] + key metric
   - Key numbers in a compact table
   - Link to full report file

2. Send via `/feishu-notify`:
   - Use `report_ready` event type
   - Include the summary
   - If AUDIENCE = "executive", send the full executive report as the message body (it's short enough)

If Feishu is not configured, skip silently.

### Phase 6: Rapid Iteration on Feedback

When called again after stakeholder feedback:

1. Read feedback (from Feishu reply, updated report, or user message)
2. Translate feedback into actionable items:
   - If "continue improving" → generate new `/engineering-improve` hypotheses
   - If "change approach" → update `REPRO_TARGET.md` and restart
   - If "deploy current" → trigger `/engineering-deploy`
   - If "abandon" → document decision and archive
3. Trigger the appropriate downstream skill
4. After downstream completes, auto-generate an updated report

## Key Rules

- **Report what happened, not what you wished happened.** Include failures and rejected approaches.
- **Charts over tables when possible.** Stakeholders read charts faster.
- **Separate facts from interpretation.** Raw numbers first, analysis second.
- **Always include reproduction commands.** Any result should be reproducible from the report.
- **Language consistency.** Use LANGUAGE setting throughout. Don't mix languages.
- **Incremental reports are fine.** Don't wait for everything to be done.

## Composing with Other Skills

```
/engineering-repro "paper or requirement"    ← get verified baseline
/engineering-improve "[direction]"           ← improve baseline
/engineering-deploy "[target]"               ← deploy improved model
/engineering-report "[scope]"                ← you are here
/auctor-pipeline "requirement"               ← full end-to-end flow

Report can be generated at ANY stage — it adapts to available data.
```
