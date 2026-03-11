# meta-ads-cli: Codebase Summary

## Overview

meta-ads-cli consists of ~1000 LOC across 5 Python modules + tests. Lightweight, minimal dependencies, designed for clarity over abstraction.

**Repository**: https://github.com/attainmentlabs/meta-ads-cli
**License**: MIT
**Python**: 3.9–3.13

## Module Structure

```
meta_ads/
├── __init__.py       (3 LOC)  → Version constant
├── api.py           (255 LOC) → Meta Graph API wrapper
├── campaign.py      (138 LOC) → Campaign orchestration
├── cli.py           (203 LOC) → Click CLI interface
└── config.py        (173 LOC) → YAML loading & validation
```

## Module Details

### api.py: Meta Graph API Wrapper

**Purpose**: Lightweight wrapper around Meta Marketing API using `requests`. No SDK dependency.

**Key Classes**:
- `MetaAPIError(Exception)`: Custom exception with status code, message, error code
- `MetaAdsAPI`: Main API client class

**MetaAdsAPI Constructor**:
```python
MetaAdsAPI(access_token, ad_account_id, page_id, api_version="v21.0", dry_run=False, verbose=False)
```

**Core Methods**:
| Method | HTTP | Purpose |
|--------|------|---------|
| `_request(method, endpoint, **kwargs)` | GET/POST/DELETE | Base request handler with retry/dry-run logic |
| `upload_image(image_path)` | POST | Upload PNG/JPG/GIF/WebP to ad account → image hash |
| `create_campaign(name, objective, status, special_ad_categories)` | POST | Create campaign object |
| `create_ad_set(name, campaign_id, daily_budget, targeting, ...)` | POST | Create ad set with targeting & budget |
| `create_ad_creative(name, image_hash, primary_text, ...)` | POST | Create creative linking image & copy |
| `create_ad(name, ad_set_id, creative_id, status)` | POST | Link creative to ad set |
| `get_campaign(campaign_id, fields)` | GET | Fetch campaign details |
| `get_ad_sets(campaign_id, fields)` | GET | Fetch all ad sets (paginated) |
| `get_ads(campaign_id, fields)` | GET | Fetch all ads (paginated) |
| `update_status(object_id, status)` | POST | Update campaign/set/ad status |
| `delete_campaign(campaign_id)` | POST | Delete campaign (sets status=DELETED) |

**Features**:
- **Retry Logic**: Automatic retry (3 attempts) for 429/500/502/503 with exponential backoff (2^n seconds)
- **Dry-Run Mode**: Mocks all requests, returns fake IDs, prints preview output
- **Verbose Logging**: Optional debug output (request/response details, sans token)
- **Pagination**: `_paginate()` helper fetches all pages from paginated endpoints
- **Error Handling**: Parses Meta API error format, raises MetaAPIError with code

**API Endpoint Base**: `https://graph.facebook.com/{api_version}` (default v21.0)

**Security**:
- MIME type detection for image uploads (`.png` → `image/png`, etc.)
- Allowed HTTP methods whitelisted: GET, POST, DELETE
- Access token always appended to params
- No sensitive data in verbose logging (token redacted)

### campaign.py: Campaign Orchestration

**Purpose**: 4-step campaign creation flow with rollback on failure.

**Key Functions**:

#### `create_full_campaign(api, config)`
Orchestrates complete campaign creation:
1. Upload all ad images → collect image hashes
2. Create campaign object
3. Create ad set (wrapped in try/except for rollback)
4. Create creatives + ads (wrapped in try/except)

**Returns**: Dict with `campaign_id`, `ad_set_id`, `creatives[]`, `ads[]`

**Rollback Logic**:
- If any step after campaign creation fails, calls `_rollback_campaign()`
- Rollback deletes campaign via `api.delete_campaign()` to clean up
- If rollback also fails, warns user to delete manually

**Error Handling**:
- Catches `MetaAPIError` → prints cleanup message → re-raises
- Budget conversion: cents → dollars for display (divide by 100)
- Status defaults: PAUSED (safe default, user activates manually)

