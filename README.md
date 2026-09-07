# LLM Model Scout

Lokaler Model-Discovery- und Benchmark-Scout für Windows 11 / RTX 4080.

## Start

```powershell
cd C:\Users\psebo\Desktop\ai_projects\llm-model-scout
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src\main.py
```

Die mitgelieferte `main.py` ist zunächst ein funktionierender Skeleton-Test. Die fünf Source-Adapter und der vorhandene lokale Benchmark werden anschließend integriert.

Siehe `IMPLEMENTATION_GUIDE.md`.
