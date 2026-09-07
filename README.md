# LLM Model Scout

Lokaler Model-Discovery- und Benchmark-Scout für Ollama-Modelle, lokale Benchmark-Tests und erste Kandidaten-Auswertung.

## Überblick

Das Projekt kombiniert zwei Ebenen:

- Discovery: lokale Ollama-Modelle plus Hugging Face Kandidaten sammeln und normalisieren
- Erweiterung: zusätzlich LMArena, Artificial Analysis und SWE-bench Kandidaten einbinden
- Benchmark: ausgewählte Modelle lokal mit definierter Kontextgröße und Prompts testen
- Reporting: zusammengefasste Kandidatenliste und erste Auswertung erzeugen
- Persistence: entdeckte Kandidaten in einer SQLite-Datenbank speichern und später wieder verwenden

## Voraussetzungen

- Python 3.11+
- Ollama lokal installiert und gestartet
- optional: Internetzugang für Hugging Face API-Abfragen

Prüfen:

```powershell
ollama list
ollama serve
```

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Nutzung

### 1) Kandidaten entdecken

```powershell
python src/main.py --discover --hf-limit 10
```

Für einen reproduzierbaren Lauf ohne externe Quellen:

```powershell
python src/main.py --report --offline --output reports/offline_model_scout.md
```

Wenn Ollama nicht erreichbar ist, verwendet der Offline-Lauf die konfigurierte Baseline als Report-Grundlage.

Das sammelt derzeit:

- lokale Ollama-Modelle
- einen kurzen Satz aus Hugging Face Kandidaten
- zusätzliche Kandidaten aus LMArena, Artificial Analysis und SWE-bench
- dedupliziert und normalisiert die Modellnamen

Die Ergebnisse werden zusätzlich in einer lokalen SQLite-Datenbank unter `data/model_scout.db` persistiert.

### 2) Report erzeugen

```powershell
python src/main.py --report --hf-limit 10
```

Der Report wird als Markdown-Datei unter `reports/YYYY-MM-DD_model_scout.md` gespeichert. Mit `--output` kann ein anderer Zielpfad verwendet werden. Discovery- und Benchmark-Daten werden in `data/model_scout.db` archiviert; dieser Pfad kann mit `--db` geändert werden.

### 3) Lokalen Benchmark ausführen

```powershell
python src/main.py --run-benchmark --models qwen2.5-coder:14b-instruct --contexts 8192 16384
```

Oder ohne Einschränkung:

```powershell
python src/main.py --run-benchmark
```

### 4) Konfigurierte Baseline auflisten

```powershell
python src/main.py --list-models
```

### 5) Dashboard starten

```powershell
streamlit run dashboard.py
```

Das Dashboard liest die SQLite-Historie und zeigt Kandidaten, Empfehlungen, Benchmark-Task-Status, Report-Historie mit Lauf-Deltas, Qualitätswerte pro Kategorie, durchschnittliche Benchmark-Geschwindigkeit, Kontextvergleiche und Hardware-Telemetrie. Modelle, Empfehlungen, Quellen und Hardware-Tiers können direkt gefiltert werden. Ein anderer Datenbankpfad kann über den Startparameter gesetzt werden:

```powershell
streamlit run dashboard.py -- --db data/alternative.db
```

### 6) Adaptive Gewichtung prüfen

Die Funktion `src/adaptive.py` kann historische Benchmark-Runs auswerten und eine vorgeschlagene Gewichtung berechnen. Die Änderung wird bewusst nicht automatisch in `config.yaml` geschrieben; dadurch bleibt jede Anpassung nachvollziehbar und reviewbar.

```powershell
python src/main.py --suggest-weights --output reports/weight_suggestion.json
```

### 7) Manuelle Benchmark-Queue erzeugen

```powershell
python src/main.py --queue --baseline-only --output reports/benchmark_queue.json
```

Die Queue enthält höchstens `--max-candidates` Modelle mit `TEST_NOW` oder `SURPRISE_TEST`. Sie startet keinen Download und keinen Benchmark automatisch; jedes Element bleibt zunächst auf `PENDING_REVIEW`.

### 8) Zweiwöchigen Report automatisieren

