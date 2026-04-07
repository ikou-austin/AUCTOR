# Improvement Log

## Round 1 — BatchNorm + CosineAnnealing — REJECT

### Change
- Added BatchNorm2d after each conv layer
- Added CosineAnnealingLR scheduler (T_max=3)

### Results
| Metric | Baseline | Improved | Delta |
|--------|----------|----------|-------|
| Best Test Acc | 0.9906 | 0.9892 | -0.0014 |
| Training Time | 284.9s | 330.7s | +45.8s |

### Analysis
CosineAnnealing with only 3 epochs is too aggressive — LR drops to 0.0 by epoch 3, preventing further learning. BatchNorm adds overhead without benefit on a trivial dataset like MNIST.

### Decision
**REJECT** — accuracy decreased, training time increased.

## Round 2 — Data Augmentation + Wider Model — ACCEPT

### Change
- Data augmentation: RandomRotation(±10°), RandomAffine(translate=10%)
- Wider model: 64→128 channels, 256 FC hidden units (vs 32→64, 128 FC)

### Results
| Metric | Baseline | Improved v2 | Delta |
|--------|----------|-------------|-------|
| Best Test Acc | 0.9906 | 0.9913 | +0.0007 |
| Training Time | 284.9s | 807.8s | +522.9s |

### Analysis
Data augmentation + wider model achieved a small but positive improvement (+0.07%). Training time increased significantly due to wider model and augmentation overhead. On a saturated task like MNIST, this is about the maximum expected gain from architectural changes alone.

### Decision
**ACCEPT** — accuracy improved, direction is correct. Wider model + augmentation is the accepted improvement.

## Cumulative Summary
| Round | Hypothesis | Delta | Decision |
|-------|-----------|-------|----------|
| 1 | BatchNorm + CosineAnnealing | -0.14% | REJECT |
| 2 | Data Augmentation + Wider Model | +0.07% | ACCEPT |
