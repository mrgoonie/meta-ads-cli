# Phase 4: Unit Tests

**Status:** pending
**Priority:** important

## Changes

### 4.1 Test setup
- Add `pytest` to dev dependencies in `pyproject.toml`
- Create `tests/` directory

### 4.2 Config validation tests (`tests/test_config.py`)
- Valid config passes
- Missing sections rejected
- Invalid budget (string, negative, zero)
- Duplicate ad names
- Invalid objective/CTA/optimization_goal
- Path traversal blocked

### 4.3 API tests (`tests/test_api.py`)
- Dry run mode returns fake IDs
- HTTP method whitelist
- MIME type detection
- Timeout is set
- Error parsing from Meta API response

### 4.4 Campaign orchestration tests (`tests/test_campaign.py`)
- Rollback on failure
- Full campaign flow (dry run)

## Files
- `pyproject.toml` — add pytest
- `tests/__init__.py`
- `tests/test_config.py`
- `tests/test_api.py`
- `tests/test_campaign.py`
- `tests/conftest.py` — shared fixtures

## Success Criteria
- All tests pass
- Config validation has full coverage
