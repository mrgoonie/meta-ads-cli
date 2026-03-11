# meta-ads-cli: System Architecture

## High-Level Overview

meta-ads-cli is a **CLI-first campaign deployment tool** that bridges YAML configuration and Meta's Marketing API.

```
User (Terminal)
    ↓
CLI Interface (click)
    ├─→ Config Loading & Validation (YAML)
    ├─→ Campaign Orchestration (4 steps)
    └─→ Meta Graph API Wrapper (requests)
            ↓
        Meta Marketing API (v21.0+)
```

**Core Design Principle**: Lightweight wrapper, minimal dependencies, explicit over implicit.

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  CLI Layer (click)                                          │
│  - Commands: create, status, pause, activate, delete        │
│  - Global: --verbose, --version                             │
│  - Error handling & user confirmations                       │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼──────────────┐  ┌──────▼───────────────┐
│ Config Management    │  │ Campaign Orchestration
│                      │  │                      │
│ - load_config()      │  │ - create_full_...()  │
│ - validate_config()  │  │ - print_status()     │
│                      │  │ - _rollback_...()    │
│ Functions:           │  │                      │
│ - YAML parsing       │  │ 4-step flow:         │
│ - Schema validation  │  │ 1. Upload images     │
│ - Path security      │  │ 2. Create campaign   │
│                      │  │ 3. Create ad set     │
│ Error type:          │  │ 4. Create ads        │
│ ConfigError          │  │                      │
└──────────────────────┘  │ Error type:          │
                          │ MetaAPIError         │
                          └──────────┬───────────┘
                                     │
                          ┌──────────▼────────────┐
                          │ API Wrapper (requests)│
                          │                       │
                          │ - MetaAdsAPI class    │
                          │ - _request() base     │
                          │ - Retry logic (3x)    │
                          │ - Dry-run support     │
                          │ - Verbose logging     │
                          │ - Pagination helper   │
                          │                       │
                          │ Methods:              │
                          │ - upload_image        │
                          │ - create_campaign     │
                          │ - create_ad_set       │
                          │ - create_ad_creative  │
                          │ - create_ad           │
                          │ - get_campaign        │
                          │ - get_ad_sets         │
                          │ - get_ads             │
                          │ - update_status       │
                          │ - delete_campaign     │
                          │                       │
                          │ Error type:           │
                          │ MetaAPIError          │
                          └──────────┬────────────┘
                                     │
                          ┌──────────▼────────────┐
                          │ Meta Graph API        │
                          │ (https://graph.      │
                          │  facebook.com/...)    │
                          │                       │
                          │ Endpoints:            │
                          │ - /adimages (upload)  │
                          │ - /campaigns (create) │
                          │ - /adsets (create)    │
                          │ - /adcreatives        │
                          │ - /ads (create)       │
                          └───────────────────────┘
```

## Request/Response Flow: Campaign Creation

```
┌─────────────────────────────────────────────────────────────────┐
│ User runs: meta-ads create --config campaign.yaml               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
    ┌────────────────────────────────────────┐
    │ 1. Load & Validate YAML                │
    │    - config.load_config(path)          │
    │    - config.validate_config(config)    │
    │    - Check image files exist           │
    │    - Validate enums, budgets, etc.     │
    │    → Returns: config dict or ConfigErr │
    └────────────────────┬───────────────────┘
                         │
                         ▼
    ┌────────────────────────────────────────┐
    │ 2. Show Preview & Confirm              │
    │    - Display campaign name, budget,    │
    │      num ads, status, mode (live/dry)  │
    │    - If live: prompt "Continue?"       │
    │    → User confirms or aborts           │
    └────────────────────┬───────────────────┘
                         │
                         ▼
    ┌────────────────────────────────────────┐
    │ 3. Create API Client                   │
    │    - get_api(dry_run, verbose)         │
    │    - Load META_ACCESS_TOKEN, etc.      │
    │    → Returns: MetaAdsAPI instance      │
    └────────────────────┬───────────────────┘
                         │
                         ▼ create_full_campaign()
    ┌────────────────────────────────────────┐
    │ [STEP 1/4] Upload Images               │
    │ for each ad in config["ads"]:          │
    │   - POST /act_ID/adimages              │
    │   - Multipart file upload              │
    │   → Returns: image hash                │
    │   - Collect into image_hashes dict     │
    └────────────────────┬───────────────────┘
                         │
                         ▼
    ┌────────────────────────────────────────┐
    │ [STEP 2/4] Create Campaign             │
    │   - POST /act_ID/campaigns             │
    │   - name, objective, status, categories│
    │   → Returns: campaign_id               │
    │   - Save campaign_id (for rollback)    │
    └────────────────────┬───────────────────┘
                         │
              ┌──────────┴──────────┐
              │ TRY BLOCK: if later │
              │ steps fail, roll    │
              │ back campaign       │
              │                     │
              ▼                     │
    ┌────────────────────────────┐ │
    │ [STEP 3/4] Create Ad Set   │ │
    │   - POST /act_ID/adsets    │ │
    │   - name, budget, targeting│ │
    │   → Returns: ad_set_id     │ │
    └────────────────────┬───────┘ │
                         │         │
              ┌──────────▼───────┐ │
              │ [STEP 4/4]       │ │
              │ Create Ads       │ │
              │ for each ad cfg: │ │
              │ - POST adcreative│ │
              │   (links image & │ │
              │    copy)         │ │
              │ - POST /ads      │ │
              │   (links creative│ │
              │    to ad set)    │ │
              │ → IDs collected  │ │
              └────────┬─────────┘ │
              EXCEPT   │           │
              MetaAPI  │           │
              Error:   │           │
              ▼        │           │
    ┌────────────────┐ │           │
    │ Print cleanup  │ │           │
    │ message        │ │           │
    │ If not dry-run │ │           │
    │   DELETE /     │ │           │
    │   campaign_id  │ │           │
    │ (rollback)     │ │           │
    └────────────────┘ │           │
           │           │           │
           └───────────┴───────────┘
                       │
                       ▼
    ┌────────────────────────────────────────┐
    │ 4. Display Summary                     │
    │    - Campaign ID, Ad Set ID            │
    │    - Num creatives, num ads            │
    │    - Status (PAUSED, ACTIVE)           │
    │    - Link to Ads Manager (if live)     │
    └────────────────────┬───────────────────┘
                         │
                         ▼
                    ✓ Success or ✗ Error
