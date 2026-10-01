# Tool visibility capture / Capture de visibilité / Captura de visibilidad

## English

`doctor.py scan file.json` accepts one local JSON object. `origin.tools` is either a raw JSON-RPC `tools/list` response (`{"result":{"tools":[{"name":"find_page"}]}}`) or the client's Responses `tools` array, including `namespace` functions. `agent.tools` is the complete tool array captured at the model or agent boundary. If that array includes `tool_search`, capture an actual search and add `agent.search: {"performed": true, "results": [...]}`. Without it, absence remains inconclusive. Optional `agent_names` maps each original tool name to explicit agent-visible aliases, for example `{"find_page":["mcp__my_server__find_page"]}`. The checker does not guess prefix rules.

Capture only tool names and types. Remove prompts, arguments, URLs, authentication headers, API keys, session IDs and user data before sharing a diagnostic. The examples are reconstructed from [Codex #49758](https://github.com/openai/codex/issues/49758) and [Magpie #404](https://github.com/yetone/magpie/issues/404), not exported sessions. A visible tool is not necessarily callable; use `check.py` or the host's own invocation test for that next step.

## Français

`doctor.py scan file.json` lit un objet JSON local. `origin.tools` contient soit une réponse JSON-RPC brute à `tools/list` (`{"result":{"tools":[{"name":"find_page"}]}}`), soit la liste Responses `tools` du client, y compris les fonctions `namespace`. `agent.tools` est la liste complète des outils capturée à la frontière de l'agent ou du modèle. Si elle contient `tool_search`, effectuez une recherche et ajoutez `agent.search: {"performed": true, "results": [...]}`. Sans son résultat, l'absence reste indéterminée. `agent_names` peut déclarer les noms visibles alternatifs, par exemple `{"find_page":["mcp__my_server__find_page"]}`. Le programme ne devine pas les préfixes.

Ne capturez que les noms et types d'outils. Supprimez prompts, arguments, URL, en-têtes d'authentification, clés API, identifiants de session et données utilisateur avant de partager le diagnostic. Les exemples sont reconstruits d'après [Codex #49758](https://github.com/openai/codex/issues/49758) et [Magpie #404](https://github.com/yetone/magpie/issues/404), sans export de session. Un outil visible n'est pas forcément appelable ; utilisez ensuite `check.py` ou le test d'appel de l'hôte.

## Español

`doctor.py scan file.json` lee un objeto JSON local. `origin.tools` contiene una respuesta JSON-RPC bruta de `tools/list` (`{"result":{"tools":[{"name":"find_page"}]}}`) o la lista Responses `tools` del cliente, incluidas las funciones `namespace`. `agent.tools` es la lista completa capturada en el límite del agente o modelo. Si incluye `tool_search`, haga una búsqueda y añada `agent.search: {"performed": true, "results": [...]}`. Sin ese resultado, la ausencia sigue sin determinarse. `agent_names` permite declarar alias visibles, por ejemplo `{"find_page":["mcp__my_server__find_page"]}`. El programa no adivina prefijos.

Capture solo nombres y tipos de herramientas. Elimine prompts, argumentos, URL, cabeceras de autenticación, claves API, identificadores de sesión y datos del usuario antes de compartir un diagnóstico. Los ejemplos se reconstruyeron a partir de [Codex #49758](https://github.com/openai/codex/issues/49758) y [Magpie #404](https://github.com/yetone/magpie/issues/404); no son exportaciones de sesión. Que una herramienta sea visible no significa que se pueda invocar; compruébelo después con `check.py` o una prueba del propio cliente.
