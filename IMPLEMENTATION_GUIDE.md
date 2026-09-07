# LLM Model Scout – Implementierungsleitfaden

## 1. Ziel

Der **LLM Model Scout** entdeckt regelmäßig neue Open-Weight-LLMs, bewertet deren Eignung für das konkrete lokale Setup und schlägt nur Kandidaten für einen lokalen Benchmark vor.

### Zielsystem

- Windows 11
- NVIDIA RTX 4080, 16 GB VRAM
- AMD Ryzen 7 7800X3D
- 32 GB RAM
- Ollama
- Python 3.11+

### Aktuelle lokale Baseline

| Modell | Rolle | lokale Gen.-Geschwindigkeit |
|---|---|---:|
| GPT-OSS 20B | General / Coding / Reasoning | ~140 tok/s |
| Qwen2.5-Coder 14B Instruct | Coding | ~67 tok/s bei 8–16K |
| Qwen3.5 9B | Fast General | ~98 tok/s |
| DeepSeek-R1 8B | Reasoning | ~110 tok/s |
| Gemma4 12B | General | ~70 tok/s |
| DeepSeek-Coder | Ultra-fast Coding | ~466 tok/s |

Die Werte sind lokale Referenzwerte und müssen für faire Vergleiche unter möglichst gleichen Bedingungen gemessen werden.

---

## 2. Grundarchitektur

Discovery und Benchmark werden bewusst getrennt:

```text
Ollama ───────────────┐
Hugging Face ─────────┤
LMArena ──────────────┤
Artificial Analysis ──┤──> Discovery ─> Normalisierung
SWE-bench ────────────┘                 │
                                        v
                               Candidate Scoring
                                        │
                         ┌──────────────┼──────────────┐
                         v              v              v
                       TEST          SURPRISE        WATCH
                         │
                         v
                 lokaler Benchmark
                         │
                         v
                 Champion/Challenger
```

Das System soll **nicht jedes neue Modell automatisch herunterladen**.

---

## 3. Quellen

### Ollama

Quelle für lokale Verfügbarkeit, Tags, Größen, Kontext, Tools/Thinking und Varianten.

Die Discovery nutzt `/api/tags` für die Liste und `/api/show` für verfügbare
Architektur-, Quantisierungs-, Parameter- und Kontextmetadaten.

https://ollama.com/library

### Hugging Face

Quelle für neue Open-Weight-Modelle, Modellkarten, Parameter, Quantisierungen und Community-Benchmarks.

https://huggingface.co/

### LMArena

Quelle für menschliche Präferenzdaten. Besonders interessant ist der Software-/IT-Bereich.

https://lmarena.ai/leaderboard

### Artificial Analysis

Quelle für vergleichbare Qualitäts-, Coding-, Reasoning-, Geschwindigkeits- und Kontextdaten.

https://artificialanalysis.ai/

Für automatisierte Zugriffe API-Dokumentation und Nutzungsbedingungen beachten.

### SWE-bench

Quelle für Software-Engineering-Leistung.

https://www.swebench.com/

---

## 4. Hardware-Fit: keine harte 16-GB-Grenze

Die RTX 4080 hat 16 GB VRAM, aber Runtime-VRAM ist nicht gleich Modell-Dateigröße.

Bisher wurde beispielsweise beobachtet:

```text
Qwen2.5-Coder 14B
32K Context
~15 GB Runtime
93 % GPU / 7 % CPU
~47 tok/s
```

Deshalb gibt es einen Toleranzbereich.

| Tier | geschätzter Runtime-VRAM | Bedeutung |
|---|---:|---|
| SAFE | <= 13 GB | sehr wahrscheinlich problemlos |
| BORDERLINE | 13–18 GB | ausdrücklich testen |
| EXPERIMENTAL | 18–24 GB | nur bei interessanter Qualität/Architektur |
| SURPRISE | >24 GB, aber interessante MoE-/Architekturmerkmale | Sonderprüfung |
| UNLIKELY | >24 GB ohne besondere Merkmale | normalerweise ignorieren |

Die Werte sind **Heuristiken**, keine Garantie.

---

## 5. MoE berücksichtigen

Der Scout darf Gesamtparameter nicht mit aktiven Parametern gleichsetzen.

Beispiel:

```text
30B total / 3B active
```

kann für lokale Inferenz deutlich interessanter sein als ein dichter 30B-Ansatz.

Erfassen:

```yaml
parameters_total:
parameters_active:
is_moe:
architecture:
context_length:
quantization:
```

---

## 6. Candidate Score

Startgewichtung:

| Faktor | Gewicht |
|---|---:|
| Coding | 25 % |
| Reasoning | 20 % |
| General Quality | 15 % |
| Speed | 15 % |
| VRAM Efficiency | 10 % |
| Context | 5 % |
| Tool / Agent | 5 % |
| Freshness | 5 % |

