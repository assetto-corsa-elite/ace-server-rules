#!/usr/bin/env python3
"""Validate and render the CM content feed. This module never sends Discord messages."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

TOKEN = re.compile(r"\{\{(driver|emoji|link):([a-z0-9_]+)\}\}")
SNOWFLAKE = re.compile(r"[0-9]{17,20}\Z")
STATES = {"draft", "ready", "archived", "cancelled"}
CATEGORIES = ["practice_highlights", "forecast", "pre_race_briefing", "qualifying_report",
              "race_results", "race_insights", "standings", "next_round_forecast",
              "pre_race_announcement", "race_results_announcement"]
BAD_TEXT = ("\ufffd", "â€", "Ã©", "Ã¨", "ð\x9f", "&nbsp;", "&#", "\\n")


class FeedError(ValueError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def asset_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise FeedError("Invalid feed path")
    candidate = Path(relative)
    if candidate.is_absolute() or any(part in {"..", "."} for part in relative.split("/")):
        raise FeedError(f"Unsafe feed path: {relative}")
    path = (root / candidate).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise FeedError(f"Missing or escaped feed path: {relative}")
    return path


def checked_bytes(root: Path, item: dict) -> bytes:
    data = asset_path(root, item["path"]).read_bytes()
    if digest(data) != item["sha256"]:
        raise FeedError(f"SHA-256 mismatch: {item['path']}")
    if "size_bytes" in item and len(data) != item["size_bytes"]:
        raise FeedError(f"Byte size mismatch: {item['path']}")
    return data


def timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise FeedError("Expected an ISO-8601 date/time with UTC offset") from exc
    if parsed.tzinfo is None:
        raise FeedError("A scheduled date/time must include a UTC offset")
    return parsed


def utf16_units(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def validate_template(text: str, drivers: dict, emojis: dict) -> None:
    if text.startswith("\ufeff") or any(item in text for item in BAD_TEXT):
        raise FeedError("BOM, mojibake or escaped text found in template")
    if "@" in text or re.search(r"<a?:|<@[!&]?", text):
        raise FeedError("Templates must use stable driver/emoji tokens")
    for kind, key in TOKEN.findall(text):
        registry = drivers if kind == "driver" else (emojis if kind == "emoji" else {"results_start": True})
        if key not in registry:
            raise FeedError(f"Unknown {kind} key: {key}")
    plain = TOKEN.sub("", text)
    if "{{" in plain or "}}" in plain:
        raise FeedError("Malformed template token")
    if re.search(r"(?<!\\)_", re.sub(r"https://\S+", "URL", plain)):
        raise FeedError("Escape underscores in display text")
    if text.count("**") % 2:
        raise FeedError("Unbalanced bold formatting")
    if re.search(r"\*\*\{\{driver:|\{\{driver:[^}]+\}\}\*\*", text):
        raise FeedError("Driver mentions must stay outside bold formatting")
    paragraphs = text.strip().split("\n\n")
    if not paragraphs[0].startswith("# "):
        raise FeedError("Post requires a title")
    for paragraph in paragraphs[1:]:
        if paragraph.startswith("https://"):
            continue
        if not paragraph.startswith("{{emoji:checked}} "):
            raise FeedError("Every section must start with the checked emoji token")
    # Validate against maximum-length IDs before a CM database is connected.
    conservative = TOKEN.sub(lambda match: "<@12345678901234567890>" if match[1] == "driver"
                             else ("<:d_:12345678901234567890>" if match[1] == "emoji" else
                                   "https://discord.com/channels/12345678901234567890/12345678901234567890/12345678901234567890"), text)
    if utf16_units(conservative) > 2000:
        raise FeedError("Rendered post would exceed 2,000 UTF-16 units")


def validate(root: Path) -> tuple[dict, list[dict]]:
    catalog = read_json(root / "catalog.json")
    if catalog.get("schema_version") != 1:
        raise FeedError("Unsupported catalog version")
    for name, expected in catalog["config_sha256"].items():
        if digest(asset_path(root, name).read_bytes()) != expected:
            raise FeedError(f"Configuration digest mismatch: {name}")
    drivers = read_json(root / "config/identities.json")["drivers"]
    emojis = read_json(root / "config/emojis.json")["emojis"]
    sequence_ids, post_ids, manifests = set(), set(), []
    for entry in catalog["sequences"]:
        manifest = json.loads(checked_bytes(root, entry).decode("utf-8"))
        for field in ("sequence_id", "revision", "status", "phase", "league_id", "round", "scheduled_at"):
            if manifest[field] != entry[field]:
                raise FeedError(f"Catalog/manifest disagreement: {field}")
        sid = manifest["sequence_id"]
        if sid in sequence_ids or manifest["status"] not in STATES:
            raise FeedError("Duplicate sequence or invalid status")
        sequence_ids.add(sid)
        if manifest.get("schema_version") != 1 or type(manifest["revision"]) is not int or manifest["revision"] < 1:
            raise FeedError("Unsupported manifest version/revision")
        if manifest["scheduled_at"] is not None:
            start = timestamp(manifest["scheduled_at"])
        elif manifest["status"] == "ready":
            raise FeedError("Ready sequence requires explicit scheduled_at")
        if manifest.get("expires_at") is not None:
            if manifest["scheduled_at"] is None or timestamp(manifest["expires_at"]) <= start:
                raise FeedError("expires_at must be after scheduled_at")
        if manifest["phase"] == "post_race" and manifest["status"] == "ready" and manifest.get("race_review_complete") is not True:
            raise FeedError("Post-race publication requires completed race review")
        if not manifest["posts"]:
            raise FeedError("Sequence has no posts")
        actual_order = [post["order"] for post in manifest["posts"]]
        if actual_order != list(range(1, len(actual_order) + 1)):
            raise FeedError("Posts must be stored in contiguous publication order")
        categories = [post["category"] for post in manifest["posts"]]
        if any(category not in CATEGORIES for category in categories):
            raise FeedError("Unknown post category")
        if [CATEGORIES.index(category) for category in categories] != sorted(CATEGORIES.index(category) for category in categories):
            raise FeedError("Category publication order is invalid")
        for post in manifest["posts"]:
            if post["post_id"] in post_ids:
                raise FeedError("Post IDs must be globally unique")
            post_ids.add(post["post_id"])
            validate_post_policy(post)
            if post["kind"] == "text":
                if post["content"]["format"] != "cm-template-v1":
                    raise FeedError("Unsupported content format")
                content = checked_bytes(root, post["content"]).decode("utf-8")
                validate_template(content, drivers, emojis)
                if post["category"] == "race_results_announcement" and "{{link:results_start}}" not in content:
                    raise FeedError("Results announcement requires its complete-results link")
            elif post["content"] is not None or not post["attachments"]:
                raise FeedError("Media post requires images and null content")
            if not 0 <= len(post["attachments"]) <= 10:
                raise FeedError("A post permits at most 10 ordered attachments")
            filenames = set()
            for attachment in post["attachments"]:
                data = checked_bytes(root, attachment)
                if attachment["filename"] in filenames or Path(attachment["filename"]).name != attachment["filename"]:
                    raise FeedError("Attachment filename must be unique and contain no directories")
                filenames.add(attachment["filename"])
                if attachment["content_type"] != "image/png" or not data.startswith(b"\x89PNG\r\n\x1a\n"):
                    raise FeedError("Expected a real PNG attachment")
        manifests.append(manifest)
    for manifest in manifests:
        for dependency in manifest.get("requires_sequences", []):
            if dependency not in sequence_ids or dependency == manifest["sequence_id"]:
                raise FeedError("Unknown or self-referencing sequence prerequisite")
        if manifest["phase"] == "results_announcement":
            posts = manifest["posts"]
            if len(posts) != 3 or [p["kind"] for p in posts] != ["text", "media", "media"]:
                raise FeedError("Results announcement requires text, result posters, remaining posters")
            target = manifest.get("link_targets", {}).get("results_start", {})
            source = next((m for m in manifests if m["sequence_id"] == target.get("sequence_id")), None)
            if source is None or target.get("post_id") != source["posts"][0]["post_id"]:
                raise FeedError("Results link must target the first source-sequence message")
            if source["sequence_id"] not in manifest.get("requires_sequences", []):
                raise FeedError("Results announcement must wait for its full source sequence")
    return catalog, manifests


def validate_post_policy(post: dict) -> None:
    if post.get("kind") not in {"text", "media"}:
        raise FeedError("Unknown message kind")
    announcement = post["category"] in {"pre_race_announcement", "race_results_announcement"}
    if post["destination_key"] != ("announcements" if announcement else "results"):
        raise FeedError("Message routed to the wrong logical channel")
    must_ping = post["order"] == 1 and post["category"] in {
        "practice_highlights", "pre_race_announcement", "race_results_announcement"}
    if post.get("mention_everyone") is not must_ping:
        raise FeedError("Invalid everyone policy")
    if post["kind"] == "media" and post["mention_everyone"]:
        raise FeedError("Media follow-ups cannot ping everyone")


def render(root: Path, post: dict, bindings: dict) -> dict:
    """Bindings come from CM's existing driver DB and destination guild emoji lookup."""
    validate_post_policy(post)
    if post["kind"] == "media":
        return {"content": "", "allowed_mentions": {"parse": [], "users": [], "roles": [], "replied_user": False}}
    identities = read_json(root / "config/identities.json")["drivers"]
    emoji_registry = read_json(root / "config/emojis.json")["emojis"]
    content = checked_bytes(root, post["content"]).decode("utf-8")
    validate_template(content, identities, emoji_registry)
    mentioned_users = set()

    def replacement(match):
        kind, key = match.groups()
        if kind == "driver":
            value = bindings.get("drivers", {}).get(key)
            if not isinstance(value, str) or not SNOWFLAKE.fullmatch(value):
                raise FeedError(f"Resolve driver in CM database: {key}")
            mentioned_users.add(value)
            return f"<@{value}>"
        if kind == "link":
            value = bindings.get("links", {}).get(key)
            if not isinstance(value, str) or not re.fullmatch(r"https://discord\.com/channels/[0-9]{17,20}/[0-9]{17,20}/[0-9]{17,20}", value):
                raise FeedError("Resolve results_start from the delivery ledger")
            return value
        value = bindings.get("emojis", {}).get(key, {})
        emoji_id = value.get("id")
        name = value.get("name")
        if not isinstance(emoji_id, str) or not SNOWFLAKE.fullmatch(emoji_id) or name != emoji_registry[key]["name"]:
            raise FeedError(f"Resolve destination guild emoji: {key}")
        prefix = "a" if value.get("animated", False) else ""
        return f"<{prefix}:{name}:{emoji_id}>"

    # Tokens are substituted last. No subsequent Markdown conversion or escaping.
    content = TOKEN.sub(replacement, content)
    if post["mention_everyone"]:
        content = "@everyone\n" + content
    if utf16_units(content) > 2000:
        raise FeedError("Rendered Discord content exceeds 2,000 UTF-16 units")
    return {"content": content,
            "allowed_mentions": {"parse": ["everyone"] if post["mention_everyone"] else [], "users": sorted(mentioned_users), "roles": [], "replied_user": False}}


