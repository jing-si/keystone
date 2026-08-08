#!/usr/bin/env python3
"""Classify an exact graph delta set against the current source generation."""

import argparse
import json
import sys
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from graph_runtime.classification import (
    ClassificationInputError,
    classify,
    error_envelope,
)
from graph_runtime.companion import load_authoritative_json


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        root = args.root.resolve(strict=True)
        if not root.is_dir():
            raise OSError("repository root is not a directory")
    except OSError as error:
        payload = error_envelope("root_unavailable", str(error), "root")
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 2
    try:
        raw = args.manifest.read_bytes()
        manifest = load_authoritative_json(raw.decode("utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        payload = error_envelope(
            "classification_manifest_json_invalid", str(error), "manifest"
        )
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 2
    try:
        payload = classify(root, manifest)
    except ClassificationInputError as error:
        code = (
            "source_coverage_delta_omitted"
            if str(error).startswith("source_coverage_delta_omitted:")
            else "classification_manifest_invalid"
        )
        if code == "source_coverage_delta_omitted":
            payload = error_envelope(code, str(error), "source_context.sources")
            payload["status"] = "fail"
            payload["summary"] = {"errors": 1, "warnings": 0}
            print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
            return 1
        payload = error_envelope(code, str(error), "manifest")
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
