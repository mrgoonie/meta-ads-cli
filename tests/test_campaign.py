"""Tests for campaign orchestration."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from meta_ads.api import MetaAdsAPI, MetaAPIError
from meta_ads.campaign import create_full_campaign


class TestCreateFullCampaign:
    """Tests for create_full_campaign()."""

    def test_dry_run_full_flow(self, dry_run_api, tmp_path):
        img = tmp_path / "ad.png"
        img.write_bytes(b"fake png")
        config = {
            "campaign": {"name": "Test", "objective": "OUTCOME_TRAFFIC", "status": "PAUSED"},
            "ad_set": {"name": "Set", "daily_budget": 1000, "targeting": {"countries": ["US"]}},
            "ads": [{"name": "Ad 1", "image": str(img), "primary_text": "Copy", "headline": "H",
                      "description": "D", "link": "https://x.com", "cta": "LEARN_MORE"}],
        }
        result = create_full_campaign(dry_run_api, config)
        assert result["campaign_id"] is not None
        assert result["ad_set_id"] is not None
        assert len(result["creatives"]) == 1
        assert len(result["ads"]) == 1


class TestRollback:
    """Tests for rollback on failure."""

    def test_rollback_on_ad_set_failure(self, tmp_path):
        img = tmp_path / "ad.png"
        img.write_bytes(b"fake png")
        config = {
            "campaign": {"name": "Test", "status": "PAUSED"},
            "ad_set": {"name": "Set", "daily_budget": 1000, "targeting": {"countries": ["US"]}},
            "ads": [{"name": "Ad", "image": str(img), "primary_text": "Copy", "headline": "H",
                      "description": "D", "link": "https://x.com"}],
        }

        api = MagicMock(spec=MetaAdsAPI)
        api.dry_run = False
        api.upload_image.return_value = "hash123"
        api.create_campaign.return_value = "campaign_123"
        api.create_ad_set.side_effect = MetaAPIError(400, "Invalid targeting")

        with pytest.raises(MetaAPIError):
            create_full_campaign(api, config)

        # Campaign should be rolled back (deleted)
        api.delete_campaign.assert_called_once_with("campaign_123")

    def test_rollback_on_creative_failure(self, tmp_path):
        img = tmp_path / "ad.png"
        img.write_bytes(b"fake png")
        config = {
            "campaign": {"name": "Test", "status": "PAUSED"},
            "ad_set": {"name": "Set", "daily_budget": 1000, "targeting": {"countries": ["US"]}},
            "ads": [{"name": "Ad", "image": str(img), "primary_text": "Copy", "headline": "H",
                      "description": "D", "link": "https://x.com"}],
        }

        api = MagicMock(spec=MetaAdsAPI)
        api.dry_run = False
        api.upload_image.return_value = "hash123"
        api.create_campaign.return_value = "campaign_123"
        api.create_ad_set.return_value = "adset_456"
        api.create_ad_creative.side_effect = MetaAPIError(400, "Bad creative")

        with pytest.raises(MetaAPIError):
            create_full_campaign(api, config)

        api.delete_campaign.assert_called_once_with("campaign_123")

    def test_no_rollback_in_dry_run(self, tmp_path):
        img = tmp_path / "ad.png"
        img.write_bytes(b"fake png")
        config = {
            "campaign": {"name": "Test", "status": "PAUSED"},
            "ad_set": {"name": "Set", "daily_budget": 1000, "targeting": {"countries": ["US"]}},
            "ads": [{"name": "Ad", "image": str(img), "primary_text": "Copy", "headline": "H",
                      "description": "D", "link": "https://x.com"}],
        }

        api = MagicMock(spec=MetaAdsAPI)
        api.dry_run = True
        api.upload_image.return_value = "hash"
        api.create_campaign.return_value = "dry_1"
        api.create_ad_set.side_effect = MetaAPIError(400, "fail")

        with pytest.raises(MetaAPIError):
            create_full_campaign(api, config)

        # Should NOT attempt rollback in dry-run mode
        api.delete_campaign.assert_not_called()
