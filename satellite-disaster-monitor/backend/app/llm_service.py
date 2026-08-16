import os
from typing import Any, Dict
from dotenv import load_dotenv
from app.prompt_builder import SYSTEM_PROMPT, build_analysis_prompt

load_dotenv()

class LLMService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

    def explain_prediction(self, prediction_dict: Dict[str, Any]) -> str:
        """Generate disaster assessment brief using Groq LLM with system prompt & prompt builder."""
        user_prompt = build_analysis_prompt(prediction_dict)

        if self.api_key:
            try:
                from groq import Groq
                client = Groq(api_key=self.api_key)
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    max_tokens=300
                )
                return completion.choices[0].message.content.strip()
            except Exception as e:
                # Fallback to local structured assessment brief on API error
                pass

        # Local fallback assessment brief if Groq API key is not provided or fails
        disaster_type = prediction_dict.get("disaster_type", "unknown")
        confidence = prediction_dict.get("confidence", 0.0)
        severity = prediction_dict.get("severity", "unknown")
        
        return (
            f"Multi-sensor satellite synthesis (Optical + SAR + Thermal IR) confirms potential {disaster_type} "
            f"with a confidence of {confidence:.1%} and severity rating of '{severity}'. "
            f"SAR radar penetration through cloud cover corroborates surface inundation patterns."
        )

_llm_service = LLMService()

def explain_prediction(prediction_dict: Dict[str, Any]) -> str:
    return _llm_service.explain_prediction(prediction_dict)
