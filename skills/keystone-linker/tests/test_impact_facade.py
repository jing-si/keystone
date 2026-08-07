import unittest

from graph_runtime.impact import (
    ImpactGrade,
    TraversalCandidate,
    candidate_budget_projection,
    changed_seed_candidates,
)
from graph_runtime.model import (
    ArtifactKind,
    GraphSnapshot,
    Locator,
    Node,
    NodeKind,
    Lifecycle,
    Relation,
    RelationType,
)
from graph_runtime.planner import (
    ImpactGrade as PlannerImpactGrade,
    TraversalCandidate as PlannerTraversalCandidate,
    candidate_budget_projection as planner_candidate_budget_projection,
    changed_seed_candidates as planner_changed_seed_candidates,
)


class ImpactFacadeCharacterizationTest(unittest.TestCase):
    def test_planner_reexports_impact_types_and_entry_points(self):
        self.assertIs(ImpactGrade, PlannerImpactGrade)
        self.assertIs(TraversalCandidate, PlannerTraversalCandidate)
        self.assertIs(candidate_budget_projection, planner_candidate_budget_projection)
        self.assertIs(changed_seed_candidates, planner_changed_seed_candidates)

    def test_direct_and_planner_candidate_projection_match(self):
        node = Node(
            "key.code.candidate",
            NodeKind.OUTPUT_ARTIFACT,
            ArtifactKind.CODE,
            Locator("src/candidate.py", symbol="candidate"),
        )
        candidate = TraversalCandidate(
            node, ImpactGrade.STRONG_CANDIDATE, ("key.claim.seed",)
        )

        self.assertEqual(
            candidate_budget_projection((candidate,), 1),
            planner_candidate_budget_projection((candidate,), 1),
        )
        self.assertEqual(
            changed_seed_candidates(GraphSnapshot(nodes=(node,)), (node.id,)),
            planner_changed_seed_candidates(GraphSnapshot(nodes=(node,)), (node.id,)),
        )

    def test_retired_seed_is_excluded_and_deprecated_seed_is_informational(self):
        target = Node(
            "key.code.target",
            NodeKind.OUTPUT_ARTIFACT,
            ArtifactKind.CODE,
            Locator("src/target.py", symbol="target"),
        )
        for lifecycle in (
            Lifecycle.SUPERSEDED,
            Lifecycle.ARCHIVED,
            Lifecycle.REMOVED,
        ):
            with self.subTest(lifecycle=lifecycle):
                seed = Node(
                    "key.cap.seed",
                    NodeKind.CAPABILITY,
                    locator=Locator("docs/seed.md"),
                    lifecycle=lifecycle,
                )
                relation = Relation(target.id, RelationType.PROVIDES, seed.id)
                self.assertEqual(
                    (),
                    changed_seed_candidates(
                        GraphSnapshot((seed, target), (relation,)), (seed.id,)
                    ),
                )

        deprecated = Node(
            "key.cap.seed",
            NodeKind.CAPABILITY,
            locator=Locator("docs/seed.md"),
            lifecycle=Lifecycle.DEPRECATED,
        )
        relation = Relation(target.id, RelationType.PROVIDES, deprecated.id)
        candidates = changed_seed_candidates(
            GraphSnapshot((deprecated, target), (relation,)), (deprecated.id,)
        )
        self.assertEqual(ImpactGrade.INFORMATIONAL, candidates[0].grade)


if __name__ == "__main__":
    unittest.main()
