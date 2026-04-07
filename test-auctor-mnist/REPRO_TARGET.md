# Reproduction Target

## Paper Identity
- **Title**: Gradient-Based Learning Applied to Document Recognition
- **Authors**: Y. LeCun, L. Bottou, Y. Bengio, P. Haffner
- **Venue**: Proceedings of the IEEE, 1998
- **URL**: http://yann.lecun.com/exdb/publis/pdf/lecun-98.pdf

## What to Reproduce
- **Primary target**: LeNet-5 style CNN on MNIST test set
- **Metric**: Test accuracy
- **Target value**: >= 99.0% (modern PyTorch implementation of a simple CNN easily reaches this)
- **Tolerance**: 0.5% (i.e., >= 98.5% is acceptable)

## Dataset
- **Name**: MNIST
- **Source**: `torchvision.datasets.MNIST`
- **Train**: 60,000 images
- **Test**: 10,000 images
- **Format**: 28x28 grayscale

## Compute Constraints
- **Hardware**: Google Colab, single T4/L4 GPU
- **Time budget**: < 10 minutes total training
- **Framework**: PyTorch

## Code Availability
- **Official code**: No (1998 paper, original code in C)
- **Path**: Paper-only → use PyTorch to implement a modern LeNet-5 variant
- **Reference**: PyTorch MNIST tutorial (https://github.com/pytorch/examples/tree/main/mnist)

## Success Criteria
- [ ] Model trains without errors on Colab
- [ ] Test accuracy >= 99.0%
- [ ] Training completes in < 10 minutes
- [ ] Results saved as JSON for downstream skills
