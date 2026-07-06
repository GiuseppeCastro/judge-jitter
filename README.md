# judge-jitter

Your LLM judge might be changing its mind all the time. 

## The problem

LLM as a judge is everywhere, you ask GPT or Claude to score model outputs and
trust the number. But most people run each judgment **once**. Send the exact
same example to the same judge ten times and it will often give different
scores — which means your eval results are partly noise.

`judge-jitter` runs the same judgment `k` times per example and tells you
whether your judge is stable enough to trust.

## Install

```bash
git clone https://github.com/GiuseppeCastro/judge-jitter
cd judge-jitter
pip install -e .
```

## Configure

```bash
cp .env.example .env
# add your OPENAI_API_KEY
```

## Use

```bash
judge-jitter run \
  --data examples/examples.jsonl \
  --judge-prompt examples/judge_prompt.txt \
  --model gpt-4o-mini \
  --runs 10 \
  --output results.jsonl

judge-jitter report results.jsonl
```

Or in one shot:

```bash
judge-jitter run --data examples/examples.jsonl --judge-prompt examples/judge_prompt.txt --runs 10 --report
```

Dataset is JSONL, one example per line (`reference` is optional):

```json
{"id": "example_001", "input": "User question", "answer": "Model answer", "reference": "Expected answer"}
```

## Output

```text
                    Judge consistency
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┓
┃ Example     ┃ Scores              ┃ Distinct ┃ Variance ┃ Status   ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━┩
│ example_001 │ 5 5 5 5 5 5 5 5 5 5 │        1 │     0.00 │ stable   │
│ example_002 │ 2 4 2 3 4 2 3 4 2 3 │        3 │     0.69 │ unstable │
│ example_003 │ 1 1 1 1 1 1 1 1 1 1 │        1 │     0.00 │ stable   │
└─────────────┴─────────────────────┴──────────┴──────────┴──────────┘

Agreement score: 0.94  (1.00 = the judge always gives the same score)
Unstable examples: 1/3

Your judge changed its mind on 33.3% of examples.
This means your evaluation may not be reliable if you run it only once.
```

Scores are color-coded in the terminal (red → green), so the table doubles as
a per-run heatmap.

## Metrics

- **Distinct scores per item** — how many different scores the judge gave the
  same example.
- **Score variance per item** — population variance of those scores.
- **Overall instability** — % of examples where the judge gave more than one
  distinct score.
- **Agreement score** — `1 - normalized average variance` (1.0 means the judge
  always agrees with itself; 0.0 means maximum disagreement on a 1–5 scale).

Runs that fail (API error, unparseable judge output) are recorded and excluded
from the metrics instead of crashing the run.

## Why this matters

If your judge flips scores on 20% of examples, a one-shot eval comparing two
models can rank them in either order by pure luck. Measuring jitter first
tells you whether you need a better judge prompt, a different model, or
majority voting — before you trust a leaderboard built on top of it.

## Roadmap

- Anthropic provider
- CSV/HTML report
- Pairwise judging (A vs B)
- CI mode (fail the build if instability > threshold)
- Judge comparison (same dataset, multiple judges)

## License

MIT
