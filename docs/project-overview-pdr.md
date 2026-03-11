# meta-ads-cli: Project Overview & Product Development Requirements

## Executive Summary

**meta-ads-cli** is a lightweight Python CLI tool that enables developers to create and manage Meta (Facebook/Instagram) ad campaigns programmatically via YAML configuration files. Built by Attainment Labs, it eliminates the friction of Meta Ads Manager UI by offering one-command campaign deployment.

- **Version**: 0.1.0
- **License**: MIT
- **Python**: 3.9+ required
- **Status**: Beta (production-ready, actively maintained)

## Problem Statement

Meta Ads Manager UI is slow and cumbersome. Creating a single campaign requires:
- Navigating 15+ screens
- Manually configuring targeting, budgets, creatives, and copy
- Repetitive copy-paste operations
- Hours of setup time for multi-ad campaigns

**Target Users**: Marketing engineers, performance marketers, agencies, developers who need programmatic campaign management.

## Solution Overview

A command-line interface that:
1. Accepts campaign definitions in YAML (human-readable, version-controllable)
2. Validates configuration before API calls
3. Deploys complete campaigns (campaign → ad set → creatives → ads) in seconds
4. Provides campaign management operations (status, pause, activate, delete)
5. Includes dry-run mode for safe previewing

## Key Features

| Feature | Status | Notes |
|---------|--------|-------|
| Campaign creation from YAML | ✓ Complete | 4-step orchestration with rollback |
| Campaign status inspection | ✓ Complete | Includes ad sets and ads |
| Pause/activate campaigns | ✓ Complete | With confirmation prompts |
| Delete campaigns | ✓ Complete | Permanent, requires confirmation |
| Config validation | ✓ Complete | Pre-deployment check |
| Dry-run mode | ✓ Complete | Preview without API calls |
| Image upload | ✓ Complete | Automatic, handles PNG/JPG/GIF/WebP |
| Pagination support | ✓ Complete | For ad set and ad listing |
| Verbose logging | ✓ Complete | Debug API requests/responses |
| Retry logic | ✓ Complete | Handles rate limits (429, 5xx) |

## Technical Architecture

### Core Modules
- **api.py**: Meta Graph API wrapper with retry & dry-run support
- **campaign.py**: Campaign orchestration & rollback logic
- **cli.py**: Click-based CLI with 6 commands
- **config.py**: YAML validation with path security checks

### Data Flow
1. User provides YAML config + environment credentials
2. Config validation (schema, file existence, objective/CTA validity)
3. Image upload (PNG/JPG → image hashes)
4. Campaign creation (campaign object)
5. Ad set creation (budget & targeting)
6. Creatives & ads linking images to ad set
7. All created as PAUSED by default (user reviews before activation)

### API Integration
- Uses Meta Graph API (no SDK dependency)
- Supports v21.0+ (configurable via `META_API_VERSION`)
- Retry logic: 3 attempts for 429/500/502/503 errors
- Timeout: 30 seconds per request
- Request/response logging in verbose mode

## Product Requirements

### Functional Requirements

#### F1: Campaign Creation
- **Input**: YAML config file + env vars (access token, account ID, page ID)
- **Output**: Campaign ID, ad set ID, creative IDs, ad IDs
- **Process**: Upload images → create campaign → create ad set → create ads
- **Error Handling**: Rollback (delete campaign) if any step fails after campaign creation
- **Modes**: Live (confirms before deploying) and dry-run (preview only)
- **Default Status**: All objects created as PAUSED for safety review

#### F2: Campaign Management
- **Status**: Fetch campaign details + ad sets + ads with pagination
- **Pause/Activate**: Update campaign status with confirmation
- **Delete**: Permanently delete campaigns (requires confirmation)
- **Query Fields**: Name, status, objective, budget, effective status

#### F3: Configuration Management
- **Format**: YAML (human-readable, version-controllable)
- **Validation**: Campaign name/objective, ad set name/budget, ad name/image/copy
- **Path Resolution**: Image paths resolved relative to YAML directory
- **Security**: Path traversal protection (prevent escape from config dir)
- **Defaults**: Objective (OUTCOME_TRAFFIC), status (PAUSED), optimization goal (LINK_CLICKS)

#### F4: Image Management
- **Upload**: PNG, JPG, GIF, WebP to ad account
- **Storage**: Meta's ad image library (returned as hash)
- **Reference**: Ads link to creatives which link to image hashes
- **Error Handling**: MIME type detection, file not found checks

#### F5: Targeting Support
- **Demographics**: Age min/max, genders (0=all, 1=male, 2=female)
- **Geography**: Country codes (e.g., US, CA, UK)
- **Interests**: Meta interest IDs (searchable via API)
- **Platforms**: Facebook and/or Instagram
- **Placements**: Facebook (feed), Instagram (stream, story, reels)

#### F6: Error Handling & Resilience
- **Config Errors**: Clear validation messages, early exit
- **API Errors**: Formatted messages with error codes when available
- **Retries**: Automatic retry for transient errors (rate limit, server errors)
- **Rollback**: Delete partially-created campaigns if mid-creation fails
- **Logging**: Optional verbose output for debugging

### Non-Functional Requirements

#### NF1: Performance
- Campaign creation: <10 seconds (excluding image upload time)
- Config validation: <100ms
- Dry-run: <2 seconds (no API calls)
- Pagination: Handles 1000+ ad sets/ads per campaign

#### NF2: Reliability
- Retry logic: Up to 3 attempts for transient failures
- Timeout: 30 seconds per API request
- Dry-run safety: No actual campaigns created during preview
- Idempotent status checks: Multiple calls return consistent results

