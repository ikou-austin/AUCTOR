# Reproduction Resources

## Code Search Results

| Source | URL | Overlap | Status |
|--------|-----|---------|--------|
| PyTorch official MNIST example | https://github.com/pytorch/examples/tree/main/mnist | High — same dataset, same task, modern CNN | SELECTED as reference |
| Original LeNet-5 (C code) | http://yann.lecun.com/exdb/lenet/ | Exact — but C, not usable directly | Reference only |

## Dataset

| Name | Source | Size | License |
|------|--------|------|---------|
| MNIST | `torchvision.datasets.MNIST(download=True)` | 60K train + 10K test, ~50MB | Public domain (Yann LeCun) |

## Backbone / Pretrained Models

Not applicable — training from scratch (small model, fast convergence).

## Decision

- **Path**: B (Paper-Only) — implement modern LeNet-5 variant in PyTorch
- **Reference**: PyTorch official MNIST example for code structure
- **Rationale**: Original 1998 code is in C; using PyTorch is the standard modern approach
