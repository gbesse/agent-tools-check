#!/usr/bin/env python3
"""Locate the boundary where an advertised tool becomes unavailable to an agent."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LABELS = {
    "en": {
        "visible": "VISIBLE: {visible}/{total} advertised tools found in the agent surface.",
        "missing": "MISSING: {missing}/{total} advertised tools absent from the agent surface.",
        "inconclusive": "INCONCLUSIVE: tool search is available but its result was not captured.",
        "invalid": "Invalid diagnostic: {error}",
        "names": "Tools: {names}",
        "boundary": "Boundary: after tool discovery, before agent exposure.",
        "compare": "Visible in direct session, missing in delegated task: {names}",
        "compare_none": "No confirmed tool loss between these two captured sessions.",
        "compare_uncertain": "The delegated capture is inconclusive because a deferred tool search was not captured.",
    },
    "fr": {
        "visible": "VISIBLES : {visible}/{total} outils annoncés trouvés côté agent.",
        "missing": "ABSENTS : {missing}/{total} outils annoncés absents côté agent.",
        "inconclusive": "INDÉTERMINÉ : la recherche d'outils existe, mais son résultat n'a pas été capturé.",
        "invalid": "Diagnostic invalide : {error}",
        "names": "Outils : {names}",
        "boundary": "Frontière : après la découverte des outils, avant leur exposition à l'agent.",
        "compare": "Visibles en session directe, absents de la tâche déléguée : {names}",
        "compare_none": "Aucune perte d'outil confirmée entre ces deux captures.",
        "compare_uncertain": "La capture déléguée reste indéterminée : le résultat d'une recherche différée manque.",
    },
    "es": {
        "visible": "VISIBLES: {visible}/{total} herramientas anunciadas aparecen ante el agente.",
        "missing": "AUSENTES: {missing}/{total} herramientas anunciadas faltan ante el agente.",
        "inconclusive": "INCONCLUSO: existe búsqueda de herramientas, pero no se capturó su resultado.",
        "invalid": "Diagnóstico no válido: {error}",
        "names": "Herramientas: {names}",
        "boundary": "Límite: después del descubrimiento de herramientas, antes de mostrarlas al agente.",
        "compare": "Visibles en la sesión directa, ausentes en la tarea delegada: {names}",
        "compare_none": "No se confirma pérdida de herramientas entre estas dos capturas.",
        "compare_uncertain": "La captura delegada es inconclusa: falta el resultado de una búsqueda diferida.",
    },
}
NOTES = {
    "en": "This compares captured tool catalogs; it does not prove a call succeeded or identify the client-side root cause.",
    "fr": "Ce contrôle compare des catalogues d'outils capturés ; il ne prouve ni la réussite d'un appel ni la cause côté client.",
    "es": "Esta comprobación compara catálogos de herramientas capturados; no prueba que una llamada funcione ni identifica la causa en el cliente.",
}
ERRORS = {
    "en": {"root": "root must be an object", "stages": "origin and agent must be objects", "required": "origin.tools and agent.tools are required", "agent_tools": "agent.tools must be a captured list or object", "empty": "origin.tools contains no named tools", "search": "agent.search must be an object", "aliases": "agent_names must be an object mapping advertised tools to non-empty name arrays", "path": "scan requires a diagnostic JSON file", "compare_path": "compare requires direct and delegated JSON files"},
    "fr": {"root": "la racine doit être un objet", "stages": "origin et agent doivent être des objets", "required": "origin.tools et agent.tools sont requis", "agent_tools": "agent.tools doit être une liste ou un objet capturé", "empty": "origin.tools ne contient aucun outil nommé", "search": "agent.search doit être un objet", "aliases": "agent_names doit associer des outils annoncés à des listes non vides de noms", "path": "scan exige un fichier JSON de diagnostic", "compare_path": "compare exige les fichiers JSON direct et délégué"},
    "es": {"root": "la raíz debe ser un objeto", "stages": "origin y agent deben ser objetos", "required": "se requieren origin.tools y agent.tools", "agent_tools": "agent.tools debe ser una lista u objeto capturado", "empty": "origin.tools no contiene herramientas con nombre", "search": "agent.search debe ser un objeto", "aliases": "agent_names debe asociar herramientas anunciadas con listas no vacías de nombres", "path": "scan requiere un archivo JSON de diagnóstico", "compare_path": "compare requiere los archivos JSON directo y delegado"},
}


def tool_names(value):
    """Read names from a tools/list response, Responses tools, or a name array."""
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return set().union(*(tool_names(item) for item in value)) if value else set()
    if not isinstance(value, dict):
        return set()
    if "result" in value:
        return tool_names(value["result"])
    if value.get("type") == "namespace":
        namespace = value.get("name")
        if not isinstance(namespace, str) or not namespace:
            return set()
        return {
            f"{namespace}__{name}"
            for child in value.get("tools", [])
            if isinstance(child, dict) and child.get("type") == "function"
            for name in tool_names(child)
        }
    if "tools" in value and "name" not in value:
        return tool_names(value["tools"])
    name = value.get("name")
    return {name} if isinstance(name, str) and name else set()


def diagnose(document, lang="en"):
    if not isinstance(document, dict):
        raise ValueError(ERRORS[lang]["root"])
    origin = document.get("origin")
    agent = document.get("agent")
    if not isinstance(origin, dict) or not isinstance(agent, dict):
        raise ValueError(ERRORS[lang]["stages"])
    if "tools" not in origin or "tools" not in agent:
        raise ValueError(ERRORS[lang]["required"])
    if not isinstance(agent["tools"], (list, dict)):
        raise ValueError(ERRORS[lang]["agent_tools"])
    advertised = tool_names(origin["tools"])
    if not advertised:
        raise ValueError(ERRORS[lang]["empty"])
    direct = tool_names(agent["tools"])
    search = agent.get("search")
    if search is not None and not isinstance(search, dict):
        raise ValueError(ERRORS[lang]["search"])
    if search and search.get("performed") is True and not isinstance(search.get("results"), (list, dict)):
        raise ValueError(ERRORS[lang]["search"])
    searched = tool_names(search.get("results", [])) if search and search.get("performed") is True else set()
    observed = direct | searched
    aliases = document.get("agent_names", {})
    if not isinstance(aliases, dict):
        raise ValueError(ERRORS[lang]["aliases"])
    for key, values in aliases.items():
        if key not in advertised or not isinstance(values, list) or not all(isinstance(v, str) and v for v in values):
            raise ValueError(ERRORS[lang]["aliases"])
    visible = sorted(name for name in advertised if ({name} | set(aliases.get(name, []))) & observed)
    absent = sorted(advertised - set(visible))
    search_pending = "tool_search" in direct and not (search and search.get("performed") is True)
    status = "inconclusive" if absent and search_pending else "missing" if absent else "visible"
    return {
        "status": status,
        "boundary": "after_origin_discovery" if status == "missing" else None,
        "advertised": len(advertised),
        "visible": len(visible),
        "visible_names": visible,
        "missing": absent if status == "missing" else [],
        "unverified": absent if status == "inconclusive" else [],
        "search_performed": bool(search and search.get("performed") is True),
        "note": NOTES[lang],
    }


def compare_sessions(direct_document, delegated_document, lang="en"):
    """Compare captured host surfaces; never infer why a host omitted a tool."""
    direct = diagnose(direct_document, lang)
    delegated = diagnose(delegated_document, lang)
    lost = sorted(set(direct["visible_names"]) - set(delegated["visible_names"]))
    uncertain = delegated["status"] == "inconclusive"
    return {
        "status": "inconclusive" if uncertain else "lost" if lost else "no_confirmed_loss",
        "visible_only_direct": [] if uncertain else lost,
        "unverified": lost if uncertain else [],
        "direct": direct,
        "delegated": delegated,
        "note": NOTES[lang],
    }


def render(result, lang):
    labels = LABELS[lang]
    status = result["status"]
    if status == "visible":
        lines = [labels[status].format(visible=result["visible"], total=result["advertised"])]
    elif status == "missing":
        lines = [labels[status].format(missing=len(result["missing"]), total=result["advertised"])]
    else:
        lines = [labels[status]]
    names = result["missing"] or result["unverified"]
    if names:
        lines.append(labels["names"].format(names=", ".join(names[:10])))
    if status == "missing":
        lines.append(labels["boundary"])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("demo", "scan", "compare"))
    parser.add_argument("path", nargs="?", type=Path)
    parser.add_argument("second_path", nargs="?", type=Path)
    parser.add_argument("--lang", choices=LABELS, default="en")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "scan" and args.path is None:
        parser.error(ERRORS[args.lang]["path"])
    if args.command == "compare":
        if args.path is None or args.second_path is None:
            parser.error(ERRORS[args.lang]["compare_path"])
        try:
            result = compare_sessions(json.loads(args.path.read_text(encoding="utf-8")),
                                      json.loads(args.second_path.read_text(encoding="utf-8")), args.lang)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            print(LABELS[args.lang]["invalid"].format(error=error), file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        elif result["status"] == "inconclusive":
            print(LABELS[args.lang]["compare_uncertain"])
        elif result["status"] == "lost":
            print(LABELS[args.lang]["compare"].format(names=", ".join(result["visible_only_direct"])))
        else:
            print(LABELS[args.lang]["compare_none"])
        return {"lost": 2, "inconclusive": 3, "no_confirmed_loss": 0}[result["status"]]
    paths = ([Path(__file__).parent / "examples" / name for name in
              ("magpie-namespaced-missing.json", "codex-ready-unverified.json", "working-visibility.json")]
             if args.command == "demo" else [args.path])
    final_status = 0
    for path in paths:
        try:
            result = diagnose(json.loads(path.read_text(encoding="utf-8")), args.lang)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            print(LABELS[args.lang]["invalid"].format(error=error), file=sys.stderr)
            return 1
        if args.command == "demo" and not args.json:
            print(f"{path.stem}:")
        print(json.dumps(result, ensure_ascii=False) if args.json else render(result, args.lang))
        final_status = max(final_status, {"visible": 0, "inconclusive": 3, "missing": 2}[result["status"]])
    return 0 if args.command == "demo" else final_status


if __name__ == "__main__":
    raise SystemExit(main())
