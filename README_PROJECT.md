# LLM Model Scout

Dieses Projekt kombiniert einen lokalen Ollama-Benchmark mit einem Modell-Scout,
der Kandidaten sammelt, normalisiert, bewertet und mit nachvollziehbaren
Reports sowie einer SQLite-Historie dokumentiert.

## Aktueller Status

Die folgende Implementierung ist in der aktuellen Codebasis verifiziert:

- Discovery über Ollama, Hugging Face, Artificial Analysis und SWE-bench
- Deduplizierung und Normalisierung von Modellnamen und Metadaten
- Benchmark-Planung, Task-Lifecycle und Wiederaufnahme nach Abbruch
- Champion/Challenger-Vergleich mit Benchmark-Deltas
- Dashboard mit Tabellen, Filtern und Chart-/Summaries
- Hardware-Telemetrie mit Peak-/Delta-Werten und Multi-GPU-Aggregation
- Reports mit Source-Coverage, Status und Kandidatenbewertung

## Einstieg

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/main.py --discover --hf-limit 10
python src/main.py --report --hf-limit 10
```

Für das Dashboard:

```powershell
streamlit run dashboard.py
```

## Kernkomponenten

- [ollama_benchmark.py](ollama_benchmark.py): reproduzierbarer Ollama-Benchmark mit CSV-Ausgabe und Telemetrie
- [benchmark/runner.py](benchmark/runner.py): CLI-Wrapper für Modell- und Kontextfilter
- [benchmark/prompts/personal.py](benchmark/prompts/personal.py): versionierter persönlicher Prompt-Katalog
- [src/pipeline.py](src/pipeline.py): Discovery über mehrere Quellen
- [src/discovery.py](src/discovery.py): Normalisierung und Deduplizierung
- [src/scoring.py](src/scoring.py): Score, Hardware-Tier, Champion-Deltas und Kandidatenempfehlungen
- [src/database.py](src/database.py): SQLite-Historie, Migrations- und Persistenzschicht
- [src/report.py](src/report.py): Markdown-Report mit Benchmark-Evidence und Champion-Vergleich
- [dashboard.py](dashboard.py): Read-only-Übersicht der gespeicherten Historie mit Filters und Summaries
- [src/telemetry.py](src/telemetry.py): GPU-, RAM- und CPU-Telemetrie mit nachlaufender Aggregation

## Daten und Reports

- `data/model_scout.db`: Kandidaten, Benchmark-Runs, Empfehlungen, Reports, Tasks und Source-Status
- `reports/`: datierte Markdown-Reports inklusive Offline- und Benchmark-Evidenz
- `ollama_benchmark_*.csv`: detaillierte lokale Benchmark-Ergebnisse mit Telemetrie

## Verifizierte Workflow-Schritte

1. Discovery und Quellenstatus prüfen
2. Benchmark-Queue und Download-Plan erzeugen
3. Benchmark-Plan mit Aufgabenstatus ausführen
4. Ergebnisse in SQLite persistieren
5. Dashboard und Reports mit Historie visualisieren
6. Champion/Challenger-Delta anhand erfolgreicher Benchmark-Runs vergleichen

Externe Quellen sind Hinweise und werden nicht automatisch als lokale
Benchmark-Ergebnisse behandelt. Modelle werden bewusst nicht automatisch
heruntergeladen oder bestehende Champions entfernt.
