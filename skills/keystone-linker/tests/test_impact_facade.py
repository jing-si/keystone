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


if __name__ == "__main__":
    unittest.main()
