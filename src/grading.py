from __future__ import annotations


def grade_response(response: str, category: str) -> dict[str, object]:
    """Return a transparent heuristic score; this is not a human-quality claim."""
    text = (response or "").strip()
    if not text:
        return {"quality_score": 0.0, "quality_method": "heuristic_v1"}

    score = 30.0
    if len(text) >= 200:
        score += 20.0
    if len(text) >= 600:
        score += 15.0
    if "```" in text:
        score += 15.0
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
    score += min(20.0, sum(term in lowered for term in category_terms.get(category, ())) * 10.0)
    return {"quality_score": min(100.0, round(score, 2)), "quality_method": "heuristic_v1"}
