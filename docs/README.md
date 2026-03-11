# meta-ads-cli Documentation

Welcome to the meta-ads-cli documentation hub. This directory contains comprehensive guides for understanding, using, and contributing to the project.

## Quick Links

| Document | Purpose | Audience | Time |
|----------|---------|----------|------|
| [project-overview-pdr.md](./project-overview-pdr.md) | Project vision, requirements, scope | PMs, stakeholders, decision-makers | 10 min |
| [codebase-summary.md](./codebase-summary.md) | Code structure, modules, data flow | Developers, code reviewers | 15 min |
| [code-standards.md](./code-standards.md) | Development conventions, patterns | Contributors, new developers | 20 min |
| [system-architecture.md](./system-architecture.md) | System design, component interactions | Architects, senior engineers | 20 min |
| [project-roadmap.md](./project-roadmap.md) | Future features, timeline, vision | PMs, product strategists | 15 min |

## Reading Paths

### I'm new to the project
Start here:
1. [../README.md](../README.md) - Quick start (5 min)
2. [project-overview-pdr.md](./project-overview-pdr.md) - Understand the vision (10 min)

### I want to contribute code
Read these:
1. [codebase-summary.md](./codebase-summary.md) - Understand the structure (15 min)
2. [code-standards.md](./code-standards.md) - Follow conventions (20 min)
3. [../README.md](../README.md) - Setup development env (5 min)

### I'm building features or maintaining the project
Read all of:
1. [system-architecture.md](./system-architecture.md) - Design patterns (20 min)
2. [project-roadmap.md](./project-roadmap.md) - Future direction (15 min)
3. [code-standards.md](./code-standards.md) - Quality standards (20 min)

### I'm reviewing architecture decisions
Focus on:
1. [system-architecture.md](./system-architecture.md) - Component design
2. [project-overview-pdr.md](./project-overview-pdr.md) - Requirements context
3. [project-roadmap.md](./project-roadmap.md) - Scalability considerations

## Documentation Overview

### project-overview-pdr.md (286 lines)
**Executive summary and product requirements**

Contains:
- Project purpose, problem statement, solution
- 12 complete features (v0.1.0)
- Functional & non-functional requirements
- Acceptance criteria and success metrics
- Dependencies, configuration, constraints

Best for: Understanding *what* the project is and *why*

### codebase-summary.md (346 lines)
**Complete codebase structure and module descriptions**

Contains:
- All 5 Python modules documented
- 25+ public methods with signatures
- Data models and API flows
- Dependency graph and test structure
- Performance characteristics

Best for: Understanding *how* the code is organized

### code-standards.md (455 lines)
**Development conventions and best practices**

Contains:
- Naming conventions (Python)
- Code organization patterns
- Error handling strategies
- Testing approach (pytest)
- Security best practices
- Common pitfalls and solutions

Best for: Writing code that fits the project

### system-architecture.md (499 lines)
**System design, flows, and integration patterns**

Contains:
- Component architecture diagram
- Request/response flow (with error handling)
- Data models (campaign hierarchy)
- API integration patterns
- Deployment architecture
- Performance characteristics

Best for: Understanding *how systems interact*

### project-roadmap.md (469 lines)
**Future direction, planned features, timeline**

Contains:
- Current v0.1.0 status and limitations
- Roadmap through v1.0.0 (3 phases)
- Planned features (bulk upload, templates, A/B tests, etc.)
- Success metrics and milestones
- Breaking changes policy
- 2-year vision statement

Best for: Understanding *where the project is going*

## Key Information at a Glance

### Project Metadata
- **Name**: meta-ads-cli
- **Current Version**: 0.1.0 (Beta)
- **Python**: 3.9–3.13
- **License**: MIT
- **Repository**: https://github.com/attainmentlabs/meta-ads-cli
- **Author**: Attainment Labs

### Core Statistics
- **Codebase**: ~1000 LOC (5 modules)
- **Test Coverage**: >80%
- **Documentation**: 2,055 lines (5 files)
- **Dependencies**: 4 core (click, requests, pyyaml, python-dotenv)
- **CLI Commands**: 6 (create, status, pause, activate, delete, validate)

### What It Does
Create and manage Meta (Facebook/Instagram) ad campaigns from YAML configuration files via command-line interface.

**Example**:
```bash
meta-ads create --config campaign.yaml
```

Creates a complete campaign in seconds:
1. Uploads ad images
2. Creates campaign object
3. Creates ad set with budget & targeting
4. Creates ad creatives and ads
5. All created as PAUSED (user reviews before activation)

### Key Features
- Single-command campaign deployment from YAML
- Dry-run mode (preview without API calls)
- Automatic rollback on failure
- Retry logic with backoff (429, 5xx errors)
- Campaign management (status, pause, activate, delete)
- Full targeting configuration (age, gender, geo, interests)
- Path traversal protection
- Verbose logging for debugging

## Common Tasks

### Deploy your first campaign
→ See [../README.md - Quick Start](../README.md#quick-start) (5 min)

### Understand the campaign YAML schema
→ See [project-overview-pdr.md - Configuration Requirements](./project-overview-pdr.md#configuration-requirements) (3 min)

### Set up development environment
→ See [../README.md - Contributing](../README.md#contributing) (5 min)

### Add a new CLI command
→ Read [code-standards.md](./code-standards.md) + [system-architecture.md - CLI Layer](./system-architecture.md#high-level-overview) (30 min)

### Understand campaign creation flow
→ See [system-architecture.md - Request/Response Flow](./system-architecture.md#requestresponse-flow-campaign-creation) (10 min)

### Plan a new feature
→ See [project-roadmap.md](./project-roadmap.md) + [project-overview-pdr.md - Future Roadmap](./project-overview-pdr.md#future-roadmap) (20 min)

## Documentation Quality

✓ **Accuracy**: All code examples verified against source
✓ **Coverage**: All modules, commands, and patterns documented
✓ **Usability**: Clear navigation, examples, diagrams
✓ **Maintainability**: Timestamps, version info, ownership noted
✓ **Size**: All files under 800 LOC limit for optimal readability

## Contributing

To contribute to meta-ads-cli:

1. Read [code-standards.md](./code-standards.md) for conventions
2. Follow the development workflow in [../README.md - Contributing](../README.md#contributing)
3. Reference [codebase-summary.md](./codebase-summary.md) for module details
4. Check [project-roadmap.md](./project-roadmap.md) for planned features

## FAQ

**Q: Where do I start?**
A: Start with [../README.md](../README.md) for quick start, then [project-overview-pdr.md](./project-overview-pdr.md) for context.

**Q: How do I understand the code?**
A: Read [codebase-summary.md](./codebase-summary.md) for module overview, then [code-standards.md](./code-standards.md) for patterns.

**Q: What's coming next?**
A: See [project-roadmap.md](./project-roadmap.md) for v0.2.0 and beyond.

**Q: How do I report a bug?**
A: File an issue on GitHub: https://github.com/attainmentlabs/meta-ads-cli/issues

**Q: Can I contribute?**
A: Yes! See [../README.md - Contributing](../README.md#contributing) for guidelines.

## Maintenance

- **Documentation Owner**: Attainment Labs
- **Last Updated**: 2026-03-11
- **Version**: 0.1.0
- **Update Frequency**: With each release

---

**Need help?** Open an issue on [GitHub](https://github.com/attainmentlabs/meta-ads-cli/issues)

**Have suggestions?** Please contribute improvements!
