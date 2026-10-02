#!/usr/bin/env python3
"""Compare declared MCP App entrypoint modes with a captured host trace."""
import argparse
import json
import sys
from pathlib import Path

WORDS = {
    "en": {"mode_mismatch": "Declared fullscreen is not offered by the host", "entrypoint_missing": "Declared entrypoint is not listed by the host", "call_missing": "Entrypoint was listed but no tools/call was observed", "inconclusive": "Capture incomplete", "pass": "No mismatch in the supplied capture", "invalid": "Invalid capture"},
    "fr": {"mode_mismatch": "Le plein écran déclaré n'est pas proposé par l'hôte", "entrypoint_missing": "L'entrée déclarée n'est pas listée par l'hôte", "call_missing": "L'entrée est listée, mais aucun tools/call n'a été observé", "inconclusive": "Capture incomplète", "pass": "Aucun écart dans la capture fournie", "invalid": "Capture invalide"},
    "es": {"mode_mismatch": "El anfitrión no ofrece la pantalla completa declarada", "entrypoint_missing": "El anfitrión no muestra la entrada declarada", "call_missing": "La entrada aparece, pero no se observó tools/call", "inconclusive": "Captura incompleta", "pass": "Sin discrepancias en la captura proporcionada", "invalid": "Captura no válida"},
}
NOTES = {
    "en": "Checks supplied declarations and host observations; it does not execute or diagnose the ChatGPT host.",
    "fr": "Contrôle les déclarations et observations fournies ; ne lance pas et ne diagnostique pas l'hôte ChatGPT.",
    "es": "Comprueba declaraciones y observaciones aportadas; no ejecuta ni diagnostica el anfitrión ChatGPT.",
}


def inspect(record, lang="en"):
    if not isinstance(record, dict):
        raise ValueError("root must be an object")
    declared = record.get("declared_modes")
    offered = record.get("host_modes")
    if not isinstance(declared, list) or not all(isinstance(x, str) for x in declared):
        raise ValueError("declared_modes must be a string array")
    if offered is not None and (not isinstance(offered, list) or not all(isinstance(x, str) for x in offered)):
        raise ValueError("host_modes must be a string array or null")
    if not isinstance(record.get("entrypoint_listed"), bool) or not isinstance(record.get("trace_complete"), bool):
        raise ValueError("entrypoint_listed and trace_complete must be booleans")
    if record.get("call_observed") is not None and not isinstance(record["call_observed"], bool):
        raise ValueError("call_observed must be boolean or null")
    findings = []
    if offered is not None and "fullscreen" in declared and "fullscreen" not in offered:
        findings.append("mode_mismatch")
    if record["trace_complete"] and not record["entrypoint_listed"]:
        findings.append("entrypoint_missing")
    if record["entrypoint_listed"] and record["trace_complete"] and record.get("call_observed") is False:
        findings.append("call_missing")
    inconclusive = offered is None or not record["trace_complete"] or record.get("call_observed") is None
    return {"status": "mismatch" if findings else "inconclusive" if inconclusive else "pass",
            "findings": findings,
            "note": NOTES[lang]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("demo", "check"))
    parser.add_argument("path", nargs="?", type=Path)
    parser.add_argument("--lang", choices=WORDS, default="en")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    path = Path(__file__).parent / "fixtures" / "host-trace.json" if args.command == "demo" else args.path
    if path is None:
        parser.error("check requires a JSON capture path")
    try:
        result = inspect(json.loads(path.read_text(encoding="utf-8")), args.lang)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"{WORDS[args.lang]['invalid']}: {type(error).__name__}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        if result["findings"]:
            for finding in result["findings"]:
                print(WORDS[args.lang][finding])
        else:
            print(WORDS[args.lang][result["status"]])
    return 0 if args.command == "demo" or result["status"] == "pass" else 3 if result["status"] == "inconclusive" else 2


if __name__ == "__main__":
    raise SystemExit(main())
