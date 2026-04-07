# Reproduction Plan

## Selected Approach
- **Path**: B (Paper-Only) — no usable code, implement from reference
- **Reference repo**: PyTorch MNIST example
- **What we implement**: LeNet-5 style CNN with modern PyTorch conventions

## Architecture
- Conv2d(1, 32, 3) → ReLU → Conv2d(32, 64, 3) → ReLU → MaxPool → Dropout → FC(9216, 128) → ReLU → Dropout → FC(128, 10)
- This is a standard modernized LeNet-5 that should reach 99%+ on MNIST

## Environment
- Python 3.10+
- PyTorch 2.x (Colab default)
- torchvision (for dataset and transforms)
- No additional dependencies

## Data Preparation
- `torchvision.datasets.MNIST(download=True)`
- Transform: ToTensor() + Normalize((0.1307,), (0.3081,))
- Standard 60K/10K split

## Training Configuration
- Optimizer: Adam, lr=1e-3
- Epochs: 10 (should be sufficient for 99%+)
- Batch size: 64
- Seed: 42

## Evaluation
- Metric: Test accuracy (correct / total)
- Target: >= 99.0%
- Tolerance: 0.5%

## Milestones

| ID | Stage | Goal | Status |
|----|-------|------|--------|
| M0 | sanity | imports, data loads, 1 batch forward+backward | PENDING |
| M1 | train | full 10-epoch training | PENDING |
| M2 | eval | test accuracy >= 99.0% | PENDING |
