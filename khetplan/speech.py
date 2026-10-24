"""Browser speech recognition bridge (Web Speech API) with a typed fallback.

Recognition runs in the user's browser. Chrome and Edge may send audio to the vendor's
speech service; KhetPlan's Python server never receives or stores audio.
"""
from __future__ import annotations

from pathlib import Path

import streamlit.components.v1 as components

_COMPONENT = components.declare_component(
    "khetplan_speech", path=str(Path(__file__).resolve().parent.parent / "components" / "speech")
)


def speech_input(locale: str, labels: dict, key: str = "speech"):
    """Returns None, {"kind": "transcript", "text", "seq"} or {"kind": "error", "error", "seq"}."""
    return _COMPONENT(lang=locale, labels=labels, key=key, default=None)