def delivery_key(guild_id: str, channel_id: str, sequence_id: str, post_id: str) -> str:
    # Revision deliberately excluded: a content update never creates a duplicate message.
    return "/".join((guild_id, channel_id, sequence_id, post_id))


def message_nonce(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]


def due_sequences(manifests: list[dict], now: datetime, completed: set[str] | None = None) -> list[dict]:
    if now.tzinfo is None:
        raise FeedError("now must include a timezone")
    completed = completed or set()
    ready = []
    for manifest in manifests:
        if manifest["status"] != "ready":
            continue
        if manifest["phase"] == "post_race" and manifest.get("race_review_complete") is not True:
            raise FeedError("Post-race review is incomplete")
        if manifest["scheduled_at"] is None:
            raise FeedError("Missing publication time")
        if timestamp(manifest["scheduled_at"]) > now:
            continue
        if manifest.get("expires_at") and now >= timestamp(manifest["expires_at"]):
            continue
        if not set(manifest.get("requires_sequences", [])).issubset(completed):
            continue
        ready.append(manifest)
    return sorted(ready, key=lambda manifest: (timestamp(manifest["scheduled_at"]), manifest["sequence_id"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate", "list", "plan", "render"])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--now", help="Timezone-aware ISO-8601 timestamp for planning")
    parser.add_argument("--bindings", type=Path)
    parser.add_argument("--sequence-id")
    parser.add_argument("--post-id")
    args = parser.parse_args()
    try:
        catalog, manifests = validate(args.root)
        if args.command == "validate":
            output = {"valid": True, "sequences": len(manifests), "posts": sum(len(m["posts"]) for m in manifests)}
        elif args.command == "list":
            output = catalog
        elif args.command == "plan":
            now = timestamp(args.now) if args.now else datetime.now(timezone.utc)
            output = [{"sequence_id": m["sequence_id"], "posts": [p["post_id"] for p in m["posts"]]}
                      for m in due_sequences(manifests, now)]
        else:
            if not args.bindings or not args.sequence_id or not args.post_id:
                raise FeedError("render requires --bindings, --sequence-id and --post-id")
            manifest = next(m for m in manifests if m["sequence_id"] == args.sequence_id)
            post = next(p for p in manifest["posts"] if p["post_id"] == args.post_id)
            output = render(args.root, post, read_json(args.bindings))
        print(json.dumps(output, ensure_ascii=False, indent=2))
    except (FeedError, KeyError, ValueError, OSError, StopIteration) as exc:
        parser.exit(1, f"Feed error: {exc}\n")


if __name__ == "__main__":
    main()
