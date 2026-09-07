# Model Scout Report

- Generated: 2026-09-07
- Total candidates: 14
- 14 candidates
- Sources: ollama, huggingface, lmarena, artificial_analysis, swebench

## Executive Summary
- Benchmark evidence: available
- Benchmark progress: 0/0 completed (0.00%), pending=0, failed=0
- Test Now: 2
- Surprise Candidates: 0
- Watchlist: 4
- Needs Data: 8
- Ignored: 0

## Source Coverage
- ollama: 13
- huggingface: 1
- lmarena: 0
- artificial_analysis: 0
- swebench: 0

## Source Status
- ollama: OK
- huggingface: OK
- lmarena: EMPTY
- artificial_analysis: EMPTY
- swebench: EMPTY

## Recommendations

### Test Now
- deepseek-coder:latest (score=88.65, tier=SAFE, source=ollama, VRAM=0.72 GB, assessment=ASSESSED) Reason: TEST_NOW: score 88.65, hardware tier SAFE, estimated VRAM 0.72 GB.
- gpt-oss:20b (score=87.65, tier=SAFE, source=ollama, VRAM=12.85 GB, assessment=ASSESSED) Reason: TEST_NOW: score 87.65, hardware tier SAFE, estimated VRAM 12.85 GB.

### Surprise Candidates
- None

### Watchlist
- deepseek-r1:8b (score=84.65, tier=SAFE, source=ollama, VRAM=4.87 GB, assessment=ASSESSED) Reason: WATCH: score 84.65, hardware tier SAFE, estimated VRAM 4.87 GB.
- qwen3.5:9B (score=83.45, tier=SAFE, source=ollama, VRAM=6.14 GB, assessment=ASSESSED) Reason: WATCH: score 83.45, hardware tier SAFE, estimated VRAM 6.14 GB.
- gemma4:12B (score=80.65, tier=SAFE, source=ollama, VRAM=7.04 GB, assessment=ASSESSED) Reason: WATCH: score 80.65, hardware tier SAFE, estimated VRAM 7.04 GB.
- qwen2.5-coder:14b-instruct (score=80.35, tier=SAFE, source=ollama, VRAM=8.37 GB, assessment=ASSESSED) Reason: WATCH: score 80.35, hardware tier SAFE, estimated VRAM 8.37 GB.

### Needs Data
- qwen3.6:27b-q4_K_M (score=not assessed, tier=BORDERLINE, source=ollama, VRAM=16.22 GB, assessment=METADATA_ONLY) Reason: NEEDS_DATA: quality benchmark data is not assessed; hardware tier BORDERLINE, estimated VRAM 16.22 GB.
- ministral-3:14b (score=not assessed, tier=SAFE, source=ollama, VRAM=8.46 GB, assessment=METADATA_ONLY) Reason: NEEDS_DATA: quality benchmark data is not assessed; hardware tier SAFE, estimated VRAM 8.46 GB.
- devstral-small-2:latest (score=not assessed, tier=BORDERLINE, source=ollama, VRAM=14.14 GB, assessment=METADATA_ONLY) Reason: NEEDS_DATA: quality benchmark data is not assessed; hardware tier BORDERLINE, estimated VRAM 14.14 GB.
- Codestral:latest (score=not assessed, tier=SAFE, source=ollama, VRAM=11.71 GB, assessment=METADATA_ONLY) Reason: NEEDS_DATA: quality benchmark data is not assessed; hardware tier SAFE, estimated VRAM 11.71 GB.
- nomic-embed-text:latest (score=not assessed, tier=SAFE, source=ollama, VRAM=0.26 GB, assessment=METADATA_ONLY) Reason: NEEDS_DATA: quality benchmark data is not assessed; hardware tier SAFE, estimated VRAM 0.26 GB.
- qwen2.5-coder:14b (score=not assessed, tier=SAFE, source=ollama, VRAM=8.37 GB, assessment=METADATA_ONLY) Reason: NEEDS_DATA: quality benchmark data is not assessed; hardware tier SAFE, estimated VRAM 8.37 GB.
- gemma3:4b (score=not assessed, tier=SAFE, source=ollama, VRAM=3.11 GB, assessment=METADATA_ONLY) Reason: NEEDS_DATA: quality benchmark data is not assessed; hardware tier SAFE, estimated VRAM 3.11 GB.
- google/electra-base-discriminator (score=not assessed, tier=EXTERNAL, source=huggingface, VRAM=None GB, assessment=NEEDS_DATA) Reason: NEEDS_DATA: quality benchmark data is not assessed; hardware tier EXTERNAL, VRAM estimate unavailable.

