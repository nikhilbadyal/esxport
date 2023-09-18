"""CLI."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import click
from click import Context, Parameter
from click_params import URL

from src import esxport
from src.__init__ import __version__
from src.click_opt.cli_options import CliOptions
from src.click_opt.click_custom import JSON, sort
from src.constant import META_FIELDS
from src.elastic import ElasticsearchClient

if TYPE_CHECKING:
    from pathlib import Path


def print_version(ctx: Context, _: Parameter, value: bool) -> None:  # noqa: FBT001
    """Print Version information."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"EsXport Cli {__version__}")
    ctx.exit()


@click.command(context_settings={"show_default": True})
@click.option(
    "-q",
    "--query",
    type=JSON,
    required=True,
    help="Query string in Query DSL syntax.",
)
@click.option(
    "-o",
    "--output-file",
    type=click.Path(),
    required=True,
    help="CSV file location.",
)
@click.option("-i", "--index-prefixes", required=True, multiple=True, help="Index name prefix(es).")
@click.option(
    "-u",
    "--url",
    type=URL,
    required=False,
    default="https://localhost:9200",
    help="Elasticsearch host URL.",
)
@click.option(
    "-U",
    "--user",
    required=False,
    default="elastic",
    help="Elasticsearch basic authentication user.",
)
@click.password_option(
    "-p",
    "--password",
    required=True,
    confirmation_prompt=False,
    help="Elasticsearch basic authentication password.",
)
@click.option(
    "-f",
    "--fields",
    default=["_all"],
    multiple=True,
    help="List of _source fields to present be in output.",
)
@click.option(
    "-S",
    "--sort",
    type=sort,
    multiple=True,
    help="List of fields to sort on in form <field>:<direction>",
)
@click.option(
    "-d",
    "--delimiter",
    default=",",
    help="Delimiter to use in CSV file.",
)
@click.option(
    "-m",
    "--max-results",
    default=10,
    type=int,
    help="Maximum number of results to return.",
)
@click.option(
    "-s",
    "--scroll-size",
    default=100,
    type=int,
    help="Scroll size for each batch of results.",
)
@click.option(
    "-e",
    "--meta-fields",
    type=click.Choice(META_FIELDS),
    default=[],
    multiple=True,
    help="Add meta-fields in output.",
)
@click.option(
    "--verify-certs",
    is_flag=True,
    help="Verify SSL certificates.",
)
@click.option(
    "--ca-certs",
    type=click.Path(exists=True),
    help="Location of CA bundle.",
)
@click.option(
    "--client-cert",
    type=click.Path(exists=True),
    help="Location of Client Auth cert.",
)
@click.option(
    "--client-key",
    type=click.Path(exists=True),
    help="Location of Client Cert Key.",
)
@click.option(
    "-v",
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    help="Show version and exit.",
)
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="Debug mode on.",
)
def cli(  # noqa: PLR0913
    query: str,
    output_file: Path,
    url: str,
    user: str,
    password: str,
    index_prefixes: str,
    fields: str,
    sort: str,
    delimiter: str,
    max_results: str,
    scroll_size: str,
    meta_fields: str,
    verify_certs: str,
    ca_certs: str,
    client_cert: str,
    client_key: str,
    debug: str,
) -> None:
    """Elastic Search to CSV Exporter."""
    kwargs: dict[str, Any] = {k: v for k, v in locals().items() if k != "self"}
    cli_options = CliOptions(kwargs)
    client = ElasticsearchClient(cli_options)
    es = esxport.EsXport(cli_options, client)
    es.export()


if __name__ == "__main__":
    cli()
