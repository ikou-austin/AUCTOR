# Paper Reproduction Plan

> Written by `/paper-reproduction`. Save as `repro-logs/PAPER_REPRO_PLAN.md`.

## Target Summary

- **Paper**:
- **Primary reproduction target**:
- **Tolerance**:
- **Hardware / budget**:

## Code Source Decision

- **Official repo found?**: yes / no
- **Selected repo**:
- **Why this repo**:
- **Rejected candidates**:

## Repo Lineage

| Level | Candidate | URL / Path | Overlap | Decision | Notes |
|-------|-----------|------------|---------|----------|-------|
| Paper |           |            |         |          |       |
| Parent method |   |            |         |          |       |
| Base model |      |            |         |          |       |
| Benchmark harness | |          |         |          |       |

## Repo-to-Paper Delta

- **Architecture changes**:
- **Loss / objective changes**:
- **Training recipe changes**:
- **Inference / decoding changes**:
- **Metric / evaluation changes**:
- **Data preprocessing changes**:

## Environment Plan

- **Base environment**:
- **Install commands**:
- **CUDA / Python / framework constraints**:
- **Expected entrypoints**:

## Data Plan

- **Dataset acquisition**:
- **Preprocessing steps**:
- **Expected directory layout**:
- **Potential licensing or access blockers**:

## Execution Ladder

| Milestone | Goal | Expected artifact | Pass condition |
|-----------|------|-------------------|----------------|
| M0 | Repo sanity | log + metric file | one tiny run completes |
| M1 | Upstream baseline | baseline metric | close to upstream / paper baseline |
| M2 | Paper patch | patched checkpoint / result | paper-specific modules active |
| M3 | Reproduction run | target metric | within tolerance or trend matches |
| M4 | Gap analysis | ablation notes | reasons for miss identified |

## Assumptions

- **Explicit assumptions made during reconstruction**:

## Final Verdict

- **Status**: TODO
- **Best metric so far**:
- **Gap vs paper**:
- **Next unblocker**:
