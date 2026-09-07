# LLM Model Scout – Implementierungsleitfaden

## 1. Ziel

Der **LLM Model Scout** entdeckt regelmäßig neue Open-Weight-LLMs, bewertet deren Eignung für das konkrete lokale Setup und schlägt nur Kandidaten für einen lokalen Benchmark vor.

### Verifizierter Umsetzungsstand (2026-09-07)

Die aktuelle Implementierung umfasst die folgenden, in der Test-Suite bestätigten Funktionen:

- Discovery über Ollama, Hugging Face, Artificial Analysis und SWE-bench
- Kandidaten-Normalisierung und De-Duplizierung
- SQLite-basierte Persistenz mit Kandidaten, Runs, Empfehlungen, Tasks und Source-Status
- Benchmark-Task-Lifecycle mit `PENDING_EXECUTION`, `RUNNING`, `COMPLETED` und `FAILED`
- Champion/Challenger-Vergleich mit Benchmark-Speeed-/Quality-Deltas
- Dashboard mit Filtern, Summaries und Bewertungs-/Telemetrie-Tabellen
- Hardware-Telemetrie mit GPU-, RAM-, CPU- und Peak-/Delta-Metriken
- Markdown-Reports mit Source-Coverage und Benchmark-Evidence

---

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

Die aktuelle Implementierung nutzt SQLite mit einem nachvollziehbaren, in der Praxis bewährten Schema.

Aktuelle Tabellen:

```text
candidates
benchmark_runs
recommendations
report_snapshots
benchmark_tasks
source_status
```

Wichtige Felder:

```text
candidates:
  name, source, parameter_size, quantization, architecture,
  estimated_vram_gb, parameters_total_b, context_length

benchmark_runs:
  model, context, category, status, tok_per_sec, prompt_version,
  prompt_tok_per_sec, ttft_seconds, quality_score,
  quality_method, quality_confidence, quality_components, error,
  telemetry_captured_at, telemetry_duration_seconds,
  gpu_count, gpu_utilization_percent, gpu_utilization_peak_percent,
  gpu_memory_used_mb, gpu_memory_total_mb, gpu_memory_utilization_percent,
  ram_used_mb, cpu_percent

recommendations:
  model, score, hardware_tier, recommendation

report_snapshots:
  total_candidates, test_now, surprise_test, watch, needs_data, ignored

benchmark_tasks:
  model, context, category, prompt_version, status

source_status:
  source, status, candidates, error
```

Die Tabelle `benchmark_runs` enthält außerdem Peak- und Delta-Werte für GPU-, RAM- und CPU-Telemetrie, um Laufvergleich und Dashboard-Visualisierung sauber zu unterstützen.

---

## 12. Discovery

Alle Quellen liefern zunächst Kandidaten:

```python
candidates = []
candidates.extend(ollama.discover())
candidates.extend(huggingface.discover())
candidates.extend(artificial_analysis.discover())
candidates.extend(swebench.discover())
candidates = deduplicate(candidates)
```

Danach werden die Daten zu einem Modellprofil zusammengeführt.

Ein Modell kann beispielsweise gleichzeitig in Ollama, Hugging Face und Artificial Analysis auftauchen.

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

Der vorhandene Benchmark ist als zweite Phase integriert und lauffähig.

Für ausgewählte Kandidaten werden typischerweise folgende Context-Größen gemessen:

```text
8K
16K
32K
```

Gemessen werden unter anderem:

- TTFT
- Prompt tok/s
- Generation tok/s
- Gesamtdauer
- Prompt Tokens
- Output Tokens
- VRAM-/GPU-Metriken
- CPU/GPU-Aufteilung
- RAM
- GPU-Auslastung
- Telemetrie-Delta und Peak-Werte

Der aktuelle Benchmark misst Prompt tok/s und speichert die Prompt-Version.
TTFT wird über Ollama-Streaming ermittelt und persistiert. Wenn die lokale
Umgebung `nvidia-smi` und `psutil` bereitstellt, werden zusätzlich
GPU-Auslastung, GPU-Speicher, RAM und CPU-Auslastung erfasst. Fehlende
Telemetrie-Tools bleiben ohne Einfluss auf den Benchmarklauf.

Generation tok/s:

```python
generation_tps = eval_count / (eval_duration / 1_000_000_000)
```

Für jeden Run werden außerdem ein UTC-Zeitstempel, die Messdauer und die
Vorher-/Nachher-Delta-Werte gespeichert, damit Performance-Unterschiede im
Dashboard und in Reports nachvollziehbar bleiben.

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

Die aktuelle Logik ist implementiert und in der Datenbank sowie im Dashboard sichtbar:

```text
score >= 85
    -> TEST_NOW

score >= 80 + ungewöhnlich hoher Hardware-/Architekturwert
    -> SURPRISE_TEST

score >= 70
    -> WATCH

quality data missing
        -> NEEDS_DATA

sonst
    -> IGNORE
```

Zusätzlich wird der jeweilige Champion berücksichtigt. Der Vergleich nutzt
`benchmark_profile()` und `champion_comparison()` mit tatsächlichen
Benchmark-Runs, sodass Speed- und Quality-Delta statt nur eines Gesamt-Score-Deltas
berücksichtigt werden.

---

## 17. Reports

Das Reporting ist implementiert und in der Praxis nutzbar. Ein Beispiel:

```text
reports/2026-09-07_model_scout.md
```

Der Report enthält:

```text
Executive Summary
Source Coverage
Source Status
Recommendations
Candidates
Benchmark Evidence
Champion Comparison
Benchmark task progress
```

Zusätzlich weist der Report die Kandidatenanzahl je Quelle aus und dokumentiert
Quellenstatus (`OK`, `EMPTY`, `DISABLED`, `ERROR`). Nicht verfügbare oder
nicht strukturierte externe Endpunkte werden dadurch sichtbar, ohne lokale
Discovery-Ergebnisse zu verschleiern.

Jede Empfehlung begründet:

- Warum?
- Gegen welchen Champion?
- Erwarteter Vorteil?
- Geschätzter VRAM?
- Risiken?
- Welche Quellen stützen die Empfehlung?

---

## 18. Automatisierung

Für Windows 11 ist die Automated-Report-Pipeline bereits vorbereitet:

```text
Windows Task Scheduler
        ↓
python src/main.py --report --offline
        ↓
Discovery/Scoring
        ↓
Markdown Report
```

Der aktuelle Stand stellt die CLI, das Dashboard und
`scripts/run_scout_report.ps1` bereit. Das Skript kann im Windows Task
Scheduler als Aktion für einen zweiwöchigen Offline-Report hinterlegt werden.
Downloads und lokale Modellbenchmarks bleiben bewusst manuell, während die
Benchmark-Planung, Task-Status-Verwaltung und Recovery gesteuert werden.

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

Benchmark-Antworten werden zusätzlich mit dem transparent gekennzeichneten
`heuristic_v2`-Grader bewertet. Er liefert Teilwerte für Vollständigkeit,
Struktur und Relevanz sowie eine Konfidenz. Für produktive Qualitätsentscheidungen sollte
dieser später durch domänenspezifische oder menschlich validierte Grader
ergänzt werden.

Gespeicherte erfolgreiche Runs werden bei der Report-Erzeugung wieder in die
Kandidatenprofile und deren Score übernommen.

Die Hardware-Telemetrie wird pro Benchmark-Run vor und nach der Anfrage erfasst.
GPU-Werte werden über alle von `nvidia-smi` gemeldeten Geräte aggregiert. Neben
Durchschnitts- und Peak-Werten werden Messdauer sowie Deltas für GPU, Speicher,
RAM und CPU gespeichert. Nicht verfügbare Sensoren bleiben `NULL`.

Jeder Kandidat wird außerdem als `ASSESSED`, `METADATA_ONLY` oder `NEEDS_DATA`
gekennzeichnet. Champion/Challenger-Vergleiche verwenden verfügbare lokale
Benchmarkprofile für Speed- und Quality-Deltas.

Der Report weist zusätzlich die gemessene Benchmark-Evidence pro Modell aus:
Generation tok/s, Quality-Score und Anzahl erfolgreicher Runs.

### V3
SQLite-Historie

### V4
Streamlit-Dashboard mit Modell-/Empfehlungsfiltern, Kontextvergleich und Hardware-Telemetrie (implementiert in `dashboard.py`)

### V5
automatischer Champion/Challenger-Vergleich (implementiert in `src/scoring.py` und `src/report.py`)

### V6
kontrollierte Downloads ausgewählter Kandidaten (implementiert als Planungs- und Freigabefluss in `src/download_queue.py`)

Nach einer expliziten Freigabe erzeugt `src/benchmark_plan.py` aus den
freigegebenen Modellen, konfigurierten Kontextgrößen und dem versionierten
Promptkatalog reproduzierbare `PENDING_EXECUTION`-Tasks.

Vor der Ausführung kann `--dry-run-plan` die offenen Tasks anzeigen, ohne
Ollama zu starten oder Benchmark-Daten zu verändern.

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
