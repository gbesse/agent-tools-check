# Agent Tools Check

**¿Tu servidor MCP está conectado, pero el agente no ve sus herramientas?** Compara los catálogos para encontrar el primer límite donde desaparecen. Un segundo comando comprueba si una gateway conservó las llamadas y los mensajes de tarea.

[Français](README.fr.md) · [English](README.md) · Español

## Proyectos relacionados

- [Codex #49758](https://github.com/openai/codex/issues/49758) describe un servidor MCP READY cuyas herramientas no ve el agente. El nuevo diagnóstico distingue la ausencia confirmada de una búsqueda diferida no comprobada.
- [Codex #50201](https://github.com/openai/codex/issues/50201) informa de un servidor STDIO visible directamente pero ausente en una tarea local delegada; `compare` comprueba dos capturas aportadas de ese límite.
- [MCP Extensions #28](https://github.com/openai/mcp-extensions/issues/28) y [#29](https://github.com/openai/mcp-extensions/issues/29) describen una discrepancia de pantalla completa y una entrada visible sin `tools/call` observado. `entrypoint.py` comprueba trazas aportadas, sin integración con el anfitrión en vivo.
- [Magpie #404](https://github.com/yetone/magpie/issues/404) describe funciones `namespace` eliminadas antes de llegar a Grok; el ejemplo reconstruido comprueba ese punto. [Magpie #130](https://github.com/yetone/magpie/issues/130) expone un problema cercano.
- [LLMConform](https://github.com/aitk-org/LLMConform) cubre ampliamente las gateways. Este repositorio compara una captura pequeña de herramientas. Estos enlaces no implican integración ni afiliación.

## Ver el problema en 10 segundos

```sh
python3 doctor.py demo --lang es
python3 check.py demo --lang es
```

La primera demostración muestra una herramienta ausente, una búsqueda diferida inconclusa y una herramienta visible. La segunda muestra tres comprobaciones fallidas en una gateway ficticia y luego el intercambio correcto. No requiere modelo, cuenta, clave API ni red. Los ejemplos son **sintéticos o reconstruidos**: no son una prueba real de Codex, Magpie u otra gateway.

## Comparar una sesión directa y una tarea delegada

```sh
python3 doctor.py compare examples/working-visibility.json examples/delegated-missing.json --lang es
```

El ejemplo sintético muestra `find_page` solo en la sesión directa. Códigos de salida: `2` pérdida confirmada, `3` búsqueda diferida no capturada, `0` ninguna pérdida confirmada, `1` entrada no válida. El comando lee dos catálogos locales capturados. No recopila una tarea real de Codex ni identifica el defecto del anfitrión. [Codex #50201](https://github.com/openai/codex/issues/50201) es el informe relacionado.

## Comprobar un intercambio capturado

```sh
python3 check.py check examples/working-trace.json --lang es
python3 check.py check examples/broken-trace.json --json
```

Códigos de salida: `0` conservado; `2` capacidad perdida; `1` traza no válida. El JSON debe contener `client_request`, `upstream_request`, `upstream_response` y `client_response`, las cuatro superficies que debes capturar al diagnosticar tu gateway. Consulta el [formato de trazas](docs/trace-format.md). El verificador acepta una herramienta transmitida como `namespace__name`, exige que la llamada devuelta tenga su espacio de nombres original, comprueba `encrypted_function_args: []` para argumentos en claro y verifica que el texto de `agent_message` llegue a la solicitud del proveedor.

**Límite actual:** no hay captura automática ni integración con Magpie. La herramienta funciona sin conexión sobre tus trazas; la demostración sintética no prueba que una gateway real funcione. El contrato Responses cubierto es limitado.

## Comprobar la traza de entrada de un plugin

```sh
python3 entrypoint.py demo --lang es
python3 entrypoint.py check fixtures/host-trace.json --lang es
```

La captura contiene `declared_modes`, `host_modes`, `entrypoint_listed`, `trace_complete` y `call_observed`. El control distingue discrepancias confirmadas de evidencia incompleta. La muestra es sintética. No abre un plugin de ChatGPT ni identifica la causa en el anfitrión.

## Diagnosticar una herramienta conectada pero invisible

```sh
python3 doctor.py demo --lang es
python3 doctor.py scan examples/magpie-namespaced-missing.json --lang es --json
```

`doctor.py` compara la respuesta MCP `tools/list` o el catálogo de una gateway con las herramientas visibles para el agente. Lee respuestas brutas `tools/list` y herramientas Responses `namespace`; use `agent_names` para declarar explícitamente nombres cambiados o con prefijo. Si existe `tool_search` pero no se capturó su resultado, devuelve **inconcluso** en vez de declarar ausente la herramienta. Códigos: `0` visible, `2` ausente, `3` inconcluso, `1` entrada no válida. Consulte el [formato y la guía de expurgación](docs/doctor-format.md).

Los ejemplos reconstruyen solo los nombres y estados descritos en las issues enlazadas: **no son capturas de sesión ni integraciones reales con Codex o Magpie**. El diagnóstico sitúa la ausencia en los catálogos proporcionados; no identifica el fallo del cliente ni prueba que la invocación funcione. [Magpie #141](https://github.com/yetone/magpie/issues/141) sigue siendo el caso independiente de mensaje de tarea cubierto por `check.py`.

## Pruebas

```sh
python3 -m unittest discover -s tests -v
```

Python 3.11+, sin dependencias. MIT. Herramienta alfa de diagnóstico para quienes mantienen gateways.
