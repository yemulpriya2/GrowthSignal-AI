import json
from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"


def read_prompt(filename: str) -> str:
    return (PROMPT_DIR / filename).read_text(encoding="utf-8")



def _records_as_json(records):
    return json.dumps(records, ensure_ascii=False, indent=2)



def analyze_feedback(service, records: list[dict], business_context: str = "") -> list[dict]:
    system = read_prompt("feedback_analysis.txt")
    user = f"""Business context: {business_context or "Not provided"}
Analyze each feedback item. Preserve item_id and feedback. Return JSON array only.
Feedback records:
{_records_as_json([{"item_id": i+1, **r} for i, r in enumerate(records)])}
"""
    data = service.complete_json(system, user)
    if isinstance(data, dict):
        data = data.get("results", data.get("analyses", []))
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array from feedback analysis.")
    return data





def detect_opportunities(service, analyses: list[dict], business_context: str = "") -> list[dict]:
    system = read_prompt("opportunity_detection.txt")
    user = f"""Business context: {business_context or "Not provided"}
Analyze these individual feedback analyses and find patterns. Return JSON array.
{_records_as_json(analyses)}
"""
    data = service.complete_json(system, user)
    if isinstance(data, dict):
        data = data.get("opportunities", data.get("results", []))
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array from opportunity detection.")
    return data





def generate_strategy(service, opportunities: list[dict], business_context: str = "") -> dict:
    system = read_prompt("strategy_generation.txt")
    user = f"""Business context: {business_context or "Not provided"}
Generate a realistic, evidence-grounded growth plan based on these opportunities:
{_records_as_json(opportunities)}
"""
    data = service.complete_json(system, user)
    if isinstance(data, list):
        return {"north_star": "Review opportunities and select a measurable focus.", "action_plan": [], "experiments": [], "risks_assumptions": "Model returned a list instead of object.", "raw": data}
    return data





def generate_automations(service, opportunities: list[dict], business_context: str = "") -> list[dict]:
    system = read_prompt("automation_generation.txt")
    user = f"""Business context: {business_context or "Not provided"}
Generate 3 to 5 practical automation ideas from these opportunities:
{_records_as_json(opportunities)}
"""
    data = service.complete_json(system, user)
    if isinstance(data, dict):
        data = data.get("automations", data.get("results", []))
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array from automation generation.")
    return data
