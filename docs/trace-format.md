# Trace format / Format des traces / Formato de trazas

The input is one JSON object with four objects: `client_request`, `upstream_request`, `upstream_response`, `client_response`. Capture or construct them from one gateway exchange. The examples in `examples/` are synthetic. Do not publish captures containing prompts, task content or credentials without reviewing and redacting them.

L'entrée est un objet JSON avec quatre objets : `client_request`, `upstream_request`, `upstream_response`, `client_response`. Capturez ou construisez-les à partir d'un échange. Les exemples de `examples/` sont synthétiques. Relisez et expurgez toute capture contenant des prompts, tâches ou identifiants avant de la publier.

La entrada es un objeto JSON con cuatro objetos: `client_request`, `upstream_request`, `upstream_response`, `client_response`. Captúralos o constrúyelos a partir de un intercambio. Los ejemplos de `examples/` son sintéticos. Revisa y elimina prompts, tareas o credenciales antes de publicar una captura.

- `client_request.tools`: Responses `namespace` tools with nested `function` items.
- `upstream_request.tools`: functions forwarded to the model, conventionally `namespace__name`.
- `client_request.input`: optional `agent_message` with `content[].text`.
- `upstream_request.messages` or `.input`: message containing the task text.
- `upstream_response.output`: `function_call` from the model.
- `client_response.output`: restored `function_call`, `namespace` and empty `encrypted_function_args` when arguments are plain text.

This checker reports protocol-field preservation only. It does not prove the model chose the right tool or that a delegated task completed. / Ce contrôle ne démontre ni le bon choix d'outil ni la réussite de la tâche. / Esta comprobación no demuestra que se eligiera la herramienta correcta ni que la tarea terminara bien.
