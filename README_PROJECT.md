# LLM Model Scout

Dieses Projekt kombiniert einen lokalen Ollama-Benchmark mit einem Model Scout.
Der Scout entdeckt Kandidaten, normalisiert Quellen, bewertet Hardware-Fit und
erstellt nachvollziehbare Reports. Benchmark-Runs und Empfehlungen werden in
SQLite archiviert.

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

- [ollama_benchmark.py](ollama_benchmark.py): reproduzierbarer Ollama-Benchmark mit CSV-Ausgabe
- [benchmark/runner.py](benchmark/runner.py): CLI-Wrapper für Modell- und Kontextfilter
- [benchmark/prompts/personal.py](benchmark/prompts/personal.py): versionierter persönlicher Prompt-Katalog
- [src/pipeline.py](src/pipeline.py): Discovery über mehrere Quellen
- [src/discovery.py](src/discovery.py): Normalisierung und Deduplizierung
- [src/scoring.py](src/scoring.py): Score, Hardware-Tier und Empfehlung
- [src/database.py](src/database.py): SQLite-Historie
- [src/report.py](src/report.py): Markdown-Report mit Champion-Vergleich
- [dashboard.py](dashboard.py): read-only Übersicht der gespeicherten Historie

## Daten und Reports

- `data/model_scout.db`: Kandidaten, Benchmark-Runs und Empfehlungen
- `reports/`: datierte Markdown-Reports
- `ollama_benchmark_*.csv`: detaillierte lokale Benchmark-Ergebnisse

Externe Quellen sind Hinweise und werden nicht automatisch als lokale
Benchmark-Ergebnisse behandelt. Modelle werden bewusst nicht automatisch
heruntergeladen oder bestehende Champions entfernt.
