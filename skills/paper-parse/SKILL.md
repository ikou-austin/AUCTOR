---
name: paper-parse
description: "Parse a research paper (PDF or arXiv URL) and extract all reproduction-critical details into structured Markdown. Outputs PAPER_ANALYSIS.md and auto-fills REPRO_TARGET.md for downstream engineering-repro. Use when user says \"解析论文\", \"parse paper\", \"提取论文信息\", \"分析论文\", \"读论文\", \"paper parse\", or provides a paper PDF/URL and wants structured extraction before reproduction."
argument-hint: [paper-pdf-path-or-arxiv-url]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch
---

# Paper Parse — Structured Extraction for Reproduction

Parse and extract: **$ARGUMENTS**

## Goal

Read a research paper and extract **every detail needed to reproduce its experiments**, outputting two machine-readable Markdown files:

1. **`PAPER_ANALYSIS.md`** — Complete structured analysis (the "paper's spec sheet")
2. **`REPRO_TARGET.md`** — Pre-filled reproduction target, ready for `/engineering-repro`

This skill does NOT run any code, does NOT search for repos, does NOT set up environments. It is a **pure extraction and formatting** step. Its only job is to turn a paper PDF into structured, actionable information that a reproduction workflow can consume.

## Constants

- **OUTPUT_DIR = `.`** — Where to write output files. Default: project root.
- **ANALYSIS_DEPTH = full** — `full` extracts everything; `quick` extracts only identity + primary target + dataset + code links.
- **AUTO_FILL_TARGET = true** — Automatically generate `REPRO_TARGET.md` from the analysis.
- **LANGUAGE = zh** — Output language: `zh` (Chinese) or `en` (English).

> Override: `/paper-parse "paper.pdf" — depth: quick, language: en, output: papers/tf-gridnet/`

## Inputs

Accepts **one** of the following (in preference order):

1. Local PDF file path → use `Read` tool to extract text
2. arXiv URL (abs or pdf) → use `WebFetch` to retrieve content
3. arXiv ID (e.g. `2211.12433`) → construct URL, then `WebFetch`
4. Other paper URL → `WebFetch`

If the input is ambiguous, prefer the interpretation that yields a readable paper.

## Output Files

```text
PAPER_ANALYSIS.md        # Full structured extraction
REPRO_TARGET.md          # Pre-filled reproduction target for /engineering-repro
```

If `REPRO_TARGET.md` already exists at OUTPUT_DIR, do NOT overwrite. Instead, write `REPRO_TARGET_DRAFT.md` and inform the user.

---

## Extraction Checklist

The following sections define what MUST be extracted. For each field:
- If the paper states it clearly → extract the exact value
- If the paper implies it → extract with `[inferred]` tag
- If the paper does not mention it → mark as `[NOT STATED]`

**Never fabricate a value. Never guess without tagging it.**

### Section 1: Paper Identity

| Field | Description |
|-------|-------------|
| Title | Exact paper title |
| Authors | Full author list |
| Affiliation | Primary institutions |
| Venue | Conference/journal name (e.g. IEEE TASLP, NeurIPS 2023) |
| Year | Publication year (submission / camera-ready / arXiv) |
| arXiv ID | If applicable |
| Paper URL | arXiv abs, conference page, or provided path |
| PDF URL | Direct link to PDF |
| Project Page | If mentioned in paper |
| Demo | If mentioned in paper |

### Section 2: Code & Resource Availability

#### 2a: Proposed Method Code (本文代码)

| Field | Description |
|-------|-------------|
| Official Code URL | GitHub/GitLab link from the paper |
| Framework | PyTorch / TensorFlow / JAX / other |
| Toolkit Integration | E.g. ESPnet, HuggingFace, MMDetection |
| Pretrained Models | URLs or hub identifiers for the proposed method |
| License | If stated |
| Code Maturity | active (recent commits) / archived / unknown |

#### 2b: Backbone Code (基座模型代码)

