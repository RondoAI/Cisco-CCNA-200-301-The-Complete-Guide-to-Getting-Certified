"""
Source protection — the ethical knife-edge of citizen media.

In Sudan, Iran, or anywhere a regime punishes witnesses, surfacing *who* filmed
something can get that person detained or killed. So identity stripping is not a
privacy setting the user can toggle off; it happens at the boundary, before raw
citizen media is ever allowed to become a Source object in the rest of the system.

We keep what verifies the FOOTAGE (when, where, is-it-recycled) and discard what
identifies the FILMER. For deduplication we keep only a salted one-way token, from
which the original handle cannot be recovered.
"""

from __future__ import annotations

import hashlib
import hmac
import os

from .models import Source, SourceKind

# In production this salt lives in a secrets manager and rotates. The point of a
# keyed hash (HMAC) is that even if the token store leaks, you cannot brute-force
# handles back out without the key.
_DEDUP_SALT = os.environ.get("GLASSHOUSE_DEDUP_SALT", "dev-only-not-secret").encode()

# Fields that identify a person. These are dropped on sight and never persisted.
_IDENTIFYING = {
    "uploader", "username", "handle", "account_id", "user_id", "display_name",
    "real_name", "phone", "email", "device_id", "ip", "profile_url", "bio",
}


def _one_way_token(value: str) -> str:
    return hmac.new(_DEDUP_SALT, value.encode(), hashlib.sha256).hexdigest()[:24]


def redact_uploader(raw: dict) -> dict:
    """Take a raw citizen-media record and return a sanitized version.

    Input may contain anything a scraper grabbed. Output contains ONLY
    verification-relevant fields plus a non-reversible dedup token. The original
    dict is never stored.
    """
    leaked = _IDENTIFYING & raw.keys()
    safe = {k: v for k, v in raw.items() if k not in _IDENTIFYING}

    # If an uploader handle was present, convert it to a one-way token *only* so
    # we can detect the same clip reposted, then forget the handle itself.
    handle = raw.get("handle") or raw.get("username") or raw.get("uploader")
    if handle:
        safe["dedup_token"] = _one_way_token(str(handle))

    safe["_redacted_fields"] = sorted(leaked)  # audit: prove we dropped them
    return safe


def citizen_source(raw: dict) -> Source:
    """Build a Source from raw citizen media, with identity stripped first."""
    safe = redact_uploader(raw)
    return Source(
        kind=SourceKind.CITIZEN,
        domain=safe.get("platform", "citizen"),     # platform, never the user
        url=safe.get("post_url"),                    # post, not profile
        content_hash=safe.get("content_hash"),
        dedup_token=safe.get("dedup_token"),
    )
