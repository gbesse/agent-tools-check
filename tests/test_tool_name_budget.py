import unittest

from tool_name_budget import inspect


class BudgetTests(unittest.TestCase):
    def test_boundary_and_namespaced_overflow(self):
        self.assertEqual(inspect([{"name": "x" * 64}])["status"], "pass")
        report = inspect([{"name": "namespace__" + "x" * 60}])
        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["tools"][0]["characters"], 71)


if __name__ == "__main__":
    unittest.main()
