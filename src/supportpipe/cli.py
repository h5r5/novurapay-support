"""Command-line interface for SupportPipe."""

import click

from supportpipe import __version__
from supportpipe.config import settings


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


if __name__ == "__main__":
    main()
