# meta-ads-cli: Code Standards & Conventions

## Python Version & Compatibility

- **Minimum**: Python 3.9
- **Tested**: Python 3.9–3.13
- **Style**: PEP 8 compliant, minimal strict linting
- **Type Hints**: Not enforced (project predates widespread adoption)

## Naming Conventions

### Modules & Files
- **Case**: snake_case (e.g., `meta_ads/api.py`, `test_config.py`)
- **Purpose**: Self-documenting filenames for tooling (Grep, Glob)
- **Clarity**: Descriptive names even if longer (e.g., `test_api.py` not `test.py`)

### Classes
- **Case**: PascalCase
- **Examples**: `MetaAdsAPI`, `MetaAPIError`, `ConfigError`
- **Convention**: Usually follow noun+purpose (e.g., `Error` suffix for exceptions)

### Functions & Methods
- **Case**: snake_case
- **Prefix**: `_` for private/internal (e.g., `_request()`, `_paginate()`, `_rollback_campaign()`)
- **Clarity**: Full words, no abbreviations (e.g., `create_ad_set` not `create_adset`)

### Variables
- **Case**: snake_case
- **Scope**: Module constants UPPER_SNAKE_CASE (e.g., `_MIME_TYPES`, `_RETRYABLE_CODES`)
- **Clarity**: Descriptive names (e.g., `image_hashes`, `campaign_cfg`, not `img_h`)

### Constants
- **Location**: Module-level, private prefix (e.g., `_VALID_OBJECTIVES`)
- **Scope**: Used by config.py validation functions
- **Convention**: UPPER_SNAKE_CASE, list of string enum values

## Code Organization

### Module Structure

**api.py** (255 LOC):
1. Imports
2. MIME type dict + constants (retry codes, HTTP methods)
3. Exception classes (MetaAPIError)
4. API wrapper class (MetaAdsAPI)
   - Constructor
   - Private `_request()` helper
   - Public API methods (alphabetical order)

**config.py** (173 LOC):
1. Imports
2. Validation constants (VALID_OBJECTIVES, etc.)
3. Exception class (ConfigError)
4. Public functions (load_config, validate_config)

**campaign.py** (138 LOC):
1. Imports
2. Private helper function (_rollback_campaign)
3. Public orchestration functions (create_full_campaign, print_campaign_status)

**cli.py** (203 LOC):
1. Imports
2. Helper function (get_api)
3. Click group decorator
4. Click commands (alphabetical order)

### Import Style

**Order** (PEP 8):
1. Standard library (os, sys, time, json, pathlib)
2. Third-party (click, requests, yaml, dotenv)
3. Local (meta_ads.api, meta_ads.config, etc.)

**Example**:
```python
import os
import sys
import click
import requests
from pathlib import Path
from meta_ads.api import MetaAdsAPI, MetaAPIError
```

## Error Handling & Validation

### Exception Classes

All custom exceptions inherit from Exception:
```python
class MetaAPIError(Exception):
    """Raised when the Meta API returns an error."""
    def __init__(self, status_code, message, error_code=None):
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)

class ConfigError(Exception):
    """Raised when campaign config is invalid."""
    pass
```

### Validation Pattern

Config validation **accumulates errors** rather than fail-fast:
```python
def validate_config(config):
    errors = []
    # ... check conditions, append to errors list ...
    if errors:
        raise ConfigError("\n".join(f"  - {e}" for e in errors))
    return config
```

**Benefits**:
- Users see ALL problems at once, not one by one
- Clear formatted error messages with field paths
- Exit early with full context

### API Error Handling

MetaAdsAPI._request() handles 3 categories:

**Success** (200):
```python
if resp.status_code == 200:
    return resp.json()
```

**Retryable** (429, 500, 502, 503):
```python
if resp.status_code in _RETRYABLE_CODES and attempt < 3:
    wait = 2 ** attempt  # Exponential backoff
    time.sleep(wait)
    continue
```

**Failure** (anything else):
```python
error_data = resp.json().get("error", {})
message = error_data.get("message", resp.text)
error_code = error_data.get("code")
raise MetaAPIError(resp.status_code, message, error_code)
```

### Path Traversal Security

