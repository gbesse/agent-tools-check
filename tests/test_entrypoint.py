import unittest

from entrypoint import inspect


class EntrypointTests(unittest.TestCase):
    def test_detects_both_host_contract_gaps(self):
        result = inspect({"declared_modes": ["inline", "fullscreen"], "host_modes": ["inline"],
                          "entrypoint_listed": True, "trace_complete": True, "call_observed": False})
        self.assertEqual(result["findings"], ["mode_mismatch", "call_missing"])

    def test_missing_trace_is_inconclusive(self):
        result = inspect({"declared_modes": ["inline"], "host_modes": None,
                          "entrypoint_listed": True, "trace_complete": False, "call_observed": None})
        self.assertEqual(result["status"], "inconclusive")

    def test_complete_matching_trace_passes(self):
        result = inspect({"declared_modes": ["inline"], "host_modes": ["inline"],
                          "entrypoint_listed": True, "trace_complete": True, "call_observed": True})
        self.assertEqual(result["status"], "pass")

    def test_complete_trace_without_listed_entrypoint_is_mismatch(self):
        result = inspect({"declared_modes": ["inline"], "host_modes": ["inline"],
                          "entrypoint_listed": False, "trace_complete": True, "call_observed": False})
        self.assertEqual(result["findings"], ["entrypoint_missing"])


if __name__ == "__main__":
    unittest.main()
