from statistics import pvariance

from pydantic import BaseModel

MAX_VARIANCE = 4.0  # population variance of 1-5 scores split between the extremes


class ItemStats(BaseModel):
    id: str
    scores: list[int]
    errors: int
    distinct: int
    variance: float
    stable: bool


class Summary(BaseModel):
    total: int
    unstable: int
    instability: float
    agreement: float


def item_stats(item_id: str, scores: list[int], errors: int = 0) -> ItemStats:
    distinct = len(set(scores))
    return ItemStats(
        id=item_id,
        scores=scores,
        errors=errors,
        distinct=distinct,
        variance=pvariance(scores) if len(scores) > 1 else 0.0,
        stable=distinct <= 1,
    )


def summarize(items: list[ItemStats]) -> Summary:
    unstable = sum(1 for item in items if not item.stable)
    avg_variance = sum(item.variance for item in items) / len(items)
    return Summary(
        total=len(items),
        unstable=unstable,
        instability=unstable / len(items),
        agreement=1 - avg_variance / MAX_VARIANCE,
    )
