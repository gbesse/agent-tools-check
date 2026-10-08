#!/usr/bin/env python3
"""Find literal MCP authentication values copied into agent configuration files."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path

from pi_mcp import jsonc

TEXT = {
    "en": {
        "title": "MCP authentication copy check",
        "found": "Possible literal authentication values found",
        "clear": "No literal MCP authentication values found in supplied files",
        "entries": "Literal entries",
        "groups": "Values copied to multiple entries",
        "files": "Files examined",
        "note": "Only supplied MCP entries were checked; a literal may be a test value, and no live agent behavior was tested.",
        "invalid": "Invalid or unreadable configuration",
    },
    "fr": {
        "title": "Contrôle des copies d’authentification MCP",
        "found": "Valeurs d’authentification littérales possibles trouvées",
        "clear": "Aucune valeur d’authentification MCP littérale trouvée dans les fichiers fournis",
        "entries": "Entrées littérales",
        "groups": "Valeurs copiées dans plusieurs entrées",
        "files": "Fichiers examinés",
        "note": "Seules les entrées MCP fournies sont contrôlées ; une valeur littérale peut être un test et aucun agent actif n’est vérifié.",
        "invalid": "Configuration invalide ou illisible",
    },
    "es": {
        "title": "Comprobación de copias de autenticación MCP",
        "found": "Posibles valores de autenticación literales encontrados",
        "clear": "No se encontraron valores de autenticación MCP literales en los archivos aportados",
        "entries": "Entradas literales",
        "groups": "Valores copiados en varias entradas",
        "files": "Archivos examinados",
        "note": "Solo se comprueban las entradas MCP aportadas; un valor literal puede ser de prueba y no se verifica ningún agente activo.",
        "invalid": "Configuración no válida o ilegible",
    },
}

REF = re.compile(r"^(?:\$\{[A-Za-z_][A-Za-z0-9_]*\}|\{env:[A-Za-z_][A-Za-z0-9_]*\}|\$[A-Za-z_][A-Za-z0-9_]*)$")
AUTH_KEYS = {"authorization", "x-api-key", "api-key", "x-auth-token", "x-access-token"}


def auth_values(headers):
    if headers is None:
        return [], 0
    if not isinstance(headers, dict):
        raise ValueError("headers_shape")
    literals, references = [], 0
    for key, value in headers.items():
        if not isinstance(key, str) or key.lower() not in AUTH_KEYS:
            continue
        if not isinstance(value, str):
            raise ValueError("header_value")
        candidate = value.strip()
        if key.lower() == "authorization" and candidate.lower().startswith("bearer "):
            candidate = candidate[7:].strip()
        if not candidate:
            continue
        if REF.fullmatch(candidate):
            references += 1
        else:
            literals.append(candidate)
    return literals, references


def entries(kind, document):
    if not isinstance(document, dict):
        raise ValueError("root_shape")
    if kind == "magpie":
        servers = document.get("mcp", [])
        if not isinstance(servers, list):
            raise ValueError("mcp_shape")
        rows = servers
    else:
        key = {"codex": "mcp_servers", "claude": "mcpServers", "opencode": "mcp"}[kind]
        servers = document.get(key, {})
        if not isinstance(servers, dict):
            raise ValueError("mcp_shape")
        rows = list(servers.values())
    for ordinal, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError("server_shape")
        if isinstance(row.get("url"), str) and (kind != "magpie" or row.get("transport") in ("http", "sse")):
            yield ordinal, row


def load(kind, path: Path):
    raw = path.read_text(encoding="utf-8")
    return tomllib.loads(raw) if kind == "codex" else jsonc(raw)


def scan(inputs):
    """Return counts and positional hints only. Authentication values stay in memory."""
    literals = {}
    by_source = {}
    reference_count = 0
    for kind, path in inputs.items():
        document = load(kind, path)
        positions = []
        for ordinal, row in entries(kind, document):
            found, references = auth_values(row.get("http_headers") if kind == "codex" else row.get("headers"))
            reference_count += references
            if kind == "codex":
                if isinstance(row.get("bearer_token_env_var"), str) and row["bearer_token_env_var"]:
                    reference_count += 1
                env_headers = row.get("env_http_headers", {})
                if not isinstance(env_headers, dict):
                    raise ValueError("env_headers_shape")
                reference_count += len(env_headers)
            for value in found:
                # Never include the value or its fingerprint in the returned report.
                literals.setdefault(value, []).append((kind, ordinal))
                positions.append(ordinal)
        by_source[kind] = {"literal_entries": len(positions), "server_positions": sorted(set(positions))}
    groups = [locations for locations in literals.values() if len(locations) >= 2]
    return {
        "status": "literal_found" if literals else "no_literals",
        "files_examined": list(inputs),
        "literal_entries": sum(len(locations) for locations in literals.values()),
        "repeated_value_groups": len(groups),
        "largest_copy_group": max((len(group) for group in groups), default=0),
        "variable_references": reference_count,
        "by_source": by_source,
        "note_code": "supplied_mcp_entries_only",
    }


def render(report, lang):
    words = TEXT[lang]
    return "\n".join([
        words["title"],
        words["found"] if report["status"] == "literal_found" else words["clear"],
        f"{words['entries']}: {report['literal_entries']}",
        f"{words['groups']}: {report['repeated_value_groups']}",
        f"{words['files']}: {len(report['files_examined'])}",
        words["note"],
    ])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("demo", "scan"))
    for kind in ("magpie", "codex", "claude", "opencode"):
        parser.add_argument(f"--{kind}", type=Path)
    parser.add_argument("--lang", choices=TEXT, default="en")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "demo":
        base = Path(__file__).parent / "examples" / "mcp-secret-map"
        inputs = {kind: base / filename for kind, filename in {
            "magpie": "library.json", "codex": "config.toml", "claude": "claude.json",
            "opencode": "opencode.json"}.items()}
    else:
        inputs = {kind: getattr(args, kind) for kind in ("magpie", "codex", "claude", "opencode")
                  if getattr(args, kind) is not None}
        if not inputs:
            print(TEXT[args.lang]["invalid"], file=sys.stderr)
            return 1
    try:
        report = scan(inputs)
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError, tomllib.TOMLDecodeError):
        print(TEXT[args.lang]["invalid"], file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render(report, args.lang))
    if args.command == "demo":
        return 0 if report["literal_entries"] == 4 and report["repeated_value_groups"] == 1 else 1
    return 2 if report["status"] == "literal_found" else 0


if __name__ == "__main__":
    raise SystemExit(main())
