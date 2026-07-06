from pathlib import Path
from typing import Annotated

import typer
from openai import OpenAI
from rich.console import Console
from rich.progress import track

from judge_jitter import config, report, storage
from judge_jitter.data import build_prompt, load_examples
from judge_jitter.judge import judge_once

app = typer.Typer(help="Measure whether your LLM judge is consistent.", no_args_is_help=True)
console = Console()

DataOption = Annotated[
    Path, typer.Option(exists=True, dir_okay=False, help="JSONL dataset to judge.")
]
PromptOption = Annotated[Path, typer.Option(exists=True, dir_okay=False, help="Judge prompt file.")]
ResultsArgument = Annotated[
    Path, typer.Argument(exists=True, dir_okay=False, help="Results file from `run`.")
]


@app.command()
def run(
    data: DataOption,
    judge_prompt: PromptOption,
    model: Annotated[str, typer.Option(help="OpenAI model used as judge.")] = "gpt-4o-mini",
    runs: Annotated[int, typer.Option(min=2, help="Times to repeat each judgment.")] = 10,
    output: Annotated[Path, typer.Option(help="Where to write results.")] = Path("results.jsonl"),
    show_report: Annotated[
        bool, typer.Option("--report", help="Print the report after running.")
    ] = False,
):
    """Judge every example RUNS times and save the raw scores."""
    try:
        client = OpenAI(api_key=config.load_api_key())
        examples = load_examples(data)
    except (RuntimeError, ValueError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    template = judge_prompt.read_text()
    results = []
    for example in track(examples, description="Judging", console=console):
        prompt = build_prompt(template, example)
        judgments = [judge_once(client, model, prompt) for _ in range(runs)]
        results.append({"id": example.id, "judgments": [j.model_dump() for j in judgments]})

    storage.save_results(output, results)
    console.print(f"Saved {len(results)} results to [bold]{output}[/bold]")
    if show_report:
        report.render(results, console)


@app.command("report")
def report_command(results: ResultsArgument):
    """Print a consistency report for an existing results file."""
    report.render(storage.load_results(results), console)
