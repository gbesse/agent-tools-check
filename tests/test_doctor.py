import json
import unittest
from pathlib import Path

from doctor import compare_sessions, diagnose

EXAMPLES = Path(__file__).parents[1] / "examples"


class DoctorTests(unittest.TestCase):
    def fixture(self, name):
        return json.loads((EXAMPLES / name).read_text())

    def test_missing_namespaced_tools_after_search(self):
        result = diagnose(self.fixture("magpie-namespaced-missing.json"))
        self.assertEqual(result["status"], "missing")
        self.assertEqual(result["missing"], ["collaboration__spawn_agent", "collaboration__wait_agent"])

    def test_deferred_tools_remain_unverified_without_search(self):
        result = diagnose(self.fixture("codex-ready-unverified.json"))
        self.assertEqual(result["status"], "inconclusive")
        self.assertEqual(result["missing"], [])

    def test_visible_tool(self):
        self.assertEqual(diagnose(self.fixture("working-visibility.json"))["status"], "visible")

    def test_search_can_resolve_deferred_tool(self):
        trace = self.fixture("codex-ready-unverified.json")
        trace["agent"]["search"] = {"performed": True, "results": [{"name": "elementor-read-resource"}]}
        result = diagnose(trace)
        self.assertEqual(result["visible"], 1)
        self.assertEqual(result["missing"], ["elementor-get-page-structure"])

    def test_explicit_alias_matches_prefixed_agent_name(self):
        trace = self.fixture("working-visibility.json")
        trace["agent"]["tools"][0]["name"] = "mcp__my_server__find_page"
        trace["agent_names"] = {"find_page": ["mcp__my_server__find_page"]}
        self.assertEqual(diagnose(trace)["status"], "visible")

    def test_namespace_skips_non_function_children(self):
        trace = self.fixture("magpie-namespaced-missing.json")
        trace["origin"]["tools"][0]["tools"].append({"type": "custom", "name": "apply_patch"})
        self.assertEqual(diagnose(trace)["advertised"], 2)

    def test_empty_origin_is_invalid(self):
        with self.assertRaises(ValueError):
            diagnose({"origin": {"tools": []}, "agent": {"tools": []}})

    def test_claimed_search_without_results_is_invalid(self):
        trace = self.fixture("codex-ready-unverified.json")
        trace["agent"]["search"] = {"performed": True}
        with self.assertRaises(ValueError):
            diagnose(trace)

    def test_direct_to_delegated_loss_is_confirmed(self):
        result = compare_sessions(self.fixture("working-visibility.json"), self.fixture("delegated-missing.json"))
        self.assertEqual(result["status"], "lost")
        self.assertEqual(result["visible_only_direct"], ["find_page"])

    def test_deferred_search_prevents_false_loss_claim(self):
        result = compare_sessions(self.fixture("working-visibility.json"), self.fixture("codex-ready-unverified.json"))
        self.assertEqual(result["status"], "inconclusive")
        self.assertEqual(result["visible_only_direct"], [])
