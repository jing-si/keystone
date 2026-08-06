from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple


SCHEMA_VERSION = 1


class WireEnum(str, Enum):
    pass


class NodeKind(WireEnum):
    SOURCE_DOCUMENT = "source_document"
    DOCUMENT_SECTION = "document_section"
    DOCUMENT_ITEM = "document_item"
    CLAIM = "claim"
    DECISION = "decision"
    WORK_ORDER = "work_order"
    WORK_STEP = "work_step"
    CAPABILITY = "capability"
    OUTPUT_ARTIFACT = "output_artifact"
    VERIFICATION_RESULT = "verification_result"


class ArtifactKind(WireEnum):
    SKILL_SOURCE = "skill_source"
    CODE = "code"
    CONFIG = "config"
    SCHEMA = "schema"
    API = "api"
    TEST = "test"
    GENERATED_FILE = "generated_file"
    DOC_ARTIFACT = "doc_artifact"
    NONE = "none"


class RelationType(WireEnum):
    PRODUCES = "produces"
    PROVIDES = "provides"
    USES = "uses"
    IMPLEMENTS = "implements"
    REQUIRES_VERIFICATION_OF = "requires_verification_of"
    VERIFIES = "verifies"
    DEPENDS_ON = "depends_on"
    GOVERNED_BY = "governed_by"
    DOCUMENTS = "documents"
    SUPERSEDES = "supersedes"
    DERIVED_FROM = "derived_from"


class Evidence(WireEnum):
    DECLARED = "declared"
    OBSERVED = "observed"
    INFERRED = "inferred"


class MutationEvidence(WireEnum):
    DECLARED = "declared"
    OBSERVED = "observed"


