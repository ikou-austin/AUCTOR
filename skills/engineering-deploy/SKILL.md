---
name: engineering-deploy
description: "Deploy an improved model/system to production or staging. Handles model export, performance optimization, deployment verification, and integration testing. Use when user says \"部署\", \"落地\", \"deploy\", \"上线\", \"export model\", \"engineering deploy\", or has an improved model ready for production."
argument-hint: [deployment-target-or-description]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent, Skill, mcp__codex__codex, mcp__codex__codex-reply
---

# Engineering Deployment

Deploy to production: **$ARGUMENTS**

## Goal

Take an improved model/system from `/engineering-improve` and prepare it for production deployment: export, optimize, validate, and verify in the target environment.

## Constants

- **PERF_REGRESSION_TOLERANCE = 0.01** — Maximum acceptable accuracy regression from export/optimization (1%).
- **LATENCY_TARGET = null** — Target inference latency in ms. Set in AUCTOR.md or override.
- **EXPORT_FORMATS = ["onnx"]** — Target export formats. Options: onnx, torchscript, tensorrt, coreml, openvino.
- **RUN_INTEGRATION_TESTS = true** — Whether to run integration tests after deployment.
- **AUTO_ESCALATE = true** — Feishu notification on deployment issues.

> Override: `/engineering-deploy "speech model v2" — formats: onnx,tensorrt, latency target: 50ms`

## Inputs

1. Improved model checkpoint from `/engineering-improve`
   - `improve-logs/ACCEPTED_CHANGES.md` — what was changed
   - `improve-logs/IMPROVE_TRACKER.md` — final metrics
2. Deployment requirements from AUCTOR.md or user specification
3. Target environment specification (hardware, OS, runtime)

## Files This Skill Maintains

```text
deploy-logs/
  DEPLOY_PLAN.md                # Deployment strategy and checklist
  EXPORT_REPORT.md              # Model export results and validation
  PERF_BENCHMARK.md             # Performance benchmark (latency, throughput, memory)
  INTEGRATION_TEST_REPORT.md    # Integration test results
  DEPLOY_TRACKER.md             # Overall deployment status
```

## Workflow

### Phase 1: Deployment Planning

1. Read model info from improvement logs
2. Read deployment requirements (target env, latency, throughput, memory limits)
3. Write `deploy-logs/DEPLOY_PLAN.md`:

```markdown
# Deployment Plan

## Source
- Model: [name and version]
- Checkpoint: [path]
- Framework: [PyTorch/TF/JAX]
- Accuracy: [metric] = [value]

## Target Environment
- Hardware: [GPU/CPU/edge device]
- Runtime: [ONNX Runtime / TensorRT / CoreML / custom]
- OS: [Linux/macOS/Android/iOS]
- Constraints: latency < [X]ms, memory < [Y]MB

## Export Strategy
1. [format 1]: [rationale]
2. [format 2]: [rationale]

## Optimization Strategy
- [ ] Quantization: [INT8/FP16/none]
- [ ] Pruning: [if applicable]
- [ ] Knowledge distillation: [if applicable]
- [ ] Operator fusion: [auto/manual]

## Validation Checklist
- [ ] Exported model produces same output as original (within tolerance)
- [ ] Latency meets target
- [ ] Memory usage within limits
- [ ] Integration tests pass
```

### Phase 2: Model Export

For each target format:

1. **Export the model**:
   - ONNX: `torch.onnx.export()` with proper dynamic axes
   - TorchScript: `torch.jit.trace()` or `torch.jit.script()`
   - TensorRT: via ONNX → TRT conversion
   - CoreML: via `coremltools`
   - OpenVINO: via Model Optimizer

2. **Validate export accuracy**:
   - Run the same test set through both original and exported model
   - Compare outputs (max absolute difference, mean difference)
   - Compare final metrics
   - If accuracy drops > PERF_REGRESSION_TOLERANCE → diagnose and fix

3. Document in `deploy-logs/EXPORT_REPORT.md`:

```markdown
## Export: [format]

- Export command: [exact command]
- File size: [original] → [exported]
- Accuracy: [original metric] → [exported metric] (delta: [X])
- Status: PASS / FAIL / NEEDS_FIX
```

### Phase 3: Performance Optimization

1. **Benchmark baseline inference**:
   - Latency (p50, p95, p99)
   - Throughput (samples/sec)
   - Memory usage (peak, average)

2. **Apply optimizations** (from plan):
   - FP16 / INT8 quantization
   - Graph optimization / operator fusion
   - Batch inference optimization

3. **Re-benchmark after each optimization**:
   - Compare latency, throughput, memory
   - Verify accuracy is still within tolerance

4. Document in `deploy-logs/PERF_BENCHMARK.md`:

```markdown
## Performance Benchmark

| Config | Latency p50 | Latency p99 | Throughput | Memory | Accuracy |
|--------|------------|------------|------------|--------|----------|
| Original (PyTorch) | Xms | Xms | X/s | XMB | X.XX |
| ONNX FP32 | Xms | Xms | X/s | XMB | X.XX |
| ONNX FP16 | Xms | Xms | X/s | XMB | X.XX |
| TensorRT INT8 | Xms | Xms | X/s | XMB | X.XX |
```

### Phase 4: Integration Testing (if RUN_INTEGRATION_TESTS = true)

1. **Define test cases** based on real usage scenarios:
   - Normal inputs (expected data distribution)
   - Edge cases (empty input, max length, unusual format)
   - Adversarial inputs (out-of-distribution, corrupted)
   - Batch processing (various batch sizes)

2. **Run tests** against deployed model endpoint or local runtime

3. **Verify**:
   - All test cases produce valid output
   - Error handling works correctly
   - No memory leaks under sustained load
   - Graceful degradation on invalid input

4. Document in `deploy-logs/INTEGRATION_TEST_REPORT.md`

### Phase 5: Deployment Verification

1. Deploy to staging environment (if available)
2. Run a subset of production-like traffic
3. Monitor for errors, latency spikes, resource usage
4. Compare with production baseline (if upgrading existing system)

### Phase 6: Completion

Update `deploy-logs/DEPLOY_TRACKER.md`:

```markdown
# Deployment Status

## Summary
- Model: [name] v[version]
- Format: [deployed format]
- Target: [environment]
- Status: DEPLOYED / STAGING / BLOCKED

## Metrics
| Metric | Requirement | Actual | Status |
|--------|------------|--------|--------|
| Accuracy | >= [X] | [Y] | PASS |
| Latency p99 | < [X]ms | [Y]ms | PASS |
| Memory | < [X]MB | [Y]MB | PASS |
| Integration tests | 100% | [Y]% | PASS |

## Artifacts
- Exported model: [path]
- Config: [path]
- Deployment script: [path]
```

Handoff:

```
Deployment complete:
- Model: [name] → [format]
- Accuracy: [value] (regression: [delta])
- Latency: [p50]ms / [p99]ms
- Status: [DEPLOYED/STAGING]
- Next step: /engineering-report
```

## Key Rules

- **Never deploy without accuracy validation.** Export can silently break accuracy.
- **Benchmark before and after every optimization.** Quantify the trade-off.
- **Test edge cases.** Production sees things training didn't.
- **Document the exact deployment command.** Reproducibility applies to deployment too.
- **Keep the original checkpoint.** Never delete the source model after export.

## Composing with Other Skills

```
/engineering-repro "paper or requirement"    ← get verified baseline
/engineering-improve "[direction]"           ← improve baseline
/engineering-deploy "[target]"               ← you are here
/engineering-report                          ← report deployment results
/auctor-pipeline "requirement"               ← full end-to-end flow
```