#### `print_campaign_status(api, campaign_id)`
Displays campaign + ad sets + ads in formatted output.

**Fields**:
- Campaign: name, ID, status, objective
- Ad Sets: name, status, daily budget (cents → dollars)
- Ads: name, status, effective_status

### cli.py: Click CLI Interface

**Purpose**: Command-line interface for all operations.

**Global Command Group**:
```python
@click.group()
@click.version_option(version=__version__)
@click.option("--verbose", "-v", is_flag=True)
def cli(ctx, verbose):
```

**Helper Function**:
`get_api(dry_run=False, verbose=False)`: Loads env vars, validates, creates MetaAdsAPI instance.

**Commands** (6 total):

| Command | Args | Options | Purpose |
|---------|------|---------|---------|
| `create` | — | `--config`, `--dry-run`, `--yes` | Deploy campaign from YAML |
| `status` | `campaign_id` | — | Show campaign status |
| `pause` | `campaign_id` | — | Pause campaign |
| `activate` | `campaign_id` | `--yes` | Activate campaign (confirms budget spend) |
| `delete` | `campaign_id` | `--yes` | Delete campaign (requires confirmation) |
| `validate` | — | `--config` | Validate YAML without API calls |

**Features**:
- Colored output (click.style with fg/bold)
- Progress indicators (step counters like [1/4])
- Confirmation prompts for destructive ops
- Summary output with all created IDs
- Links to Ads Manager for live campaigns

**Error Handling**:
- Catches ConfigError → exits with formatted message
- Catches MetaAPIError → exits with code if available
- Missing env vars → clear guidance with links

### config.py: Configuration Management

**Purpose**: YAML loading, validation, security checks.

**Constants** (validation lists):
- `VALID_OBJECTIVES`: 6 options (OUTCOME_TRAFFIC, OUTCOME_AWARENESS, etc.)
- `VALID_OPTIMIZATION_GOALS`: 7 options (LINK_CLICKS, IMPRESSIONS, etc.)
- `VALID_CTAS`: 11 options (LEARN_MORE, SIGN_UP, etc.)
- `VALID_STATUSES`: 2 options (PAUSED, ACTIVE)
- `VALID_SPECIAL_AD_CATEGORIES`: 4 options (CREDIT, EMPLOYMENT, etc.)

**Custom Exception**:
- `ConfigError`: Raised on validation failures

**Functions**:

#### `load_config(path)`
1. Load YAML file
2. Resolve image paths relative to YAML directory
3. Security check: prevent path traversal (image path must stay under config dir)
4. Return parsed config dict

#### `validate_config(config)`
Validates against YAML schema:
- Campaign section: name (required), objective, status, special categories
- Ad set section: name, daily budget >0, optimization goal, targeting (countries required)
- Ads section: name (unique), image (exists), primary_text, headline, link, cta

**Behavior**:
- Accumulates all errors before raising (not fail-fast)
- Checks image files exist on disk
- Validates budget is positive integer
- Detects duplicate ad names
- Provides clear error messages with field paths

## Data Models & Flow

### Campaign Config Schema
```yaml
campaign:
  name: string          # Required: display name
  objective: string     # Default: OUTCOME_TRAFFIC
  status: string        # Default: PAUSED
  special_ad_categories: []  # Default: []

ad_set:
  name: string          # Required
  daily_budget: int     # Required, in cents, >0
  optimization_goal: string  # Default: LINK_CLICKS
  targeting:
    age_min: int        # Default: 18
    age_max: int        # Default: 65
    genders: [int]      # Default: [0] (all)
    countries: [string] # Required, e.g., ["US"]
    interests: [{id, name}]  # Optional
    platforms: [string] # Default: ["facebook", "instagram"]
    facebook_positions: [string]  # Optional
    instagram_positions: [string] # Optional

ads: [{
  name: string          # Required, unique
  image: path           # Required, resolved relative to YAML
  primary_text: string  # Required (ad copy)
  headline: string      # Required
  description: string   # Optional
  cta: string           # Default: LEARN_MORE
  link: url             # Required (landing page)
}]
```

