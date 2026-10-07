import json
import tempfile
import unittest
from pathlib import Path

from pi_mcp import compare, inspect, jsonc, scan

ROOT = Path(__file__).resolve().parents[1] / "examples" / "pi-mcp"


class PiMcpTests(unittest.TestCase):
    def test_stale_adapter_folder_leaves_native_servers_unread(self):
        report = compare(ROOT / "before", ROOT / "after-stale", "1.0.3")
        self.assertEqual(report["status"], "lost")
        self.assertEqual(report["lost_servers"], ["docs", "tickets"])
        self.assertTrue(report["after"]["stale_adapter_directory"])
        self.assertEqual(report["after"]["adapter_servers"], ["docs", "tickets"])

    def test_native_configuration_is_preserved(self):
        report = compare(ROOT / "before", ROOT / "before", "1.0.3")
        self.assertEqual(report["status"], "no_confirmed_loss")

    def test_scan_current_directory_marks_unread_servers_as_suspected(self):
        result = scan(ROOT / "after-stale", "1.0.3")
        self.assertEqual(result["status"], "suspected_unread")
        self.assertEqual(result["suspected_unread"], ["docs", "tickets"])

    def test_declared_adapter_is_not_called_stale(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "settings.json").write_text(json.dumps({"packages": ["npm:pi-mcp-adapter@3.1.0"]}))
            (root / "mcp-adapter.json").write_text('{"mcpServers":{"docs":{"command":"docs-mcp"}}}')
            (root / "npm/node_modules/pi-mcp-adapter").mkdir(parents=True)
            result = inspect(root, "1.0.3")
            self.assertFalse(result["stale_adapter_directory"])
            self.assertEqual(result["reader"], "adapter_v3_assumed")
            self.assertFalse(result["certain"])

    def test_jsonc_comments_and_trailing_commas_do_not_change_strings(self):
        data = jsonc('''{
          // comment
          "mcpServers": {"x": {"url": "http://localhost/a,}"},},
        }''')
        self.assertEqual(data["mcpServers"]["x"]["url"], "http://localhost/a,}")

    def test_pre_native_pi_is_inconclusive(self):
        report = compare(ROOT / "before", ROOT / "after-stale", "0.98.0")
        self.assertEqual(report["status"], "inconclusive")


if __name__ == "__main__":
    unittest.main()
