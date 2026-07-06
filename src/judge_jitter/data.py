from pathlib import Path

from pydantic import BaseModel, ValidationError


class Example(BaseModel):
    id: str
    input: str
    answer: str
    reference: str | None = None


def load_examples(path: Path) -> list[Example]:
    examples = []
    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            examples.append(Example.model_validate_json(line))
        except ValidationError as exc:
            raise ValueError(f"{path}:{lineno}: invalid example: {exc}") from exc
    if not examples:
        raise ValueError(f"{path}: no examples found")
    return examples


def build_prompt(judge_prompt: str, example: Example) -> str:
    parts = [
        judge_prompt.strip(),
        f"Input:\n{example.input}",
        f"Answer:\n{example.answer}",
    ]
    if example.reference:
        parts.append(f"Reference:\n{example.reference}")
    return "\n\n".join(parts)
