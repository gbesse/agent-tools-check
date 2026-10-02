# Agent Tools Check

**Votre serveur MCP est connecté, mais votre agent ne voit pas ses outils ?** Comparez les catalogues pour trouver la première frontière où ils disparaissent. Une seconde commande vérifie si une gateway conserve les appels et messages de tâche.

Français · [English](README.md) · [Español](README.es.md)

## Projets voisins

- [Codex #49758](https://github.com/openai/codex/issues/49758) décrit un serveur MCP READY dont l'agent ne voit pas les outils. Le nouveau diagnostic distingue une absence confirmée d'une recherche différée non testée.
- [Codex #50201](https://github.com/openai/codex/issues/50201) rapporte un serveur STDIO visible directement mais absent dans une tâche locale déléguée ; `compare` contrôle deux captures fournies de cette frontière.
- [MCP Extensions #28](https://github.com/openai/mcp-extensions/issues/28) et [#29](https://github.com/openai/mcp-extensions/issues/29) rapportent un écart de mode plein écran et une entrée visible sans `tools/call` observé. `entrypoint.py` contrôle des traces fournies, sans intégration à l'hôte en direct.
- [Magpie #404](https://github.com/yetone/magpie/issues/404) décrit des fonctions `namespace` supprimées avant Grok ; notre exemple reconstruit contrôle cette frontière. [Magpie #130](https://github.com/yetone/magpie/issues/130) rapporte un problème voisin.
- [LLMConform](https://github.com/aitk-org/LLMConform) couvre largement les gateways. Ce dépôt compare une petite capture des outils. Ces liens n'impliquent ni intégration ni affiliation.

## Voir le problème en 10 secondes

```sh
python3 doctor.py demo --lang fr
python3 check.py demo --lang fr
```

La première démo montre un outil absent, une recherche différée indéterminée et un outil visible. La seconde montre trois contrôles qui échouent sur une gateway fictive, puis réussissent après correction. Aucun modèle, compte, clé API ni réseau n'est nécessaire. Les fixtures sont **synthétiques ou reconstruites** : ce n'est pas un test réel de Codex, Magpie ou d'une autre gateway.

## Comparer une session directe et une tâche déléguée

```sh
python3 doctor.py compare examples/working-visibility.json examples/delegated-missing.json --lang fr
```

L'exemple synthétique signale `find_page` comme visible seulement en session directe. Codes de sortie : `2` perte confirmée, `3` recherche différée non capturée, `0` aucune perte confirmée, `1` entrée invalide. La commande lit deux catalogues capturés localement. Elle ne collecte pas une tâche Codex réelle et n'identifie pas le défaut de l'hôte. [Codex #50201](https://github.com/openai/codex/issues/50201) est le rapport voisin.

## Vérifier un échange capturé

```sh
python3 check.py check examples/working-trace.json --lang fr
python3 check.py check examples/broken-trace.json --json
```

Codes de sortie : `0` conservé ; `2` capacité perdue ; `1` trace invalide. Le JSON doit contenir `client_request`, `upstream_request`, `upstream_response` et `client_response`, les quatre surfaces à capturer lors du diagnostic de votre gateway. Voir le [format des traces](docs/trace-format.md). Le vérificateur accepte un outil transmis comme `namespace__name`, exige que l'appel retourné porte son espace de noms d'origine, contrôle `encrypted_function_args: []` pour les arguments en clair et vérifie que le texte d'`agent_message` atteint la requête amont.

**Limite actuelle :** pas de capture automatique ni d'intégration Magpie. Cet outil hors ligne contrôle vos traces ; la réussite de la démo synthétique ne prouve rien sur une gateway réelle. Le contrat Responses couvert est étroit.

## Contrôler la trace d'entrée d'un plugin

```sh
python3 entrypoint.py demo --lang fr
python3 entrypoint.py check fixtures/host-trace.json --lang fr
```

La capture porte `declared_modes`, `host_modes`, `entrypoint_listed`, `trace_complete` et `call_observed`. Le contrôle distingue un écart confirmé d'une preuve incomplète. La fixture est synthétique. Il n'ouvre pas de plugin ChatGPT et n'identifie pas la cause côté hôte.

## Diagnostiquer un outil connecté mais invisible

```sh
python3 doctor.py demo --lang fr
python3 doctor.py scan examples/magpie-namespaced-missing.json --lang fr --json
```

`doctor.py` compare la réponse MCP `tools/list` ou le catalogue d'une gateway aux outils visibles par l'agent. Il lit les réponses brutes `tools/list` et les outils Responses `namespace` ; utilisez `agent_names` pour déclarer explicitement un nom renommé ou préfixé. Si `tool_search` existe sans résultat capturé, le diagnostic est **indéterminé** : il ne conclut pas à une absence. Codes : `0` visible, `2` absent, `3` indéterminé, `1` entrée invalide. Voir le [format et le guide d'expurgation](docs/doctor-format.md).

Les exemples reconstruisent seulement les noms et états décrits dans les issues liées : **ce ne sont ni des captures de session ni des intégrations réelles Codex/Magpie**. Le diagnostic localise une absence dans les catalogues fournis ; il ne trouve pas la cause côté client et ne prouve pas qu'un appel fonctionne. [Magpie #141](https://github.com/yetone/magpie/issues/141) reste le cas distinct de message de tâche couvert par `check.py`.

## Tester

```sh
python3 -m unittest discover -s tests -v
```

Python 3.11+, aucune dépendance. MIT. Outil alpha de diagnostic pour mainteneurs de gateways.
