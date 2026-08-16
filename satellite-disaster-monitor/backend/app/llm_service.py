import os
from typing import Any, Dict
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

    def explain_prediction(self, prediction_dict: Dict[str, Any]) -> str:
        """Generate human-readable disaster analysis explanation from model output."""
        disaster_type = prediction_dict.get("disaster_type", "unknown")
        confidence = prediction_dict.get("confidence", 0.0)
        severity = prediction_dict.get("severity", "unknown")
        image_type = prediction_dict.get("image_type_detected", "RGB")
        
        # TODO: replace stub below with real Groq client call if GROQ_API_KEY is configured
        # Example using groq SDK:
        #   from groq import Groq
        #   client = Groq(api_key=self.api_key)
        #   response = client.chat.completions.create(...)
        
        return (
            f"Satellite analysis ({image_type} imagery) identified potential {disaster_type} "
            f"with a confidence of {confidence:.1%} and a severity rating of '{severity}'. "
            f"Immediate situational assessment and monitoring recommended."
        )

# Module level instance helper
_llm_service = LLMService()

def explain_prediction(prediction_dict: Dict[str, Any]) -> str:
    return _llm_service.explain_prediction(prediction_dict)
