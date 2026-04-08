import re
from typing import Any, Dict

from app.core.rag import retrieve


def _parse_infection_confidence(wound_description: str) -> float:
    """Extract infection confidence percentage from text like 'Infected (Confidence: 94.3%)'."""
    match = re.search(r"confidence\s*:\s*(\d+(?:\.\d+)?)%", wound_description, re.IGNORECASE)
    if not match:
        return 0.0
    return float(match.group(1))


def _is_infected(wound_description: str) -> bool:
    text = wound_description.lower()
    return "infected" in text and "not infected" not in text


def _classify_severity(pain_level: int, infected: bool, confidence: float) -> str:
    if pain_level >= 8:
        return "high"
    if infected and pain_level >= 6:
        return "high"
    if infected and confidence >= 90 and pain_level >= 5:
        return "high"
    if pain_level >= 5 or infected:
        return "medium"
    return "low"


def _build_answer(description: str, severity: str, infected: bool) -> str:
    context = retrieve(description)

    if severity == "high":
        return (
            "High-risk symptoms detected. Please seek urgent medical attention today. "
            "Keep the wound clean and covered, avoid self-medicating with antibiotics, "
            f"and monitor for fever, spreading redness, or pus.\n\nRelevant guidance: {context}"
        )

    if severity == "medium":
        infection_note = "Possible infection signs are present. " if infected else ""
        return (
            f"{infection_note}Clean with saline, apply a sterile dressing, and observe closely for 24-48 hours. "
            "If pain worsens, redness spreads, or fever develops, consult a clinician.\n\n"
            f"Relevant guidance: {context}"
        )

    return (
        "Symptoms look low-risk at the moment. Keep the wound clean and dry, change dressing daily, "
        "and continue monitoring for worsening signs.\n\n"
        f"Relevant guidance: {context}"
    )


def chatbot(payload: Dict[str, Any]) -> Dict[str, str]:
    """Process wound-oriented payload and return triage response fields."""
    pain_level = int(payload.get("pain_level", 0))
    wound_description = str(payload.get("wound_description", ""))
    description = str(payload.get("description", ""))

    infected = _is_infected(wound_description)
    confidence = _parse_infection_confidence(wound_description)
    severity = _classify_severity(pain_level=pain_level, infected=infected, confidence=confidence)

    medical_attention_needed = "yes" if severity == "high" else "no"
    answer = _build_answer(description=description, severity=severity, infected=infected)

    return {
        "answer": answer,
        "medical_attention_needed": medical_attention_needed,
        "severity": severity,
    }