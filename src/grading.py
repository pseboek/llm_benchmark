from __future__ import annotations


def grade_response(response: str, category: str) -> dict[str, object]:
    """Return transparent heuristic components; this is not a human-quality claim."""
    text = (response or "").strip()
    if not text:
        return {
            "quality_score": 0.0,
            "quality_method": "heuristic_v2",
            "quality_confidence": 0.0,
            "quality_components": {"completeness": 0.0, "structure": 0.0, "relevance": 0.0},
        }

    completeness = 30.0
    if len(text) >= 200:
        completeness += 20.0
    if len(text) >= 600:
        completeness += 15.0
    structure = 0.0
    if "```" in text:
        structure += 40.0
    if "\n" in text:
        structure += 20.0
    category_terms = {
        "Java": ("class", "service"),
        "Spring Boot": ("dependency", "bean"),
        "React": ("state", "component"),
        "TypeScript": ("type", "interface"),
        "SQL DB2": ("select", "query"),
        "Debugging": ("diagnos", "measure"),
        "Architecture": ("component", "deployment"),
        "MCP": ("tool", "schema"),
        "RAG": ("retriev", "context"),
        "General Reasoning": ("because", "trade-off"),
    }
    lowered = text.lower()
    relevance = min(100.0, sum(term in lowered for term in category_terms.get(category, ())) * 50.0)
    score = (completeness * 0.4) + (structure * 0.2) + (relevance * 0.4)
    confidence = min(1.0, round((len(text) / 1000) + (0.25 if category in category_terms else 0), 2))
    return {
        "quality_score": min(100.0, round(score, 2)),
        "quality_method": "heuristic_v2",
        "quality_confidence": confidence,
        "quality_components": {
            "completeness": round(min(100.0, completeness), 2),
            "structure": round(min(100.0, structure), 2),
            "relevance": round(relevance, 2),
        },
    }
