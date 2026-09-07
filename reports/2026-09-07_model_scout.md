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
- Needs Data: 4
- Ignored: 4

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
- nomic-embed-text:latest (score=not assessed, tier=SAFE, source=ollama, VRAM=0.26 GB, assessment=METADATA_ONLY) Reason: NEEDS_DATA: quality benchmark data is not assessed; hardware tier SAFE, estimated VRAM 0.26 GB.
- qwen2.5-coder:14b (score=not assessed, tier=SAFE, source=ollama, VRAM=8.37 GB, assessment=METADATA_ONLY) Reason: NEEDS_DATA: quality benchmark data is not assessed; hardware tier SAFE, estimated VRAM 8.37 GB.
- google/electra-base-discriminator (score=not assessed, tier=EXTERNAL, source=huggingface, VRAM=None GB, assessment=NEEDS_DATA) Reason: NEEDS_DATA: quality benchmark data is not assessed; hardware tier EXTERNAL, VRAM estimate unavailable.

### Ignored
- gemma3:4b (score=30.28, tier=SAFE, source=ollama, VRAM=3.11 GB, assessment=ASSESSED) Reason: IGNORE: score 30.28, hardware tier SAFE, estimated VRAM 3.11 GB.
- ministral-3:14b (score=25.49, tier=SAFE, source=ollama, VRAM=8.46 GB, assessment=ASSESSED) Reason: IGNORE: score 25.49, hardware tier SAFE, estimated VRAM 8.46 GB.
- Codestral:latest (score=18.27, tier=SAFE, source=ollama, VRAM=11.71 GB, assessment=ASSESSED) Reason: IGNORE: score 18.27, hardware tier SAFE, estimated VRAM 11.71 GB.
- devstral-small-2:latest (score=17.05, tier=BORDERLINE, source=ollama, VRAM=14.14 GB, assessment=ASSESSED) Reason: IGNORE: score 17.05, hardware tier BORDERLINE, estimated VRAM 14.14 GB.

## Candidates
- qwen3.6:27b-q4_K_M (ollama, BORDERLINE, not assessed, VRAM=16.22 GB, assessment=METADATA_ONLY)
- ministral-3:14b (ollama, SAFE, 25.49, VRAM=8.46 GB, assessment=ASSESSED)
- devstral-small-2:latest (ollama, BORDERLINE, 17.05, VRAM=14.14 GB, assessment=ASSESSED)
- Codestral:latest (ollama, SAFE, 18.27, VRAM=11.71 GB, assessment=ASSESSED)
- qwen3.5:9B (ollama, SAFE, 83.45, VRAM=6.14 GB, assessment=ASSESSED)
- gemma4:12B (ollama, SAFE, 80.65, VRAM=7.04 GB, assessment=ASSESSED)
- nomic-embed-text:latest (ollama, SAFE, not assessed, VRAM=0.26 GB, assessment=METADATA_ONLY)
- qwen2.5-coder:14b-instruct (ollama, SAFE, 80.35, VRAM=8.37 GB, assessment=ASSESSED)
- gpt-oss:20b (ollama, SAFE, 87.65, VRAM=12.85 GB, assessment=ASSESSED)
- deepseek-coder:latest (ollama, SAFE, 88.65, VRAM=0.72 GB, assessment=ASSESSED)
- qwen2.5-coder:14b (ollama, SAFE, not assessed, VRAM=8.37 GB, assessment=METADATA_ONLY)
- deepseek-r1:8b (ollama, SAFE, 84.65, VRAM=4.87 GB, assessment=ASSESSED)
- gemma3:4b (ollama, SAFE, 30.28, VRAM=3.11 GB, assessment=ASSESSED)
- google/electra-base-discriminator (huggingface, EXTERNAL, not assessed, VRAM=None GB, assessment=NEEDS_DATA)

## Benchmark Evidence
- Codestral:latest: 25.85 tok/s, 33.20 quality, runs=30
- deepseek-coder:latest: 429.08 tok/s, 35.40 quality, runs=30
- deepseek-r1:8b: 106.63 tok/s, 14.40 quality, runs=30
- devstral-small-2:latest: 11.82 tok/s, 36.40 quality, runs=30
- gemma3:4b: 165.10 tok/s, 36.40 quality, runs=30
- gemma4:12B: 68.88 tok/s, 36.40 quality, runs=30
- gpt-oss:20b: 135.64 tok/s, 29.60 quality, runs=30
- ministral-3:14b: 67.57 tok/s, 36.67 quality, runs=30
- qwen2.5-coder:14b-instruct: 58.67 tok/s, 33.53 quality, runs=30
- qwen3.5:9B: 89.29 tok/s, 36.40 quality, runs=30

