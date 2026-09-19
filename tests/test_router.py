import unittest

from dub.router import route, work_order


class RouterTests(unittest.TestCase):
    def test_campaign_prefers_workflows_and_review_prioritizes_attack(self):
        candidates = [
            {"provider": "a", "capabilities": []},
            {"provider": "b", "capabilities": ["workflows", "effort"]},
        ]
        result = route(candidates, "test", mode="campaign")
        self.assertEqual(result[0]["provider"], "b")
        self.assertEqual(result[0]["role"], "architecture")
        self.assertEqual(route(candidates, "test", task_class="review")[0]["role"], "adversarial")

    def test_deterministic_distinct_roles_and_task_context(self):
        candidates = [{"provider": key} for key in ("a", "b", "c", "d", "e")]
        first = route(candidates, "goal", task_class="security")
        self.assertEqual(first, route(list(reversed(candidates)), "goal", task_class="security"))
        self.assertEqual(len({item["role"] for item in first}), 5)
        self.assertIn("security", work_order("goal", first[0]))
        self.assertIn("Analyze only", work_order("goal", first[0]))

    def test_empty(self):
        self.assertEqual(route([], "goal"), [])
