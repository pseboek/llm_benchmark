from __future__ import annotations

PROMPT_VERSION = "v1"

PERSONAL_PROMPTS = {
    "01 Java": "Write a production-quality Java service that validates input and handles a missing repository result. Explain the design decisions.",
    "02 Spring Boot": "Diagnose a Spring Boot circular dependency and propose a production-safe refactoring.",
    "03 React": "Build a small React component with state, an event handler, and a derived value. Explain render behavior.",
    "04 TypeScript": "Design a type-safe TypeScript API client with discriminated error results and one usage example.",
    "05 SQL DB2": "Write a parameterized SQL query that finds duplicate business keys and explain its indexing implications.",
    "06 Debugging": "Given a slow web request, describe a concrete, evidence-driven debugging sequence and likely measurements.",
    "07 Architecture": "Design a maintainable React and Spring Boot application with PostgreSQL, REST, Docker, and CI/CD.",
    "08 MCP": "Explain how to expose a safe read-only MCP tool and define its input validation and error behavior.",
    "09 RAG": "Design a grounded RAG flow with chunking, retrieval, citations, and a response refusal policy.",
    "10 General Reasoning": "Compare two plausible solutions to a technical problem, state assumptions, and recommend one with trade-offs.",
}
