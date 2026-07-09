"""
ollama/health.py

Answers the two questions the app needs on every startup:
1. Is Ollama running at all?
2. Is the target model pulled?

This is the logic that will later drive the Phase 8 "detect and guide"
onboarding flow — for now it just powers the /health endpoint.

Depends on: config.py, ollama/client.py
Called from: routers/health.py
"""

from app.backend import config
from app.backend.ollama import client


def check_ollama_status() -> dict:
    """
    check_ollama_status
    Reports whether Ollama is reachable and whether the default target
    model is present.
    @return  dict  {
                 "reachable": bool,
                 "model_present": bool,
                 "target_model": str,
             }
    """
    reachable = client.is_reachable()

    model_present = False
    if reachable:
        models = client.list_models()
        # Ollama model names include a tag (e.g. "qwen2.5:3b") — exact match.
        model_present = config.DEFAULT_MODEL in models

    return {
        "reachable": reachable,
        "model_present": model_present,
        "target_model": config.DEFAULT_MODEL,
    }
