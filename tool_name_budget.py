#!/usr/bin/env python3
"""Preflight visible MCP tool names against a target agent's name limit."""

import argparse
import json
import sys
from pathlib import Path

WORDS = {
    "en": {"pass": "All tool names fit the limit", "fail": "Tool names exceed the limit", "invalid": "Invalid tool catalog"},
    "fr": {"pass": "Tous les noms d’outils respectent la limite", "fail": "Des noms d’outils dépassent la limite", "invalid": "Catalogue d’outils invalide"},
    "es": {"pass": "Todos los nombres de herramientas cumplen el límite", "fail": "Algunos nombres de herramientas superan el límite", "invalid": "Catálogo de herramientas no válido"},
}


def inspect(catalog, limit=64):
    tools = catalog.get("tools") if isinstance(catalog, dict) else catalog
    if not isinstance(tools, list) or not isinstance(limit, int) or limit < 1:
        raise ValueError("tools array and positive limit required")
    rows = []
    for index, tool in enumerate(tools):
        name = tool.get("name") if isinstance(tool, dict) else None
        if not isinstance(name, str) or not name:
            raise ValueError("each tool requires a nonempty name")
        rows.append({"index": index, "name": name, "characters": len(name), "utf8_bytes": len(name.encode("utf-8")), "over_limit": len(name) > limit})
    return {"status": "fail" if any(row["over_limit"] for row in rows) else "pass",
            "limit": limit, "tools": rows}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("demo", "check"))
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--limit", type=int, default=64)
    parser.add_argument("--lang", choices=WORDS, default="en")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            catalog = {"tools": [{"name": "cf__" + "long_namespace_" * 4 + "search"}, {"name": "search"}]}
        else:
            if not args.catalog:
                parser.error("check requires --catalog")
            catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        report = inspect(catalog, args.limit)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        print(f"{WORDS[args.lang]['invalid']}: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False) if args.json else WORDS[args.lang][report["status"]])
    return 0 if args.command == "demo" or report["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