class Lifecycle(WireEnum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    REMOVED = "removed"


class DeltaKind(WireEnum):
    DOCUMENT = "document_delta"
    ARTIFACT = "artifact_delta"


class MutationOperation(WireEnum):
    ADD = "add"
    UPDATE = "update"
    REMOVE = "remove"


class MutationEntity(WireEnum):
    NODE = "node"
    RELATION = "relation"


class PatchOwner(WireEnum):
    AUTHOR = "author"
    MAIN = "main"
    COORDINATOR = "coordinator"


class PatchSurface(WireEnum):
    DOCUMENT_METADATA = "document_metadata"
    CODE_ANCHOR = "code_anchor"
    CONFIG_ANCHOR = "config_anchor"
    SCHEMA_ANCHOR = "schema_anchor"
    API_ANCHOR = "api_anchor"
    TEST_ANCHOR = "test_anchor"
    COMPANION_METADATA = "companion_metadata"


_REPOSITORY_PATCH_SURFACES = frozenset({
    PatchSurface.CODE_ANCHOR, PatchSurface.CONFIG_ANCHOR, PatchSurface.SCHEMA_ANCHOR,
    PatchSurface.API_ANCHOR, PatchSurface.TEST_ANCHOR,
})


def patch_owner_matches_surface(owner: PatchOwner, surface: PatchSurface,
                                target_path: str) -> bool:
    """Return whether the physical writer owns this explicitly described surface."""
    try:
        owner, surface = PatchOwner(owner), PatchSurface(surface)
    except ValueError:
        return False
    if surface == PatchSurface.DOCUMENT_METADATA:
        return owner == PatchOwner.AUTHOR
    if surface in _REPOSITORY_PATCH_SURFACES:
        return owner in {PatchOwner.MAIN, PatchOwner.COORDINATOR}
    if surface != PatchSurface.COMPANION_METADATA or not isinstance(target_path, str):
        return False
    source_path = (target_path[:-len(".keystone.json")]
                   if target_path.endswith(".keystone.json") else "")
    if not source_path:
        return False
    is_document = source_path.lower().endswith((".md", ".markdown"))
    return (owner == PatchOwner.AUTHOR if is_document
            else owner in {PatchOwner.MAIN, PatchOwner.COORDINATOR})


class AttestationDecision(WireEnum):
    CONFIRM = "confirm"
    REJECT = "reject"
    NEEDS_REVISION = "needs_revision"


class ApplicationStatus(WireEnum):
    APPLIED = "applied"
    FAILED = "failed"
    STALE_BASELINE = "stale_baseline"


class TransactionState(WireEnum):
    PROPOSED = "proposed"
    AWAITING_ATTESTATION = "awaiting_attestation"
    READY_TO_APPLY = "ready_to_apply"
    APPLYING = "applying"
    PARTIALLY_APPLIED = "partially_applied"
    VERIFIED = "verified"
    CONFLICTED = "conflicted"
    FAILED = "failed"


class Severity(WireEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class GraphDisposition(WireEnum):
    REQUIRED = "required"
    NOT_APPLICABLE = "not_applicable"
    DEFERRED = "deferred"


@dataclass(frozen=True)
class Locator:
    path: str
    heading: Optional[str] = None
    symbol: Optional[str] = None
    test_name: Optional[str] = None
    config_key: Optional[str] = None
    schema_name: Optional[str] = None


@dataclass(frozen=True)
class Provenance:
    produced_from: Tuple[str, ...] = ()
    governed_by: Tuple[str, ...] = ()
    surface: Optional[str] = None
    locator: Optional[Locator] = None
    attested_by: Optional[str] = None


@dataclass(frozen=True)
class Node:
    id: str
    kind: NodeKind
    artifact_kind: ArtifactKind = ArtifactKind.NONE
    locator: Locator = field(default_factory=lambda: Locator(path=""))
    lifecycle: Lifecycle = Lifecycle.ACTIVE
    provenance: Provenance = field(default_factory=Provenance)


@dataclass(frozen=True)
class Relation:
    source: str
    relation: RelationType
    target: str
    evidence: Evidence = Evidence.DECLARED
    provenance: Provenance = field(default_factory=Provenance)
    lifecycle: Lifecycle = Lifecycle.ACTIVE


@dataclass(frozen=True)
class GraphSnapshot:
    nodes: Tuple[Node, ...] = ()
    relations: Tuple[Relation, ...] = ()
    schema_version: int = SCHEMA_VERSION


@dataclass(frozen=True)
class Delta:
    kind: DeltaKind
    source_surface: str
    changed_locators: Tuple[Locator, ...] = ()
    semantic_summary: str = ""
    baseline_digest: str = "absent"
    graph_relevant: bool = True


@dataclass(frozen=True)
class CanonicalMutation:
    operation: MutationOperation
    entity: MutationEntity
    before: Optional[Any]
    after: Optional[Any]
    evidence: MutationEvidence
    direct_relation_reason: Optional[str] = None

    def __post_init__(self) -> None:
        try:
            admitted = MutationEvidence(self.evidence)
        except ValueError as error:
            raise ValueError("canonical mutation evidence must be declared or observed") from error
        object.__setattr__(self, "evidence", admitted)


@dataclass(frozen=True)
class SurfacePatch:
    patch_id: str
    owner: PatchOwner
    surface: PatchSurface
    target_path: str
    baseline_digest: str
    exact_patch: str
    required: bool = True


@dataclass(frozen=True)
class SurfaceAttestation:
    patch_id: str
    owner: PatchOwner
    decision: AttestationDecision
    evidence: str = ""


@dataclass(frozen=True)
class ApplicationResult:
    patch_id: str
    result: ApplicationStatus
    resulting_digest: Optional[str] = None
    evidence: str = ""


@dataclass(frozen=True)
class Diagnostic:
    code: str
    message: str
    severity: Severity = Severity.ERROR
    path: Optional[str] = None
    locator: Optional[Locator] = None


@dataclass(frozen=True)
class GraphTransaction:
    transaction_id: str
    scope_ref: str
    input_deltas: Tuple[Delta, ...] = ()
    canonical_mutations: Tuple[CanonicalMutation, ...] = ()
    surface_patches: Tuple[SurfacePatch, ...] = ()
    attestations: Tuple[SurfaceAttestation, ...] = ()
    apply_results: Tuple[ApplicationResult, ...] = ()
    state: TransactionState = TransactionState.PROPOSED
    reconstruction: Optional[GraphSnapshot] = None
    mechanical_validation: Tuple[Diagnostic, ...] = ()
    coverage_debt: Tuple[str, ...] = ()
    schema_version: int = SCHEMA_VERSION


@dataclass(frozen=True)
class ParseResult:
    snapshot: GraphSnapshot = field(default_factory=GraphSnapshot)
    diagnostics: Tuple[Diagnostic, ...] = ()
    baseline_digest: Optional[str] = None


@dataclass(frozen=True)
class GraphRelevance:
    relevant: bool
    disposition: GraphDisposition
    reason: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "disposition", GraphDisposition(self.disposition))
        if not isinstance(self.relevant, bool) or not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("graph relevance requires boolean relevant and a non-empty reason")


def _locator_wire(locator: Locator) -> Dict[str, Any]:
    return {name: getattr(locator, name) for name in
            ("path", "heading", "symbol", "test_name", "config_key", "schema_name")
            if getattr(locator, name) is not None}


def _provenance_wire(provenance: Provenance) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "produced_from": list(provenance.produced_from),
        "governed_by": list(provenance.governed_by),
    }
    if provenance.surface is not None:
        result["surface"] = provenance.surface
    if provenance.locator is not None:
        result["locator"] = _locator_wire(provenance.locator)
    if provenance.attested_by is not None:
        result["attested_by"] = provenance.attested_by
    return result


def _node_wire(node: Node) -> Dict[str, Any]:
    return {"id": node.id, "kind": node.kind.value, "artifact_kind": node.artifact_kind.value,
            "locator": _locator_wire(node.locator), "lifecycle": node.lifecycle.value,
            "provenance": _provenance_wire(node.provenance)}


