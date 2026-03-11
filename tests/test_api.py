"""Tests for Meta API client."""

from pathlib import Path
from unittest.mock import patch, MagicMock
import json

import pytest

from meta_ads.api import MetaAdsAPI, MetaAPIError, _MIME_TYPES, _ALLOWED_METHODS


class TestDryRun:
    """Tests for dry-run mode."""

    def test_dry_run_returns_fake_ids(self, dry_run_api):
        result = dry_run_api._request("POST", "act_123/campaigns", params={"name": "Test"})
        assert result["id"].startswith("dry_run_")

    def test_dry_run_increments_counter(self, dry_run_api):
        dry_run_api._request("POST", "endpoint1")
        dry_run_api._request("POST", "endpoint2")
        assert dry_run_api._dry_run_counter == 2

    def test_dry_run_upload_returns_hash(self, dry_run_api, tmp_path):
        img = tmp_path / "test.png"
        img.write_bytes(b"fake png data")
        result = dry_run_api.upload_image(img)
        assert result == "dry_run_hash"


class TestMIMETypes:
    """Tests for MIME type detection."""

    def test_png_mime(self):
        assert _MIME_TYPES[".png"] == "image/png"

    def test_jpg_mime(self):
        assert _MIME_TYPES[".jpg"] == "image/jpeg"
        assert _MIME_TYPES[".jpeg"] == "image/jpeg"

    def test_webp_mime(self):
        assert _MIME_TYPES[".webp"] == "image/webp"

    def test_unknown_extension_defaults(self, dry_run_api, tmp_path):
        img = tmp_path / "test.bmp"
        img.write_bytes(b"fake bmp")
        # Dry run, so it won't actually upload, but the method should not error
        result = dry_run_api.upload_image(img)
        assert result == "dry_run_hash"


class TestMethodWhitelist:
    """Tests for HTTP method validation."""

    def test_allowed_methods(self):
        assert "GET" in _ALLOWED_METHODS
        assert "POST" in _ALLOWED_METHODS
        assert "DELETE" in _ALLOWED_METHODS

    @patch("meta_ads.api.requests")
    def test_invalid_method_raises(self, mock_requests):
        api = MetaAdsAPI("token", "123", "456", dry_run=False)
        with pytest.raises(ValueError, match="not allowed"):
            api._request("PATCH", "some/endpoint")


class TestRetryLogic:
    """Tests for retry on transient errors."""

    @patch("meta_ads.api.time.sleep")
    @patch("meta_ads.api.requests")
    def test_retries_on_500(self, mock_requests, mock_sleep):
        api = MetaAdsAPI("token", "123", "456", dry_run=False)
        # First call returns 500, second returns 200
        fail_resp = MagicMock(status_code=500, text="Internal Server Error")
        fail_resp.json.return_value = {"error": {"message": "Server Error"}}
        ok_resp = MagicMock(status_code=200)
        ok_resp.json.return_value = {"id": "12345"}
        mock_requests.post.side_effect = [fail_resp, ok_resp]

        result = api._request("POST", "act_123/campaigns", params={"name": "Test"})
        assert result["id"] == "12345"
        assert mock_requests.post.call_count == 2
        mock_sleep.assert_called_once()

    @patch("meta_ads.api.time.sleep")
    @patch("meta_ads.api.requests")
    def test_raises_after_max_retries(self, mock_requests, mock_sleep):
        api = MetaAdsAPI("token", "123", "456", dry_run=False)
        fail_resp = MagicMock(status_code=502, text="Bad Gateway")
        fail_resp.json.return_value = {"error": {"message": "Bad Gateway"}}
        mock_requests.post.side_effect = [fail_resp, fail_resp, fail_resp]

        with pytest.raises(MetaAPIError):
            api._request("POST", "act_123/campaigns")
        assert mock_requests.post.call_count == 3

    @patch("meta_ads.api.requests")
    def test_no_retry_on_400(self, mock_requests):
        api = MetaAdsAPI("token", "123", "456", dry_run=False)
        fail_resp = MagicMock(status_code=400, text="Bad Request")
        fail_resp.json.return_value = {"error": {"message": "Invalid params", "code": 100}}
        mock_requests.post.side_effect = [fail_resp]

        with pytest.raises(MetaAPIError) as exc_info:
            api._request("POST", "act_123/campaigns")
        assert exc_info.value.error_code == 100
        assert mock_requests.post.call_count == 1


class TestTimeout:
    """Tests for request timeout."""

    @patch("meta_ads.api.requests")
    def test_timeout_is_set(self, mock_requests):
        api = MetaAdsAPI("token", "123", "456", dry_run=False)
        ok_resp = MagicMock(status_code=200)
        ok_resp.json.return_value = {"id": "123"}
        mock_requests.get.return_value = ok_resp

        api._request("GET", "123", params={"fields": "name"})
        call_kwargs = mock_requests.get.call_args
        assert call_kwargs.kwargs.get("timeout") == 30 or call_kwargs[1].get("timeout") == 30