### API Request/Response Flow

**Campaign Creation Request → Response**:
```
POST /act_ACCOUNT_ID/campaigns → {id: CAMPAIGN_ID}
POST /act_ACCOUNT_ID/adsets → {id: ADSET_ID}
POST /act_ACCOUNT_ID/adcreatives → {id: CREATIVE_ID}
POST /act_ACCOUNT_ID/ads → {id: AD_ID}
```

**Pagination**:
```
GET /CAMPAIGN_ID/adsets?fields=... → {data: [...], paging: {next: url}}
GET /next_url → {data: [...], paging: {...}}
```

## Dependency Graph

```
cli.py
 ├── config.py (load_config, validate_config)
 ├── campaign.py (create_full_campaign, print_campaign_status)
 │   └── api.py (MetaAdsAPI, MetaAPIError)
 └── api.py (get_api helper)

External:
 ├── click (CLI framework)
 ├── requests (HTTP)
 ├── pyyaml (YAML parsing)
 └── python-dotenv (env loading)
```

## Test Structure

**test_api.py**: Tests for MetaAdsAPI
- Mock responses for create/get/delete operations
- Error handling (invalid method, API errors)
- Retry logic verification
- Dry-run mode behavior

**test_campaign.py**: Tests for campaign orchestration
- Full campaign creation (mocked API)
- Rollback on failure scenario
- Status display formatting

**test_config.py**: Tests for config validation
- Valid/invalid YAML parsing
- Image path resolution & traversal protection
- Schema validation (required fields, enum values, duplicates)

**conftest.py**: pytest fixtures
- Mock MetaAdsAPI instance
- Sample YAML configs
- Temporary file handling

## Code Standards & Patterns

**Error Handling**:
- Custom exceptions with meaningful context (MetaAPIError, ConfigError)
- Accumulate validation errors before raising (not fail-fast)
- Clear error messages with field paths

**Retry Logic**:
- 3 attempts for transient errors (429, 5xx)
- Exponential backoff: 2^attempt seconds
- Logs retry attempts with status codes

**Security**:
- Credentials via environment variables
- Path traversal protection (resolve + is_relative_to check)
- Token redaction in verbose logging

**CLI/UX**:
- Colored output (green=success, red=error, yellow=warning, cyan=debug)
- Progress indicators ([1/4] [2/4], etc.)
- Confirmation prompts for destructive ops
- Budget formatted as dollars (cents ÷ 100)

**YAML Defaults**:
- Objective: OUTCOME_TRAFFIC
- Status: PAUSED
- Optimization goal: LINK_CLICKS
- Age: 18–65
- Gender: 0 (all)
- Platforms: [facebook, instagram]

## Entry Points

**Package entry point** (pyproject.toml):
```
[project.scripts]
meta-ads = "meta_ads.cli:cli"
```

**Installation**:
```bash
pip install meta-ads-cli    # From PyPI
pip install -e .            # From source (dev)
```

**CLI Invocation**:
```bash
meta-ads --help             # Show commands
meta-ads create --config campaign.yaml
meta-ads status CAMPAIGN_ID
meta-ads --version          # Show version (0.1.0)
```

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Config validation | <100ms | Local YAML parsing + schema check |
| Image upload | 500ms–2s | Depends on file size |
| Campaign creation | <10s total | 4 API calls + image uploads |
| Status fetch | <1s | 3 paginated API calls |
| Dry-run | <2s | No API calls, instant mock responses |

## Build & Deployment

**Build System**: hatchling (pyproject.toml)

**Package Config**:
- Name: meta-ads-cli
- Version: 0.1.0 (from `__init__.py`)
- Entry point: `meta-ads` CLI command
- Dependencies: click, requests, pyyaml, python-dotenv

**Testing**: pytest (dev dependency)

**CI/CD**: GitHub Actions (ci.yml)
- Python 3.9–3.13 matrix
- Runs linting + tests on push/PR
- Publishes to PyPI on release

---

**Last Updated**: 2026-03-11
**Codebase Size**: ~1000 LOC (Python) + 400 LOC (tests) + 7KB docs