#### NF3: Usability
- Clear CLI help text (`meta-ads --help`)
- Confirmation prompts for destructive operations
- Progress indication (step counters in campaign creation)
- Formatted output (colors, tables, clear structure)

#### NF4: Security
- Credentials via environment variables (no hardcoding)
- Path traversal protection in image path resolution
- No sensitive data in log output (tokens masked)
- Minimal dependencies (click, requests, pyyaml, python-dotenv)

#### NF5: Compatibility
- Python 3.9–3.13 support
- Cross-platform (Linux, macOS, Windows via bash/Windows Terminal)
- PyPI distribution (installable via `pip install meta-ads-cli`)

## Acceptance Criteria

### Campaign Creation
- [ ] YAML config validates without API calls
- [ ] Dry-run shows correct operation sequence without creating objects
- [ ] Live deployment creates campaign + ad set + ads in correct order
- [ ] Rollback deletes campaign if ad creation fails mid-process
- [ ] All objects created with correct status (PAUSED by default)
- [ ] Summary shows all IDs and instructions to view in Ads Manager

### Campaign Management
- [ ] Status command returns campaign + ad sets + ads details
- [ ] Pause/activate commands update status correctly
- [ ] Delete command removes campaign permanently
- [ ] Confirmations prevent accidental destructive operations

### Config Validation
- [ ] Required fields enforced (campaign name, ad set name/budget, ad name/image/copy)
- [ ] Invalid objectives/CTAs/statuses rejected
- [ ] Image files must exist before deployment
- [ ] Path traversal attempts rejected
- [ ] Duplicate ad names detected
- [ ] Clear error messages guide users to fixes

### Error Scenarios
- [ ] Missing env vars: exit with helpful message
- [ ] Invalid YAML: clear parsing error
- [ ] API rate limit (429): retry automatically
- [ ] API server error (5xx): retry with backoff
- [ ] Image upload failure: stop before campaign creation
- [ ] Campaign creation failure: rollback with warning
- [ ] Partial failure: rollback entire transaction

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Campaign creation time | <10s | Benchmark on test account |
| User friction reduction | 50% | Vs. Ads Manager UI |
| Error message clarity | 100% | User can fix issues from output |
| Test coverage | >80% | Unit + integration tests |
| Installation success | 100% | Pip install on Python 3.9+ |
| API call efficiency | 1 campaign = 5 calls | Upload + create campaign/set/creative/ad |

## Future Roadmap

### Phase 2 (Planned)
- [ ] Bulk campaign upload (multiple YAMLs)
- [ ] Template variables in YAML (e.g., dynamic budget, dates)
- [ ] A/B test framework (auto-create variants)
- [ ] Budget distribution (split across multiple ad sets)
- [ ] Reporting dashboard (spend, conversions, ROAS)
- [ ] Webhook notifications (campaign milestones)

### Phase 3 (Stretch)
- [ ] Campaign cloning & modification
- [ ] Audience upload (CSV → Custom Audience)
- [ ] Creative asset library management
- [ ] Auto-pause low-performing ads
- [ ] Integration with analytics (GA4, Mixpanel)

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| click | ≥8.0 | CLI framework |
| requests | ≥2.28 | HTTP client for Graph API |
| pyyaml | ≥6.0 | YAML parsing |
| python-dotenv | ≥1.0 | Environment variable loading |
| pytest | ≥7.0 | Testing (dev-only) |
| hatchling | Latest | Build system |

## Configuration Requirements

### Environment Variables (Required at Runtime)
- `META_ACCESS_TOKEN`: Long-lived API token (60+ day duration recommended)
- `META_AD_ACCOUNT_ID`: Ad account number (no `act_` prefix)
- `META_PAGE_ID`: Facebook page ID

### Optional
- `META_API_VERSION`: API version (default: v21.0)

### Campaign YAML Schema
```yaml
campaign:
  name: string (required)
  objective: enum (default: OUTCOME_TRAFFIC)
  status: enum (default: PAUSED)
  special_ad_categories: list (default: [])

ad_set:
  name: string (required)
  daily_budget: int in cents (required, >0)
  optimization_goal: enum (default: LINK_CLICKS)
  targeting: object (required: countries)
    age_min: int (default: 18)
    age_max: int (default: 65)
    genders: [int] (default: [0])
    countries: [string] (required)
    interests: [{id, name}] (optional)
    platforms: [string] (default: ["facebook", "instagram"])
    facebook_positions: [string] (optional)
    instagram_positions: [string] (optional)

ads:
  - name: string (required, unique)
    image: path (required, resolved relative to YAML)
    primary_text: string (required)
    headline: string (required)
    description: string (optional)
    cta: enum (default: LEARN_MORE)
    link: url (required)
```

## Constraints & Assumptions

**Constraints**:
- Lightweight wrapper only (no SDK, minimal dependencies)
- Single campaign per deployment (1 campaign → 1 ad set → N ads)
- Images must be PNG/JPG/GIF/WebP
- Targeting limited to built-in Meta API options

**Assumptions**:
- Users have valid Meta Ads account with admin access
- Access token is long-lived (not short-lived from Graph API Explorer)
- Campaign approval not required by Meta (no pre-approval gate)
- Budget in cents (1000 = $10/day)

## Support & Maintenance

- **Issue Tracking**: GitHub issues
- **Documentation**: README.md + inline code comments
- **Testing**: Pytest with fixtures for API mocking
- **CI/CD**: GitHub Actions (Python 3.9–3.13 matrix)
- **Release Cadence**: Ad-hoc (when features/fixes ready)

---

**Last Updated**: 2026-03-11
**Maintained By**: Attainment Labs
**Repository**: https://github.com/attainmentlabs/meta-ads-cli
