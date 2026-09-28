# Agent Tools Check

**¿Perdió tu agente de IA sus herramientas o su tarea al cambiar de gateway?** Compara las cuatro etapas JSON de una llamada. La herramienta indica si la gateway descartó una herramienta con espacio de nombres, no restituyó su llamada, cambió los argumentos o perdió el mensaje del subagente.

[Français](README.fr.md) · [English](README.md) · Español

## Ver el problema en 10 segundos

```sh
python3 check.py demo --lang es
```

La demostración muestra tres comprobaciones que fallan con una gateway ficticia y luego el mismo intercambio correcto. No requiere modelo, cuenta, clave API ni red. Las pruebas de protocolo son **sintéticas**: no son una prueba real de Magpie ni de otra gateway.

## Comprobar un intercambio capturado

```sh
python3 check.py check examples/working-trace.json --lang es
python3 check.py check examples/broken-trace.json --json
```

Códigos de salida: `0` conservado; `2` capacidad perdida; `1` traza no válida. El JSON debe contener `client_request`, `upstream_request`, `upstream_response` y `client_response`, las cuatro superficies que debes capturar al diagnosticar tu gateway. Consulta el [formato de trazas](docs/trace-format.md). El verificador acepta una herramienta transmitida como `namespace__name`, exige que la llamada devuelta tenga su espacio de nombres original, comprueba `encrypted_function_args: []` para argumentos en claro y verifica que el texto de `agent_message` llegue a la solicitud del proveedor.

**Límite actual:** no hay captura automática ni integración con Magpie. La herramienta funciona sin conexión sobre tus trazas; la demostración sintética no prueba que una gateway real funcione. El contrato Responses cubierto es limitado.

## Proyectos relacionados

- [Magpie #130](https://github.com/yetone/magpie/issues/130) describe la desaparición de herramientas Codex con espacio de nombres al pasar por Magpie. Su forma concreta de `spawn_agent` guía la comprobación.
- [Magpie #141](https://github.com/yetone/magpie/issues/141) describe un subagente MultiAgentV2 que no recibe la tarea. Los casos `agent_message` y argumentos en claro guían la comprobación.
- [LLMConform](https://github.com/aitk-org/LLMConform) cubre ampliamente la compatibilidad de gateways. Agent Tools Check se centra en las cuatro etapas de una delegación. No se afirma integración ni afiliación.

## Pruebas

```sh
python3 -m unittest discover -s tests -v
```

Python 3.11+, sin dependencias. MIT. Herramienta alfa de diagnóstico para quienes mantienen gateways.