| Field | Description |
|-------|-------------|
| Backbone Name | The base architecture this paper builds upon |
| Backbone Code URL | GitHub/GitLab link (from citations or known repos) |
| Backbone Framework | PyTorch / TensorFlow / JAX / other |
| Backbone Pretrained | URLs for pretrained weights (if used) |
| Gap from Backbone to Paper | Brief: what must be added/changed to go from backbone → proposed |

> If the paper has official code (2a), backbone code (2b) is secondary context.
> If the paper has NO official code, backbone code becomes **the critical reproduction path** — this is where `/engineering-repro` Phase 4B starts.

### Section 3: Core Method Summary

Extract a concise (10-20 lines) technical summary covering:
- What is the input and output?
- **What is inherited from the backbone?** (What you DON'T need to build from scratch)
- **What is the core innovation on top of the backbone?** (What you DO need to implement)
- What are the key new components / modules?
- How does training work at a high level?

This is NOT an abstract copy. It should be written as a **reproduction briefing** — enough for an engineer to understand what to reuse vs. what to build.

### Section 4: Architecture Details

> **CRITICAL DISTINCTION — Backbone vs. Baseline**
>
> - **Backbone (基座模型)**: The foundational architecture/model that the paper's proposed method is **built on top of**. When no official code exists, finding the backbone's open-source implementation is the key to reproduction — you implement the paper's changes ON TOP of it.
>   - Examples: TFPSNet for TF-GridNet; ResNet-50 for a new detection head; wav2vec2 for a downstream ASR system.
>
> - **Baseline (基线对照组)**: Other methods listed in the results tables **for comparison only**. They may use entirely different architectures, frameworks, or training pipelines. They are NOT part of the reproduction path — they are reference numbers to compare against.
>   - Examples: Conv-TasNet, DPRNN, SepFormer listed as competing systems in a speaker separation paper.
>
> **Never confuse the two.** A baseline's code is useful only for metric validation; the backbone's code is the foundation for building the proposed method.

#### 4.1 Backbone / Base Architecture (基座模型)

Identify what existing architecture or system the paper's method is built upon:

```markdown
| Field | Value |
|-------|-------|
| Backbone Name | [e.g. TFPSNet, ResNet-50, wav2vec2-base] |
| Relationship | [e.g. "TF-GridNet is an improved TFPSNet with added cross-frame self-attention"] |
| Backbone Paper | [title + citation] |
| Backbone Code | [URL if known from citations/references, or "NOT STATED"] |
| What This Paper Adds | [list of architectural changes on top of backbone] |
| What This Paper Keeps | [which components are inherited unchanged] |
| Pretrained Weights Used? | [yes (source) / no (train from scratch) / NOT STATED] |
```

If the method is built from scratch (no identifiable backbone), state: **"Novel architecture — no backbone dependency."**

If the method chains multiple components (e.g. DNN1 → Beamformer → DNN2), describe each component's backbone lineage separately.

#### 4.2 Proposed Architecture (本文模型)

Extract ALL architecture hyperparameters into a structured table:

```markdown
| Parameter | Symbol | Value | Notes |
|-----------|--------|-------|-------|
| Embedding dimension | D | 64 | per T-F unit |
| Number of blocks | B | 6 | stacked |
| ... | ... | ... | ... |
```

Also extract:
- Architecture diagram description (if Fig. N shows the architecture, describe it)
- Input representation (e.g. complex RI spectrogram, mel-fbank, raw waveform)
- Output representation (e.g. predicted RI components, mask, waveform)
- Normalization methods used (LayerNorm, BatchNorm, GroupNorm, etc.)
- Activation functions (ReLU, PReLU, GELU, etc.)
- Any non-standard operations (e.g. `torch.unfold`, custom attention)

### Section 5: Dataset Details

For EACH dataset used in the paper, extract:

```markdown
### Dataset: [Name]
- **Task**: [e.g. speaker separation, dereverberation]
- **Version**: [e.g. "min, 8kHz", "v2.0", or NOT STATED]
- **Source / Download URL**: [official URL, corpus name, or hosting platform]
- **License/Access**: [open / restricted / LDC / application required]
- **Size**: [total size in GB/hours, or number of utterances/samples]
- **Format**: [e.g. WAV 16-bit, FLAC, HDF5, numpy]
- **Sampling Rate**: [e.g. 8kHz, 16kHz]
- **Train/Val/Test Split**: [exact numbers and durations for each]
- **Mixture Creation**: [how mixtures are generated, SNR ranges, etc.]
- **Microphone Config**: [channels, array geometry if applicable]
- **Preprocessing**: [any required transforms before training]
- **Special Notes**: [e.g. "speakers disjoint between train/test", "simulated by authors"]
```

### Section 6: Training Recipe

Extract the complete training configuration:

| Field | Value |
|-------|-------|
| Optimizer | (e.g. Adam, AdamW, SGD) |
| Initial Learning Rate | |
| LR Schedule | (e.g. halve if no improve in N epochs, cosine, warmup+decay) |
| Batch Size | (or segment-based description) |
| Training Segment Length | (e.g. 4 seconds per sample) |
| Total Epochs | (if stated) |
| Gradient Clipping | (norm type and value) |
| Weight Decay | |
| Data Augmentation | (list or "none") |
| Dynamic Mixing | (yes/no) |
| Input Normalization | (e.g. sample variance → 1.0) |
| Random Seed | (if stated) |
| Multi-stage Training | (e.g. DNN1 first, then DNN2 sequentially) |
| Mixed Precision | (fp16, bf16, or not stated) |

### Section 7: Loss Functions

For EACH loss function used, extract:

```markdown
### Loss: [Name] (Eq. N)
- **Formula**: [LaTeX or text description]
- **Applied to**: [which task/dataset]
- **Components**: [list sub-terms if composite]
- **Weighting**: [between sub-terms, or "no weighting"]
- **Notes**: [e.g. "scaling estimate variant of SI-SDR, not scaling source"]
```

### Section 8: Evaluation Protocol

| Field | Value |
|-------|-------|
| Metrics | (list all: SI-SDR, PESQ, STOI, WER, etc.) |
| Metric Toolkits | (specific versions if stated, e.g. python-pesq v0.0.2) |
| Evaluation Split | (test set details) |
| Computation Cost Metric | (GMAC/s, MACs, FLOPs — how measured) |
| ASR Backend | (if WER is reported, what ASR system) |

### Section 9: Main Results — Reproduction Targets

Extract results tables that define the reproduction targets. **Separate proposed method results from baseline comparisons.**

For each results table:

```markdown
### Table N: [Caption]

#### Proposed Method (复现目标)
| Config/Variant | Metric1 | Metric2 | ... | Notes |
|----------------|---------|---------|-----|-------|
| Proposed (best) ★ | X.X | Y.Y | ... | primary target |
| Proposed (lightweight) | X.X | Y.Y | ... | lower compute variant |

#### Baselines (对照基线 — 仅供比较，不需复现)
| System | Domain | Year | #Params | Metric1 | Metric2 | Shares Backbone? |
|--------|--------|------|---------|---------|---------|-----------------|
| DPRNN [15] | Time | 2020 | 2.6M | A.A | B.B | No |
| TFPSNet [25] | T-F | 2022 | 2.7M | C.C | D.D | Yes (predecessor) |
| SepFormer [19] | Time | 2021 | 26.0M | E.E | F.F | No |
```

> **"Shares Backbone?" column**: Indicates whether a baseline uses the same backbone as the proposed method. This matters because:
> - `Yes` → its code may contain useful backbone implementation
> - `Yes (predecessor)` → the proposed method directly extends this system
> - `No` → unrelated architecture, only useful as a comparison number

Mark the **primary reproduction target** (the paper's headline result) with `★`.

If the paper has multiple tasks/datasets, create one sub-table per task and mark which is the primary (simplest or cheapest) reproduction target.

### Section 10: Ablation & Configuration Variants

Extract any per-task or per-dataset configuration differences:

```markdown
### Config per Task
| Dataset | B | D | I | J | H | Loss | STFT Window |
|---------|---|---|---|---|---|------|-------------|
| WSJ0-2mix | 6 | 64 | 4 | 1 | 256 | SI-SDR+MC | 32ms/8ms |
| SMS-WSJ | 4 | 48 | 4 | 1 | 192 | Wav+Mag+MC | 32ms/8ms |
```

Also extract ablation study results if they reveal critical design choices.

### Section 11: Compute Requirements

| Field | Value |
|-------|-------|
| Training GPU | (e.g. NVIDIA A100 40GB) |
| Training Time per Epoch | |
| Total Training Time | (if derivable) |
| Inference GPU | |
| Inference Speed | (ms per segment, real-time factor) |
| Memory (forward) | |
| Memory (backward) | |
| Model Size | (parameter count) |

### Section 12: Identified Gaps & Risks

List what the paper does NOT state but reproduction NEEDS:

```markdown
| Gap | Impact | Mitigation |
|-----|--------|------------|
| Batch size not stated | Medium | Infer from "utilize all GPU memory" + model size |
| Total epochs not stated | Medium | Use LR schedule + early stopping |
| WSJ0CAM-DEREVERB is self-simulated | High | Need exact simulation script or replicate from description |
| Random seed not specified | Low | Use standard seed (42), report variance if possible |
```

---

## PAPER_ANALYSIS.md Output Format

Write `PAPER_ANALYSIS.md` with the following structure:

```markdown
# Paper Analysis: [Title]

> Auto-generated by `/paper-parse` on [date]
> Source: [PDF path or URL]
> Extraction depth: [full/quick]

## 1. Paper Identity
[Section 1 content]

## 2. Code & Resources
[Section 2 content]

## 3. Core Method Summary
[Section 3 content]

## 4. Architecture Details
### 4.1 Backbone / Base Architecture
[Section 4.1 content — what the method is built on]
### 4.2 Proposed Architecture
[Section 4.2 content — what the paper adds]

## 5. Datasets
[Section 5 content]

## 6. Training Recipe
[Section 6 content]

## 7. Loss Functions
[Section 7 content]

## 8. Evaluation Protocol
[Section 8 content]

## 9. Reproduction Targets (Proposed vs. Baselines)
[Section 9 content — proposed results with ★ on primary target, baselines separated below]

## 10. Configuration Variants & Ablations
[Section 10 content]

## 11. Compute Requirements
[Section 11 content]

## 12. Gaps & Risks
[Section 12 content]

---
## Reproduction Readiness Score

| Dimension | Score (1-5) | Rationale |
|-----------|-------------|-----------|
| Code Availability (本文代码) | | |
| Backbone Availability (基座代码) | | |
| Dataset Accessibility | | |
| Training Recipe Completeness | | |
| Compute Feasibility | | |
| Detail Sufficiency | | |
| **Overall** | **/5** | |

Legend: 5=trivial, 4=straightforward, 3=moderate effort, 2=significant gaps, 1=major blockers

> **Scoring note**: If the paper has NO official code but the backbone has a mature open-source implementation, "Code Availability" may be 1 but "Backbone Availability" could be 5 — this means the Paper-Only path (Phase 4B in `/engineering-repro`) is still viable.
```

---

## REPRO_TARGET.md Auto-Fill Logic

When AUTO_FILL_TARGET = true, generate `REPRO_TARGET.md` by mapping:

| REPRO_TARGET field | Source in PAPER_ANALYSIS |
|--------------------|-------------------------|
| Paper Identity (title, authors, venue, **year**, URL) | Section 1 |
| What to Reproduce (primary) | Section 9 — the row marked ★ |
| Metric + Target value | Section 9 ★ row's best metric |
| Tolerance | Default BENCHMARK_TOLERANCE (0.02) unless paper reports variance |
| Dataset (name, **version**, source, access, **size**, **format**, **splits**, preprocessing) | Section 5 — dataset for the ★ target |
| Compute Constraints (**GPU-hour budget**) | Section 11 — minimum viable GPU + training time estimate |
| Code Availability (本文 + 基座) | Section 2a (proposed) + Section 2b (backbone) + Section 4.1 (gap description) |
| **Code Search Policy** (official required?, upstream allowed?, framework) | Section 2 — framework + toolkit; default: official preferred, upstream allowed |
| Success Criteria | Derived from Section 8 metrics + Section 9 target numbers |
| Known Implementation Clues | Section 4 architecture + Section 6 recipe + Section 10 config |
| Known Blockers | Section 12 gaps with "High" impact |

Use this `REPRO_TARGET.md` structure (aligned with `/engineering-repro` expectations):

```markdown
# Reproduction Target

## Paper Identity
- **Title**: [from §1]
- **Authors**: [from §1]
- **Venue**: [from §1]
- **Year**: [from §1]
- **URL**: [from §1]

## What to Reproduce
- **Primary target**: [from §9 ★, e.g. "Table IV: TF-GridNet on WSJ0-2mix, 23.5 dB SI-SDRi"]
- **Secondary targets**: [other notable results from §9]
- **Out of scope**: [any sections explicitly excluded]

## Target Metrics
| Metric | Target | Tolerance | Table/Figure |
|--------|--------|-----------|-------------|
| [metric] | [value] | ±[tol] | Table N |

## Dataset
- **Name**: [from §5]
- **Version**: [from §5, e.g. "min, 8kHz" or specific release]
- **Source**: [from §5]
- **Access**: [open / restricted / LDC required]
- **Size**: [from §5]
- **Format**: [from §5]
- **Train/Val/Test Splits**: [from §5, exact numbers]
- **Preprocessing**: [from §5]

## Compute Constraints
- **Minimum GPU**: [from §11]
- **Estimated Training Time**: [from §11]
- **GPU-hour Budget**: [from §11, or user-specified upper limit]
- **Framework**: [from §2]

## Code Availability
- **Official code (本文)**: [URL or "None"]
- **Backbone code (基座)**: [URL or "None" — critical if no official code]
- **Backbone name**: [from §4.1]
- **Gap: backbone → paper**: [brief description of what to implement]
- **Path**: [Code-Available / Paper-Only-With-Backbone / Paper-Only-No-Backbone]
- **Toolkit**: [from §2]

## Code Search Policy
- **Official code required?**: [yes / no / preferred]
- **Allow upstream base repos?**: [yes / no]
- **Preferred framework**: [from §2]

## Success Criteria
- [ ] Environment runs without errors
- [ ] Data loads and preprocesses correctly
- [ ] Model trains and loss decreases
- [ ] Primary metric within tolerance: [metric] >= [target - tolerance]
- [ ] Results saved for downstream /engineering-improve

## Known Implementation Clues
[Key details from §4, §6, §7, §10 that are easy to miss]

## Known Blockers
[High-impact gaps from §12]

## Notes
[Any additional context from the paper analysis]
```

---

## Workflow

### Step 1: Acquire Paper Content

```
IF input is local PDF path:
    content = Read(path)
ELIF input is arXiv URL or ID:
    content = WebFetch(arxiv_abs_url)   # for metadata
    content += WebFetch(arxiv_pdf_url)  # for full text (auto-converted)
ELIF input is other URL:
    content = WebFetch(url)
```

If the content is too large for a single read (>2000 lines), read in chunks:
- First 300 lines (abstract, intro)
- Experimental setup section (search for "experiment", "setup", "evaluation")
- Results section (search for "result", "Table", "performance")
- Last 200 lines (conclusion, references — useful for finding code/data URLs)

### Step 2: Extract All Sections

Walk through the Extraction Checklist (Sections 1-12) systematically. For each section:

1. Scan the paper content for relevant information
2. Extract into the structured format defined above
3. Tag uncertain items with `[inferred]` or `[NOT STATED]`

Prioritize extraction order by reproduction importance:
1. Section 9 (targets) — what to hit
2. Section 5 (datasets) — what data is needed
3. Section 6 (training) — how to train
4. Section 4 (architecture) — what to build
5. Section 7 (loss) — what to optimize
6. Section 2 (code) — whether code exists
7. Section 8 (eval) — how to measure
8. Section 11 (compute) — what hardware is needed
9. Section 12 (gaps) — what's missing
10. Section 1 (identity) — metadata
11. Section 3 (method) — conceptual overview
12. Section 10 (ablation) — refinement details

### Step 3: Compute Reproduction Readiness Score

Score each dimension 1-5 based on:

| Dimension | 5 (trivial) | 3 (moderate) | 1 (blocked) |
|-----------|-------------|--------------|-------------|
| Code Availability | Official code, well-maintained | Community reimplementation | No code anywhere |
| **Backbone Availability** | **Backbone has mature OSS impl (e.g. in ESPnet/HF)** | **Backbone code exists but needs adaptation** | **No backbone code; novel arch from scratch** |
| Dataset Accessibility | Public download, standard format | Requires application/license | Private or self-simulated |
| Training Recipe | All hyperparams stated explicitly | Most stated, some inferred | Major gaps (no LR, no epochs) |
| Compute Feasibility | Single consumer GPU | Single datacenter GPU (A100) | Multi-node or TPU-only |
| Detail Sufficiency | Reproduction appendix, configs shared | Standard detail level | Critical details missing |

### Step 4: Generate REPRO_TARGET.md

Apply the auto-fill mapping defined above. Select the primary reproduction target using this priority:
1. The paper's headline/abstract claim (e.g. "23.5 dB SI-SDRi on WSJ0-2mix")
2. The simplest task that validates the core method
3. The table with the most baselines for comparison

If the paper covers multiple tasks, set the simplest (or cheapest) as primary and others as secondary.

### Step 5: Write Output Files

1. Write `PAPER_ANALYSIS.md` to OUTPUT_DIR
2. Write `REPRO_TARGET.md` (or `REPRO_TARGET_DRAFT.md` if exists) to OUTPUT_DIR

### Step 6: Summary

Print a concise summary for the user:

```
Paper parsed: [Title]
- Reproduction readiness: [N]/5
- Primary target: [metric] = [value] on [dataset]
- Code available: [Yes (URL) / No]
- Datasets: [list with access status]
- Estimated compute: [GPU type] × [time]
- Gaps found: [N] ([high-impact count] high-impact)
- Output: PAPER_ANALYSIS.md, REPRO_TARGET.md

Next step: /engineering-repro "[paper title or path]"
```

## Key Rules

- **Pure extraction.** This skill reads and writes Markdown. It does NOT install packages, clone repos, or run experiments.
- **Faithful to the paper.** Extract what the paper says, not what you think it should say. Tag inferences explicitly.
- **Reproduction-oriented.** Every extracted field serves a downstream reproduction need. Skip pure theory that doesn't affect implementation.
- **Structured output.** Tables over prose. Numbers over descriptions. Exact values over ranges.
- **No fabrication.** If the paper doesn't state a value, write `[NOT STATED]` — never invent.
- **Idempotent.** Running twice on the same paper produces the same output (modulo timestamp).
- **Encoding-safe.** Handle papers with mathematical symbols, Unicode, and special characters gracefully.

## Composing with Other Skills

```
/paper-parse "paper.pdf"           ← you are here (extract info)
/engineering-repro "method"         ← consume REPRO_TARGET.md to reproduce
/engineering-improve "method"       ← after baseline verified
/engineering-deploy "method"        ← after improvement validated
/engineering-report                 ← generate reports at any stage
/auctor-pipeline "requirement"      ← full end-to-end flow
```

## Examples

```bash
# Parse a local PDF
/paper-parse "/path/to/TF-GridNet.pdf"

# Parse from arXiv URL
/paper-parse "https://arxiv.org/abs/2211.12433"

# Parse with quick extraction
/paper-parse "2211.12433" — depth: quick

# Parse with custom output directory
/paper-parse "paper.pdf" — output: papers/tf-gridnet/

# Parse in English
/paper-parse "paper.pdf" — language: en
```
