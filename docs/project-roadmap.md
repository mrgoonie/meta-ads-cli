# meta-ads-cli: Project Roadmap & Future Vision

## Current Release: v0.1.0 (Beta)

**Status**: Production-ready, actively maintained
**Release Date**: 2026-03-11
**Python Support**: 3.9–3.13

### v0.1.0 Features (Complete)

| Feature | Status | Notes |
|---------|--------|-------|
| Campaign creation from YAML | ✓ | Single campaign → 1 ad set → N ads |
| Campaign management (pause/activate/delete) | ✓ | With confirmation prompts |
| Config validation | ✓ | Pre-deployment schema check |
| Dry-run mode | ✓ | Preview without API calls |
| Image upload & management | ✓ | PNG, JPG, GIF, WebP support |
| Targeting configuration | ✓ | Demographics, geography, interests, platforms |
| Error handling & rollback | ✓ | Automatic cleanup on failure |
| Retry logic (3x with backoff) | ✓ | Handles 429, 5xx errors |
| Verbose logging | ✓ | Debug API requests/responses |
| Pagination support | ✓ | For ad set & ad listing |
| CLI help & documentation | ✓ | Built-in `--help` for all commands |
| Unit test suite | ✓ | >80% coverage (api, config, campaign) |
| GitHub Actions CI | ✓ | Lint + test on push/PR |

### Known Limitations v0.1.0

| Limitation | Impact | Workaround |
|-----------|--------|-----------|
| Single campaign per deployment | Low | Run CLI multiple times |
| No bulk YAML processing | Medium | Manual parallelization in shell |
| No template variables | Medium | Pre-process YAML before deploy |
| No campaign cloning | Medium | Copy + edit YAML manually |
| No reporting/analytics | Medium | Use Meta Ads Manager dashboard |
| Image uploads sequential | Low | Typically <10 ads per campaign |
| No audience upload | Medium | Use Meta Ads Manager for audiences |
| No webhook notifications | Low | Check status command manually |

## Roadmap Overview

```
v0.1.0 (Current)
├─ Campaign creation ✓
├─ Campaign management ✓
└─ Config validation ✓

v0.2.0 (Next, Q2 2026)
├─ Bulk campaign upload
├─ Template variables
├─ A/B test framework
└─ Parallel image uploads

v0.3.0 (Q3 2026)
├─ Campaign cloning
├─ Budget distribution
├─ Auto-pause low performers
└─ Reporting dashboard

v1.0.0 (Q4 2026)
├─ Audience management
├─ Analytics integration
├─ Webhook notifications
└─ Production hardening
```

## Phase 2: v0.2.0 Planned Features

**Target**: Q2 2026 (May–June)
**Focus**: Bulk operations, templating, optimization

### F1: Bulk Campaign Upload

**Requirement**: Deploy multiple campaigns in one command

```bash
meta-ads create-batch campaigns/
  (processes all *.yaml files)
```

**Implementation**:
- Glob pattern matching for multiple YAML files
- Sequential deployment (one at a time, with delays between)
- Summary report (successes, failures, created IDs)
- Partial failure handling (continue on error, collect results)

**Complexity**: Medium
**Dependencies**: None (uses existing create_full_campaign)
**Testing**: Mock multiple YAML files, test aggregation

---

### F2: Template Variables in YAML

**Requirement**: Dynamic values in campaign config

```yaml
campaign:
  name: "My Campaign - {{ date }}"

ad_set:
  daily_budget: {{ budget }}

ads:
  - primary_text: "Sale until {{ end_date }}"
```

**Implementation**:
- Jinja2-style template rendering (or simple ${VAR} substitution)
- Environment variable substitution (`${META_AD_ACCOUNT_ID}`)
- CLI flag: `--vars budget=1000,date=2026-03-15`
- Default values for missing vars

**Complexity**: Low–Medium
**Dependencies**: Optional (jinja2 or use string.Template)
**Testing**: Test variable substitution, missing vars

---

### F3: A/B Test Framework

**Requirement**: Auto-create campaign variants for testing

```bash
meta-ads create --config campaign.yaml --ab-test
  (creates base + 2 variants)
```

**Variants Generated**:
- Headline A/B (test copy variations)
- Image A/B (test visual variations)
- CTA A/B (test button text)
- Landing page A/B (test URLs)

**Implementation**:
- Extend YAML schema with `ab_variants` section
- Duplicate creatives/ads with variant labels
- Track variant tags for analysis

**Complexity**: Medium
**Dependencies**: None (uses existing API)
**Testing**: Test variant generation, naming

---

### F4: Parallel Image Uploads