```

## Data Model: Campaign Structure

```
Campaign
├── ID (unique identifier)
├── Name (user-defined)
├── Objective (OUTCOME_TRAFFIC, etc.)
├── Status (PAUSED, ACTIVE, DELETED)
├── Special Ad Categories (CREDIT, EMPLOYMENT, etc.)
│
└── Ad Set (1 per campaign)
    ├── ID
    ├── Name
    ├── Daily Budget (cents)
    ├── Optimization Goal (LINK_CLICKS, etc.)
    ├── Billing Event (IMPRESSIONS, etc.)
    ├── Bid Strategy (LOWEST_COST_WITHOUT_CAP)
    ├── Status (PAUSED, ACTIVE)
    │
    └── Targeting
        ├── Age Min/Max (18–65)
        ├── Genders (0=all, 1=male, 2=female)
        ├── Countries (["US", "CA"])
        ├── Interests [{id, name}]
        ├── Platforms (["facebook", "instagram"])
        ├── Facebook Positions (["feed"])
        └── Instagram Positions (["stream", "story", "reels"])
    │
    └── Ads (N per ad set)
        ├── ID
        ├── Name (unique per campaign)
        ├── Status (PAUSED, ACTIVE)
        ├── Effective Status (tracking actual status)
        │
        └── Creative
            ├── ID
            ├── Name
            ├── Image Hash (from upload)
            ├── Primary Text (ad copy)
            ├── Headline
            ├── Description
            ├── Link (landing page URL)
            └── CTA (LEARN_MORE, SIGN_UP, etc.)
```

## API Integration Pattern

### Request Structure
All requests follow this pattern:
```
GET/POST/DELETE /graph.facebook.com/{api_version}/{endpoint}
  ?access_token={token}
  &field1=value1
  &field2=value2
```

### Retry & Timeout Logic
```
for attempt in [1, 2, 3]:
  - Make HTTP request (timeout=30s)
  - If 200: return response.json()
  - If 429/500/502/503 and attempt < 3:
      wait = 2^attempt seconds
      sleep(wait)
      retry
  - Else:
      parse error from response
      raise MetaAPIError(status, message, code)
```

### Pagination Pattern
```
result = GET /campaign_id/adsets
all_data = result["data"]

while result["paging"]["next"]:
  next_url = result["paging"]["next"]
  result = GET next_url
  all_data += result["data"]

return all_data
```

## Error Handling Strategy

### Config Validation Errors
- **Type**: ConfigError
- **When**: load_config() or validate_config() fails
- **Action**: Print formatted error message → exit(1)
- **Examples**: Missing fields, invalid enums, file not found, path traversal attempt

### API Errors
- **Type**: MetaAPIError
- **When**: Meta API returns non-200 status
- **Action**: Print error message + error code → exit(1)
- **Retry**: Automatic (3 attempts with backoff) for 429/5xx
- **Rollback**: If error during campaign creation steps 3–4, delete campaign

### Missing Credentials
- **Type**: SystemExit
- **When**: get_api() finds missing env vars
- **Action**: Print missing vars + help link → exit(1)

### Rollback Logic
```
try:
  create_campaign() → campaign_id
  try:
    create_ad_set() → ad_set_id
    create_ads() → ad_ids
  except MetaAPIError:
    delete_campaign(campaign_id)  # Cleanup
    raise
except MetaAPIError:
  print "Campaign creation failed"
  exit(1)
```

## Dry-Run Mode

When `--dry-run` flag is used:

```python
def _request(method, endpoint, **kwargs):
    if self.dry_run:
        self._dry_run_counter += 1
        fake_id = f"dry_run_{self._dry_run_counter}"
        print(f"[DRY RUN] {method} {endpoint}")
        print(f"Params: {json.dumps(params)}")
        return {"id": fake_id}
