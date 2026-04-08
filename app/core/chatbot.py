import json
from app.llm.groq_client import groq_call
from app.core.rag import retrieve


def parse_json(response):
    try:
        return json.loads(response)
    except:
        return {
            "answer": "Error processing response",
            "medical_attention_needed": "yes",
            "severity": "high"
        }


def apply_rules(result, infection, pain, discomfort):

    # Rule 1: Severe pain → HIGH
    if pain >= 8:
        return {
            "answer": "Severe pain detected. Please consult a doctor immediately.",
            "medical_attention_needed": "yes",
            "severity": "high"
        }

    # Rule 2: Infection + moderate pain → HIGH
    if infection and pain >= 6:
        return {
            "answer": "Possible infection with significant pain. Consult a doctor.",
            "medical_attention_needed": "yes",
            "severity": "high"
        }

    # Rule 3: Medium case (FORCE it)
    if pain >= 4 or discomfort >= 5:
        result["severity"] = "medium"
        result["medical_attention_needed"] = "no"
        return result

    # Rule 4: Low case
    result["severity"] = "low"
    result["medical_attention_needed"] = "no"

    return result


def chatbot(payload):

    # Input extraction
    user_input = payload.get("message", "")
    dl_output = payload.get("dl_output", {})

    infection = dl_output.get("infection_detected", False)
    pain = payload.get("pain_level", 0)
    discomfort = payload.get("discomfort_level", 0)

    # Step 1: LLM Decision
    prompt = f"""
You are a medical assistant.

Input:
- infection_detected: {infection}
- pain_level: {pain} (0-10 scale)
- discomfort_level: {discomfort} (0-10 scale)
- user_message: {user_input}

Return ONLY JSON:
{{
  "answer": "...",
  "medical_attention_needed": "yes/no",
  "severity": "low/medium/high"
}}

Rules:
- Do NOT rely only on infection_detected
- High pain alone can indicate serious condition
- pain_level >= 7 → high severity
- pain_level 4-6 → medium
- pain_level <= 3 → low
- discomfort increases severity
"""

    raw = groq_call(prompt)

    # Step 2: Parse safely
    result = parse_json(raw)

    # Step 3: Apply rule overrides (VERY IMPORTANT)
    result = apply_rules(result, infection, pain, discomfort)

    # Step 4: RAG only for safe cases
    if result.get("severity") in ["low", "medium"]:
        query = f"{user_input} pain level {pain}"
        care = retrieve(query)
        result["answer"] += f"\n\nRecommended Care:\n{care}"

    else:
        result["answer"] = "This seems serious. Please consult a doctor immediately."

    return result