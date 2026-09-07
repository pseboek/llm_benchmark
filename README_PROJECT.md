# Ollama LLM Benchmark

Dieses Projekt benchmarket lokale LLMs, die über Ollama bereitgestellt werden. Es führt für mehrere Modelle, Kontextgrößen und Prompts automatisierte Tests aus und schreibt die Ergebnisse als CSV-Datei.

Das Projekt besteht aus:

- [ollama_benchmark.py](ollama_benchmark.py): Benchmark-Skript
- CSV-Ausgabe: z. B. `ollama_benchmark_YYYYMMDD_HHMMSS.csv`

---

## Zweck des Projekts

Das Script vergleicht Modelle wie zum Beispiel:

- `Codestral:latest`
- `deepseek-r1:8b`
- `deepseek-coder:latest`
- `gemma3:4b`
- `gpt-oss:20b`
- `qwen2.5-coder:14b-instruct`

über mehrere Kontextgrößen:

- `8192`
- `16384`
- `32768`

und verschiedene Prompt-Kategorien:

- General
- Java
- Spring
- React
- Architecture

Es misst dabei unter anderem:

- Tokens pro Sekunde
- Ausführungsdauer
- Prompt-Laufzeit
- Gesamtzeit
- Erfolgs-/Fehlerstatus je Run

---

## Voraussetzungen

1. Ollama muss installiert sein.
2. Der Ollama-Server muss lokal laufen.
3. Die gewünschten Modelle müssen bereits heruntergeladen sein.

Prüfen, ob Ollama aktiv ist:

```bash
ollama list
```

Wenn der Server nicht läuft:

```bash
ollama serve
```

Modelle herunterladen, z. B.:

```bash
ollama pull qwen2.5-coder:14b-instruct
ollama pull deepseek-r1:8b
ollama pull gemma3:4b
```

---

## Projektstruktur

```text
llm_benchmark/
├── README.md
├── ollama_benchmark.py
├── ollama_benchmark_20260823_113958.csv
```

Die zentrale Konfiguration liegt im Skript in den Abschnitten:

- `MODELS`
- `CONTEXT_SIZES`
- `PROMPTS`
- `OLLAMA_URL`

---

## Benchmark starten

Im Projektordner ausführen:

```bash
python ollama_benchmark.py
```

Das Skript läuft dann automatisch durch:

1. alle definierten Modelle
2. alle definierten Kontextgrößen
3. alle Prompt-Kategorien
4. jeden Lauf gegen Ollama

Am Ende wird eine CSV-Datei mit dem Namen wie z. B.:

```text
ollama_benchmark_20260907_123456.csv
```

erstellt.

---

## Was das Benchmark-Skript genau macht

Das Skript verwendet den Ollama-Endpoint:

```text
http://localhost:11434/api/generate
```

und sendet für jeden Test einen POST-Request mit:

- `model`
- `prompt`
- `stream: false`
- `options.num_ctx`
- `temperature: 0.0`

Danach werden Werte wie diese ausgewertet:

- `eval_count`
- `eval_duration`
- `prompt_eval_count`
- `tok_per_sec`
- Gesamtzeit

Am Ende wird eine kurze Zusammenfassung in der Konsole ausgegeben, z. B.:

- Durchschnittliche Tokens/Sekunde pro Modell und Kontext
- Vergleich zwischen 8K, 16K und 32K
- Min-/Max-Werte

---

## Einzelne Modelle testen

Es gibt zwei einfache Wege.

### 1) Über curl

```bash
curl http://localhost:11434/api/generate \
  -d '{
    "model": "qwen2.5-coder:14b-instruct",
    "prompt": "Erkläre kurz den Unterschied zwischen einem Prozess und einem Thread.",
    "stream": false,
    "options": {
      "num_ctx": 8192,
      "temperature": 0.0
    }
  }'
```

### 2) Über Python

```python
import requests

payload = {
    "model": "qwen2.5-coder:14b-instruct",
    "prompt": "Erkläre kurz den Unterschied zwischen einem Prozess und einem Thread.",
    "stream": False,
    "options": {
        "num_ctx": 8192,
        "temperature": 0.0,
    }
}

response = requests.post(
    "http://localhost:11434/api/generate",
    json=payload,
    timeout=600,
)

response.raise_for_status()
print(response.json()["response"])
```

---

## Modelle konfigurieren

Im Skript in [ollama_benchmark.py](ollama_benchmark.py) kannst du die Liste an Modellen anpassen:

```python
MODELS = [
    "Codestral:latest",
    "deepseek-r1:8b",
    "gemma3:4b",
    "qwen2.5-coder:14b-instruct",
]
```

Wenn du nur bestimmte Modelle testen willst, entferne einfach die Einträge aus dieser Liste.

---

## Kontextgrößen anpassen

```python
CONTEXT_SIZES = [
    8192,
    16384,
    32768,
]
```

Wenn du nur 8K oder 16K testen willst, reduziere diese Liste.

---

## Prompts anpassen

Die Prompt-Kategorien stehen in `PROMPTS`:

```python
PROMPTS = {
    "General": "...",
    "Java": "...",
    "Spring": "...",
    "React": "...",
    "Architecture": "...",
}
```

Du kannst neue Kategorien hinzufügen oder vorhandene Texte ändern.

---

## Ergebnisinterpretation

Die CSV enthält für jeden Lauf eine Zeile mit Spalten wie:

- `timestamp`
- `model`
- `context`
- `category`
- `status`
- `tokens`
- `generation_seconds`
- `tok_per_sec`
- `prompt_tokens`
- `prompt_seconds`
- `load_seconds`
- `total_seconds`
- `response`
- `error`

Wichtige Kennzahl:

```text
tok_per_sec
```

Diese Zahl hilft dabei, Modelle und Kontextgrößen untereinander zu vergleichen.

---

## typischer Ablauf

1. Ollama starten
2. Modelle herunterladen
3. Benchmark ausführen
4. CSV-Ausgabe prüfen
5. Modell mit den besten Ergebnissen für den eigenen Anwendungsfall auswählen

Beispiel:

```bash
ollama serve
ollama pull qwen2.5-coder:14b-instruct
ollama pull deepseek-coder:latest
python ollama_benchmark.py
```

---

## Hinweise

- Das Benchmarking kann je nach Hardware, Temperatur, Modellgröße und CPU/GPU-Auslastung stark variieren.
- Ein Modell mit höherer Qualität ist nicht automatisch das schnellste.
- Für reale Vergleiche solltest du dieselben Prompts und dieselben Kontextgrößen für alle Modelle verwenden.
- Wenn ein Modell fehlschlägt, prüfe zunächst, ob es korrekt in Ollama installiert ist.

---

## Schnellstart

```bash
ollama serve
ollama pull qwen2.5-coder:14b-instruct
python ollama_benchmark.py
```

Wenn du ein einzelnes Modell kurz testen möchtest:

```bash
curl http://localhost:11434/api/generate \
  -d '{
    "model": "qwen2.5-coder:14b-instruct",
    "prompt": "Schreibe einen kurzen, prägnanten Überblick über Dependency Injection in Spring Boot.",
    "stream": false,
    "options": {"num_ctx": 8192, "temperature": 0.0}
  }'
```

---

## Fazit

Das Projekt eignet sich hervorragend, um lokale Modelle schnell zu vergleichen, ohne externe APIs zu verwenden. Es ist besonders nützlich für:

- Modellvergleich
- Kontextgrößen-Tests
- Performance-Messungen
- Auswahl des passenden Modells für lokale KI-Workloads
