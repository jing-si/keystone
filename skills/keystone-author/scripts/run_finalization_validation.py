#!/usr/bin/env python3
"""Run the bundled finalization validator and map process failures fail-closed."""

import argparse
import json
import os
import stat
import subprocess
import sys
from pathlib import Path


DIAGNOSTIC_SCHEMA_VERSION = 1
RUNNER_PATH = Path(__file__).resolve()
CANONICAL_VALIDATOR = RUNNER_PATH.with_name("validate_finalization.py")
CANONICAL_GRAPH_RUNNER = (
    RUNNER_PATH.parents[2]
    / "keystone-linker"
    / "scripts"
    / "run_graph_validation.py"
)


class DuplicateJsonKey(ValueError):
    pass


def reject_duplicate_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateJsonKey("duplicate JSON key: %s" % key)
        value[key] = item
    return value


def loads_json_strict(value):
    return json.loads(value, object_pairs_hook=reject_duplicate_keys)


def emit(reason_code, message):
    print(json.dumps({
        "schema_version": DIAGNOSTIC_SCHEMA_VERSION,
        "status": "error",
        "diagnostics": [{"severity": "error", "code": reason_code, "message": message}],
        "summary": {"errors": 1, "warnings": 0},
    }, sort_keys=True))


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--validator", default=str(Path(__file__).with_name("validate_finalization.py")))
    parser.add_argument("--extension", help="Optional additive project validator Python script")
    parser.add_argument(
        "--graph-runner",
        default=str(Path(__file__).parents[2] / "keystone-linker" / "scripts" / "run_graph_validation.py"),
        help="Bundled Linker graph validation runner",
    )
    parser.add_argument(
        "--graph-evidence-root",
        help="External evidence root for graph application receipts",
    )
    parser.add_argument(
        "--graph-owner-key",
        action="append",
        default=[],
        metavar="OWNER=PATH",
    )
    parser.add_argument(
        "--graph-owner-key-sha256",
        action="append",
        default=[],
        metavar="OWNER=sha256:...",
    )
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    return parser.parse_args()


def validate_envelope(payload, returncode):
    schema_version = payload.get("schema_version") if isinstance(payload, dict) else None
    if (not isinstance(payload, dict) or type(schema_version) is not int
            or schema_version != DIAGNOSTIC_SCHEMA_VERSION):
        return "Validator output must be a JSON object."
    status = payload.get("status")
    diagnostics = payload.get("diagnostics")
    summary = payload.get("summary")
    if status not in {"pass", "fail", "error"} or not isinstance(diagnostics, list) or not isinstance(summary, dict):
        return "Validator output has an invalid diagnostic envelope."
    if not all(
        isinstance(item, dict)
        and item.get("severity") in {"error", "warning"}
        and isinstance(item.get("code"), str)
        and isinstance(item.get("message"), str)
        for item in diagnostics
    ):
        return "Validator diagnostics are malformed."
    error_count = sum(item["severity"] == "error" for item in diagnostics)
    warning_count = sum(item["severity"] == "warning" for item in diagnostics)
    summary_errors = summary.get("errors")
    summary_warnings = summary.get("warnings")
    if (
        not isinstance(summary_errors, int)
        or isinstance(summary_errors, bool)
        or not isinstance(summary_warnings, int)
        or isinstance(summary_warnings, bool)
        or summary_errors != error_count
        or summary_warnings != warning_count
    ):
        return "Validator summary does not match diagnostics."
    if (status == "pass" and error_count != 0) or (status in {"fail", "error"} and error_count == 0):
        return "Validator status does not match diagnostic severity."
    expected_status = {0: "pass", 1: "fail", 2: "error"}.get(returncode)
    if expected_status is None or status != expected_status:
        return "Validator exit code and status disagree."
    return None


def execute(command, timeout_seconds, *, environment=None):
    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
            env=environment,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return None, None, f"Validator execution failed: {error}"
    try:
        payload = loads_json_strict(process.stdout)
    except (json.JSONDecodeError, TypeError, DuplicateJsonKey):
        return process, None, "Validator output was not parseable JSON."
    envelope_error = validate_envelope(payload, process.returncode)
    return process, payload, envelope_error


