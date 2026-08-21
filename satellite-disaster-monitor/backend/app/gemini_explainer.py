import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

def _get_gemini_api_key(api_key: Optional[str] = None) -> Optional[str]:
    if api_key:
        return api_key
    env_key = os.getenv("GEMINI_API_KEY")
    if env_key:
        return env_key

    # Manual search in .env / .env.example files if dotenv library is absent
    search_dirs = [
        os.getcwd(),
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        os.path.dirname(os.path.abspath(__file__))
    ]
    for directory in search_dirs:
        for env_file in [".env", ".env.example"]:
            filepath = os.path.join(directory, env_file)
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("GEMINI_API_KEY="):
                                return line.split("=", 1)[1].strip("\"'")
                except Exception:
                    pass
    return None


class GeminiExplainer:
    """Helper to query Gemini API (e.g. gemini-3.6-flash) for elaborative parameter explanations on terminal output."""

    def __init__(self, model_name: str = "gemini-3.6-flash", api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = _get_gemini_api_key(api_key)

    def explain_parameters(self, disaster_type: str, parameters: Dict[str, Any]) -> str:
        """Call Gemini REST API to produce a clear, detailed, formatted explanation of test parameters."""
        api_key = self.api_key or _get_gemini_api_key()
        if not api_key:
            return "⚠️ Gemini Explanation Skipped: GEMINI_API_KEY is not set in environment or .env file."

        prompt = (
            f"You are an expert satellite remote sensing analyst and emergency disaster coordinator.\n"
            f"Below are the calculated satellite analysis parameters for a detected {disaster_type.upper()} event:\n\n"
            f"Data Parameters:\n" + json.dumps(parameters, indent=2) + "\n\n"
            f"STRICT INSTRUCTIONS:\n"
            f"1. DO NOT evaluate whether the ML model works, whether it passed testing, or if code is ready to deploy.\n"
            f"2. DO NOT output complex system metrics tables, software version logs, or technical benchmarking code summaries.\n"
            f"3. State clearly what the parameters tell us about the PHYSICAL CONDITION OF THE GROUND/AREA (e.g., area percentage affected, severity of impact, confidence level).\n"
            f"4. Provide practical, actionable REAL-WORLD DISASTER RESPONSE SOLUTIONS & ADVISORIES for emergency teams based on these parameters.\n"
            f"5. Keep your response clean, direct, and well-structured for terminal reading."
        )

        models_to_try = [self.model_name, "gemini-2.5-flash"]
        # Ensure we try self.model_name first without duplicates
        models_to_try = list(dict.fromkeys(models_to_try))

        last_error = ""
        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            }

            try:
                req_data = json.dumps(payload).encode("utf-8")
                request = urllib.request.Request(
                    url,
                    data=req_data,
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(request, timeout=45) as response:
                    resp_json = json.loads(response.read().decode("utf-8"))
                    candidates = resp_json.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
            except urllib.error.HTTPError as e:
                err_msg = e.read().decode("utf-8")
                last_error = f"HTTP Error ({e.code}) on model '{model}': {err_msg}"
            except Exception as e:
                last_error = f"Call Failed on model '{model}': {str(e)}"

        return f"⚠️ Gemini API Call Failed: {last_error}"

def explain_test_parameters(disaster_type: str, parameters: Dict[str, Any], model_name: str = "gemini-3.6-flash") -> str:
    explainer = GeminiExplainer(model_name=model_name)
    return explainer.explain_parameters(disaster_type, parameters)
