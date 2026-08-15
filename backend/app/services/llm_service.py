import asyncio
import json
import logging
from typing import Any, Dict, Optional

from google import genai
from google.genai import errors
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.result import ParsedResult
from app.services.prompts import PARSE_DISASTER_MODEL_PROMPT, PARSE_RETRY_PROMPT

logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    """Base exception for LLM service communication failures."""
    def __init__(self, message: str, original_error: Exception | None = None):
        self.message = message
        self.original_error = original_error
        super().__init__(message)


class LLMParsingError(LLMServiceError):
    """Raised when LLM output cannot be parsed into structured JSON or fails Pydantic schema validation after retries."""
    def __init__(
        self,
        message: str,
        raw_response: Optional[str] = None,
        original_error: Exception | None = None,
    ):
        self.raw_response = raw_response
        super().__init__(message, original_error=original_error)


_client: Optional[genai.Client] = None


def get_llm_client() -> genai.Client:
    """
    Returns a reusable singleton instance of the Gemini API client.
    Instantiates client only once across requests.
    """
    global _client
    if _client is None:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise LLMServiceError(
                "GEMINI_API_KEY is missing or not configured in environment/settings."
            )
        _client = genai.Client(api_key=api_key)
    return _client


async def call_llm(prompt: str, timeout: float = 30.0) -> str:
    """
    Sends a prompt to the Gemini API using the reusable async client and returns the raw text response.
    Applies timeout and wraps SDK exceptions in custom LLMServiceError.
    """
    client = get_llm_client()
    try:
        response = await asyncio.wait_for(
            client.aio.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
            ),
            timeout=timeout,
        )
        if not response or not response.text:
            raise LLMServiceError("Received empty response from Gemini API.")
        return response.text

    except asyncio.TimeoutError as e:
        logger.error(f"LLM API call timed out after {timeout} seconds: {e}")
        raise LLMServiceError(
            f"LLM call timed out after {timeout} seconds.",
            original_error=e,
        ) from e
    except errors.APIError as e:
        logger.error(f"Gemini API error occurred: {e}")
        raise LLMServiceError(
            f"Gemini API error: {getattr(e, 'message', str(e))}",
            original_error=e,
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error during LLM API execution: {e}")
        raise LLMServiceError(
            f"Unexpected LLM service error: {str(e)}",
            original_error=e,
        ) from e


def _clean_json_str(text: str) -> str:
    """Removes code block markdown wrapping if present in LLM response."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _parse_and_validate(llm_output_text: str, raw_model_output: Dict[str, Any]) -> ParsedResult:
    """
    Parses LLM output JSON string, handles geodata pass-through, and validates against ParsedResult schema.
    """
    cleaned_json = _clean_json_str(llm_output_text)
    data = json.loads(cleaned_json)

    if not isinstance(data, dict):
        raise ValueError(f"Parsed JSON is not an object/dict, received {type(data).__name__}")

    # Fallback/Pass-through: Real coordinates depend on the vision ML model output once delivered.
    # If raw_model_output contains latitude/longitude, preserve or pass them through as-is.
    if "latitude" in raw_model_output and data.get("latitude") is None:
        data["latitude"] = raw_model_output["latitude"]
    if "longitude" in raw_model_output and data.get("longitude") is None:
        data["longitude"] = raw_model_output["longitude"]

    # Attach original raw model output
    data["raw_model_output"] = raw_model_output

    return ParsedResult(**data)


async def parse_model_output(raw_model_output: Dict[str, Any]) -> ParsedResult:
    """
    Parses raw ML model prediction data into a clean, structured ParsedResult using the LLM.
    Retries once with a stricter follow-up prompt if JSON decoding or Pydantic validation fails.
    """
    raw_output_json = json.dumps(raw_model_output, indent=2)
    prompt = PARSE_DISASTER_MODEL_PROMPT.format(raw_model_output=raw_output_json)

    first_response = ""
    first_err: Optional[Exception] = None
    try:
        first_response = await call_llm(prompt)
        return _parse_and_validate(first_response, raw_model_output)
    except (json.JSONDecodeError, ValidationError, ValueError, TypeError) as err:
        first_err = err
        logger.warning(
            f"Failed to parse/validate LLM response on first attempt: {err}. "
            "Retrying with stricter follow-up prompt..."
        )

    # Retry attempt with stricter follow-up prompt
    retry_prompt = PARSE_RETRY_PROMPT.format(
        error_message=str(first_err),
        previous_output=first_response,
    )
    second_response = ""
    try:
        second_response = await call_llm(retry_prompt)
        return _parse_and_validate(second_response, raw_model_output)
    except (json.JSONDecodeError, ValidationError, ValueError, TypeError) as second_err:
        logger.error(f"LLM parsing/validation failed on retry attempt: {second_err}")
        raise LLMParsingError(
            f"Failed to parse LLM response into valid ParsedResult after retry: {second_err}",
            raw_response=second_response or first_response,
            original_error=second_err,
        ) from second_err