**Requirement**: Speed up image uploads for multi-ad campaigns

**Current**: Sequential (upload, wait for response, repeat)
**Target**: Concurrent (upload 3–5 simultaneously)

**Implementation**:
- Use `concurrent.futures.ThreadPoolExecutor`
- Upload 5 images in parallel
- Collect image hashes before creating campaign

**Performance Gain**:
- 10 images: 5–10s → 1–2s (5x faster)

**Complexity**: Low
**Testing**: Mock concurrent uploads, verify ordering

---

## Phase 3: v0.3.0 Planned Features

**Target**: Q3 2026 (August–September)
**Focus**: Campaign management, insights, automation

### F1: Campaign Cloning

**Requirement**: Duplicate existing campaign with modifications

```bash
meta-ads clone CAMPAIGN_ID \
  --name "Clone of Original" \
  --budget 2000
```

**Implementation**:
- Fetch campaign + ad set + ads from API
- Generate new YAML from fetched objects
- Apply CLI overrides (name, budget, etc.)
- Deploy as new campaign

**Complexity**: Medium
**Testing**: Mock fetch operations, test override logic

---

### F2: Budget Distribution

**Requirement**: Split budget across multiple ad sets

```yaml
campaign:
  name: "Multi-Region Campaign"

ad_sets:
  - name: "US Tier 1"
    daily_budget: 50%  # 500 of 1000

  - name: "US Tier 2"
    daily_budget: 30%  # 300 of 1000

  - name: "International"
    daily_budget: 20%  # 200 of 1000
```

**Implementation**:
- Extend YAML for multiple ad sets per campaign
- Parse percentage/fixed amounts
- Validate total equals campaign budget
- Create ad sets with distributed budgets

**Complexity**: Medium–High
**Breaking Change**: Schema change (support multiple ad_sets)

---

### F3: Auto-Pause Low Performers

**Requirement**: Automatically pause ads below performance threshold

```bash
meta-ads auto-manage CAMPAIGN_ID \
  --metric cpc \
  --threshold 5.00 \
  --action pause
```

**Implementation**:
- Fetch ad performance from API
- Compare against threshold
- Auto-pause low performers
- Log changes

**Complexity**: Medium
**Dependencies**: Insight API calls
**Testing**: Mock performance data, test pause logic

---

### F4: Reporting Dashboard

**Requirement**: View campaign performance at a glance

```bash
meta-ads report CAMPAIGN_ID
  (shows spend, impressions, conversions, ROAS)
```

**Implementation**:
- Fetch insights API data
- Format as table/ASCII chart
- Calculate key metrics (CPC, ROAS, CTR)
- Export to CSV/JSON

**Complexity**: Medium
**Testing**: Mock insights API, test formatting

---

## Phase 4: v1.0.0 Production Hardening

**Target**: Q4 2026 (November–December)
**Focus**: Stability, integrations, enterprise features

### Major Features

| Feature | Complexity | Impact |
|---------|-----------|--------|
| Audience upload (CSV) | High | Enable custom targeting |
| GA4 integration | High | Track campaign conversions |
| Mixpanel integration | Medium | Track user journey |
| Webhook notifications | Medium | Real-time alerts |
| Campaign scheduling | Medium | Schedule future deployments |
| Multi-account support | High | Manage multiple Ad accounts |
| Backup/restore campaigns | Medium | Disaster recovery |
| API rate limiting | Low | Graceful degradation |

### v1.0.0 Stability Goals

- **Test Coverage**: >90% (add integration tests)
- **API Compatibility**: Support v20.0–v22.0
- **Error Messages**: Contextual, actionable guidance
- **Documentation**: API docs, video tutorials
- **Performance**: <15s for typical campaign (10 ads)

---

## Feature Prioritization Matrix

```
High Impact + Low Effort (Do First)
├─ Bulk campaign upload (Phase 2) ✓
├─ Parallel image uploads (Phase 2) ✓
└─ Template variables (Phase 2) ✓

High Impact + Medium Effort (Do Next)
├─ Campaign cloning (Phase 3) ✓
├─ Budget distribution (Phase 3) ✓
└─ Reporting dashboard (Phase 3) ✓

Medium Impact + Low Effort (If Time)
├─ Auto-pause low performers (Phase 3) ✓
└─ Campaign scheduling (Phase 4) ✓

Low Impact or High Effort (Backlog)
├─ Multi-account support (Phase 4)
├─ Audience upload (Phase 4)
└─ GA4 integration (Phase 4)
```

---

## Improvement Areas

### Reliability
- [ ] Add integration tests (currently unit tests only)
- [ ] Test against actual Meta API (sandbox)
- [ ] Monitor error rates in production use
- [ ] Document common errors + fixes

