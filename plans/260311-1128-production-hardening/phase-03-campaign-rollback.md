# Phase 3: Campaign Rollback on Failure

**Status:** pending
**Priority:** important

## Changes

### 3.1 Rollback logic (`campaign.py`)
- Wrap campaign creation steps in try/except
- If any step fails after campaign created → delete campaign (cleanup)
- Print warning about partial cleanup

## Files
- `meta_ads/campaign.py`

## Success Criteria
- If ad creative fails, campaign is deleted
- User sees clear message about rollback
