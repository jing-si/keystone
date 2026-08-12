# keystone: id=key.test.linker.source-views kind=output_artifact artifact_kind=test verifies=key.code.linker.source-views key.standard.project.source-derived-semantic-views
import unittest

from graph_runtime.model import (
    ApprovalState,
    ArtifactKind,
    GraphSnapshot,
    Lifecycle,
    Locator,
    Node,
    NodeKind,
    Relation,
    RelationType,
)
from graph_runtime.source_views import source_views_from_snapshot, source_views_wire


class SourceViewsTest(unittest.TestCase):
    def test_views_join_criteria_decisions_and_work_outputs(self):
        criterion = Node(
            "key.acceptance.release.ready",
            NodeKind.CLAIM,
            locator=Locator("docs/work.md", heading="Completion Criteria"),
            approval_state=ApprovalState.PENDING,
        )
        code = Node(
            "key.code.release",
            NodeKind.OUTPUT_ARTIFACT,
            ArtifactKind.CODE,
            Locator("src/release.py", symbol="release"),
        )
        test = Node(
            "key.test.release",
            NodeKind.OUTPUT_ARTIFACT,
            ArtifactKind.TEST,
            Locator("tests/test_release.py", test_name="test_release"),
        )
        old = Node(
            "key.claim.release.old",
            NodeKind.CLAIM,
            locator=Locator("docs/decisions.md", heading="Old"),
            lifecycle=Lifecycle.SUPERSEDED,
            approval_state=ApprovalState.ACCEPTED,
        )
        current = Node(
            "key.claim.release.current",
            NodeKind.CLAIM,
            locator=Locator("docs/decisions.md", heading="Current"),
            approval_state=ApprovalState.ACCEPTED,
        )
        pending = Node(
            "key.claim.release.pending",
            NodeKind.CLAIM,
            locator=Locator("docs/decisions.md", heading="Pending"),
            approval_state=ApprovalState.PENDING,
        )
        work = Node(
            "key.work.release.order",
            NodeKind.WORK_ORDER,
            locator=Locator("docs/work.md"),
            approval_state=ApprovalState.PENDING,
        )
        snapshot = GraphSnapshot(
            nodes=(criterion, code, test, old, current, pending, work),
            relations=(
                Relation(
                    criterion.id,
                    RelationType.REQUIRES_VERIFICATION_OF,
                    code.id,
                ),
                Relation(test.id, RelationType.VERIFIES, code.id),
                Relation(current.id, RelationType.SUPERSEDES, old.id),
                Relation(work.id, RelationType.PRODUCES, code.id),
                Relation(work.id, RelationType.PRODUCES, test.id),
            ),
        )

        views = source_views_from_snapshot(
            snapshot, "sha256:" + "a" * 64
        )
        wire = source_views_wire(views)

        self.assertEqual("verified", views.criteria[0].status)
        self.assertEqual("pending", views.criteria[0].approval_state)
        self.assertEqual(("key.test.release",), views.criteria[0].targets[0].verifier_ids)
        self.assertEqual(
            ("key.claim.release.current",),
            tuple(item.decision_id for item in views.effective_decisions),
        )
        self.assertEqual(
            ("key.claim.release.pending",),
            tuple(item.decision_id for item in views.pending_decisions),
        )
        self.assertEqual(
            ("key.code.release", "key.test.release"),
            views.work_artifacts[0].output_ids,
        )
        self.assertEqual(("key.test.release",), views.work_artifacts[0].test_ids)
        self.assertEqual("sha256:" + "a" * 64, wire["source_generation"])

    def test_unbound_and_partially_verified_criteria_are_not_promoted(self):
        unbound = Node(
            "key.acceptance.unbound",
            NodeKind.CLAIM,
            locator=Locator("docs/work.md"),
            approval_state=ApprovalState.PENDING,
        )
        partial = Node(
            "key.acceptance.partial",
            NodeKind.CLAIM,
            locator=Locator("docs/work.md"),
            approval_state=ApprovalState.PENDING,
        )
        retired = Node(
            "key.acceptance.retired-target",
            NodeKind.CLAIM,
            locator=Locator("docs/work.md"),
            approval_state=ApprovalState.PENDING,
        )
        first = Node("key.code.first", NodeKind.OUTPUT_ARTIFACT, ArtifactKind.CODE)
        second = Node("key.code.second", NodeKind.OUTPUT_ARTIFACT, ArtifactKind.CODE)
        retired_code = Node(
            "key.code.retired",
            NodeKind.OUTPUT_ARTIFACT,
            ArtifactKind.CODE,
            lifecycle=Lifecycle.DEPRECATED,
        )
        test = Node("key.test.first", NodeKind.OUTPUT_ARTIFACT, ArtifactKind.TEST)
        snapshot = GraphSnapshot(
            nodes=(unbound, partial, retired, first, second, retired_code, test),
            relations=(
                Relation(
                    partial.id,
                    RelationType.REQUIRES_VERIFICATION_OF,
                    first.id,
                ),
                Relation(
                    partial.id,
                    RelationType.REQUIRES_VERIFICATION_OF,
                    second.id,
                ),
                Relation(test.id, RelationType.VERIFIES, first.id),
                Relation(
                    retired.id,
                    RelationType.REQUIRES_VERIFICATION_OF,
                    retired_code.id,
                ),
                Relation(test.id, RelationType.VERIFIES, retired_code.id),
            ),
        )

        views = source_views_from_snapshot(
            snapshot, "sha256:" + "b" * 64
        )
        statuses = {item.criterion_id: item.status for item in views.criteria}

        self.assertEqual("unbound", statuses[unbound.id])
        self.assertEqual("partial", statuses[partial.id])
        self.assertEqual("unknown", statuses[retired.id])


if __name__ == "__main__":
    unittest.main()
