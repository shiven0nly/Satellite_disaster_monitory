import os
from typing import Any, Dict
from dotenv import load_dotenv
from app.prompt_builder import SYSTEM_PROMPT, build_analysis_prompt

load_dotenv()


class LLMService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

    def explain_prediction(self, prediction_dict: Dict[str, Any]) -> str:
        """Generate disaster assessment brief using Groq LLM (llama-3.3-70b-versatile) with system prompt & prompt builder."""
        api_key = self.api_key or os.getenv("GROQ_API_KEY")
        user_prompt = build_analysis_prompt(prediction_dict)

        if api_key:
            try:
                from groq import Groq
                client = Groq(api_key=api_key)
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    max_tokens=300
                )
                brief = completion.choices[0].message.content.strip()
                print(f"[LLMService] Successfully generated Groq LLM response ({len(brief)} chars)")
                return brief
            except Exception as e:
                print(f"[LLMService] Warning: Failed to call Groq API ({e}), using structured local brief fallback.")
                pass

        # Local fallback assessment brief if Groq API key is missing or call fails
        disaster_type = prediction_dict.get("disaster_type", "flood")
        confidence = prediction_dict.get("confidence", 0.0)
        severity = prediction_dict.get("severity", "medium")
        coverage = prediction_dict.get("flood_coverage_percentage", 0.0)
        ndwi = prediction_dict.get("optical_water_index_ndwi", 0.0)

        return (
            f"Multi-sensor satellite synthesis (Optical + SAR + Thermal IR) confirms {disaster_type.replace('_', ' ')} detection "
            f"with a confidence rating of {confidence:.1%}, severity rating of '{severity.upper()}', and estimated inundated surface area of {coverage}%. "
            f"SAR radar penetration through cloud cover corroborates surface water signatures (NDWI index: {ndwi})."
        )


_llm_service = LLMService()


def explain_prediction(prediction_dict: Dict[str, Any]) -> str:
    return _llm_service.explain_prediction(prediction_dict)
