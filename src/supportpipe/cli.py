import json
import sys
from pathlib import Path

import click

from supportpipe import __version__
from supportpipe.config import settings
from supportpipe.evaluation.run_eval import execute_evaluation
from supportpipe.logging_store import ReviewQueueStore
from supportpipe.pipeline import run_batch
from supportpipe.schemas import Ticket

# Enforce UTF-8 console output on Windows
if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


@click.group()
@click.version_option(version=__version__, prog_name="supportpipe")
def main() -> None:
    """SupportPipe: Automated Support Pipeline for Iraqi Arabic tickets."""
    pass


@main.command()
def health() -> None:
    """Run environment and configuration health check."""
    click.echo(f"SupportPipe v{__version__} - Environment Health Check")
    click.echo(f"  Execution Mode: {settings.llm_mode}")
    click.echo(f"  Project Root:   {settings.project_root}")
    click.echo(f"  Taxonomy Dir:   {settings.taxonomy_dir}")
    click.echo(f"  Data Dir:       {settings.data_dir}")
    click.echo(f"  Results Dir:    {settings.results_dir}")
    click.echo("Health check status: OK")


@main.command()
@click.option(
    "--input",
    "input_path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to JSON or JSONL batch of tickets to process.",
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory to save review queue results and summary.",
)
def run(input_path: Path, output_dir: Path | None) -> None:
    """Process a batch of tickets through the pipeline and write to review queue."""
    click.echo(f"Ingesting tickets from: {input_path}")
    tickets: list[Ticket] = []

    # Detect JSON or JSONL
    if input_path.suffix == ".jsonl":
        with open(input_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    raw = json.loads(line)
                    # Check if line is LabeledTicket or raw Ticket
                    t_data = raw.get("ticket", raw)
                    tickets.append(Ticket.model_validate(t_data))
    else:
        with open(input_path, encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    t_data = item.get("ticket", item)
                    tickets.append(Ticket.model_validate(t_data))
            else:
                tickets.append(Ticket.model_validate(data))

    click.echo(f"Loaded {len(tickets)} tickets. Running batch pipeline...")
    results, summary = run_batch(tickets)

    store = ReviewQueueStore(storage_dir=output_dir)
    run_id = f"batch_{len(tickets)}_tickets"
    saved_folder = store.save_run(run_id=run_id, results=results, summary=summary)

    click.echo("Batch processing complete!")
    click.echo(f"  Total Tickets:    {summary.total_tickets}")
    click.echo(
        f"  Escalated Count:  {summary.escalated_count} ({summary.escalation_rate_pct:.1f}%)"
    )
    click.echo(f"  Avg Latency:      {summary.avg_latency_ms:.2f} ms")
    click.echo(f"  Results saved in: {saved_folder}")


@main.command()
@click.option(
    "--split",
    type=click.Choice(["dev", "test"], case_sensitive=False),
    default="test",
    help="Dataset split to evaluate on (frozen test set by default).",
)
@click.option(
    "--mode",
    type=click.Choice(["offline", "live"], case_sensitive=False),
    default="offline",
    help="Evaluation mode: 'offline' (reproducible deterministic benchmark, default) or 'live' (calls active API).",
)
def eval(split: str, mode: str) -> None:
    """Execute evaluation benchmark and produce metrics and confusion matrix."""
    click.echo(f"Starting evaluation on frozen split: {split.upper()} (Mode: {mode.upper()})...")
    settings.llm_mode = mode.lower()  # type: ignore[assignment]
    try:
        metrics = execute_evaluation(split=split.lower())
        click.echo("=" * 60)
        click.echo(f"EVALUATION RESULTS (Split: {split.upper()})")
        click.echo(f"  Run ID:                {metrics['run_id']}")
        click.echo(
            f"  Overall Accuracy:      {metrics['classification']['overall_accuracy'] * 100:.2f}%"
        )
        click.echo(
            f"  Priority Accuracy:     {metrics['classification']['priority_accuracy'] * 100:.2f}%"
        )
        click.echo(f"  Macro Avg F1:          {metrics['classification']['macro_avg_f1']:.4f}")
        click.echo(
            f"  Baseline (Majority):   {metrics['baseline']['majority_class_accuracy'] * 100:.2f}%"
        )
        click.echo(
            f"  Auto-Handled Accuracy: {metrics['escalation']['auto_handled_accuracy'] * 100:.2f}%"
        )
        click.echo(f"  Escalation Rate:       {metrics['escalation']['escalation_rate_pct']:.1f}%")
        click.echo(
            f"  Ref Exact Match:       {metrics['extraction']['ref_exact_match_rate'] * 100:.1f}%"
        )
        click.echo(
            f"  Amount Exact Match:    {metrics['extraction']['amt_exact_match_rate'] * 100:.1f}%"
        )
        click.echo(
            f"  Date Match Rate:       {metrics['extraction']['date_match_rate'] * 100:.1f}%"
        )
        click.echo(
            f"  Throughput:            {metrics['throughput']['tickets_per_second']:.1f} tickets/sec"
        )
        click.echo("=" * 60)
        click.echo(f"Detailed artifacts written to results/{metrics['run_id']}/")
    except Exception as e:
        click.echo(f"Evaluation failed: {e}", err=True)
        raise click.Abort() from e


@main.command()
@click.option(
    "--input",
    "input_path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to JSON or JSONL batch of tickets to analyze.",
)
def patterns(input_path: Path) -> None:
    """Generate weekly pattern report detecting rising issues and systemic incidents."""
    from supportpipe.patterns.report import analyze_ticket_patterns, format_markdown_pattern_report

    click.echo(f"Analyzing ticket patterns from: {input_path}")
    tickets: list[Ticket] = []
    if input_path.suffix == ".jsonl":
        with open(input_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    raw = json.loads(line)
                    t_data = raw.get("ticket", raw)
                    tickets.append(Ticket.model_validate(t_data))
    else:
        with open(input_path, encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    t_data = item.get("ticket", item)
                    tickets.append(Ticket.model_validate(t_data))
            else:
                tickets.append(Ticket.model_validate(data))

    results, _ = run_batch(tickets)
    pattern_data = analyze_ticket_patterns(results, tickets)
    report_md = format_markdown_pattern_report(pattern_data)
    click.echo(report_md)


@main.command(name="classify-one")
@click.option("--text", "-t", required=True, help="Raw ticket message text (in Iraqi Arabic).")
@click.option(
    "--channel",
    "-c",
    default="app",
    type=click.Choice(["app", "whatsapp", "sms"]),
    help="Ticket channel.",
)
def classify_one_cmd(text: str, channel: str) -> None:
    """Classify and process a single ticket in real-time through the pipeline."""
    from datetime import datetime

    from supportpipe.pipeline import process_ticket

    ticket = Ticket(
        ticket_id="CLI-TKT-LIVE",
        submitted_at=datetime.now().astimezone().isoformat(),
        synthetic_user_id="USER-CLI",
        channel=channel,  # type: ignore[arg-type]
        raw_text=text,
    )
    result = process_ticket(ticket)
    click.echo("\n" + "=" * 60)
    click.echo("SupportPipe Live Decision:")
    click.echo(
        f"  Category:        {result.category} (Confidence: {result.category_confidence:.2f})"
    )
    click.echo(
        f"  Priority:        {result.priority} (Confidence: {result.priority_confidence:.2f})"
    )
    click.echo(f"  Routed Team:     {result.team}")
    click.echo(f"  Escalated:       {result.escalated} ({result.escalation_reason or 'None'})")
    click.echo(f"  Extracted Ref:   {result.extracted_fields.transaction_ref or 'None'}")
    click.echo(f"  Extracted IQD:   {result.extracted_fields.amount_iqd or 'None'}")
    click.echo(f"  Latency:         {result.latency_ms:.1f} ms")
    click.echo(f"  Provider:        {result.provider_path}")
    click.echo("-" * 60)
    click.echo("Draft Response:")
    click.echo(result.draft_reply or "(No draft generated; ticket escalated)")
    click.echo("=" * 60 + "\n")


@main.command(name="spike")
@click.option("--count", "-n", default=15, help="Number of diverse tickets to evaluate.")
def spike_cmd(count: int) -> None:
    """Run the 15-ticket comparative spike between Jev 1.13 and baseline (Section 7.5)."""
    from supportpipe.evaluation.spike_jev import run_spike

    run_spike(count)


if __name__ == "__main__":
    main()
