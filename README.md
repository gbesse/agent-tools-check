# Agent Tools Check

**Your MCP server is connected, but your agent cannot see its tools?** Compare the tool catalogs to find the first missing boundary. A second command checks whether a model gateway preserved tool calls and task messages.

[Français](README.fr.md) · English · [Español](README.es.md)

## Related projects

- [Codex #49758](https://github.com/openai/codex/issues/49758) reports an MCP server at READY whose tools are unavailable to the agent. The new doctor distinguishes a confirmed absence from an untested deferred search.
- [Magpie #404](https://github.com/yetone/magpie/issues/404) describes `namespace` functions dropped before Grok sees them; our reconstructed example checks that boundary. [Magpie #130](https://github.com/yetone/magpie/issues/130) reports a related gateway problem.
- [LLMConform](https://github.com/aitk-org/LLMConform) covers broad gateway compatibility. This repository compares a small, captured tool surface. These links do not imply integration or affiliation.

## See it in 10 seconds

```sh
python3 doctor.py demo
python3 check.py demo
```

The first demo shows a missing tool, an inconclusive deferred search and a visible tool. The second shows a broken gateway failing three checks, then passing after repair. Both run without a model, account, API key or network. They use **synthetic or reconstructed protocol fixtures**; neither is a live test of Codex, Magpie or another gateway.

## Check a captured exchange

```sh
python3 check.py check examples/working-trace.json
python3 check.py check examples/broken-trace.json --json
```

Exit codes: `0` preserved, `2` lost capability, `1` invalid trace. The JSON file must contain `client_request`, `upstream_request`, `upstream_response` and `client_response`. These are the four surfaces to capture while debugging your own gateway. See [trace format](docs/trace-format.md). The checker accepts a namespaced tool forwarded as `namespace__name`, tests that the returned function call carries the original namespace, checks that plaintext arguments carry `encrypted_function_args: []`, and confirms that `agent_message` text reached the upstream request.

**Current limit:** there is no automatic capture or Magpie integration. This is an offline checker for traces you provide; a passing synthetic demo does not establish that a live gateway works. It checks a narrow Responses-style contract, not all provider protocols or tool semantics.

## Diagnose a tool that is connected but invisible

```sh
python3 doctor.py demo
python3 doctor.py scan examples/magpie-namespaced-missing.json --json
```

`doctor.py` compares an MCP `tools/list` response or gateway client tool catalog against captured agent-visible tools. It reads raw `tools/list` response objects and Responses-style `namespace` tools; use `agent_names` for an explicit renamed or prefixed tool. If `tool_search` exists but its result was not captured, it reports **inconclusive** rather than pretending the tool is absent. Exit codes: `0` visible, `2` missing, `3` inconclusive, `1` invalid input. See the [capture format and redaction guide](docs/doctor-format.md).

The examples reconstruct only tool names and states described in the linked issues; they are **not** session captures or live Codex/Magpie integrations. This diagnostic locates a missing tool in provided catalogs. It does not identify the client bug or prove that an invocation works. [Magpie #141](https://github.com/yetone/magpie/issues/141) remains the separate task-message case covered by `check.py`.

## Test

```sh
python3 -m unittest discover -s tests -v
```

Python 3.11+, no dependencies. MIT. An alpha diagnosis tool for gateway maintainers.