def merged_payload(*payloads):
    diagnostics = [item for payload in payloads for item in payload.get("diagnostics", [])]
    errors = sum(item["severity"] == "error" for item in diagnostics)
    warnings = sum(item["severity"] == "warning" for item in diagnostics)
    return {
        "schema_version": DIAGNOSTIC_SCHEMA_VERSION,
        "status": "fail" if errors else "pass",
        "diagnostics": diagnostics,
        "summary": {"errors": errors, "warnings": warnings},
    }


def read_graph_sync(manifest_path):
    try:
        manifest = loads_json_strict(Path(manifest_path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateJsonKey):
        return None
    graph_sync = manifest.get("graph_sync") if isinstance(manifest, dict) else None
    return graph_sync if isinstance(graph_sync, dict) else None


def read_graph_manifest_schema(manifest_path):
    try:
        manifest = loads_json_strict(Path(manifest_path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateJsonKey):
        return None
    if not isinstance(manifest, dict):
        return None
    schema_version = manifest.get("schema_version")
    return schema_version if type(schema_version) is int else None


def requested_graph_manifest_schema(root, graph_sync):
    if (
        not graph_sync
        or graph_sync.get("required") is not True
        or not isinstance(graph_sync.get("validation_manifest_path"), str)
        or not graph_sync["validation_manifest_path"]
    ):
        return None
    try:
        resolved_root = Path(root).resolve()
        graph_manifest = (
            resolved_root / graph_sync["validation_manifest_path"]
        ).resolve()
        graph_manifest.relative_to(resolved_root)
    except (OSError, RuntimeError, ValueError):
        return None
    return read_graph_manifest_schema(graph_manifest)


def canonical_package_executable(value, canonical, reason_code, label):
    candidate = Path(value)
    try:
        candidate_identity = candidate.lstat()
        resolved_candidate = candidate.resolve(strict=True)
        canonical_identity = canonical.lstat()
        resolved_canonical = canonical.resolve(strict=True)
    except (OSError, RuntimeError, ValueError):
        candidate_identity = None
        resolved_candidate = None
        canonical_identity = None
        resolved_canonical = None
    if (
        candidate_identity is None
        or canonical_identity is None
        or candidate != canonical
        or resolved_candidate != canonical
        or resolved_canonical != canonical
        or not stat.S_ISREG(candidate_identity.st_mode)
        or candidate_identity.st_nlink != 1
        or not stat.S_ISREG(canonical_identity.st_mode)
        or canonical_identity.st_nlink != 1
    ):
        return None, (
            reason_code,
            "Application authority requires the exact canonical single-link "
            "regular %s: %s" % (label, canonical),
        )
    return canonical, None


def isolated_environment():
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment.pop("PYTHONHOME", None)
    return environment


def execute_graph(command, timeout_seconds):
    try:
        process = subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds, check=False)
    except subprocess.TimeoutExpired:
        return None, None, ("graph_validation_timeout", "Graph validation timed out.")
    except (OSError, subprocess.SubprocessError) as error:
        return None, None, ("graph_validation_execution_failed", f"Graph validation failed: {error}")
    try:
        payload = loads_json_strict(process.stdout)
    except (json.JSONDecodeError, TypeError, DuplicateJsonKey):
        return process, None, ("graph_validation_output_malformed", "Graph validation output was not parseable JSON.")
    envelope_error = validate_envelope(payload, process.returncode)
    if envelope_error or payload.get("schema_version") != 1:
        return process, payload, ("graph_validation_output_malformed", envelope_error or "Graph validation schema_version must be 1.")
    return process, payload, None


def main():
    args = parse_args()
    graph_sync = read_graph_sync(args.manifest)
    authority_requested = requested_graph_manifest_schema(
        args.root, graph_sync
    ) == 2
    validator = Path(args.validator)
    graph_runner = Path(args.graph_runner)
    if authority_requested:
        validator, authority_error = canonical_package_executable(
            args.validator,
            CANONICAL_VALIDATOR,
            "authority_validator_override_forbidden",
            "finalization validator",
        )
        if authority_error:
            emit(*authority_error)
            return 2
        graph_runner, authority_error = canonical_package_executable(
            args.graph_runner,
            CANONICAL_GRAPH_RUNNER,
            "authority_graph_runner_override_forbidden",
            "Linker graph runner",
        )
        if authority_error:
            emit(*authority_error)
            return 2
    elif not validator.is_file():
        emit("validator_unavailable", f"Validator is unavailable: {validator}")
        return 2
    validator_command = [sys.executable]
    if authority_requested:
        validator_command.append("-I")
    validator_command.extend((
        str(validator), "--root", args.root, "--manifest", args.manifest,
    ))
    process, payload, execution_error = execute(
        validator_command,
        args.timeout_seconds,
        environment=isolated_environment() if authority_requested else None,
    )
    if execution_error:
        emit("validator_execution_failed", execution_error)
        return 2
    if process.returncode == 2:
        diagnostics = payload["diagnostics"]
        message = diagnostics[0]["message"] if diagnostics else "Validator returned exit 2."
        emit("validator_execution_failed", message)
        return 2
    if process.returncode == 1:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 1

    combined = payload
    if graph_sync and graph_sync.get("required") is True and graph_sync.get("validation_manifest_path"):
        if authority_requested:
            graph_runner, authority_error = canonical_package_executable(
                args.graph_runner,
                CANONICAL_GRAPH_RUNNER,
                "authority_graph_runner_override_forbidden",
                "Linker graph runner",
            )
            if authority_error:
                emit(*authority_error)
                return 2
        elif not graph_runner.is_file():
            emit("graph_validator_unavailable", f"Graph validator runner is unavailable: {graph_runner}")
            return 2
        graph_manifest = (Path(args.root).resolve() / graph_sync["validation_manifest_path"]).resolve()
        try:
            graph_manifest.relative_to(Path(args.root).resolve())
        except ValueError:
            emit("graph_validation_execution_failed", "Graph validation manifest escapes --root.")
            return 2
        graph_schema = read_graph_manifest_schema(graph_manifest)
        if graph_schema == 2 and not args.graph_evidence_root:
            emit(
                "graph_application_evidence_context_missing",
                "Graph validation manifest schema 2 requires --graph-evidence-root.",
            )
            return 2
        graph_command = [
            sys.executable,
            "-I",
            str(graph_runner),
            "--root",
            args.root,
            "--manifest",
            str(graph_manifest),
        ]
        if graph_schema == 2:
            graph_command.extend((
                "--evidence-root",
                args.graph_evidence_root,
            ))
            for value in args.graph_owner_key:
                graph_command.extend(("--owner-key", value))
            for value in args.graph_owner_key_sha256:
                graph_command.extend(("--owner-key-sha256", value))
        graph_process, graph_payload, graph_error = execute_graph(
            graph_command,
            args.timeout_seconds,
        )
        if graph_error:
            emit(*graph_error)
            return 2
        if graph_process.returncode == 2:
            diagnostics = graph_payload.get("diagnostics", [])
            message = diagnostics[0]["message"] if diagnostics else "Graph validator returned exit 2."
            code = diagnostics[0]["code"] if diagnostics else "graph_validation_execution_failed"
            emit(code, message)
            return 2
        combined = merged_payload(payload, graph_payload)
        if graph_process.returncode == 1:
            print(json.dumps(combined, ensure_ascii=False, sort_keys=True))
            return 1

    if args.extension:
        extension = Path(args.extension)
        if not extension.is_file():
            emit("validator_execution_failed", f"Project extension is unavailable: {extension}")
            return 2
        extension_process, extension_payload, extension_error = execute(
            [sys.executable, str(extension), "--root", args.root, "--manifest", args.manifest],
            args.timeout_seconds,
        )
        if extension_error or extension_process.returncode == 2:
            emit("validator_execution_failed", extension_error or "Project extension returned exit 2.")
            return 2
        combined = merged_payload(combined, extension_payload)
        print(json.dumps(combined, ensure_ascii=False, sort_keys=True))
        return 1 if combined["summary"]["errors"] else 0
    print(json.dumps(combined, ensure_ascii=False, sort_keys=True))
    return 1 if combined["summary"]["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
