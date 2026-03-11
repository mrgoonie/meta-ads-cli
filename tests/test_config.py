"""Tests for campaign config loading and validation."""

import os
import tempfile

import pytest
import yaml

from meta_ads.config import load_config, validate_config, ConfigError


class TestLoadConfig:
    """Tests for load_config()."""

    def test_load_valid_yaml(self, tmp_path):
        config_file = tmp_path / "campaign.yaml"
        img = tmp_path / "ad.png"
        img.write_bytes(b"fake png")
        config_file.write_text(yaml.dump({
            "campaign": {"name": "Test", "objective": "OUTCOME_TRAFFIC"},
            "ad_set": {"name": "Set", "daily_budget": 1000, "targeting": {"countries": ["US"]}},
            "ads": [{"name": "Ad", "image": "./ad.png", "primary_text": "Hi", "headline": "H", "link": "https://x.com"}],
        }))
        config = load_config(str(config_file))
        assert config["campaign"]["name"] == "Test"
        # Image path should be resolved to absolute
        assert os.path.isabs(config["ads"][0]["image"])

    def test_missing_file_raises(self):
        with pytest.raises(ConfigError, match="not found"):
            load_config("/nonexistent/campaign.yaml")

    def test_empty_file_raises(self, tmp_path):
        config_file = tmp_path / "empty.yaml"
        config_file.write_text("")
        with pytest.raises(ConfigError, match="empty"):
            load_config(str(config_file))

    def test_path_traversal_blocked(self, tmp_path):
        config_file = tmp_path / "campaign.yaml"
        config_file.write_text(yaml.dump({
            "campaign": {"name": "Test"},
            "ad_set": {"name": "Set", "daily_budget": 1000},
            "ads": [{"name": "Ad", "image": "../../etc/passwd", "primary_text": "x", "headline": "h", "link": "https://x.com"}],
        }))
        with pytest.raises(ConfigError, match="escapes config directory"):
            load_config(str(config_file))


class TestValidateConfig:
    """Tests for validate_config()."""

    def test_valid_config_passes(self, tmp_path):
        img = tmp_path / "ad.png"
        img.write_bytes(b"fake")
        config = {
            "campaign": {"name": "Test", "objective": "OUTCOME_TRAFFIC", "status": "PAUSED"},
            "ad_set": {"name": "Set", "daily_budget": 1000, "optimization_goal": "LINK_CLICKS",
                       "targeting": {"countries": ["US"]}},
            "ads": [{"name": "Ad", "image": str(img), "primary_text": "Copy", "headline": "H", "link": "https://x.com"}],
        }
        result = validate_config(config)
        assert result == config

    def test_missing_campaign_section(self):
        with pytest.raises(ConfigError, match="Missing 'campaign'"):
            validate_config({"ad_set": {"name": "x", "daily_budget": 1000, "targeting": {"countries": ["US"]}},
                             "ads": [{"name": "a", "image": "/x.png", "primary_text": "t", "headline": "h", "link": "https://x.com"}]})

    def test_invalid_objective(self):
        with pytest.raises(ConfigError, match="objective.*not valid"):
            validate_config({
                "campaign": {"name": "T", "objective": "INVALID"},
                "ad_set": {"name": "S", "daily_budget": 1000, "targeting": {"countries": ["US"]}},
                "ads": [{"name": "A", "image": "/x.png", "primary_text": "t", "headline": "h", "link": "https://x.com"}],
            })

    def test_budget_string_rejected(self):
        with pytest.raises(ConfigError, match="must be an integer"):
            validate_config({
                "campaign": {"name": "T"},
                "ad_set": {"name": "S", "daily_budget": "abc", "targeting": {"countries": ["US"]}},
                "ads": [{"name": "A", "image": "/x.png", "primary_text": "t", "headline": "h", "link": "https://x.com"}],
            })

    def test_budget_negative_rejected(self):
        with pytest.raises(ConfigError, match="must be > 0"):
            validate_config({
                "campaign": {"name": "T"},
                "ad_set": {"name": "S", "daily_budget": -500, "targeting": {"countries": ["US"]}},
                "ads": [{"name": "A", "image": "/x.png", "primary_text": "t", "headline": "h", "link": "https://x.com"}],
            })

    def test_budget_zero_rejected(self):
        with pytest.raises(ConfigError, match="must be > 0"):
            validate_config({
                "campaign": {"name": "T"},
                "ad_set": {"name": "S", "daily_budget": 0, "targeting": {"countries": ["US"]}},
                "ads": [{"name": "A", "image": "/x.png", "primary_text": "t", "headline": "h", "link": "https://x.com"}],
            })

    def test_duplicate_ad_names_rejected(self, tmp_path):
        img = tmp_path / "ad.png"
        img.write_bytes(b"fake")
        with pytest.raises(ConfigError, match="Duplicate ad name"):
            validate_config({
                "campaign": {"name": "T"},
                "ad_set": {"name": "S", "daily_budget": 1000, "targeting": {"countries": ["US"]}},
                "ads": [
                    {"name": "Same Name", "image": str(img), "primary_text": "t", "headline": "h", "link": "https://x.com"},
                    {"name": "Same Name", "image": str(img), "primary_text": "t2", "headline": "h2", "link": "https://x.com"},
                ],
            })

    def test_invalid_cta_rejected(self):
        with pytest.raises(ConfigError, match="cta.*not valid"):
            validate_config({
                "campaign": {"name": "T"},
                "ad_set": {"name": "S", "daily_budget": 1000, "targeting": {"countries": ["US"]}},
                "ads": [{"name": "A", "image": "/x.png", "primary_text": "t", "headline": "h", "link": "https://x.com", "cta": "BUY_NOW"}],
            })

    def test_invalid_special_ad_category(self):
        with pytest.raises(ConfigError, match="special_ad_categories.*not valid"):
            validate_config({
                "campaign": {"name": "T", "special_ad_categories": ["INVALID_CAT"]},
                "ad_set": {"name": "S", "daily_budget": 1000, "targeting": {"countries": ["US"]}},
                "ads": [{"name": "A", "image": "/x.png", "primary_text": "t", "headline": "h", "link": "https://x.com"}],
            })

    def test_missing_countries_rejected(self):
        with pytest.raises(ConfigError, match="countries is required"):
            validate_config({
                "campaign": {"name": "T"},
                "ad_set": {"name": "S", "daily_budget": 1000, "targeting": {}},
                "ads": [{"name": "A", "image": "/x.png", "primary_text": "t", "headline": "h", "link": "https://x.com"}],
            })
