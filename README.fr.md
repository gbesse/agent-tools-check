# Agent Tools Check

## Nouveau : contrôle de longueur des noms d’outils MCP

**« Mon serveur MCP se connecte, mais l’agent refuse un nom d’outil trop long. »** `python3 tool_name_budget.py demo --lang fr` montre un nom synthétique de 71 caractères dépassant la limite de 64. Vérifiez une réponse `tools/list` sauvegardée ou un tableau `tools` avec `python3 tool_name_budget.py check --catalog tools.json --limit 64 --lang fr`. Le rapport montre les noms, longueurs en caractères et octets UTF-8, et positions. Il ne renomme jamais les outils ; les alias doivent être appliqués de façon cohérente par la passerelle et le client. Relisez les catalogues avant de partager leurs noms.

**Projets voisins :** [Magpie #1393](https://github.com/yetone/magpie/issues/1393) décrit le rejet d’un long nom MCP par Kiro et des alias bidirectionnels ; [Magpie](https://github.com/yetone/magpie) est un routeur de configuration voisin. Ce contrôle hors ligne est indépendant, sans intégration ni affiliation avec Magpie ou Kiro.

## Nouveau : retrouver les tokens MCP copiés dans les configurations d’agents

`python3 mcp_secret_map.py demo --lang fr` montre **une valeur fictive** copiée dans la bibliothèque Magpie et trois configurations d’agents. La démo réussie sort avec le code 0. Examinez les fichiers que vous contrôlez sans les modifier :

```sh
python3 mcp_secret_map.py scan --magpie library.json --codex config.toml --claude claude.json --opencode opencode.json --lang fr
```

Le contrôle lit le tableau `mcp` de Magpie, le TOML `mcp_servers` de Codex, `mcpServers` de Claude et `mcp` d’OpenCode. Il examine seulement les en-têtes d’authentification MCP distants. Le rapport donne des comptes et positions de serveurs ; **ni le texte ni le JSON ne contiennent de valeur, d’URL ou d’empreinte**. Codes de sortie : 0 aucune valeur littérale dans les entrées MCP fournies, 2 valeur littérale possible, 1 entrée invalide. Une valeur peut être fictive ; un résultat vide ne vérifie ni les autres fichiers ni l’agent actif. Les références d’environnement comme `bearer_token_env_var` de Codex, `${VAR}` de Claude et `{env:VAR}` d’OpenCode sont reconnues mais non réécrites ; leur prise en charge par Magpie dépend de sa version.

**Projets voisins :** [Magpie #1250](https://github.com/yetone/magpie/issues/1250) rapporte un token recopié dans les réglages générés et demande des variables d’environnement. [cc-switch](https://github.com/farion1231/cc-switch) est cité dans cette demande comme gestionnaire voisin. Ce contrôle est indépendant, sans intégration ni affiliation avec ces projets.

## Nouveau : retrouver les serveurs MCP égarés après une synchronisation Pi

`python3 pi_mcp.py pi-demo --lang fr` montre deux serveurs déplacés du `mcp.json` natif de Pi vers un fichier d’adaptateur que la configuration active ne lit pas. La démo réussie sort avec le code 0. Comparez des **copies** avant et après synchronisation :

```sh
python3 pi_mcp.py pi-compare AVANT APRES --pi-version 1.0.3 --lang fr
```

Si vous n’avez que le dossier actuel, lancez `python3 pi_mcp.py pi-scan DOSSIER_AGENT --pi-version 1.0.3 --lang fr`. Le code 2 indique alors un serveur **supposé** illisible d’après son emplacement ; une capture avant synchronisation est nécessaire pour confirmer une perte.

Chaque dossier contient les fichiers disponibles `settings.json`, `mcp.json`, `mcp-adapter.json` et, le cas échéant, `npm/node_modules/pi-mcp-adapter/`. Le contrôle lit JSON ou JSONC, affiche seulement les **noms** des serveurs et ne modifie ni n’affiche commandes, URL, en-têtes ou secrets. Codes de sortie : 0 aucune perte confirmée, 2 serveurs absents du chemin natif attendu, 3 lecteur indéterminé, 1 capture invalide. Pour Pi 0.99+, il suppose le MCP natif sauf si l’adaptateur est déclaré dans les réglages ou présent sous `extensions/` ; un ancien répertoire npm seul ne prouve pas son chargement. Un adaptateur chargé ou une ancienne version restent indéterminés car les versions d’adaptateur diffèrent. Ce contrôle porte sur les fichiers, pas sur la visibilité réelle des outils ; utilisez `doctor.py compare` avec des catalogues capturés pour cette autre frontière.

**Projets voisins :** [Magpie #1097](https://github.com/yetone/magpie/issues/1097) décrit cette migration de configuration et une détection d’adaptateur périmé confirmée par le mainteneur ; [le MCP natif de Pi](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/mcp.md) fournit le lecteur. Cet outil indépendant ne modifie aucun des deux projets.

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

## Comparer les captures avec outil renommé

Exécutez `python3 doctor.py compare examples/renamed-direct.json examples/renamed-delegated.json --lang fr`. La capture directe synthétique associe explicitement `find_page` à `spaces__find_page` ; la capture déléguée ne contient aucun des deux noms. Le résultat confirme une perte de visibilité, sans en attribuer la cause à l’hôte.

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
