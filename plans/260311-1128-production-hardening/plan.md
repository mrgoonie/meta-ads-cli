# Production Hardening Plan

**Status:** completed
**Created:** 2026-03-11
**Priority:** High
**Mode:** fast → cook --auto

## Overview

Fix critical and important issues identified in production-readiness code review. Focus on robustness, safety, and correctness — not new features.

## Phases

| # | Phase | Status | Priority |
|---|-------|--------|----------|
| 1 | API robustness (timeout, retry, MIME) | completed | critical |
| 2 | Config validation hardening | completed | critical |
| 3 | Campaign rollback on failure | completed | important |
| 4 | Unit tests (31 tests) | completed | important |

## Changes Summary

### Phase 1: `meta_ads/api.py`
- Request timeout (30s) on all API calls
- Retry logic (3 attempts, exponential backoff) for 429/500/502/503
- MIME type detection from file extension (png/jpg/jpeg/gif/webp)
- HTTP method whitelist (GET/POST/DELETE)

### Phase 2: `meta_ads/config.py`
- Budget validation: must be integer > 0
- Duplicate ad names detection
- Image path traversal protection via `is_relative_to()`
- Special ad categories validation

### Phase 3: `meta_ads/campaign.py`
- Rollback: delete campaign if ad set/creative/ad creation fails
- Skip rollback in dry-run mode

### Phase 4: `tests/`
- 31 tests covering config validation, API client, campaign orchestration
- pytest added as dev dependency

## Out of Scope
- CI/CD, logging framework, mypy, dependency lock, pagination, --verbose flag