Config loader checks image paths:
```python
resolved = image_path.resolve()
if not resolved.is_relative_to(config_dir):
    raise ConfigError(f"Image path '{original}' escapes config directory")
```

**Prevents**: Paths like `../../etc/passwd` from loading files outside YAML dir.

## Testing Approach

### Test Framework
- **Package**: pytest
- **Fixtures**: conftest.py (shared mocks, sample data)
- **Coverage**: >80% (unit tests for all modules)

### Test Organization

**test_api.py** (API client tests):
- Mock HTTP responses for create/get/delete
- Verify retry logic (3 attempts, backoff)
- Test dry-run mode (fake IDs, printed output)
- Error handling (invalid method, API errors)

**test_config.py** (Config validation):
- Valid YAML parsing
- Invalid schemas (missing fields, bad enums, bad types)
- Image path resolution (relative, absolute, traversal attempts)
- Duplicate ad names detection

**test_campaign.py** (Campaign orchestration):
- Full 4-step campaign creation
- Rollback on failure scenario
- Status display formatting

**conftest.py** (Fixtures):
```python
@pytest.fixture
def mock_api():
    """Return mocked MetaAdsAPI instance."""
    ...

@pytest.fixture
def sample_config():
    """Return valid campaign YAML config dict."""
    ...
```

### Mocking Pattern

Tests use pytest mocks (unittest.mock) to:
- Mock requests.post/get/delete responses
- Avoid real Meta API calls
- Inject test data (YAML, image paths)
- Verify call sequences

**Example**:
```python
with patch('meta_ads.api.requests.post') as mock_post:
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"id": "test_id"}
    # ... assert behavior
```

## Coding Patterns

### Configuration Defaults

Patterns for optional config keys with defaults:
```python
# In MetaAdsAPI.__init__
api_version = api_version or "v21.0"

# In MetaAdsAPI.create_ad_set
optimization_goal = optimization_goal or "LINK_CLICKS"

# In config.py validate_config
objective = campaign.get("objective", "OUTCOME_TRAFFIC")
```

### Retry Logic

Exponential backoff pattern:
```python
for attempt in range(1, 4):  # 1, 2, 3
    # ... make request ...
    if resp.status_code in _RETRYABLE_CODES and attempt < 3:
        wait = 2 ** attempt  # 2s, 4s
        click.echo(f"[RETRY {attempt}/3] retrying in {wait}s...")
        time.sleep(wait)
        continue
```

### Context Passing in Click

Click groups pass context to subcommands:
```python
@click.group()
@click.option("--verbose", "-v", is_flag=True)
@click.pass_context
def cli(ctx, verbose):
    ctx.obj = {"verbose": verbose}

@cli.command()
@click.pass_context
def create(ctx):
    verbose = ctx.obj["verbose"]
```

### Budget Formatting

Budget stored in cents, displayed in dollars:
```python
# Cents to dollars: divide by 100
budget_dollars = int(ad_set_cfg['daily_budget']) / 100
click.echo(f"Budget: ${budget_dollars:.2f}/day")

# Dollars to cents: multiply by 100 (user input is cents)
daily_budget=ad_set_cfg["daily_budget"]  # Already in cents
```

### List Building with Defaults

Targeting spec construction:
```python
targeting_spec = {
    "age_min": targeting.get("age_min", 18),
    "age_max": targeting.get("age_max", 65),
    "genders": targeting.get("genders", [0]),
}

if targeting.get("interests"):
    targeting_spec["flexible_spec"] = [
        {"interests": targeting["interests"]}
    ]
```

## Documentation Standards

### Module Docstrings
Every module has a one-line docstring:
```python
"""Meta Graph API client for ad management."""
"""Campaign config loading and validation."""
```

### Function Docstrings
Docstrings for public functions (not required for private):
```python
def create_full_campaign(api, config):
    """Create a complete campaign from config: campaign, ad set, creatives, and ads.

    If any step fails after the campaign is created, attempts to delete
    the campaign for cleanup before re-raising the error.

    Returns a dict with all created object IDs.
    """
```

### Inline Comments
- Minimal, only for non-obvious logic
- Explain *why*, not *what* (code explains what)
- Examples:
  ```python
  # MIME types by file extension for image uploads
  _MIME_TYPES = { ... }

  # HTTP status codes that warrant a retry
  _RETRYABLE_CODES = {429, 500, 502, 503}

  # Resolve image paths relative to YAML file, with path traversal check
  ```

