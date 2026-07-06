from rich.console import Console
from rich.table import Table
from rich.text import Text

from judge_jitter.metrics import ItemStats, item_stats, summarize

SCORE_COLORS = {1: "red", 2: "dark_orange", 3: "yellow", 4: "green3", 5: "green1"}
INSTABILITY_WARNING = 0.2


def _stats_from_result(result: dict) -> ItemStats:
    scores = [j["score"] for j in result["judgments"] if j.get("score") is not None]
    errors = sum(1 for j in result["judgments"] if j.get("score") is None)
    return item_stats(result["id"], scores, errors)


def _score_strip(item: ItemStats) -> Text:
    strip = Text()
    for score in item.scores:
        strip.append(f"{score} ", style=SCORE_COLORS[score])
    strip.append("· " * item.errors, style="dim")
    return strip


def render(results: list[dict], console: Console) -> None:
    if not results:
        console.print("[red]No results to report.[/red]")
        return

    items = [_stats_from_result(result) for result in results]
    summary = summarize(items)

    table = Table(title="Judge consistency", title_style="bold")
    table.add_column("Example")
    table.add_column("Scores")
    table.add_column("Distinct", justify="right")
    table.add_column("Variance", justify="right")
    table.add_column("Status")
    for item in items:
        status = (
            Text("stable", style="green") if item.stable else Text("unstable", style="bold red")
        )
        table.add_row(
            item.id, _score_strip(item), str(item.distinct), f"{item.variance:.2f}", status
        )
    console.print(table)

    errors = sum(item.errors for item in items)
    console.print(
        f"\nAgreement score: [bold]{summary.agreement:.2f}[/bold]  "
        f"(1.00 = the judge always gives the same score)"
    )
    console.print(f"Unstable examples: {summary.unstable}/{summary.total}")
    if errors:
        console.print(f"[yellow]{errors} run(s) failed and were left out of the metrics.[/yellow]")

    if summary.instability == 0:
        console.print(
            "\n[bold green]Your judge gave the same score every time. "
            "Safe to trust single runs.[/bold green]"
        )
        return
    style = "bold red" if summary.instability >= INSTABILITY_WARNING else "bold yellow"
    console.print(
        f"\n[{style}]Your judge changed its mind on {summary.instability:.1%} of examples.\n"
        f"This means your evaluation may not be reliable if you run it only once.[/{style}]"
    )
