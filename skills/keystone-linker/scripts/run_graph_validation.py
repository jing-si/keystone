#!/usr/bin/env python3
"""Run core graph validation and an optional additive project extension fail-closed."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from graph_runtime.companion import load_authoritative_json


_ENVELOPE_FIELDS = {"schema_version", "status", "diagnostics", "summary"}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("--manifest")
    parser.add_argument("--transaction")
    parser.add_argument("--scope", choices=("transaction", "repository"))
    parser.add_argument("--validator", default=str(Path(__file__).with_name("validate_graph.py")))
    parser.add_argument("--extension", help="Optional additive validator")
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    return parser.parse_args()


def failure(code, message):
    return {"schema_version": 1, "status": "error",
            "diagnostics": [{"code": code, "message": message, "severity": "error"}],
            "summary": {"errors": 1, "warnings": 0}}


def valid_envelope(payload, returncode, *, allow_coverage=False):
    if not isinstance(payload, dict):
        return False
    expected_fields = set(_ENVELOPE_FIELDS)
    if "coverage" in payload:
        if not allow_coverage or not isinstance(payload["coverage"], dict):
            return False
        expected_fields.add("coverage")
    if (set(payload) != expected_fields
            or type(payload.get("schema_version")) is not int
            or payload.get("schema_version") != 1):
        return False
    diagnostics, summary = payload.get("diagnostics"), payload.get("summary")
    if not isinstance(diagnostics, list) or not isinstance(summary, dict):
        return False
    if not all(isinstance(item, dict) and isinstance(item.get("code"), str)
               and isinstance(item.get("message"), str) and item.get("severity") in {"error", "warning"}
               for item in diagnostics):
        return False
    errors = sum(item["severity"] == "error" for item in diagnostics)
    warnings = sum(item["severity"] == "warning" for item in diagnostics)
    expected = {0: "pass", 1: "fail", 2: "error"}.get(returncode)
    return (summary == {"errors": errors, "warnings": warnings}
            and payload.get("status") == expected)


def execute(command, timeout, *, allow_coverage=False):
    try:
        process = subprocess.run(command, capture_output=True, text=True, check=False, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, None, ("validator_timeout", "validator timed out")
    except (OSError, subprocess.SubprocessError) as error:
        return None, None, ("validator_execution_failed", str(error))
    try:
        payload = load_authoritative_json(process.stdout)
    except (TypeError, ValueError):
        return process, None, ("validator_output_malformed", "validator output is not JSON")
    if not valid_envelope(
        payload, process.returncode, allow_coverage=allow_coverage
    ):
        return process, payload, ("validator_output_malformed", "validator diagnostic envelope is invalid")
    return process, payload, None


def main():
    args = parse_args()
    validator = Path(args.validator)
    if not validator.is_file():
        print(json.dumps(failure("validator_unavailable", "core validator is unavailable"), sort_keys=True))
        return 2
    forwarded = ["--root", args.root]
    for source in args.source:
        forwarded.extend(("--source", source))
    if args.scope:
        forwarded.extend(("--scope", args.scope))
    for flag, value in (("--manifest", args.manifest), ("--transaction", args.transaction)):
        if value:
            forwarded.extend((flag, value))
    process, core, problem = execute(
        [sys.executable, str(validator), *forwarded],
        args.timeout_seconds,
        allow_coverage=True,
    )
    if problem or process.returncode == 2:
        payload = failure(*(problem or ("validator_execution_failed", "core validator returned exit 2")))
        print(json.dumps(payload, sort_keys=True))
        return 2
    diagnostics = list(core["diagnostics"])
    if args.extension:
        extension = Path(args.extension)
        if not extension.is_file():
            print(json.dumps(failure("extension_unavailable", "extension validator is unavailable"), sort_keys=True))
            return 2
        extension_process, extension_payload, problem = execute(
            [sys.executable, str(extension), *forwarded], args.timeout_seconds
        )
        if problem or extension_process.returncode == 2:
            payload = failure(*(problem or ("validator_execution_failed", "extension returned exit 2")))
            print(json.dumps(payload, sort_keys=True))
            return 2
        diagnostics.extend(extension_payload["diagnostics"])
    errors = sum(item["severity"] == "error" for item in diagnostics)
    warnings = sum(item["severity"] == "warning" for item in diagnostics)
    payload = {"schema_version": 1, "status": "fail" if errors else "pass",
               "diagnostics": diagnostics, "summary": {"errors": errors, "warnings": warnings}}
    if "coverage" in core:
        payload["coverage"] = core["coverage"]
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