Die Gewichte sollen später anhand der eigenen Benchmark-Historie angepasst werden.

---

## 7. Champion/Challenger

Bestehende Modelle bleiben Champions. Neue Modelle sind Challengers.

Ein Kandidat wird besonders interessant bei:

- >=10 % erwarteter Qualitätssteigerung
- >=10 % Coding-Steigerung
- >=10 % Reasoning-Steigerung
- ähnlicher Qualität bei >=30 % höherer Geschwindigkeit
- deutlich besserem Kontext
- deutlich besseren Tool-/Agent-Fähigkeiten
- deutlich besserer VRAM-Effizienz
- interessanter MoE-Architektur

---

## 8. Surprise Candidates

Ein Kandidat kann trotz Überschreitung der nominalen Hardwareklasse als

```text
🟣 SURPRISE
```

markiert werden.

Beispiele:

- MoE mit wenigen aktiven Parametern
- knapp oberhalb des VRAM-Budgets
- sehr gute Q4/Q5-Quantisierung
- außergewöhnliche Coding-/SWE-bench-Werte
- hohe externe Qualität bei moderatem Runtime-Bedarf

---

## 9. Projektstruktur

```text
llm-model-scout/
├── README.md
├── IMPLEMENTATION_GUIDE.md
├── requirements.txt
├── config.yaml
├── .env.example
├── .gitignore
├── dashboard.py
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── scoring.py
│   ├── database.py
│   ├── report.py
│   ├── adaptive.py
│   └── sources/
│       ├── __init__.py
│       ├── ollama.py
│       ├── huggingface.py
│       ├── lmarena.py
│       ├── artificial_analysis.py
│       └── swebench.py
├── benchmark/
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── personal.py
│   └── runner.py
├── data/
├── reports/
└── tests/
```

---

## 10. Konfiguration

Hardware, Schwellenwerte und Baseline gehören in `config.yaml`, nicht in den Python-Code.

Die mitgelieferte Konfiguration enthält dein aktuelles RTX-4080-Profil und deine bekannten Champions.

---

## 11. Datenmodell

Für Version 1 genügt SQLite.

Empfohlene Tabellen:

```text
models
sources
model_sources
benchmarks
benchmark_runs
quality_scores
recommendations
```

Wichtige Felder:

```text
model_name
version
source
release_date
parameters_total
parameters_active
is_moe
context_length
quantization
estimated_vram_gb
coding_score
reasoning_score
general_score
speed_score
tool_score
freshness_score
hardware_tier
candidate_score
recommendation
created_at
```

---

## 12. Discovery

Alle Quellen liefern zunächst Kandidaten:

```python
candidates = []
candidates.extend(ollama.discover())
candidates.extend(huggingface.discover())
candidates.extend(lmarena.discover())
candidates.extend(artificial_analysis.discover())
candidates.extend(swebench.discover())
candidates = deduplicate(candidates)
```

Danach werden die Daten zu einem Modellprofil zusammengeführt.

Ein Modell kann beispielsweise gleichzeitig in Ollama, Hugging Face, LMArena und Artificial Analysis auftauchen.

---

## 13. Normalisierung

Unterschiedliche Namen sollen auf eine gemeinsame Modellfamilie abgebildet werden:

```text
qwen3-coder
Qwen3-Coder
Qwen/Qwen3-Coder
qwen3-coder:30b
```

Sinnvolle Normalisierungsfelder:

```text
vendor
family
variant
parameter_size
quantization
```

---

## 14. Lokaler Benchmark

Der vorhandene Benchmark wird als zweite Phase integriert.

Für ausgewählte Kandidaten:

```text
8K
16K
32K
```

messen:

- TTFT
- Prompt tok/s
- Generation tok/s
- Gesamtdauer
- Prompt Tokens
- Output Tokens
- VRAM
- CPU/GPU-Aufteilung
- RAM
- GPU-Auslastung

Der aktuelle Benchmark misst Prompt tok/s und speichert die Prompt-Version.
TTFT wird inzwischen per Ollama-Streaming gemessen und persistiert. Wenn die
lokale Umgebung `nvidia-smi` und `psutil` bereitstellt, werden außerdem
GPU-Auslastung, GPU-Speicher, RAM und CPU-Auslastung erfasst. Fehlende
Telemetrie-Tools bleiben ohne Einfluss auf den Benchmarklauf.

Generation tok/s:

```python
generation_tps = eval_count / (eval_duration / 1_000_000_000)
```

---

## 15. Persönlicher Quality Benchmark

Der technische Benchmark sollte durch feste, reproduzierbare Aufgaben ergänzt werden.

Empfohlene Kategorien:

```text
01 Java
02 Spring Boot
03 React
04 TypeScript
05 SQL / DB2
06 Debugging
07 Architektur
08 MCP
09 RAG
10 General Reasoning
```

Prompts werden versioniert und zwischen Runs nicht verändert.

Das Ziel ist nicht ein allgemeiner LLM-Test, sondern ein **persönlicher Benchmark für die tatsächlichen Aufgaben**.

Die erste versionierte Sammlung liegt in `benchmark/prompts/personal.py` und
enthält die zehn Kategorien als `PROMPT_VERSION = "v1"`. Änderungen an den
Aufgaben sollen eine neue Prompt-Version erhalten, damit historische Runs
vergleichbar bleiben.

---

## 16. Entscheidungslogik

Start:

```text
score >= 85
    -> TEST_NOW

score >= 80 + ungewöhnlich hoher Hardware-/Architekturwert
    -> SURPRISE_TEST

score >= 70
    -> WATCH

sonst
    -> IGNORE
```

Zusätzlich sollte der Vergleich mit dem jeweiligen Champion berücksichtigt werden.

---

## 17. Reports

Alle zwei Wochen entsteht beispielsweise:

```text
reports/2026-09-06_model_scout.md
```

Der Report enthält:

```text
Executive Summary
Test Now
Surprise Candidates
Watchlist
Champion-Vergleich
Hardware-Fit
Quellen
```

Jede Empfehlung soll begründen:

- Warum?
- Gegen welchen Champion?
- Erwarteter Vorteil?
- Geschätzter VRAM?
- Risiken?
- Welche Quellen stützen die Empfehlung?

---

## 18. Automatisierung

Für Windows 11:

```text
Windows Task Scheduler
        ↓
python src/main.py
        ↓
Discovery
        ↓
Scoring
        ↓
Markdown Report
```

Empfehlung für V1:

**Alle 14 Tage nur Discovery und Report automatisieren.**

Download und Benchmark zunächst bewusst manuell auslösen.

Später kann die Pipeline für `TEST_NOW` automatisiert werden.

Der aktuelle Stand stellt die CLI, das Dashboard und
`scripts/run_scout_report.ps1` bereit. Das Skript kann im Windows Task
Scheduler als Aktion für einen zweiwöchigen Offline-Report hinterlegt werden.
Downloads und lokale Modellbenchmarks bleiben bewusst manuell.

---

## 19. API-Sicherheit

Keine API Keys in Git, YAML oder Python.

Verwenden:

```text
.env
```

Beispiel:

```text
ARTIFICIAL_ANALYSIS_API_KEY=
HUGGINGFACE_TOKEN=
```

`.env` muss in `.gitignore`.

Die externen Adapter lesen `HUGGINGFACE_TOKEN` und
`ARTIFICIAL_ANALYSIS_API_KEY` nur aus der Prozessumgebung. Temporäre
HTTP-Fehler werden begrenzt wiederholt; dauerhafte Fehler führen zu einer
leeren Quelle und stoppen nicht die lokale Discovery.

---

## 20. Entwicklungsstufen

### V1
Discovery + Scoring + Markdown Report

### V2
Ollama-Benchmark integrieren (inklusive persönlicher Prompts, Prompt-tok/s und TTFT)

### V3
SQLite-Historie

### V4
Streamlit-Dashboard mit Modell-/Empfehlungsfiltern und Kontextvergleich (implementiert in `dashboard.py`)

### V5
automatischer Champion/Challenger-Vergleich (implementiert in `src/scoring.py` und `src/report.py`)

### V6
kontrollierte Downloads ausgewählter Kandidaten (implementiert als Planungs- und Freigabefluss in `src/download_queue.py`)

### V7
adaptive Gewichte anhand historischer Benchmarks (Vorschlag in `src/adaptive.py` und über `--suggest-weights`, keine automatische Konfigurationsänderung)

---

## 21. Qualitätsregeln

Der Scout darf niemals:

1. Marketing-Benchmarks als absolute Wahrheit behandeln.
2. ein Modell ausschließlich wegen Parameterzahl ausschließen.
3. MoE nur anhand der Gesamtparameter bewerten.
4. Modell-Dateigröße mit Runtime-VRAM gleichsetzen.
5. externe Benchmarks mit lokalen Messungen gleichsetzen.
6. automatisch bestehende Champions löschen.

Der wichtigste Entscheidungsweg:

```text
externe Daten
+ Hardware-Fit
+ eigener Benchmark
+ Champion-Vergleich
= Entscheidung
```

---

## 22. Zielausgabe

Alle zwei Wochen soll die Ausgabe klein bleiben:

```text
🟢 1–3 Modelle testen
🟣 0–2 Surprise Candidates
🟡 2–5 beobachten
⚪ Rest ignorieren
```

Der Zweck ist nicht, möglichst viele Modelle zu sammeln, sondern zuverlässig zu erkennen:

> **Welches neue Modell ist auf meiner konkreten RTX-4080-Umgebung interessant genug, um es zu testen?**