## Output & CLI Standards

### Colored Output
Using click.style for visual hierarchy:
```python
click.style("SUCCESS", fg="green")         # Success messages
click.style("ERROR", fg="red")             # Errors
click.style("WARNING", fg="yellow")        # Warnings (confirmations, retries)
click.style("DEBUG", fg="cyan", dim=True)  # Debug output (verbose mode)
```

### Progress Indicators
Step counters for multi-step operations:
```python
click.echo(click.style("\n[1/4] Uploading images", fg="blue", bold=True))
click.echo(click.style("\n[2/4] Creating campaign", fg="blue", bold=True))
```

### Formatted Output
- Budget always formatted as dollars (e.g., `$10.00/day`)
- IDs in log output for copy-paste ease
- Status values in CAPS (PAUSED, ACTIVE, DELETED)
- Summaries use `=====` separators

### Confirmations
Destructive operations require user confirmation:
```python
if not yes:
    if not click.confirm(click.style("Continue?", fg="yellow")):
        click.echo("Aborted.")
        sys.exit(0)
```

## Security Best Practices

### Credentials
- Load from environment variables only (no hardcoding)
- Tokens not logged even in verbose mode
- Access token appended after building params dict

### File Handling
- Path resolution with `Path.resolve()` for canonicalization
- Path traversal check: `resolved.is_relative_to(config_dir)`
- Image file existence verified before API calls

### Input Validation
- YAML safe_load (not load) prevents code execution
- Enum validation (objectives, CTAs, statuses must match approved lists)
- Budget must be positive integer
- Image paths must exist on disk

### HTTP Safety
- Timeout: 30 seconds per request
- Allowed methods whitelisted: GET, POST, DELETE
- Retry only on safe status codes
- No follow redirects (explicit per-endpoint URLs)

## Version Management

**Version Source**: `meta_ads/__init__.py`
```python
__version__ = "0.1.0"
```

**Used by**: pyproject.toml (fetched dynamically) + CLI `--version` flag

**Updating**: Bump version in `__init__.py` + update pyproject.toml (optional, can be auto-fetched)

## Logging & Debugging

### Verbose Mode
Enabled via `--verbose` / `-v` global flag:
```bash
meta-ads --verbose create --config campaign.yaml
```

**Output**:
- API requests: `[DEBUG] POST /endpoint`
- Request params (sans token): `[DEBUG] Params: {...}`
- Response status: `[DEBUG] Response: HTTP 200`
- Timestamps not included (CLI is interactive)

### Debug Output Format
```python
click.echo(click.style(f"  [DEBUG] {method} {url}", fg="cyan", dim=True))
```

## Code Quality & Linting

### Scope
- **No strict linting** (project predates widespread adoption)
- Prioritize readability over style enforcement
- Focus on functionality, not formatting
- Syntax correctness required (code must compile)

### Standards Applied
- PEP 8 naming (snake_case functions, PascalCase classes)
- Docstrings for public APIs
- Clear variable names (not abbreviated)
- Proper exception handling (try/except, custom exceptions)

## Common Pitfalls & Solutions

| Issue | Solution |
|-------|----------|
| Missing env vars | `get_api()` validates and exits with clear message |
| Path traversal attack | `config.py` checks `is_relative_to()` after resolve |
| Rate limit (429) | Automatic retry with 2^n backoff |
| Partial campaign creation | Rollback deletes campaign on failure |
| Duplicate ad names | Config validation detects and reports |
| Wrong budget format | Docs say cents; validation checks integer >0 |
| Image not found | Config validation checks file exists |

## Deployment & Release

### Building
```bash
pip install hatchling
hatchling build  # Creates dist/meta-ads-cli-0.1.0.tar.gz
```

### Publishing to PyPI
```bash
python -m twine upload dist/*
```

### Versioning
- **Type**: Semantic versioning (major.minor.patch)
- **Current**: 0.1.0 (Beta)
- **Next**: 0.2.0 (minor features), 1.0.0 (stable)

---

**Last Updated**: 2026-03-11
**Maintained By**: Attainment Labs
**Repository**: https://github.com/attainmentlabs/meta-ads-cli