### By Context
- Codestral:latest @ 8192: 47.36 tok/s, 33.20 quality, runs=10
- Codestral:latest @ 16384: 20.00 tok/s, 33.20 quality, runs=10
- Codestral:latest @ 32768: 10.20 tok/s, 33.20 quality, runs=10
- deepseek-coder:latest @ 8192: 426.38 tok/s, 35.40 quality, runs=10
- deepseek-coder:latest @ 16384: 429.40 tok/s, 35.40 quality, runs=10
- deepseek-coder:latest @ 32768: 431.45 tok/s, 35.40 quality, runs=10
- deepseek-r1:8b @ 8192: 106.20 tok/s, 14.40 quality, runs=10
- deepseek-r1:8b @ 16384: 107.97 tok/s, 14.40 quality, runs=10
- deepseek-r1:8b @ 32768: 105.71 tok/s, 14.40 quality, runs=10
- devstral-small-2:latest @ 8192: 15.70 tok/s, 36.40 quality, runs=10
- devstral-small-2:latest @ 16384: 11.62 tok/s, 36.40 quality, runs=10
- devstral-small-2:latest @ 32768: 8.13 tok/s, 36.40 quality, runs=10
- gemma3:4b @ 8192: 167.34 tok/s, 36.40 quality, runs=10
- gemma3:4b @ 16384: 163.86 tok/s, 36.40 quality, runs=10
- gemma3:4b @ 32768: 164.12 tok/s, 36.40 quality, runs=10
- gemma4:12B @ 8192: 68.42 tok/s, 36.40 quality, runs=10
- gemma4:12B @ 16384: 69.24 tok/s, 36.40 quality, runs=10
- gemma4:12B @ 32768: 68.97 tok/s, 36.40 quality, runs=10
- gpt-oss:20b @ 8192: 135.58 tok/s, 29.60 quality, runs=10
- gpt-oss:20b @ 16384: 135.77 tok/s, 29.60 quality, runs=10
- gpt-oss:20b @ 32768: 135.57 tok/s, 29.60 quality, runs=10
- ministral-3:14b @ 8192: 69.11 tok/s, 37.20 quality, runs=10
- ministral-3:14b @ 16384: 64.39 tok/s, 36.40 quality, runs=10
- ministral-3:14b @ 32768: 69.21 tok/s, 36.40 quality, runs=10
- qwen2.5-coder:14b-instruct @ 8192: 66.53 tok/s, 33.80 quality, runs=10
- qwen2.5-coder:14b-instruct @ 16384: 66.61 tok/s, 33.80 quality, runs=10
- qwen2.5-coder:14b-instruct @ 32768: 42.85 tok/s, 33.00 quality, runs=10
- qwen3.5:9B @ 8192: 86.33 tok/s, 36.40 quality, runs=10
- qwen3.5:9B @ 16384: 89.70 tok/s, 36.40 quality, runs=10
- qwen3.5:9B @ 32768: 91.84 tok/s, 36.40 quality, runs=10

## Champion Comparison
- qwen3.6:27b-q4_K_M vs gpt-oss:20b: delta=not assessed (needs_data)
- ministral-3:14b vs gpt-oss:20b: delta=not assessed (needs_data, speed_delta=-68.07 tok/s, quality_delta=+7.07)
- devstral-small-2:latest vs gpt-oss:20b: delta=not assessed (needs_data, speed_delta=-123.82 tok/s, quality_delta=+6.80)
- Codestral:latest vs gpt-oss:20b: delta=not assessed (needs_data, speed_delta=-109.79 tok/s, quality_delta=+3.60)
- qwen3.5:9B vs gpt-oss:20b: delta=not assessed (needs_data, speed_delta=-46.35 tok/s, quality_delta=+6.80)
- gemma4:12B vs gpt-oss:20b: delta=not assessed (needs_data, speed_delta=-66.76 tok/s, quality_delta=+6.80)
- nomic-embed-text:latest vs gpt-oss:20b: delta=not assessed (needs_data)
- qwen2.5-coder:14b-instruct vs gpt-oss:20b: delta=not assessed (needs_data, speed_delta=-76.97 tok/s, quality_delta=+3.93)
- gpt-oss:20b vs gpt-oss:20b: delta=not assessed (needs_data, speed_delta=+0.00 tok/s, quality_delta=+0.00)
- deepseek-coder:latest vs gpt-oss:20b: delta=not assessed (needs_data, speed_delta=+293.44 tok/s, quality_delta=+5.80)
- qwen2.5-coder:14b vs gpt-oss:20b: delta=not assessed (needs_data)
- deepseek-r1:8b vs gpt-oss:20b: delta=not assessed (needs_data, speed_delta=-29.01 tok/s, quality_delta=-15.20)
- gemma3:4b vs gpt-oss:20b: delta=not assessed (needs_data, speed_delta=+29.46 tok/s, quality_delta=+6.80)
- google/electra-base-discriminator vs gpt-oss:20b: delta=not assessed (needs_data)