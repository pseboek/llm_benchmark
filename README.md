# LLM Model Scout

Lokaler Model-Discovery- und Benchmark-Scout für Ollama-Modelle, lokale Benchmark-Tests und erste Kandidaten-Auswertung.

## Überblick

Das Projekt kombiniert zwei Ebenen:

- Discovery: lokale Ollama-Modelle plus Hugging Face Kandidaten sammeln und normalisieren
- Benchmark: ausgewählte Modelle lokal mit definierter Kontextgröße und Prompts testen
- Reporting: zusammengefasste Kandidatenliste und erste Auswertung erzeugen

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

Das sammelt derzeit:

- lokale Ollama-Modelle
- einen kurzen Satz aus Hugging Face Kandidaten
- dedupliziert und normalisiert die Modellnamen

### 2) Report erzeugen

```powershell
python src/main.py --report --hf-limit 10
```

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

## Projektstruktur

```text
.
├── README.md
├── IMPLEMENTATION_GUIDE.md
├── config.yaml
├── requirements.txt
├── ollama_benchmark.py
├── benchmark/
│   └── runner.py
├── src/
│   ├── main.py
│   ├── pipeline.py
│   ├── report.py
│   ├── discovery.py
│   ├── scoring.py
│   └── sources/
│       ├── __init__.py
│       ├── ollama.py
│       └── huggingface.py
├── tests/
│   ├── test_discovery.py
│   ├── test_ollama_source.py
│   ├── test_huggingface_source.py
│   └── test_report.py
├── data/
├── reports/
└── .env.example
```

## Wichtige Hinweise

- Der lokale Benchmark nutzt Ollama auf `http://localhost:11434/api/generate`.
- Die Discovery-Ausgabe ist bewusst einfach und soll als Grundlage für spätere Scoring- und Ranking-Logik dienen.
- Die Dokumentation in [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) beschreibt die nächste Phasen-Planung für Champion/Challenger, Hardware-Fit und Automated Reports.

## Nächste Erweiterungen

- Source-Adapter für weitere Anbieter ergänzen
- Score- und Hardware-Logik tiefer mit echten Benchmarks verknüpfen
- Historie und Reporting in Dateien oder SQLite abspeichern
- Auswahl von Kandidaten für automatische Benchmark-Queues

## Weiterführende Doku

- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
- [README_PROJECT.md](README_PROJECT.md)