def _relation_wire(relation: Relation) -> Dict[str, Any]:
    return {"source": relation.source, "relation": relation.relation.value,
            "target": relation.target, "evidence": relation.evidence.value,
            "provenance": _provenance_wire(relation.provenance),
            "lifecycle": relation.lifecycle.value}


def graph_snapshot_wire(snapshot: GraphSnapshot) -> Dict[str, Any]:
    return {"schema_version": snapshot.schema_version,
            "nodes": [_node_wire(node) for node in snapshot.nodes],
            "relations": [_relation_wire(relation) for relation in snapshot.relations]}


def _entity_wire(value: Any) -> Optional[Dict[str, Any]]:
    if value is None:
        return None
    if isinstance(value, Node):
        return _node_wire(value)
    if isinstance(value, Relation):
        return _relation_wire(value)
    raise TypeError("canonical mutation entity must be Node or Relation")


def _diagnostic_wire(item: Diagnostic) -> Dict[str, Any]:
    result: Dict[str, Any] = {"code": item.code, "message": item.message,
                              "severity": item.severity.value}
    if item.path is not None:
        result["path"] = item.path
    if item.locator is not None:
        result["locator"] = _locator_wire(item.locator)
    return result


def _mechanical_envelope(diagnostics: Sequence[Diagnostic]) -> Dict[str, Any]:
    items = [_diagnostic_wire(item) for item in diagnostics]
    errors = sum(item["severity"] == "error" for item in items)
    warnings = sum(item["severity"] == "warning" for item in items)
    return {"schema_version": SCHEMA_VERSION, "status": "fail" if errors else "pass",
            "diagnostics": items, "summary": {"errors": errors, "warnings": warnings}}


def transaction_wire(transaction: GraphTransaction, *,
                     baseline_snapshot: Optional[GraphSnapshot] = None) -> Dict[str, Any]:
    """Serialize exactly the accepted canonical transaction wire, without report-only fields."""
    if transaction.reconstruction is not None and baseline_snapshot is None:
        raise ValueError("reconstruction serialization requires its baseline snapshot")
    reconstruction = (None if transaction.reconstruction is None else {
        "baseline": graph_snapshot_wire(baseline_snapshot),
        "result": graph_snapshot_wire(transaction.reconstruction),
    })
    return {
        "schema_version": transaction.schema_version,
        "transaction_id": transaction.transaction_id,
        "scope_ref": transaction.scope_ref,
        "input_deltas": [{
            "kind": delta.kind.value, "source_surface": delta.source_surface,
            "changed_locators": [_locator_wire(locator) for locator in delta.changed_locators],
            "semantic_summary": delta.semantic_summary,
            "baseline_digest": delta.baseline_digest, "graph_relevant": delta.graph_relevant,
        } for delta in transaction.input_deltas],
        "canonical_mutations": [{
            "operation": mutation.operation.value, "entity": mutation.entity.value,
            "before": _entity_wire(mutation.before), "after": _entity_wire(mutation.after),
            "evidence": mutation.evidence.value,
            "direct_relation_reason": mutation.direct_relation_reason,
        } for mutation in transaction.canonical_mutations],
        "surface_patches": [{
            "patch_id": patch.patch_id, "owner": patch.owner.value, "surface": patch.surface.value,
            "target_path": patch.target_path, "baseline_digest": patch.baseline_digest,
            "exact_patch": patch.exact_patch, "required": patch.required,
        } for patch in transaction.surface_patches],
        "attestations": [{
            "patch_id": item.patch_id, "owner": item.owner.value, "decision": item.decision.value,
            "evidence": item.evidence,
        } for item in transaction.attestations],
        "apply_results": [{
            "patch_id": item.patch_id, "result": item.result.value,
            "resulting_digest": item.resulting_digest, "evidence": item.evidence,
        } for item in transaction.apply_results],
        "state": transaction.state.value,
        "reconstruction": reconstruction,
        "mechanical_validation": _mechanical_envelope(transaction.mechanical_validation),
        "coverage_debt": list(transaction.coverage_debt),
    }


def attempt_history_wire(history: Any, graph_relevance: GraphRelevance, *,
                         current_baseline: Optional[GraphSnapshot] = None,
                         prior_baselines: Sequence[Optional[GraphSnapshot]] = ()) -> Dict[str, Any]:
    """Serialize report-level relevance and retry history outside the canonical transaction."""
    prior_attempts = tuple(history.prior_attempts)
    if len(prior_baselines) != len(prior_attempts):
        raise ValueError("each prior attempt requires a corresponding baseline entry")
    return {
        "schema_version": SCHEMA_VERSION,
        "graph_relevance": {"relevant": graph_relevance.relevant,
                            "disposition": graph_relevance.disposition.value,
                            "reason": graph_relevance.reason},
        "transaction": transaction_wire(history.current, baseline_snapshot=current_baseline),
        "prior_attempts": [transaction_wire(transaction, baseline_snapshot=baseline)
                           for transaction, baseline in zip(prior_attempts, prior_baselines)],
    }
