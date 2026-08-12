import copy
import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from graph_runtime.application_evidence import (  # noqa: E402
    application_plan_digest,
    application_plan_projection,
)


class HistoricalApplicationEvidenceTest(unittest.TestCase):
    def transaction(self):
        return {
            "schema_version": 2,
            "transaction_id": "graph-tx-1",
            "scope_ref": "R010/S06",
            "input_deltas": [],
            "canonical_mutations": [],
            "surface_patches": [],
            "attestations": [],
            "apply_results": [],
            "state": "verified",
            "failure_reason": None,
        }

    def test_historical_plan_digest_binds_only_immutable_plan(self):
        transaction = self.transaction()
        original = application_plan_digest(transaction)
        changed = copy.deepcopy(transaction)
        changed["attestations"] = [{"decision": "confirm"}]
        changed["apply_results"] = [{"result": "applied"}]
        changed["state"] = "failed"
        self.assertEqual(original, application_plan_digest(changed))

    def test_historical_plan_projection_has_no_current_authority_fields(self):
        projection = application_plan_projection(self.transaction())
        self.assertEqual({
            "schema_version", "transaction_id", "scope_ref", "input_deltas",
            "canonical_mutations", "surface_patches",
        }, set(projection))
        self.assertNotIn("attestations", projection)
        self.assertNotIn("apply_results", projection)


if __name__ == "__main__":
    unittest.main()
