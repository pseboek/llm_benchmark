from __future__ import annotations


def build_report(candidates: list[dict]) -> str:
    lines: list[str] = []
    lines.append("# Model Scout Report")
    lines.append("")
    lines.append(f"- Total candidates: {len(candidates)}")
    lines.append(f"- {len(candidates)} candidates")
    lines.append("- Sources: ollama, huggingface")
    lines.append("")
    lines.append("## Candidates")

    for candidate in candidates:
        name = candidate.get("name", "unknown")
        source = candidate.get("source", "unknown")
        lines.append(f"- {name} ({source})")

    return "\n".join(lines)
