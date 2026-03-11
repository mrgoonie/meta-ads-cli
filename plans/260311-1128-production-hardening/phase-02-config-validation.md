# Phase 2: Config Validation Hardening

**Status:** pending
**Priority:** critical

## Changes

### 2.1 Budget validation (`config.py`)
- Must be integer
- Must be > 0
- Warn if < 100 (less than $1/day)

### 2.2 Duplicate ad names (`config.py`)
- Detect and reject duplicate `ads[].name`

### 2.3 Image path safety (`config.py`)
- Resolve path then check it stays within config directory (or is absolute)
- Reject path traversal attempts

### 2.4 Special ad categories validation (`config.py`)
- Validate values against known list: CREDIT, EMPLOYMENT, HOUSING, SOCIAL_ISSUES_ELECTIONS_POLITICS

### 2.5 Type safety for budget (`campaign.py`)
- Already validated in config, but ensure int() cast is safe

## Files
- `meta_ads/config.py` — validation logic
- `meta_ads/campaign.py` — minor safety

## Success Criteria
- `daily_budget: "abc"` → clear error
- `daily_budget: -500` → rejected
- Duplicate ad names → rejected
- `image: ../../etc/passwd` → rejected
