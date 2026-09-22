"""Command-line interface for SupportPipe."""

import json
from pathlib import Path
import click
from supportpipe import __version__
from supportpipe.config import settings
from supportpipe.evaluation.run_eval import execute_evaluation
from supportpipe.logging_store import ReviewQueueStore
from supportpipe.pipeline import run_batch
from supportpipe.schemas import LabeledTicket, Ticket


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
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    raw = json.loads(line)
                    # Check if line is LabeledTicket or raw Ticket
                    t_data = raw.get("ticket", raw)
                    tickets.append(Ticket.model_validate(t_data))
    else:
        with open(input_path, "r", encoding="utf-8") as f:
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
    click.echo(f"  Escalated Count:  {summary.escalated_count} ({summary.escalation_rate_pct:.1f}%)")
    click.echo(f"  Avg Latency:      {summary.avg_latency_ms:.2f} ms")
    click.echo(f"  Results saved in: {saved_folder}")


@main.command()
@click.option(
    "--split",
    type=click.Choice(["dev", "test"], case_sensitive=False),
    default="test",
    help="Dataset split to evaluate on (frozen test set by default).",
)
def eval(split: str) -> None:
    """Execute evaluation benchmark and produce metrics and confusion matrix."""
    click.echo(f"Starting evaluation on frozen split: {split.upper()}...")
    try:
        metrics = execute_evaluation(split=split.lower())
        click.echo("=" * 60)
        click.echo(f"EVALUATION RESULTS (Split: {split.upper()})")
        click.echo(f"  Run ID:                {metrics['run_id']}")
        click.echo(f"  Overall Accuracy:      {metrics['classification']['overall_accuracy'] * 100:.2f}%")
        click.echo(f"  Priority Accuracy:     {metrics['classification']['priority_accuracy'] * 100:.2f}%")
        click.echo(f"  Macro Avg F1:          {metrics['classification']['macro_avg_f1']:.4f}")
        click.echo(f"  Baseline (Majority):   {metrics['baseline']['majority_class_accuracy'] * 100:.2f}%")
        click.echo(f"  Auto-Handled Accuracy: {metrics['escalation']['auto_handled_accuracy'] * 100:.2f}%")
        click.echo(f"  Escalation Rate:       {metrics['escalation']['escalation_rate_pct']:.1f}%")
        click.echo(f"  Ref Exact Match:       {metrics['extraction']['ref_exact_match_rate'] * 100:.1f}%")
        click.echo(f"  Amount Exact Match:    {metrics['extraction']['amt_exact_match_rate'] * 100:.1f}%")
        click.echo(f"  Date Match Rate:       {metrics['extraction']['date_match_rate'] * 100:.1f}%")
        click.echo(f"  Throughput:            {metrics['throughput']['tickets_per_second']:.1f} tickets/sec")
        click.echo("=" * 60)
        click.echo(f"Detailed artifacts written to results/{metrics['run_id']}/")
    except Exception as e:
        click.echo(f"Evaluation failed: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
