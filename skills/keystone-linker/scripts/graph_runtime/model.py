from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, Sequence, Tuple

from .relation_policy import RELATION_NAMES


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


RelationType = WireEnum("RelationType", {name.upper(): name for name in RELATION_NAMES})


class Evidence(WireEnum):
    DECLARED = "declared"
    OBSERVED = "observed"
    INFERRED = "inferred"


class MutationEvidence(WireEnum):
    DECLARED = "declared"
    OBSERVED = "observed"


class Lifecycle(WireEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"
    REMOVED = "removed"


class ApprovalState(WireEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


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


def patch_source_identity(surface: PatchSurface, target_path: str) -> str:
    """Map a physical patch target to the logical source represented by the patch."""
    try:
        surface = PatchSurface(surface)
    except (TypeError, ValueError):
        return target_path
    if (
        surface == PatchSurface.COMPANION_METADATA
        and isinstance(target_path, str)
        and target_path.endswith(".keystone.json")
    ):
        return target_path[:-len(".keystone.json")]
    return target_path


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


class ConflictReason(WireEnum):
    STALE_BASELINE = "stale_baseline"
    REJECT = "reject"
    NEEDS_REVISION = "needs_revision"
    RECONSTRUCTION_MISMATCH = "reconstruction_mismatch"


class FailureReason(WireEnum):
    TRANSIENT_IO = "transient_io"
    PERMISSION_DENIED = "permission_denied"
    VALIDATION_FAILED = "validation_failed"
    SOURCE_CONFLICT = "source_conflict"
    TOOL_FAILURE = "tool_failure"
    UNKNOWN = "unknown"


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
    approval_state: Optional[ApprovalState] = None
    source_authority: Tuple[Tuple[str, str], ...] = ()
    declared_lifecycle: Optional[Lifecycle] = None
    declared_approval_state: Optional[ApprovalState] = None
    declared_governed_by: Tuple[str, ...] = ()
    declared_source_authority: Tuple[Tuple[str, str], ...] = ()
    parent_id: Optional[str] = None


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
    patch_format: Optional[str] = None
    patch_body: Optional[str] = None
    expected_after_digest: Optional[str] = None
    baseline_content: Optional[str] = None


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
    conflict_reason: Optional[ConflictReason] = None
    failure_reason: Optional[FailureReason] = None
    reconstruction: Optional[GraphSnapshot] = None
    mechanical_validation: Tuple[Diagnostic, ...] = ()
    coverage_debt: Tuple[str, ...] = ()
    schema_version: int = SCHEMA_VERSION


@dataclass(frozen=True)
class ParseResult:
    snapshot: GraphSnapshot = field(default_factory=GraphSnapshot)
    diagnostics: Tuple[Diagnostic, ...] = ()
    baseline_digest: Optional[str] = None
    work_gates: Tuple[Any, ...] = ()
    dependency_sources: Tuple[Any, ...] = ()


@dataclass(frozen=True)
class GraphRelevance:
    relevant: bool
    disposition: GraphDisposition
    reason: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "disposition", GraphDisposition(self.disposition))
        if not isinstance(self.relevant, bool) or not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("graph relevance requires boolean relevant and a non-empty reason")


def graph_snapshot_wire(snapshot: GraphSnapshot) -> Dict[str, Any]:
    """Compatibility facade for the canonical snapshot serializer."""
    from .wire import graph_snapshot_wire as serialize

    return serialize(snapshot)


def transaction_wire(transaction: GraphTransaction, *,
                     baseline_snapshot: Optional[GraphSnapshot] = None) -> Dict[str, Any]:
    """Compatibility facade for the canonical transaction serializer."""
    from .wire import transaction_wire as serialize

    return serialize(transaction, baseline_snapshot=baseline_snapshot)


def attempt_history_wire(history: Any, graph_relevance: GraphRelevance, *,
                         current_baseline: Optional[GraphSnapshot] = None,
                         prior_baselines: Sequence[Optional[GraphSnapshot]] = ()) -> Dict[str, Any]:
    """Compatibility facade for the retry-history serializer."""
    from .wire import attempt_history_wire as serialize

    return serialize(
        history,
        graph_relevance,
        current_baseline=current_baseline,
        prior_baselines=prior_baselines,
    )
