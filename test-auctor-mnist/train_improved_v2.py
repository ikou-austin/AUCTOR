"""AUCTOR Stage 2, Round 2: Data Augmentation + Wider Model.

Hypothesis: augmentation forces better generalization, wider model adds capacity.
"""

import argparse
import json
import os
import time

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms


class LeNet5Wide(nn.Module):
    """Wider variant: 64 and 128 channels instead of 32 and 64."""

    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 64, 3, 1)
        self.conv2 = nn.Conv2d(64, 128, 3, 1)
        self.dropout1 = nn.Dropout(0.25)
        self.dropout2 = nn.Dropout(0.5)
        self.fc1 = nn.Linear(128 * 12 * 12, 256)
        self.fc2 = nn.Linear(256, 10)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        x = self.dropout2(x)
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)


def train_epoch(model, device, train_loader, optimizer, epoch):
    model.train()
    total_loss, correct, total = 0.0, 0, 0
    for data, target in train_loader:
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * data.size(0)
        pred = output.argmax(dim=1, keepdim=True)
        correct += pred.eq(target.view_as(pred)).sum().item()
        total += data.size(0)
    print(f"Epoch {epoch}: train_loss={total_loss/total:.4f}, train_acc={correct/total:.4f}")
    return total_loss / total, correct / total


def evaluate(model, device, test_loader):
    model.eval()
    test_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.nll_loss(output, target, reduction="sum").item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += data.size(0)
    acc = correct / total
    print(f"Test: loss={test_loss/total:.4f}, accuracy={acc:.4f} ({correct}/{total})")
    return test_loss / total, acc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=str, default="results")
    parser.add_argument("--save-model", action="store_true", default=True)
    parser.add_argument("--variant", type=str, default="improved_v2_wide_aug")
    parser.add_argument("--device", type=str, default="cpu")
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    os.makedirs(args.output_dir, exist_ok=True)
    device = torch.device(args.device)
    print(f"Device: {device}")

    train_transform = transforms.Compose([
        transforms.RandomRotation(10),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,)),
    ])
    test_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,)),
    ])

    train_dataset = datasets.MNIST("./data", train=True, download=False, transform=train_transform)
    test_dataset = datasets.MNIST("./data", train=False, download=False, transform=test_transform)
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=1000)

    model = LeNet5Wide().to(device)
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    start_time = time.time()
    history = []
    for epoch in range(1, args.epochs + 1):
        tl, ta = train_epoch(model, device, train_loader, optimizer, epoch)
        vl, va = evaluate(model, device, test_loader)
        history.append({"epoch": epoch, "train_loss": round(tl, 6),
                        "train_acc": round(ta, 6), "test_loss": round(vl, 6), "test_acc": round(va, 6)})
    elapsed = time.time() - start_time

    results = {
        "variant": args.variant,
        "improvements": ["Data augmentation (rotation ±10°, translate 10%)", "Wider model (64→128 channels, 256 FC)"],
        "config": {"epochs": args.epochs, "batch_size": args.batch_size, "lr": args.lr,
                   "seed": args.seed, "device": str(device)},
        "final_test_accuracy": history[-1]["test_acc"],
        "final_test_loss": history[-1]["test_loss"],
        "best_test_accuracy": max(h["test_acc"] for h in history),
        "training_time_seconds": round(elapsed, 1),
        "history": history,
    }
    with open(os.path.join(args.output_dir, f"results_{args.variant}.json"), "w") as f:
        json.dump(results, f, indent=2)
    if args.save_model:
        torch.save(model.state_dict(), os.path.join(args.output_dir, f"model_{args.variant}.pt"))
    print(f"\nResults saved. Best acc: {results['best_test_accuracy']:.4f}")


if __name__ == "__main__":
    main()
