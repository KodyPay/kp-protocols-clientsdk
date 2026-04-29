#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
STABLE_TAG_PATTERN = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
RELEASE_LABEL_TO_BUMP = {
    "release:major": "major",
    "release:minor": "minor",
    "release:patch": "patch",
    "release:none": "none",
}


def run_git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or "git command failed"
        raise RuntimeError(message)
    return completed.stdout.strip()


def normalize_labels(raw_labels_json: str) -> list[str]:
    try:
        payload = json.loads(raw_labels_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid labels JSON: {exc}") from exc

    if not isinstance(payload, list):
        raise ValueError("labels JSON must be an array")

    normalized: list[str] = []
    for item in payload:
        if isinstance(item, str):
            label = item.strip()
        elif isinstance(item, dict):
            label = str(item.get("name") or "").strip()
        else:
            label = str(item).strip()
        if label:
            normalized.append(label)
    return normalized


def latest_stable_tag() -> tuple[str, tuple[int, int, int]]:
    latest_tag = "v0.0.0"
    latest_version = (0, 0, 0)

    for tag in run_git("tag", "--list", "v*").splitlines():
        candidate_tag = tag.strip()
        match = STABLE_TAG_PATTERN.fullmatch(candidate_tag)
        if match is None:
            continue

        candidate_version = tuple(int(part) for part in match.groups())
        if candidate_version > latest_version:
            latest_tag = candidate_tag
            latest_version = candidate_version

    return latest_tag, latest_version


def select_release_label(labels: list[str]) -> tuple[str, str]:
    matching_labels = [label for label in labels if label in RELEASE_LABEL_TO_BUMP]
    supported = ", ".join(sorted(RELEASE_LABEL_TO_BUMP))

    if not matching_labels:
        raise ValueError(f"Expected exactly one release label ({supported}), found none.")

    if len(matching_labels) > 1:
        joined = ", ".join(sorted(matching_labels))
        raise ValueError(f"Expected exactly one release label ({supported}), found multiple: {joined}.")

    release_label = matching_labels[0]
    return release_label, RELEASE_LABEL_TO_BUMP[release_label]


def bump_version(current: tuple[int, int, int], bump: str) -> tuple[int, int, int]:
    major, minor, patch = current
    if bump == "major":
        return major + 1, 0, 0
    if bump == "minor":
        return major, minor + 1, 0
    if bump == "patch":
        return major, minor, patch + 1
    if bump == "none":
        return current
    raise ValueError(f"Unsupported bump kind: {bump}")


def write_outputs(outputs: dict[str, str]) -> None:
    github_output = os.environ.get("GITHUB_OUTPUT")
    if not github_output:
        return

    with Path(github_output).open("a", encoding="utf-8") as handle:
        for key, value in outputs.items():
            handle.write(f"{key}={value}\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Resolve the next stable release version from git tags and release labels."
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--labels-json",
        help="JSON array of pull request labels. Items may be label names or label objects.",
    )
    source_group.add_argument(
        "--bump",
        choices=["major", "minor", "patch", "none"],
        help="Manual bump kind for local validation.",
    )
    args = parser.parse_args()

    latest_tag, latest_version = latest_stable_tag()

    if args.labels_json:
        labels = normalize_labels(args.labels_json)
        release_label, bump = select_release_label(labels)
    else:
        bump = str(args.bump)
        release_label = f"release:{bump}"

    should_release = bump != "none"
    if should_release:
        next_version = bump_version(latest_version, bump)
        next_tag = f"v{next_version[0]}.{next_version[1]}.{next_version[2]}"
        next_version_text = f"{next_version[0]}.{next_version[1]}.{next_version[2]}"
    else:
        next_tag = ""
        next_version_text = ""

    outputs = {
        "release_label": release_label,
        "bump": bump,
        "latest_stable_tag": latest_tag,
        "should_release": str(should_release).lower(),
        "next_version": next_version_text,
        "next_tag": next_tag,
    }
    write_outputs(outputs)

    print(f"release_label={release_label}")
    print(f"bump={bump}")
    print(f"latest_stable_tag={latest_tag}")
    if should_release:
        print(f"next_tag={next_tag}")
    else:
        print("next_tag=<skipped>")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc