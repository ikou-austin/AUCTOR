"""AUCTOR Stage 3: Export model to ONNX and validate accuracy is preserved."""

import argparse
import json
import os

import numpy as np
import torch
import torch.nn.functional as F
from torchvision import datasets, transforms

from train_baseline import LeNet5Modern
from train_improved import LeNet5Improved


def export_to_onnx(model, export_path, device):
    model.eval()
    dummy_input = torch.randn(1, 1, 28, 28, device=device)
    torch.onnx.export(
        model,
        dummy_input,
        export_path,
        export_params=True,
        opset_version=17,
        do_constant_folding=True,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
    )
    file_size_mb = os.path.getsize(export_path) / (1024 * 1024)
    print(f"Exported to {export_path} ({file_size_mb:.2f} MB)")
    return file_size_mb


def validate_onnx(onnx_path, pytorch_model, device, test_loader):
    try:
        import onnxruntime as ort
    except ImportError:
        print("onnxruntime not installed, skipping ONNX validation")
        return None, None

    session = ort.InferenceSession(onnx_path)
    pytorch_model.eval()

    onnx_correct = 0
    pytorch_correct = 0
    total = 0
    max_diff = 0.0

    with torch.no_grad():
        for data, target in test_loader:
            data_np = data.numpy()
            data_torch = data.to(device)

            onnx_out = session.run(None, {"input": data_np})[0]
            pytorch_out = pytorch_model(data_torch).cpu().numpy()

            diff = np.abs(onnx_out - pytorch_out).max()
            max_diff = max(max_diff, diff)

            onnx_pred = np.argmax(onnx_out, axis=1)
            pytorch_pred = np.argmax(pytorch_out, axis=1)
            target_np = target.numpy()

            onnx_correct += (onnx_pred == target_np).sum()
            pytorch_correct += (pytorch_pred == target_np).sum()
            total += len(target)

    onnx_acc = onnx_correct / total
    pytorch_acc = pytorch_correct / total

    print(f"PyTorch accuracy:  {pytorch_acc:.6f}")
    print(f"ONNX accuracy:     {onnx_acc:.6f}")
    print(f"Max output diff:   {max_diff:.8f}")
    print(f"Accuracy match:    {'YES' if abs(onnx_acc - pytorch_acc) < 1e-6 else 'NO'}")

    return onnx_acc, max_diff


def benchmark_onnx(onnx_path, n_runs=100):
    try:
        import onnxruntime as ort
    except ImportError:
        return None

    import time

    session = ort.InferenceSession(onnx_path)
    dummy = np.random.randn(1, 1, 28, 28).astype(np.float32)

    # Warmup
    for _ in range(10):
        session.run(None, {"input": dummy})

    times = []
    for _ in range(n_runs):
        start = time.perf_counter()
        session.run(None, {"input": dummy})
        times.append((time.perf_counter() - start) * 1000)

    p50 = np.percentile(times, 50)
    p95 = np.percentile(times, 95)
    p99 = np.percentile(times, 99)
    print(f"ONNX latency: p50={p50:.2f}ms, p95={p95:.2f}ms, p99={p99:.2f}ms")
    return {"p50_ms": round(p50, 2), "p95_ms": round(p95, 2), "p99_ms": round(p99, 2)}


def main():
    parser = argparse.ArgumentParser(description="AUCTOR: Export and Validate")
    parser.add_argument("--variant", type=str, required=True, choices=["baseline", "improved_batchnorm"])
    parser.add_argument("--results-dir", type=str, default="results")
    parser.add_argument("--output-dir", type=str, default="results")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if args.variant == "baseline":
        model = LeNet5Modern().to(device)
    else:
        model = LeNet5Improved().to(device)

    model_path = os.path.join(args.results_dir, f"model_{args.variant}.pt")
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,)),
    ])
    test_dataset = datasets.MNIST("./data", train=False, transform=transform)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=1000, shuffle=False)

    onnx_path = os.path.join(args.output_dir, f"model_{args.variant}.onnx")
    file_size = export_to_onnx(model, onnx_path, device)

    onnx_acc, max_diff = validate_onnx(onnx_path, model, device, test_loader)
    latency = benchmark_onnx(onnx_path)

    report = {
        "variant": args.variant,
        "onnx_path": onnx_path,
        "file_size_mb": round(file_size, 2),
        "onnx_accuracy": float(onnx_acc) if onnx_acc is not None else None,
        "max_output_diff": float(max_diff) if max_diff is not None else None,
        "latency": latency,
        "accuracy_preserved": abs(onnx_acc - float(onnx_acc)) < 0.001 if onnx_acc is not None else None,
    }

    report_path = os.path.join(args.output_dir, f"export_report_{args.variant}.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nExport report saved to {report_path}")


if __name__ == "__main__":
    main()
