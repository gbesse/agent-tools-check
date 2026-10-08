import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mcp_secret_map import auth_values, scan

BASE = Path(__file__).resolve().parents[1] / "examples" / "mcp-secret-map"
INPUTS = {"magpie": BASE / "library.json", "codex": BASE / "config.toml",
          "claude": BASE / "claude.json", "opencode": BASE / "opencode.json"}


class SecretMapTests(unittest.TestCase):
    def test_four_copies_reported_without_values(self):
        report = scan(INPUTS)
        self.assertEqual(report["literal_entries"], 4)
        self.assertEqual(report["repeated_value_groups"], 1)
        self.assertEqual(report["largest_copy_group"], 4)
        self.assertNotIn("fixture-value-not-a-token", json.dumps(report))
        self.assertNotIn("example.test", json.dumps(report))

    def test_variable_references_are_not_literal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "claude.json").write_text('{"mcpServers":{"x":{"url":"https://example.test/mcp","headers":{"Authorization":"Bearer ${MCP_TOKEN}"}}}}')
            (root / "opencode.json").write_text('{"mcp":{"x":{"url":"https://example.test/mcp","headers":{"Authorization":"Bearer {env:MCP_TOKEN}"}}}}')
            (root / "config.toml").write_text('[mcp_servers.x]\nurl="https://example.test/mcp"\nbearer_token_env_var="MCP_TOKEN"\n')
            report = scan({"claude": root / "claude.json", "opencode": root / "opencode.json",
                           "codex": root / "config.toml"})
            self.assertEqual(report["status"], "no_literals")
            self.assertEqual(report["variable_references"], 3)

    def test_only_mcp_auth_headers_count(self):
        values, refs = auth_values({"X-Trace": "Bearer test", "Authorization": "Bearer ${TOKEN}"})
        self.assertEqual(values, [])
        self.assertEqual(refs, 1)

    def test_bad_config_does_not_echo_value_in_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "claude.json").write_text('{"mcpServers":{"x":{"url":"https://example.test/mcp","headers":"Bearer private-value"}}}')
            with self.assertRaises(ValueError):
                scan({"claude": root / "claude.json"})
            result = subprocess.run([sys.executable, str(Path(__file__).resolve().parents[1] / "mcp_secret_map.py"),
                                     "scan", "--claude", str(root / "claude.json"), "--lang", "fr"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertNotIn("private-value", result.stdout + result.stderr)

    def test_json_cli_does_not_echo_literal_or_url(self):
        result = subprocess.run([sys.executable, str(Path(__file__).resolve().parents[1] / "mcp_secret_map.py"),
                                 "scan", "--magpie", str(INPUTS["magpie"]), "--json"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("fixture-value-not-a-token", result.stdout + result.stderr)
        self.assertNotIn("example.test", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
