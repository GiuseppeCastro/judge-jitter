import json
from pathlib import Path


def save_results(path: Path, results: list[dict]) -> None:
    with path.open("w") as fh:
        for result in results:
            fh.write(json.dumps(result, ensure_ascii=False) + "\n")


def load_results(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
