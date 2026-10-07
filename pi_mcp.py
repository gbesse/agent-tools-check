#!/usr/bin/env python3
"""Compare Pi MCP configuration before and after a router synchronization."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TEXT = {
    "en": {"title": "Pi MCP configuration check", "lost": "Servers no longer on Pi's expected path",
           "suspect": "Servers may be stranded in a file native Pi does not read",
           "safe": "No confirmed server loss", "unknown": "Pi MCP reader cannot be determined",
           "stale": "Installed adapter directory is not declared as loaded",
           "error": "Invalid capture"},
    "fr": {"title": "Contrôle de configuration MCP Pi", "lost": "Serveurs absents du chemin attendu par Pi",
           "suspect": "Serveurs peut-être bloqués dans un fichier non lu par Pi natif",
           "safe": "Aucune perte de serveur confirmée", "unknown": "Lecteur MCP Pi indéterminé",
           "stale": "Répertoire d’adaptateur présent mais non déclaré comme chargé",
           "error": "Capture invalide"},
    "es": {"title": "Comprobación de configuración MCP Pi", "lost": "Servidores ausentes de la ruta esperada por Pi",
           "suspect": "Servidores posiblemente en un archivo que Pi nativo no lee",
           "safe": "No se confirma pérdida de servidores", "unknown": "No se puede determinar el lector MCP de Pi",
           "stale": "Directorio del adaptador presente pero no declarado como cargado",
           "error": "Captura no válida"},
}


def jsonc(text: str):
    """Strip JSONC comments and trailing commas without touching quoted strings."""
    output = []
    index = 0
    quoted = False
    escaped = False
    while index < len(text):
        char = text[index]
        if quoted:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            index += 1
        elif char == '"':
            quoted = True
            output.append(char)
            index += 1
        elif text.startswith("//", index):
            end = text.find("\n", index)
            output.append(" ")
            index = len(text) if end < 0 else end
        elif text.startswith("/*", index):
            end = text.find("*/", index + 2)
            if end < 0:
                raise ValueError("unterminated JSONC comment")
            output.append(" ")
            index = end + 2
        else:
            output.append(char)
            index += 1
    stripped = "".join(output)
    result = []
    quoted = escaped = False
    for index, char in enumerate(stripped):
        if quoted:
            result.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
            result.append(char)
        elif char == "," and stripped[index + 1:].lstrip().startswith(("}", "]")):
            continue
        else:
            result.append(char)
    return json.loads("".join(result))


def read_object(path: Path):
    if not path.exists():
        return {}
    value = jsonc(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must be a JSON object")
    return value


def server_names(path: Path):
    data = read_object(path)
    names = set()
    for key in ("mcpServers", "mcp-servers"):
        value = data.get(key, {})
        if not isinstance(value, dict):
            raise ValueError(f"{path.name}: {key} must be an object")
        names.update(value)
    return names


def declared_adapter(settings: dict, agent_dir: Path):
    packages = settings.get("packages", [])
    extensions = settings.get("extensions", [])
    if not isinstance(packages, list) or not isinstance(extensions, list):
        raise ValueError("settings packages/extensions must be arrays")
    specs = [p.get("source", "") if isinstance(p, dict) else p for p in packages]
    specs += extensions
    if not all(isinstance(item, str) for item in specs):
        raise ValueError("settings packages/extensions contain an invalid entry")
    loaded = any("pi-mcp-adapter" in item and not item.startswith("-") for item in specs)
    loaded = loaded or (agent_dir / "extensions" / "pi-mcp-adapter").is_dir()
    stale = (agent_dir / "npm" / "node_modules" / "pi-mcp-adapter").is_dir() and not loaded
    native_disabled = "-builtin:mcp" in extensions
    return loaded, stale, native_disabled


def inspect(agent_dir: Path, pi_version: str):
    agent_dir = Path(agent_dir)
    if not agent_dir.is_dir():
        raise ValueError("agent directory does not exist")
    match = re.match(r"^(\d+)\.(\d+)(?:\.\d+)?(?:[-+].*)?$", pi_version)
    if not match:
        raise ValueError("pi version must look like 1.0.3")
    native_available = tuple(map(int, match.groups())) >= (0, 99)
    settings = read_object(agent_dir / "settings.json")
    loaded, stale, native_disabled = declared_adapter(settings, agent_dir)
    native = server_names(agent_dir / "mcp.json")
    adapter = server_names(agent_dir / "mcp-adapter.json")
    if loaded:
        reader = "adapter_v3_assumed"
        effective = adapter
        certain = False  # An older adapter may still read mcp.json.
    elif native_available and not native_disabled:
        reader = "native"
        effective = native
        certain = True
    else:
        reader = "unknown"
        effective = set()
        certain = False
    return {"reader": reader, "certain": certain,
            "expected_servers": sorted(effective), "native_servers": sorted(native),
            "adapter_servers": sorted(adapter), "stale_adapter_directory": stale,
            "native_disabled": native_disabled}


def compare(before_dir: Path, after_dir: Path, pi_version: str):
    before = inspect(before_dir, pi_version)
    after = inspect(after_dir, pi_version)
    if not before["certain"] or not after["certain"]:
        status, lost = "inconclusive", []
    else:
        lost = sorted(set(before["expected_servers"]) - set(after["expected_servers"]))
        status = "lost" if lost else "no_confirmed_loss"
    return {"status": status, "lost_servers": lost, "before": before, "after": after,
            "note": "Configuration paths only; actual tools/list visibility is not observed."}


def scan(agent_dir: Path, pi_version: str):
    current = inspect(agent_dir, pi_version)
    suspects = sorted(set(current["adapter_servers"]) - set(current["native_servers"]))
    if not current["certain"]:
        status, suspects = "inconclusive", []
    else:
        status = "suspected_unread" if suspects else "no_confirmed_loss"
    return {"status": status, "suspected_unread": suspects, "current": current,
            "note": "Suspected from file placement only; no before snapshot or tools/list capture."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("pi-demo", "pi-compare", "pi-scan"))
    parser.add_argument("before", nargs="?", type=Path)
    parser.add_argument("after", nargs="?", type=Path)
    parser.add_argument("--pi-version", default="1.0.3")
    parser.add_argument("--lang", choices=TEXT, default="en")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "pi-demo":
        base = Path(__file__).parent / "examples" / "pi-mcp"
        before, after = base / "before", base / "after-stale"
    elif args.command == "pi-scan":
        if args.before is None:
            parser.error("pi-scan requires AGENT_DIR")
    else:
        if args.before is None or args.after is None:
            parser.error("pi-compare requires BEFORE_DIR and AFTER_DIR")
        before, after = args.before, args.after
    try:
        report = scan(args.before, args.pi_version) if args.command == "pi-scan" else compare(before, after, args.pi_version)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        print(f"{TEXT[args.lang]['error']}: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        words = TEXT[args.lang]
        print(words["title"])
        print(words[{"lost": "lost", "suspected_unread": "suspect",
                     "no_confirmed_loss": "safe", "inconclusive": "unknown"}[report["status"]]])
        names = report.get("lost_servers", report.get("suspected_unread", []))
        if names:
            print(", ".join(names))
        current = report.get("after", report.get("current", {}))
        if current.get("stale_adapter_directory"):
            print(words["stale"])
    if args.command == "pi-demo":
        return 0 if report["status"] == "lost" and report["after"]["stale_adapter_directory"] else 1
    return {"lost": 2, "suspected_unread": 2, "inconclusive": 3,
            "no_confirmed_loss": 0}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
