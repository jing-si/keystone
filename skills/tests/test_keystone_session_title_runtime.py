# keystone: id=key.test.r020.keystone-session-title-runtime kind=output_artifact artifact_kind=test verifies=key.standard.project.std-keystone-063 key.standard.skill.reader.round-session-focus
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest


ROOT = Path(__file__).parents[2]
MODULE_PATH = ROOT / "skills/keystone-reader/scripts/keystone_session_title.py"
SPEC = importlib.util.spec_from_file_location("keystone_session_title", MODULE_PATH)
SESSION_TITLE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SESSION_TITLE)


def state_with_rounds(rounds):
    hierarchy = []
    works = []
    for item in rounds:
        parent = item[0]
        status = item[1]
        children = item[2] if len(item) > 2 else []
        hierarchy.append({
            "round_ref": parent,
            "path": "00_docs/{}/00_key-index.md".format(parent.lower()),
            "status": status,
            "child_rounds": [
                {
                    "round_ref": child_ref,
                    "path": "00_docs/{}/00_key-index.md".format(child_ref.lower()),
                    "status": child_status,
                }
                for child_ref, child_status in children
            ],
        })
        if status == "active":
            works.append({
                "parent_round_ref": parent,
                "round_ref": parent,
                "work_ref": "{}-work".format(parent.lower()),
                "path": "00_docs/{}/work/00_key-index.md".format(parent.lower()),
                "active_step_refs": [parent + "/S01"],
            })
        for child_ref, child_status in children:
            if child_status == "active":
                works.append({
                    "parent_round_ref": parent,
                    "round_ref": child_ref,
                    "work_ref": "{}-work".format(child_ref.lower()),
                    "path": "00_docs/{}/work/00_key-index.md".format(child_ref.lower()),
                    "active_step_refs": [child_ref + "/S02"],
                })
    return {
        "status": "pass",
        "state": {
            "active_rounds": [item[0] for item in rounds if item[1] == "active"],
            "active_works": works,
            "round_hierarchy": hierarchy,
        },
    }


class FakePendingStore:
    def __init__(self):
        self.values = {}

    def load(self, thread_id):
        return self.values.get(thread_id)

    def save(self, thread_id, value):
        self.values[thread_id] = value

    def clear(self, thread_id):
        self.values.pop(thread_id, None)


class KeystoneSessionTitleRuntimeTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        config = self.root / ".codex/config.toml"
        config.parent.mkdir()
        config.write_text(
            '[tui]\nterminal_title = ["activity", "thread-title", "task-progress"]\n',
            encoding="utf-8",
        )
        self.thread_id = "01a04618-38e3-72c1-bc7e-6a49b8e44f28"
        self.payload = {
            "cwd": str(self.root),
            "hook_event_name": "UserPromptSubmit",
            "prompt": "$keystone-reader",
            "session_id": self.thread_id,
        }
        self.pending = FakePendingStore()
        self.queued = []

    def tearDown(self):
        self.temporary.cleanup()

    def run_hook(self, state):
        return SESSION_TITLE.handle_user_prompt_submit(
            self.payload,
            evaluator=lambda _root: state,
            queue_message=lambda thread_id, message, _cwd: self.queued.append(
                (thread_id, message)
            ) or True,
            pending_store=self.pending,
        )

    def test_non_reader_prompt_is_untouched(self):
        self.payload["prompt"] = "버그를 고쳐주세요"
        self.assertEqual({}, self.run_hook(state_with_rounds([("R015", "active")])))
        self.assertEqual([], self.queued)

    def test_bare_reader_lists_one_incomplete_round_without_auto_selecting(self):
        result = self.run_hook(state_with_rounds([("R015", "active")]))

        self.assertEqual("block", result["decision"])
        self.assertFalse(result["suppressOutput"])
        self.assertEqual(
            "\n".join((
                "Keystone ready · 미완료 Round 1개",
                "",
                "╭─ Round 선택 ─────────────────────────",
                "│",
                "│  1. R015 · active · r015 work",
                "│",
                "╰─ 어느 Round에 집중할까요?",
            )),
            result["reason"],
        )
        self.assertEqual([], self.queued)
        self.assertEqual(["R015"], self.pending.load(self.thread_id)["candidates"])

    def test_incomplete_rounds_include_unaccepted_complete_and_exclude_closed_statuses(self):
        result = self.run_hook(state_with_rounds([
            ("R010", "accepted", [("R010-AE", "planned")]),
            ("R015", "active", [("R015-AE", "complete")]),
            ("R018", "planned"),
            ("R020", "cancelled"),
            ("R021", "complete"),
        ]))

        reason = result["reason"]
        self.assertNotIn("- R010 ·", reason)
        self.assertNotIn("1. R010\n", reason)
        self.assertIn("R010-AE", reason)
        self.assertIn("R015", reason)
        self.assertIn("R018", reason)
        self.assertIn("└─ R015-AE · complete / pending · 수용 대기", reason)
        self.assertIn("R021 · complete / pending · 수용 대기", reason)
        self.assertNotIn("R020", reason)

    def test_all_candidates_are_shown_in_round_ascending_order(self):
        rounds = [("R{:03d}".format(number), "planned") for number in range(30, 52)]
        rounds.append(("R015", "active"))

        result = self.run_hook(state_with_rounds(rounds))
        lines = [
            line for line in result["reason"].splitlines()
            if re.match(r"│  \d+\. R", line)
        ]

        expected_refs = ["R015"] + ["R{:03d}".format(number) for number in range(30, 52)]
        self.assertEqual(expected_refs, [re.search(r"R\d+", line).group() for line in lines])
        self.assertIn("미완료 Round 23개", result["reason"])
        self.assertNotIn("외 ", result["reason"])

    def test_all_children_are_shown_beyond_the_former_limit(self):
        child_refs = ["R015-" + chr(letter) for letter in range(ord("A"), ord("Z") + 1)]
        child_refs.extend(["R015-AA", "R015-AB"])
        result = self.run_hook(state_with_rounds([
            ("R015", "active", [(ref, "planned") for ref in reversed(child_refs)]),
            ("R016", "complete"),
        ]))

        lines = result["reason"].splitlines()
        displayed_children = [
            re.search(r"R\d+-[A-Z]+", line).group() for line in lines if "└─" in line
        ]
        self.assertEqual(child_refs, displayed_children)
        self.assertIn("미완료 Round 30개", result["reason"])
        self.assertIn("│  2. R016 · complete / pending · 수용 대기", result["reason"])
        self.assertNotIn("외 ", result["reason"])

    def test_children_are_nested_below_parent_in_excel_suffix_order(self):
        result = self.run_hook(state_with_rounds([
            ("R016", "active", [
                ("R016-AE", "planned"),
                ("R016-B", "planned"),
                ("R016-A", "active"),
            ]),
            ("R010", "planned", [("R010-C", "planned")]),
        ]))

        lines = result["reason"].splitlines()
        parent_10 = next(index for index, line in enumerate(lines) if line.startswith("│  1. R010"))
        child_c = next(index for index, line in enumerate(lines) if line.startswith("│     └─ R010-C "))
        parent_16 = next(index for index, line in enumerate(lines) if line.startswith("│  2. R016"))
        child_a = next(index for index, line in enumerate(lines) if line.startswith("│     └─ R016-A "))
        child_b = next(index for index, line in enumerate(lines) if line.startswith("│     └─ R016-B "))
        child_ae = next(index for index, line in enumerate(lines) if line.startswith("│     └─ R016-AE "))
        self.assertLess(parent_10, child_c)
        self.assertLess(child_c, parent_16)
        self.assertLess(parent_16, child_a)
        self.assertLess(child_a, child_b)
        self.assertLess(child_b, child_ae)
        self.assertEqual("│", lines[parent_16 - 1])
        self.assertTrue(result["reason"].endswith("╰─ 어느 Round에 집중할까요?"))

    def test_no_incomplete_round_allows_reader_without_title_hint(self):
        result = self.run_hook(state_with_rounds([("R019", "accepted")]))

        self.assertEqual({}, result)
        self.assertEqual([], self.queued)

    def test_pending_explicit_assignment_queues_title_hint_without_prefix(self):
        self.run_hook(state_with_rounds([("R015", "active")]))
        self.payload["prompt"] = "R015를 계속 진행해 주세요"

        result = self.run_hook(state_with_rounds([("R015", "active")]))

        self.assertEqual("block", result["decision"])
        message = self.queued[0][1]
        self.assertIn("`R015:{대표문구}`", message)
        self.assertNotIn("프로그래스 R015", message)
        self.assertIn("사용자의 주 언어", message)
        self.assertIn("어떤 작업인지", message)
        self.assertIn("선택 라운드: R015", message)
        self.assertIsNone(self.pending.load(self.thread_id))

    def test_pending_assignment_selects_one_round_from_multiple_candidates(self):
        current_state = state_with_rounds([
            ("R015", "active"),
            ("R018", "planned"),
            ("R022", "active"),
        ])
        self.run_hook(current_state)
        self.payload["prompt"] = "R022를 계속 진행해 주세요"

        result = self.run_hook(current_state)

        self.assertEqual("block", result["decision"])
        self.assertIn("`R022:{대표문구}`", self.queued[0][1])
        self.assertNotIn("`R015:{대표문구}`", self.queued[0][1])

    def test_child_assignment_does_not_collapse_to_parent_prefix(self):
        current_state = state_with_rounds([
            ("R015", "active", [
                ("R015-A", "active"),
                ("R015-AE", "active"),
            ]),
        ])
        self.run_hook(current_state)
        self.payload["prompt"] = "R015-AE를 진행해 주세요"

        result = self.run_hook(current_state)

        self.assertEqual("block", result["decision"])
        message = self.queued[0][1]
        self.assertIn("`R015-AE:{대표문구}`", message)
        self.assertIn("선택 라운드: R015-AE", message)
        self.assertNotIn("`R015:{대표문구}`", message)
        self.assertNotIn("`R015-A:{대표문구}`", message)

    def test_direct_reader_assignment_queues_title_hint(self):
        self.payload["prompt"] = "$keystone-reader R015 작업을 시작해 주세요"

        result = self.run_hook(state_with_rounds([("R015", "active")]))

        self.assertEqual("block", result["decision"])
        self.assertIn("`R015:{대표문구}`", self.queued[0][1])

    def test_pending_new_child_work_order_uses_next_suffix_including_cancelled(self):
        current_state = state_with_rounds([
            ("R015", "active", [
                ("R015-A", "accepted"),
                ("R015-AE", "cancelled"),
            ]),
        ])
        self.run_hook(current_state)
        self.payload["prompt"] = (
            "여기서는 신규 라운드 작업을 하겠습니다. "
            "초기 수집 완료 표기를 수정하며 작업서는 R015 하위로 만들겠습니다."
        )

        result = self.run_hook(current_state)

        self.assertEqual("block", result["decision"])
        message = self.queued[0][1]
        self.assertIn("`R015-AF:{대표문구}`", message)
        self.assertIn("예정 라운드: R015-AF", message)
        self.assertIn("write 직전에", message)
        self.assertIn("초기 수집 완료 표기", message)

    def test_pending_new_child_work_order_rolls_z_to_aa(self):
        current_state = state_with_rounds([
            ("R015", "active", [("R015-Z", "accepted")]),
        ])
        self.run_hook(current_state)
        self.payload["prompt"] = "R015 하위에 새 라운드 작업서를 작성해 주세요"

        result = self.run_hook(current_state)

        self.assertEqual("block", result["decision"])
        self.assertIn("`R015-AA:{대표문구}`", self.queued[0][1])

    def test_direct_new_parent_work_order_uses_next_parent_number(self):
        self.payload["prompt"] = "$keystone-reader 신규 라운드 작업서를 만들겠습니다"

        result = self.run_hook(state_with_rounds([
            ("R015", "accepted"),
            ("R022", "accepted"),
        ]))

        self.assertEqual("block", result["decision"])
        self.assertIn("`R023:{대표문구}`", self.queued[0][1])
        self.assertIn("예정 라운드: R023", self.queued[0][1])

    def test_existing_work_order_revision_uses_exact_round_ref(self):
        self.payload["prompt"] = "$keystone-reader R015-AE 작업서를 수정해 주세요"

        result = self.run_hook(state_with_rounds([
            ("R015", "accepted", [("R015-AE", "accepted")]),
        ]))

        self.assertEqual("block", result["decision"])
        self.assertIn("`R015-AE:{대표문구}`", self.queued[0][1])
        self.assertIn("기존 라운드: R015-AE", self.queued[0][1])

    def test_work_order_revision_review_is_not_authoring_assignment(self):
        current_state = state_with_rounds([
            ("R015", "active", [("R015-AE", "planned")]),
        ])
        self.run_hook(current_state)
        self.payload["prompt"] = "R015-AE 작업서 수정안을 검토해 주세요"

        result = self.run_hook(current_state)

        self.assertEqual("block", result["decision"])
        message = self.queued[0][1]
        self.assertIn("후속 요청: R015-AE 작업서 수정안을 검토해 주세요", message)
        self.assertNotIn("{대표문구}", message)
        self.assertNotIn("예정 라운드", message)

    def test_explicit_new_child_ref_is_preserved_for_work_order_creation(self):
        self.payload["prompt"] = "$keystone-reader R015-AF 작업서를 생성해 주세요"

        result = self.run_hook(state_with_rounds([("R015", "active")]))

        self.assertEqual("block", result["decision"])
        self.assertIn("`R015-AF:{대표문구}`", self.queued[0][1])
        self.assertIn("예정 라운드: R015-AF", self.queued[0][1])

    def test_planned_round_title_uses_round_heading_as_phrase_source(self):
        round_index = self.root / "00_docs/r018/00_key-index.md"
        round_index.parent.mkdir(parents=True)
        round_index.write_text(
            "---\nround_status: planned\n---\n# R018 Keymeta Discovery 작업서 색인\n",
            encoding="utf-8",
        )
        self.payload["prompt"] = "$keystone-reader R018을 시작해 주세요"

        result = self.run_hook(state_with_rounds([("R018", "planned")]))

        self.assertEqual("block", result["decision"])
        self.assertIn("Keymeta Discovery", self.queued[0][1])

    def test_dependency_completion_confirmation_is_not_assignment(self):
        self.payload["prompt"] = "$keystone-reader R016-B 작업이 완료되었습니다. 확인해 주세요."

        result = self.run_hook(state_with_rounds([
            ("R016", "active", [("R016-A", "active"), ("R016-B", "planned")]),
        ]))

        self.assertEqual({}, result)
        self.assertEqual([], self.queued)

    def test_pending_freeform_review_resumes_without_keystone_title_hint(self):
        self.run_hook(state_with_rounds([("R015", "active")]))
        self.payload["prompt"] = "세션 제목 자동화 문제를 조사해 주세요"

        result = self.run_hook(state_with_rounds([("R015", "active")]))

        self.assertEqual("block", result["decision"])
        message = self.queued[0][1]
        self.assertIn(SESSION_TITLE.REENTRY_MARKER, message)
        self.assertIn("세션 제목 자동화 문제를 조사해 주세요", message)
        self.assertNotIn("{대표문구}", message)
        self.assertIsNone(self.pending.load(self.thread_id))

    def test_reentry_marker_allows_queued_prompt_without_recursion(self):
        self.payload["prompt"] = SESSION_TITLE.REENTRY_MARKER + " $keystone-reader R015"
        self.assertEqual({}, self.run_hook(state_with_rounds([("R015", "active")])))
        self.assertEqual([], self.queued)

    def test_queue_failure_allows_original_reader_request(self):
        self.payload["prompt"] = "$keystone-reader R015를 진행해 주세요"
        result = SESSION_TITLE.handle_user_prompt_submit(
            self.payload,
            evaluator=lambda _root: state_with_rounds([("R015", "active")]),
            queue_message=lambda *_args: False,
            pending_store=self.pending,
        )

        self.assertNotIn("decision", result)
        self.assertIn("계속 진행", result["systemMessage"])

    def test_missing_opt_in_does_not_evaluate_or_queue(self):
        (self.root / ".codex/config.toml").unlink()
        result = SESSION_TITLE.handle_user_prompt_submit(
            self.payload,
            evaluator=lambda _root: self.fail("must not evaluate"),
            queue_message=lambda *_args: self.fail("must not queue"),
            pending_store=self.pending,
        )
        self.assertEqual({}, result)

    def test_main_emits_one_valid_json_document(self):
        output = SESSION_TITLE.serialize_hook_output({"decision": "block", "reason": "x"})
        self.assertEqual({"decision": "block", "reason": "x"}, json.loads(output))


if __name__ == "__main__":
    unittest.main()
