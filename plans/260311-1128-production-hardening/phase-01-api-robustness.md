# Phase 1: API Robustness

**Status:** pending
**Priority:** critical

## Changes

### 1.1 Request timeout (`api.py`)
- Add `timeout=30` to all requests calls in `_request()`

### 1.2 Retry logic (`api.py`)
- Add simple retry (3 attempts, exponential backoff) for 429/500/502/503
- No new dependency — use `time.sleep` + loop

### 1.3 MIME type detection (`api.py`)
- Detect MIME from file extension instead of hardcoding `image/png`
- Support: png, jpg/jpeg, gif, webp

### 1.4 HTTP method whitelist (`api.py`)
- Validate method is GET/POST/DELETE before `getattr(requests, ...)`

## Files
- `meta_ads/api.py` — all changes

## Success Criteria
- Requests timeout after 30s
- Transient errors retried 3 times
- JPG images uploaded with correct MIME type
- Invalid HTTP methods rejected