### Ignored
- None

## Candidates
- qwen3.6:27b-q4_K_M (ollama, BORDERLINE, not assessed, VRAM=16.22 GB, assessment=METADATA_ONLY)
- ministral-3:14b (ollama, SAFE, not assessed, VRAM=8.46 GB, assessment=METADATA_ONLY)
- devstral-small-2:latest (ollama, BORDERLINE, not assessed, VRAM=14.14 GB, assessment=METADATA_ONLY)
- Codestral:latest (ollama, SAFE, not assessed, VRAM=11.71 GB, assessment=METADATA_ONLY)
- qwen3.5:9B (ollama, SAFE, 83.45, VRAM=6.14 GB, assessment=ASSESSED)
- gemma4:12B (ollama, SAFE, 80.65, VRAM=7.04 GB, assessment=ASSESSED)
- nomic-embed-text:latest (ollama, SAFE, not assessed, VRAM=0.26 GB, assessment=METADATA_ONLY)
- qwen2.5-coder:14b-instruct (ollama, SAFE, 80.35, VRAM=8.37 GB, assessment=ASSESSED)
- gpt-oss:20b (ollama, SAFE, 87.65, VRAM=12.85 GB, assessment=ASSESSED)
- deepseek-coder:latest (ollama, SAFE, 88.65, VRAM=0.72 GB, assessment=ASSESSED)
- qwen2.5-coder:14b (ollama, SAFE, not assessed, VRAM=8.37 GB, assessment=METADATA_ONLY)
- deepseek-r1:8b (ollama, SAFE, 84.65, VRAM=4.87 GB, assessment=ASSESSED)
- gemma3:4b (ollama, SAFE, not assessed, VRAM=3.11 GB, assessment=METADATA_ONLY)
- google/electra-base-discriminator (huggingface, EXTERNAL, not assessed, VRAM=None GB, assessment=NEEDS_DATA)

## Benchmark Evidence
- No successful benchmark runs available.

### By Context

## Champion Comparison
- qwen3.6:27b-q4_K_M vs gpt-oss:20b: delta=not assessed (needs_data)
- ministral-3:14b vs gpt-oss:20b: delta=not assessed (needs_data)
- devstral-small-2:latest vs gpt-oss:20b: delta=not assessed (needs_data)
- Codestral:latest vs gpt-oss:20b: delta=not assessed (needs_data)
- qwen3.5:9B vs gpt-oss:20b: delta=not assessed (needs_data)
- gemma4:12B vs gpt-oss:20b: delta=not assessed (needs_data)
- nomic-embed-text:latest vs gpt-oss:20b: delta=not assessed (needs_data)
- qwen2.5-coder:14b-instruct vs gpt-oss:20b: delta=not assessed (needs_data)
- gpt-oss:20b vs gpt-oss:20b: delta=not assessed (needs_data)
- deepseek-coder:latest vs gpt-oss:20b: delta=not assessed (needs_data)
- qwen2.5-coder:14b vs gpt-oss:20b: delta=not assessed (needs_data)
- deepseek-r1:8b vs gpt-oss:20b: delta=not assessed (needs_data)
- gemma3:4b vs gpt-oss:20b: delta=not assessed (needs_data)
- google/electra-base-discriminator vs gpt-oss:20b: delta=not assessed (needs_data)