# Assumptions

## Paper Facts vs Reconstruction Choices

| # | Paper Fact | Our Choice | Justification |
|---|-----------|------------|---------------|
| 1 | LeNet-5 uses 5x5 convolutions, tanh activations, subsampling | We use 3x3 conv, ReLU, MaxPool | Modern equivalent; goal is reaching the benchmark, not exact architectural reproduction |
| 2 | Original trained on full MNIST | Same — using standard 60K/10K split | Direct match |
| 3 | Original reported ~99.05% (Table II) | Target >= 99.0% | Aligns with original claim |
| 4 | Original used custom C implementation | PyTorch implementation | Framework change is expected and standard |
