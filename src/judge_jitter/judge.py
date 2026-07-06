import json
import re

from openai import OpenAI
from pydantic import BaseModel

MIN_SCORE, MAX_SCORE = 1, 5


class Judgment(BaseModel):
    score: int | None = None
    reason: str | None = None
    error: str | None = None


def parse_judgment(text: str) -> Judgment:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return Judgment(error=f"no JSON found in response: {text[:200]!r}")
    try:
        payload = json.loads(match.group())
    except json.JSONDecodeError as exc:
        return Judgment(error=f"invalid JSON in response: {exc}")
    score = payload.get("score")
    if not isinstance(score, int) or not MIN_SCORE <= score <= MAX_SCORE:
        return Judgment(
            error=f"score must be an int from {MIN_SCORE} to {MAX_SCORE}, got {score!r}"
        )
    return Judgment(score=score, reason=payload.get("reason"))


def judge_once(client: OpenAI, model: str, prompt: str) -> Judgment:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:
        return Judgment(error=f"API call failed: {exc}")
    return parse_judgment(response.choices[0].message.content or "")
