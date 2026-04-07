"""AUCTOR Stage 2: MNIST CNN Improvement — BatchNorm + LR Scheduler.

A/B comparison variant that adds BatchNorm and cosine annealing to the baseline.
Uses the same evaluation protocol for fair comparison.
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


class LeNet5Improved(nn.Module):
    """Improved LeNet-5: adds BatchNorm after each conv layer."""

    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.bn2 = nn.BatchNorm2d(64)
        self.dropout1 = nn.Dropout(0.25)
        self.dropout2 = nn.Dropout(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = F.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        x = self.dropout2(x)
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)


def train_epoch(model, device, train_loader, optimizer, epoch):
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0
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
    avg_loss = total_loss / total
    accuracy = correct / total
    print(f"Epoch {epoch}: train_loss={avg_loss:.4f}, train_acc={accuracy:.4f}")
    return avg_loss, accuracy


def evaluate(model, device, test_loader):
    model.eval()
    test_loss = 0.0
    correct = 0
    total = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.nll_loss(output, target, reduction="sum").item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += data.size(0)
    test_loss /= total
    accuracy = correct / total
    print(f"Test: loss={test_loss:.4f}, accuracy={accuracy:.4f} ({correct}/{total})")
    return test_loss, accuracy


def main():
    parser = argparse.ArgumentParser(description="AUCTOR: MNIST Improved Model")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=str, default="results")
    parser.add_argument("--save-model", action="store_true", default=True)
    parser.add_argument("--variant", type=str, default="improved_batchnorm",
                        help="Experiment variant name")
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    os.makedirs(args.output_dir, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,)),
    ])

    train_dataset = datasets.MNIST("./data", train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST("./data", train=False, transform=transform)
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=1000, shuffle=False)

    model = LeNet5Improved().to(device)
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    start_time = time.time()
    history = []

    for epoch in range(1, args.epochs + 1):
        train_loss, train_acc = train_epoch(model, device, train_loader, optimizer, epoch)
        test_loss, test_acc = evaluate(model, device, test_loader)
        scheduler.step()
        history.append({
            "epoch": epoch,
            "train_loss": round(train_loss, 6),
            "train_acc": round(train_acc, 6),
            "test_loss": round(test_loss, 6),
            "test_acc": round(test_acc, 6),
            "lr": round(optimizer.param_groups[0]["lr"], 8),
        })

    elapsed = time.time() - start_time

    results = {
        "variant": args.variant,
        "improvements": ["BatchNorm after conv layers", "CosineAnnealingLR scheduler"],
        "config": {
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "lr": args.lr,
            "seed": args.seed,
            "device": str(device),
        },
        "final_test_accuracy": history[-1]["test_acc"],
        "final_test_loss": history[-1]["test_loss"],
        "best_test_accuracy": max(h["test_acc"] for h in history),
        "training_time_seconds": round(elapsed, 1),
        "history": history,
    }

    result_path = os.path.join(args.output_dir, f"results_{args.variant}.json")
    with open(result_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {result_path}")

    if args.save_model:
        model_path = os.path.join(args.output_dir, f"model_{args.variant}.pt")
        torch.save(model.state_dict(), model_path)
        print(f"Model saved to {model_path}")


if __name__ == "__main__":
    main()