Das portable Skript [scripts/run_scout_report.ps1](scripts/run_scout_report.ps1) erzeugt einen Offline-Report mit repository-relativen Pfaden:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_scout_report.ps1
```

Für den Windows Task Scheduler wird dieses Skript als Aktion mit dem Trigger `Alle 14 Tage` hinterlegt. Es startet keine Downloads und keinen lokalen Modellbenchmark.

### 9) Download-Plan prüfen und freigeben

```powershell
python src/main.py --download-queue reports/benchmark_queue.json --output reports/download_plan.json
```

Das erzeugt zunächst nur `PENDING_APPROVAL`-Einträge. Nach manueller Prüfung können ausgewählte Modelle explizit freigegeben und ausgeführt werden:

```powershell
python src/main.py --download-queue reports/benchmark_queue.json --approve-models deepseek-coder:latest --execute-downloads
```

Ohne `--execute-downloads` wird kein `ollama pull` gestartet.

### 10) Benchmark-Plan nach Freigabe erzeugen

```powershell
python src/main.py --benchmark-plan reports/benchmark_queue.json --approve-models deepseek-coder:latest --contexts 8192 16384 --output reports/benchmark_plan.json
```

Der Plan erzeugt je freigegebenem Modell, Kontext und persönlicher Prompt-Kategorie einen `PENDING_EXECUTION`-Task. Die Ausführung bleibt ein separater, kontrollierbarer Schritt.

Nach Prüfung kann der Plan explizit ausgeführt werden:

```powershell
python src/main.py --run-plan reports/benchmark_plan.json --db data/model_scout.db
```

Dabei werden ausschließlich Tasks mit `PENDING_EXECUTION` ausgeführt und die Ergebnisse anschließend in SQLite gespeichert.

Vor der Ausführung kann der Plan sicher geprüft werden:

```powershell
python src/main.py --dry-run-plan reports/benchmark_plan.json
```

Der Dry Run startet kein Ollama und verändert keine Benchmark-Daten.

## Projektstruktur

```text
.
├── README.md
├── IMPLEMENTATION_GUIDE.md
├── config.yaml
├── requirements.txt
├── ollama_benchmark.py
├── dashboard.py
├── reports/
│   ├── benchmark_queue.json
│   ├── benchmark_plan.json
│   ├── download_plan.json
│   └── offline_model_scout.md
├── scripts/
│   └── run_scout_report.ps1
├── benchmark/
│   ├── runner.py
│   └── prompts/
│       ├── __init__.py
│       └── personal.py
├── src/
│   ├── main.py
│   ├── pipeline.py
│   ├── report.py
│   ├── database.py
│   ├── discovery.py
│   ├── scoring.py
│   ├── adaptive.py
│   ├── benchmark_plan.py
│   ├── benchmark_queue.py
│   ├── download_queue.py
│   ├── grading.py
│   ├── telemetry.py
│   └── sources/
│       ├── __init__.py
│       ├── lmarena.py
│       ├── artificial_analysis.py
│       ├── swebench.py
│       ├── ollama.py
│       └── huggingface.py
├── tests/
│   ├── test_discovery.py
│   ├── test_ollama_source.py
│   ├── test_huggingface_source.py
│   ├── test_report.py
│   ├── test_dashboard.py
│   ├── test_workflow.py
│   ├── test_champion.py
│   ├── test_adaptive.py
│   ├── test_prompts.py
│   ├── test_dashboard_filters.py
│   ├── test_telemetry.py
│   ├── test_source_http.py
│   ├── test_download_queue.py
│   ├── test_ollama_details.py
│   ├── test_ollama_metadata.py
│   ├── test_stream_metrics.py
│   ├── test_report_reasons.py
│   ├── test_configured_scoring.py
│   ├── test_scheduler_script.py
│   ├── test_adaptive_cli.py
│   ├── test_benchmark_plan.py
│   ├── test_benchmark_task_status.py
│   ├── test_benchmark_scoring.py
│   ├── test_grading.py
│   ├── test_huggingface_filter.py
│   └── test_dashboard_quality.py
├── data/
├── reports/
└── .env.example
```

## Wichtige Hinweise

- Der lokale Benchmark nutzt Ollama auf `http://localhost:11434/api/generate`.
- Der Benchmark verwendet den versionierten Promptkatalog `v1` und speichert Prompt-Version sowie Prompt-tok/s in SQLite und CSV.
- Jeder Benchmark-Run erhält zusätzlich einen transparent gekennzeichneten `heuristic_v1`-Quality-Score; dieser ist ein technischer Hinweis und kein menschlicher Qualitätsentscheid.
- Bei der nächsten Report-Erzeugung werden gespeicherte Benchmark-Runs wieder in Speed-, Coding- und Reasoning-Score der betroffenen Modelle übernommen.
- TTFT wird im Benchmark über Ollama-Streaming bis zum ersten Antworttoken gemessen und in CSV sowie SQLite gespeichert.
- Wenn verfügbar, werden zusätzlich GPU-Auslastung, GPU-Speicher, RAM-Nutzung und CPU-Auslastung über `nvidia-smi` und `psutil` erfasst.
- Ollama-Kandidaten werden über `/api/show` um Architektur, Quantisierung, Parametergröße und Kontextlänge angereichert.
- Hugging Face filtert bekannte Nicht-Text-Generationsmodelle wie Embedding- und Encoder-Modelle aus der LLM-Kandidatenliste.
- Externe Quellen verwenden `.env`-Tokens, JSON-Validierung, Timeouts und Retries für temporäre HTTP-Fehler.
- Die Discovery-Ausgabe ist bewusst einfach und soll als Grundlage für spätere Scoring- und Ranking-Logik dienen.
- Jeder Report enthält eine Source-Coverage mit Kandidatenanzahl pro Quelle; `0` bedeutet, dass die Quelle in diesem Lauf keine verwertbaren Kandidaten geliefert hat.
- Jeder Report enthält zusätzlich den Quellenstatus `OK`, `EMPTY`, `DISABLED` oder `ERROR`, damit leere externe Quellen diagnostizierbar bleiben.
- Die Kandidaten werden anhand der konfigurierten Gewichtung bewertet und in `TEST_NOW`, `SURPRISE_TEST`, `WATCH` und `IGNORE` eingeteilt.
- Kandidaten ohne eigene Qualitätsmessung werden als `NEEDS_DATA` mit Score `not assessed` geführt; sie werden nicht fälschlich als `IGNORE` mit neutralem Score bewertet.
- Die Quellenadapter sind fehlertolerant: eine nicht erreichbare externe Quelle verhindert nicht die lokale Ollama-Auswertung.
- Welche Quellen aktiv sind, wird im Abschnitt `sources` von `config.yaml` gesteuert.
- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) beschreibt Architektur, Datenmodell und verbleibende Betriebsschritte.

## Nächste Erweiterungen

- bessere externe Quellenadapter mit verifizierten API-Endpunkten
- zusätzliche Qualitätsgrader für Antwortqualität und Coding-Ergebnisse

## Weiterführende Doku

- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
- [README_PROJECT.md](README_PROJECT.md)
