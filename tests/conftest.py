"""Shared test fixtures for meta-ads-cli tests."""

import pytest


@pytest.fixture
def valid_config():
    """A minimal valid campaign config dict (image paths won't exist on disk)."""
    return {
        "campaign": {
            "name": "Test Campaign",
            "objective": "OUTCOME_TRAFFIC",
            "status": "PAUSED",
            "special_ad_categories": [],
        },
        "ad_set": {
            "name": "Test Ad Set",
            "daily_budget": 1000,
            "optimization_goal": "LINK_CLICKS",
            "targeting": {
                "countries": ["US"],
            },
        },
        "ads": [
            {
                "name": "Test Ad",
                "image": "/tmp/test-image.png",
                "primary_text": "Test copy",
                "headline": "Test Headline",
                "link": "https://example.com",
                "cta": "LEARN_MORE",
            },
        ],
    }


@pytest.fixture
def dry_run_api():
    """A MetaAdsAPI instance in dry-run mode."""
    from meta_ads.api import MetaAdsAPI
    return MetaAdsAPI(
        access_token="fake_token",
        ad_account_id="123456",
        page_id="789",
        dry_run=True,
    )