```

**Behavior**:
- No real API calls made
- Fake IDs returned (dry_run_1, dry_run_2, etc.)
- Request params printed (preview mode)
- Completes in <2 seconds
- Same CLI output formatting

**Use Case**: Preview campaign before deploying to live account.

## Verbose Logging

When `--verbose` / `-v` flag is used:

```
[DEBUG] POST /graph.facebook.com/v21.0/act_123/campaigns
[DEBUG] Params: {"name": "My Campaign", "objective": "OUTCOME_TRAFFIC"}
[DEBUG] Response: HTTP 200
```

**Content**:
- API endpoint + method
- Request parameters (access_token redacted)
- Response status code

**Use Case**: Debugging API issues, understanding request flow.

## Security Model

### Authentication
- Access token loaded from `META_ACCESS_TOKEN` env var
- Token appended to every API request
- No hardcoding, no logging of token (redacted in verbose)

### Authorization
- Assumes user has valid Meta Ads account
- API validates permissions (ad account access, page access)
- Tool doesn't check permissions (delegates to API)

### Input Validation
- **YAML**: Parsed with `yaml.safe_load()` (no code execution)
- **Enums**: Campaign objectives, CTAs, statuses matched against whitelist
- **Budget**: Validated as positive integer
- **Paths**: Image paths resolved + checked against config directory

### Path Security
```python
image_path = Path(ad["image"])
if not image_path.is_absolute():
    image_path = config_dir / image_path
resolved = image_path.resolve()
if not resolved.is_relative_to(config_dir):
    raise ConfigError("Path escape attempt")
```

Prevents: `../../etc/passwd`, symlink attacks, etc.

## Concurrency & Scalability

**Current Model**: Single-threaded, synchronous

**Limitations**:
- Image uploads sequential (not parallelized)
- API calls sequential (not batched)
- One campaign per CLI invocation

**Scalability**:
- Suitable for: Single campaigns, routine deployments
- Not suitable for: Bulk 1000s of campaigns per minute

**Future**: Phase 2 could add parallel image uploads, bulk YAML processing.

## Dependency Isolation

```
meta-ads-cli (this package)
├── click (CLI framework) — for command parsing, prompts, colored output
├── requests (HTTP client) — for API calls to Meta
├── pyyaml (YAML parser) — for campaign config files
└── python-dotenv (env loader) — for credential loading
```

**Design**: Minimal, focused dependencies. No heavy SDKs (avoids Meta SDK).

**Isolation**: Each module imports only what it needs (no circular imports).

## Testing Architecture

### Unit Tests
- Mock API responses (no real calls)
- Test config validation (happy path + error cases)
- Test campaign orchestration flow

### Integration Tests
- Not included (would require real Meta credentials)
- Manual testing via `--dry-run` recommended

### Test Fixtures (conftest.py)
```python
@pytest.fixture
def mock_api():
    """Return mocked MetaAdsAPI."""

@pytest.fixture
def sample_config():
    """Return valid campaign config dict."""

@pytest.fixture
def tmp_yaml(tmp_path):
    """Create temp YAML file for testing."""
```

## Deployment Architecture

### Installation
```bash
pip install meta-ads-cli  # From PyPI
# or
git clone ...
pip install -e .           # From source
```

### Entry Point
```toml
[project.scripts]
meta-ads = "meta_ads.cli:cli"
```

Creates `meta-ads` command available in $PATH after install.

### Runtime Requirements
- Python 3.9+
- .env file (or exported env vars) with credentials
- YAML config file with campaign definition
- Image files referenced in YAML (PNG, JPG, GIF, WebP)

### CI/CD Pipeline
GitHub Actions (`ci.yml`):
- Triggers on: push, pull_request
- Tests: Python 3.9–3.13 matrix
- Tasks: lint, test, build
- Publishes: PyPI on release tags

## Performance Characteristics

| Operation | Time | Bottleneck |
|-----------|------|------------|
| Config load + validate | <100ms | YAML parsing + schema check (local) |
| Image upload (1 img) | 500ms–2s | File I/O + network to Meta |
| Campaign creation (4 calls) | 3–7s | Network latency to Meta API |
| Ad set creation | 1–2s | API call latency |
| Ad creation (10 ads) | 5–10s | 10 sequential API calls |
| **Total (10 ads)** | **10–15s** | Image uploads + API calls |
| Status fetch | <1s | 3 paginated API calls |
| Dry-run | <2s | No network, instant mocks |

## Future Architecture Enhancements

### Phase 2
- Parallel image uploads (3–5 concurrent)
- Bulk campaign upload (multiple YAMLs)
- Template variables in YAML (${budget}, ${date})

### Phase 3
- Campaign cloning & modification
- Reporting dashboard
- Webhook notifications
- Analytics integration (GA4, Mixpanel)

---

**Last Updated**: 2026-03-11
**Architecture Style**: Service-oriented with CLI wrapper
**Complexity**: Low (lightweight, minimal coupling)