### Performance
- [ ] Profile image upload bottleneck
- [ ] Consider async/await for I/O operations
- [ ] Cache API responses (campaign details)
- [ ] Benchmark against Ads Manager UI

### Usability
- [ ] Interactive config wizard (instead of manual YAML)
- [ ] Template library (common campaign types)
- [ ] Config diff viewer (before/after)
- [ ] Campaign comparison tool

### Documentation
- [ ] Video walkthrough (setup + first campaign)
- [ ] Advanced targeting guide
- [ ] Common error scenarios
- [ ] Migration guide (from Ads Manager)

### Developer Experience
- [ ] Plugin system for custom actions
- [ ] Programmatic API (Python library, not just CLI)
- [ ] Webhooks for automation
- [ ] Export/import campaign data

---

## Dependency Roadmap

### Current (v0.1.0)
- click 8.0+
- requests 2.28+
- pyyaml 6.0+
- python-dotenv 1.0+
- pytest 7.0+ (dev)

### v0.2.0 (Planned Additions)
- jinja2 (optional, for templates)
- tqdm (optional, for progress bars)

### v1.0.0 (Stretch)
- sqlite3 (for caching, bundled)
- reportlab (for PDF reports, optional)

**Philosophy**: Keep dependencies minimal. Add only if clear benefit.

---

## Community & Contribution Roadmap

### v0.1.0 (Current)
- [ ] Close GitHub issues from production hardening work
- [ ] Publish to PyPI ✓
- [ ] Document contribution guidelines

### v0.2.0
- [ ] Accept community PRs (bulk features)
- [ ] Host community examples (ecommerce, SaaS, etc.)
- [ ] Gather user feedback

### v1.0.0
- [ ] Announce 1.0 (production-ready)
- [ ] Support long-term (LTS for Python 3.9+)
- [ ] Consider sponsorship model

---

## Success Metrics & Milestones

### By v0.2.0 (Q2 2026)
- [ ] 5K+ PyPI downloads
- [ ] 10+ GitHub stars
- [ ] 2+ external contributions
- [ ] 0 critical bugs reported

### By v1.0.0 (Q4 2026)
- [ ] 50K+ PyPI downloads
- [ ] 50+ GitHub stars
- [ ] 10+ external contributors
- [ ] 99% uptime for API compatibility

### Long-term (2027+)
- [ ] Become de-facto Meta Ads CLI standard
- [ ] Support GraphQL API (v2.0)
- [ ] Enterprise deployment guide
- [ ] Integration marketplace (plugins)

---

## Timeline & Resource Allocation

| Phase | Target | Team | Effort | Status |
|-------|--------|------|--------|--------|
| v0.1.0 | Done (2026-03) | 1 dev | 80h | ✓ Complete |
| v0.2.0 | Q2 2026 | 1–2 devs | 40h | ⏳ Planned |
| v0.3.0 | Q3 2026 | 2 devs | 60h | 📋 Backlog |
| v1.0.0 | Q4 2026 | 2 devs | 80h | 📋 Backlog |

**Assumption**: Part-time maintenance (10–15 hrs/week)

---

## Breaking Changes Policy

**Semantic Versioning**:
- 0.1.0 → 0.2.0: May break YAML schema (pre-1.0)
- 1.0.0 → 1.1.0: No breaking changes (backcompat guaranteed)
- 1.x.0 → 2.0.0: Major breaking changes allowed

**Communication**:
- Document breaking changes in CHANGELOG.md
- Provide migration guide for users
- Deprecate features 1 release in advance

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Meta API breaking change | Medium | High | Monitor API docs, pin version |
| Python EOL (3.9) | Low | Low | Drop support in v2.0 |
| User data loss (rollback bug) | Low | Critical | Extensive testing, dry-run default |
| Rate limiting (too many calls) | Low | Medium | Backoff, document limits |
| Token expiration handling | Medium | Medium | Refresh token docs, error message |

---

## Vision Statement

**2-Year Vision**: meta-ads-cli becomes the developer's default choice for Meta Ads automation.

**Pillars**:
1. **Simplicity**: One command = one campaign (no UI complexity)
2. **Reliability**: Zero data loss, automatic rollback on failure
3. **Speed**: Deploy campaigns faster than Ads Manager UI
4. **Flexibility**: YAML-first, script-friendly, extensible
5. **Community**: Open, welcoming, actively maintained

---

**Last Updated**: 2026-03-11
**Maintained By**: Attainment Labs
**License**: MIT
**Repository**: https://github.com/attainmentlabs/meta-ads-cli
