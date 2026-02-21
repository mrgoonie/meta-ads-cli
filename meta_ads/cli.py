"""CLI entry point for meta-ads."""

import os
import sys

import click
from dotenv import load_dotenv

from meta_ads import __version__
from meta_ads.api import MetaAdsAPI, MetaAPIError
from meta_ads.campaign import create_full_campaign, print_campaign_status
from meta_ads.config import load_config, validate_config, ConfigError


def get_api(dry_run=False):
    """Create a MetaAdsAPI instance from environment variables."""
    access_token = os.getenv("META_ACCESS_TOKEN")
    ad_account_id = os.getenv("META_AD_ACCOUNT_ID")
    page_id = os.getenv("META_PAGE_ID")
    api_version = os.getenv("META_API_VERSION", "v21.0")

    missing = []
    if not access_token:
        missing.append("META_ACCESS_TOKEN")
    if not ad_account_id:
        missing.append("META_AD_ACCOUNT_ID")
    if not page_id:
        missing.append("META_PAGE_ID")

    if missing:
        click.echo(click.style("Missing required environment variables:", fg="red"))
        for var in missing:
            click.echo(click.style(f"  {var}", fg="red"))
        click.echo("\nSet them in .env or export them in your shell.")
        click.echo("See: https://github.com/attainmentlabs/meta-ads-cli#configuration")
        sys.exit(1)

    return MetaAdsAPI(
        access_token=access_token,
        ad_account_id=ad_account_id,
        page_id=page_id,
        api_version=api_version,
        dry_run=dry_run,
    )


@click.group()
@click.version_option(version=__version__, prog_name="meta-ads")
def cli():
    """Create and manage Meta ad campaigns from your terminal."""
    load_dotenv()


@cli.command()
@click.option("--config", "config_path", default="campaign.yaml", help="Path to campaign YAML config.")
@click.option("--dry-run", is_flag=True, help="Preview what would be created without making API calls.")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt.")
def create(config_path, dry_run, yes):
    """Create a full campaign from a YAML config file."""
    try:
        config = load_config(config_path)
        validate_config(config)
    except ConfigError as e:
        click.echo(click.style(f"Config error:\n{e}", fg="red"))
        sys.exit(1)

    campaign_name = config["campaign"]["name"]
    status = config["campaign"].get("status", "PAUSED")
    budget = int(config["ad_set"]["daily_budget"]) / 100
    num_ads = len(config["ads"])

    click.echo(click.style("=" * 50, fg="blue"))
    click.echo(click.style("meta-ads create", fg="blue", bold=True))
    click.echo(click.style("=" * 50, fg="blue"))
    click.echo(f"Campaign:  {campaign_name}")
    click.echo(f"Budget:    ${budget:.2f}/day")
    click.echo(f"Ads:       {num_ads}")
    click.echo(f"Status:    {status}")
    click.echo(f"Mode:      {'DRY RUN' if dry_run else 'LIVE'}")

    if not dry_run and not yes:
        click.echo()
        if not click.confirm(click.style("This will create real campaigns. Continue?", fg="yellow")):
            click.echo("Aborted.")
            sys.exit(0)

    api = get_api(dry_run=dry_run)

    try:
        result = create_full_campaign(api, config)
    except MetaAPIError as e:
        click.echo(click.style(f"\nAPI Error: {e}", fg="red"))
        if e.error_code:
            click.echo(click.style(f"Error code: {e.error_code}", fg="red"))
        sys.exit(1)

    # Summary
    click.echo(click.style("\n" + "=" * 50, fg="green"))
    click.echo(click.style("Done!", fg="green", bold=True))
    click.echo(click.style("=" * 50, fg="green"))
    click.echo(f"Campaign:  {result['campaign_id']} ({status})")
    click.echo(f"Ad Set:    {result['ad_set_id']} ({status})")
    click.echo(f"Creatives: {len(result['creatives'])}")
    click.echo(f"Ads:       {len(result['ads'])}")

    if not dry_run:
        click.echo(f"\nView in Ads Manager:")
        click.echo(f"  https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={api.ad_account_id}")


@cli.command()
@click.argument("campaign_id")
def status(campaign_id):
    """Show the status of a campaign and its ads."""
    api = get_api()
    try:
        print_campaign_status(api, campaign_id)
    except MetaAPIError as e:
        click.echo(click.style(f"API Error: {e}", fg="red"))
        sys.exit(1)


@cli.command()
@click.argument("campaign_id")
def pause(campaign_id):
    """Pause a campaign."""
    api = get_api()
    try:
        api.update_status(campaign_id, "PAUSED")
        click.echo(click.style(f"Campaign {campaign_id} paused.", fg="green"))
    except MetaAPIError as e:
        click.echo(click.style(f"API Error: {e}", fg="red"))
        sys.exit(1)


@cli.command()
@click.argument("campaign_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt.")
def activate(campaign_id, yes):
    """Activate a campaign. This will start spending your budget."""
    if not yes:
        if not click.confirm(click.style("This will start spending your ad budget. Continue?", fg="yellow")):
            click.echo("Aborted.")
            return

    api = get_api()
    try:
        api.update_status(campaign_id, "ACTIVE")
        click.echo(click.style(f"Campaign {campaign_id} activated.", fg="green"))
    except MetaAPIError as e:
        click.echo(click.style(f"API Error: {e}", fg="red"))
        sys.exit(1)


@cli.command()
@click.argument("campaign_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt.")
def delete(campaign_id, yes):
    """Delete a campaign. This cannot be undone."""
    if not yes:
        if not click.confirm(click.style("This will permanently delete the campaign. Continue?", fg="red")):
            click.echo("Aborted.")
            return

    api = get_api()
    try:
        api.delete_campaign(campaign_id)
        click.echo(click.style(f"Campaign {campaign_id} deleted.", fg="green"))
    except MetaAPIError as e:
        click.echo(click.style(f"API Error: {e}", fg="red"))
        sys.exit(1)


@cli.command()
@click.option("--config", "config_path", default="campaign.yaml", help="Path to campaign YAML config.")
def validate(config_path):
    """Validate a campaign YAML config without making API calls."""
    try:
        config = load_config(config_path)
        validate_config(config)
    except ConfigError as e:
        click.echo(click.style(f"Validation failed:\n{e}", fg="red"))
        sys.exit(1)

    campaign_name = config["campaign"]["name"]
    num_ads = len(config["ads"])
    budget = int(config["ad_set"]["daily_budget"]) / 100

    click.echo(click.style("Config is valid.", fg="green"))
    click.echo(f"  Campaign: {campaign_name}")
    click.echo(f"  Budget:   ${budget:.2f}/day")
    click.echo(f"  Ads:      {num_ads}")
