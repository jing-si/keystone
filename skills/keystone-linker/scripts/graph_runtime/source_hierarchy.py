"""Declared and effective source-node hierarchy resolution."""

from dataclasses import dataclass
from typing import Any, Mapping, Optional, Tuple

from .lifecycle_policy import node_lifecycle_admitted, node_lifecycle_domain
from .metadata_support import metadata_strings
from .model import (
    ApprovalState,
    ArtifactKind,
    Diagnostic,
    Lifecycle,
    Locator,
    Node,
    NodeKind,
    Provenance,
)
from .yaml_subset import MetadataError


@dataclass(frozen=True)
class SourceNodeResult:
    node: Node
    diagnostics: Tuple[Diagnostic, ...]


def build_source_node(
    data: Mapping[str, Any],
    node_id: str,
    kind: NodeKind,
    artifact_kind: ArtifactKind,
    locator: Locator,
    surface: str,
    parent: Optional[Node],
    path: str,
) -> SourceNodeResult:
    diagnostics = []
    raw_lifecycle = data.get("_document_lifecycle", data.get("lifecycle"))
    declared_lifecycle = (
        _lifecycle(raw_lifecycle)
        if raw_lifecycle not in (None, "")
        else None
    )
    effective_lifecycle = declared_lifecycle or (
        parent.lifecycle if parent is not None else Lifecycle.ACTIVE
    )
    if not node_lifecycle_admitted(kind, effective_lifecycle):
        diagnostics.append(Diagnostic(
            "node_lifecycle_domain_invalid",
            "%s node cannot use %s lifecycle" % (
                node_lifecycle_domain(kind), effective_lifecycle.value,
            ),
            path=path,
            locator=locator,
        ))

    declared_approval = _approval(data.get("_approval_state"))
    effective_approval = (
        declared_approval
        if declared_approval is not None
        else (parent.approval_state if parent is not None else None)
    )
    if (
        parent is not None
        and parent.approval_state in {
            ApprovalState.PENDING,
            ApprovalState.REJECTED,
        }
        and declared_approval == ApprovalState.ACCEPTED
    ):
        diagnostics.append(Diagnostic(
            "approval_authority_expansion",
            "child approval cannot expand parent approval",
            path=path,
            locator=locator,
        ))
        effective_approval = parent.approval_state

    declared_governed_by = metadata_strings(data.get("governed_by"))
    parent_governed_by = (
        parent.provenance.governed_by if parent is not None else ()
    )
    effective_governed_by = tuple(dict.fromkeys(
        parent_governed_by + declared_governed_by
    ))

    declared_authority = _authority_entries(data.get("_source_authority"))
    effective_authority = declared_authority or (
        parent.source_authority if parent is not None else ()
    )
    if (
        parent is not None
        and declared_authority
        and not set(declared_authority) <= set(parent.source_authority)
    ):
        diagnostics.append(Diagnostic(
            "source_authority_expansion",
            "child source authority cannot expand parent authority",
            path=path,
            locator=locator,
        ))
        effective_authority = parent.source_authority

    provenance = Provenance(
        produced_from=metadata_strings(data.get("produced_from")),
        governed_by=effective_governed_by,
        surface=surface,
        locator=locator,
    )
    node = Node(
        node_id,
        kind,
        artifact_kind,
        locator,
        effective_lifecycle,
        provenance,
        effective_approval,
        effective_authority,
        declared_lifecycle,
        declared_approval,
        declared_governed_by,
        declared_authority,
        parent.id if parent is not None else None,
    )
    return SourceNodeResult(node=node, diagnostics=tuple(diagnostics))


def _lifecycle(value: Any) -> Lifecycle:
    try:
        return Lifecycle(str(value or "active"))
    except ValueError as error:
        raise MetadataError("unknown lifecycle: %s" % value) from error


def _approval(value: Any) -> Optional[ApprovalState]:
    if value in (None, ""):
        return None
    try:
        return ApprovalState(str(value))
    except ValueError as error:
        raise MetadataError("unknown approval state: %s" % value) from error


def _authority_entries(value: Any) -> Tuple[Tuple[str, str], ...]:
    if value in (None, "", {}):
        return ()
    if not isinstance(value, dict):
        raise MetadataError("authority must be a mapping")
    entries = []
    for key, raw in value.items():
        if isinstance(raw, list):
            entries.extend((str(key), str(item)) for item in raw)
        elif isinstance(raw, (str, int, bool)):
            entries.append((str(key), str(raw)))
        elif raw is not None:
            raise MetadataError("authority values must be scalar or string arrays")
    return tuple(sorted(entries))
