"""Campaign config loading and validation."""

from pathlib import Path

import yaml


VALID_OBJECTIVES = [
    "OUTCOME_TRAFFIC",
    "OUTCOME_AWARENESS",
    "OUTCOME_ENGAGEMENT",
    "OUTCOME_LEADS",
    "OUTCOME_SALES",
    "OUTCOME_APP_PROMOTION",
]

VALID_OPTIMIZATION_GOALS = [
    "LINK_CLICKS",
    "IMPRESSIONS",
    "REACH",
    "LANDING_PAGE_VIEWS",
    "APP_INSTALLS",
    "OFFSITE_CONVERSIONS",
    "LEAD_GENERATION",
]

VALID_CTAS = [
    "LEARN_MORE",
    "SIGN_UP",
    "DOWNLOAD",
    "SHOP_NOW",
    "BOOK_NOW",
    "GET_OFFER",
    "SUBSCRIBE",
    "CONTACT_US",
    "APPLY_NOW",
    "WATCH_MORE",
    "INSTALL_MOBILE_APP",
]

VALID_STATUSES = ["PAUSED", "ACTIVE"]

VALID_SPECIAL_AD_CATEGORIES = [
    "CREDIT",
    "EMPLOYMENT",
    "HOUSING",
    "SOCIAL_ISSUES_ELECTIONS_POLITICS",
]


class ConfigError(Exception):
    """Raised when campaign config is invalid."""
    pass


def load_config(path):
    """Load and validate a campaign YAML config file.

    Returns the parsed config dict. Image paths are resolved
    relative to the YAML file's directory.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {path}")

    with open(config_path) as f:
        config = yaml.safe_load(f)

    if not config:
        raise ConfigError("Config file is empty")

    # Resolve image paths relative to the YAML file, with path traversal check
    config_dir = config_path.parent.resolve()
    for ad in config.get("ads", []):
        if "image" in ad:
            original = ad["image"]
            image_path = Path(original)
            if not image_path.is_absolute():
                image_path = config_dir / image_path
            resolved = image_path.resolve()
            if not resolved.is_relative_to(config_dir):
                raise ConfigError(f"Image path '{original}' escapes config directory")
            ad["image"] = str(resolved)

    return config


def validate_config(config):
    """Validate a campaign config dict. Raises ConfigError on problems."""
    errors = []

    # Campaign section
    campaign = config.get("campaign")
    if not campaign:
        errors.append("Missing 'campaign' section")
    else:
        if not campaign.get("name"):
            errors.append("campaign.name is required")
        objective = campaign.get("objective", "OUTCOME_TRAFFIC")
        if objective not in VALID_OBJECTIVES:
            errors.append(f"campaign.objective '{objective}' is not valid. Options: {', '.join(VALID_OBJECTIVES)}")
        status = campaign.get("status", "PAUSED")
        if status not in VALID_STATUSES:
            errors.append(f"campaign.status must be PAUSED or ACTIVE")
        special_cats = campaign.get("special_ad_categories", [])
        for cat in special_cats:
            if cat not in VALID_SPECIAL_AD_CATEGORIES:
                errors.append(
                    f"campaign.special_ad_categories '{cat}' is not valid. "
                    f"Options: {', '.join(VALID_SPECIAL_AD_CATEGORIES)}"
                )

    # Ad set section
    ad_set = config.get("ad_set")
    if not ad_set:
        errors.append("Missing 'ad_set' section")
    else:
        if not ad_set.get("name"):
            errors.append("ad_set.name is required")
        daily_budget = ad_set.get("daily_budget")
        if daily_budget is None:
            errors.append("ad_set.daily_budget is required (in cents, e.g. 1000 = $10/day)")
        else:
            try:
                budget_int = int(daily_budget)
            except (TypeError, ValueError):
                errors.append(f"ad_set.daily_budget must be an integer, got: {daily_budget!r}")
                budget_int = None
            if budget_int is not None and budget_int <= 0:
                errors.append(f"ad_set.daily_budget must be > 0, got: {daily_budget}")
        opt_goal = ad_set.get("optimization_goal", "LINK_CLICKS")
        if opt_goal not in VALID_OPTIMIZATION_GOALS:
            errors.append(f"ad_set.optimization_goal '{opt_goal}' is not valid. Options: {', '.join(VALID_OPTIMIZATION_GOALS)}")

        targeting = ad_set.get("targeting", {})
        if not targeting.get("countries"):
            errors.append("ad_set.targeting.countries is required (e.g. ['US', 'CA'])")

    # Ads section
    ads = config.get("ads")
    if not ads:
        errors.append("Missing 'ads' section (need at least one ad)")
    else:
        for i, ad in enumerate(ads):
            prefix = f"ads[{i}]"
            if not ad.get("name"):
                errors.append(f"{prefix}.name is required")
            if not ad.get("image"):
                errors.append(f"{prefix}.image is required")
            elif not Path(ad["image"]).exists():
                errors.append(f"{prefix}.image not found: {ad['image']}")
            if not ad.get("primary_text"):
                errors.append(f"{prefix}.primary_text is required")
            if not ad.get("headline"):
                errors.append(f"{prefix}.headline is required")
            if not ad.get("link"):
                errors.append(f"{prefix}.link is required")
            cta = ad.get("cta", "LEARN_MORE")
            if cta not in VALID_CTAS:
                errors.append(f"{prefix}.cta '{cta}' is not valid. Options: {', '.join(VALID_CTAS)}")

        # Check for duplicate ad names
        ad_names = [ad.get("name") for ad in ads if ad.get("name")]
        seen = set()
        for name in ad_names:
            if name in seen:
                errors.append(f"Duplicate ad name: '{name}'. Each ad must have a unique name.")
            seen.add(name)

    if errors:
        raise ConfigError("\n".join(f"  - {e}" for e in errors))

    return config
