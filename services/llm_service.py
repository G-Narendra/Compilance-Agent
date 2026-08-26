# wraps nvidia nims api.
# temp=0 to kill hallucinations.

import json
import re
import time
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from config import get_settings
from utils.logger import get_logger


# ── AI Safety: Prompt Injection Defense ──────────────────────────────────────
# Strips known injection patterns from user-supplied text before it reaches
# the LLM. This is a defense-in-depth measure — the system prompt also
# instructs the model to ignore injected instructions.
_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions?", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(prior|previous|above)\s+instructions?", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+", re.IGNORECASE),
    re.compile(r"act\s+as\s+(if\s+)?(you\s+are\s+)?", re.IGNORECASE),
    re.compile(r"pretend\s+(you\s+are|to\s+be)\s+", re.IGNORECASE),
    re.compile(r"system\s*prompt\s*:\s*", re.IGNORECASE),
    re.compile(r"<\|im_start\|>", re.IGNORECASE),
    re.compile(r"<\|im_end\|>", re.IGNORECASE),
]


def sanitize_user_input(text: str, max_length: int = 50000) -> str:
    """Strip prompt injection patterns and enforce length limits.

    Returns the sanitized text. Patterns are replaced with '[REDACTED]'
    so the LLM still receives the surrounding context.
    """
    if not text:
        return text
    # Enforce max length to prevent context overflow
    if len(text) > max_length:
        text = text[:max_length]
    # Strip known injection patterns
    for pattern in _INJECTION_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text

log = get_logger("llm_service")
settings = get_settings()

class LLMService:
    def __init__(self):
        self.model = settings.compliance_model
        if not settings.nvidia_api_key:
            log.warning("NVIDIA_API_KEY is not set. LLM calls will fail.")
        
        self.client = AsyncOpenAI(
            base_url=settings.nvidia_base_url,
            api_key=settings.nvidia_api_key,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def analyze_with_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> dict:
        # AI Safety: sanitize user input before sending to LLM
        user_prompt = sanitize_user_input(user_prompt)
        start_time = time.time()
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                top_p=0.1,
                max_tokens=max_tokens,
                stream=False,
            )

            content = response.choices[0].message.content or ""
            tokens_used = response.usage.total_tokens if response.usage else 0
            latency_ms = (time.time() - start_time) * 1000

            result = {
                "content": content,
                "tokens_used": tokens_used,
                "latency_ms": round(latency_ms, 1),
                "model": self.model,
                "parsed": None,
                "error_message": "",
                "raw_response": content
            }

            try:
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0].strip()
                else:
                    start = content.find("{")
                    end = content.rfind("}") + 1
                    json_str = content[start:end]

                result["parsed"] = json.loads(json_str)
            except Exception as e:
                log.warning("couldn't extract json from llm output", error=str(e))
                result["json_parse_error"] = str(e)
                result["error_message"] = f"JSON Parse Error: {str(e)}"

            return result

        except Exception as e:
            log.error("llm call failed", error=str(e))
            return {
                "parsed": None,
                "error_message": f"API Error: {str(e)}",
                "raw_response": "",
                "tokens_used": 0,
                "latency_ms": round((time.time() - start_time) * 1000, 1),
                "model": self.model
            }

llm_service = LLMService()

def build_rag_prompt(retrieved_context: list[dict], target_text: str) -> tuple[str, str]:
    context_text = ""
    for i, ctx in enumerate(retrieved_context):
        context_text += f"--- RULEBOOK EXCERPT {i+1} (Page {ctx['page_num']}) ---\n{ctx['text']}\n\n"

    system_prompt = """You are a strict Compliance Auditor. 
Your job is to determine if the TARGET DOCUMENT complies with the provided RULEBOOK EXCERPTS.

CRITICAL INSTRUCTIONS:
1. Hallucinations are UNACCEPTABLE. You must only base your decision on the provided Rulebook Excerpts.
2. If the rulebook excerpts do not mention a topic found in the target document, ignore it.
3. Every finding MUST include an exact quote from the rulebook excerpt and its page number.
4. DO NOT INVENT FINDINGS. If the target document perfectly complies with the rulebook excerpts, return an empty "findings" list and a score of 100.
5. LIMIT YOUR OUTPUT to a maximum of the 7 most critical findings. Do not exceed 7 findings to ensure the report remains concise and does not get cut off due to API token limits.
6. You must output ONLY valid JSON.

JSON FORMAT:
{
  "status": "pass" | "partial" | "fail",
  "score": <0-100>,
  "summary": "<Overall assessment>",
  "findings": [
    {
      "rule_id": "<Short name for the rule violated/matched>",
      "severity": "critical" | "high" | "medium" | "low" | "info",
      "title": "<Finding title>",
      "description": "<Why it matches or fails>",
      "recommendation": "<How to fix if failed>",
      "evidence": "<EXACT QUOTE FROM TARGET DOCUMENT>",
      "rulebook_citation": "<EXACT QUOTE FROM RULEBOOK EXCERPT (Page X)>"
    }
  ]
}"""

    user_prompt = f"""
{context_text}

--- TARGET DOCUMENT CLAUSE ---
{target_text}
--- END TARGET DOCUMENT ---

Analyze the target document against the rulebook excerpts and output the JSON report.
"""
    return system_prompt, user_prompt
