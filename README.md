# Agent Tools Check

**Did your AI agent lose its tools or its task after you switched model gateways?** Compare the four JSON stages of one tool call. This command tells you whether the gateway dropped a namespaced tool, failed to restore its call, changed arguments, or lost the subagent's message.

[Français](README.fr.md) · English · [Español](README.es.md)

## See it in 10 seconds

```sh
python3 check.py demo
```

The demo shows a broken gateway failing three checks, then the same exchange passing after repair. It runs without a model, account, API key or network. It uses **synthetic protocol fixtures**; it is not a live test of Magpie or another gateway.

## Check a captured exchange

```sh
python3 check.py check examples/working-trace.json
python3 check.py check examples/broken-trace.json --json
```

Exit codes: `0` preserved, `2` lost capability, `1` invalid trace. The JSON file must contain `client_request`, `upstream_request`, `upstream_response` and `client_response`. These are the four surfaces to capture while debugging your own gateway. See [trace format](docs/trace-format.md). The checker accepts a namespaced tool forwarded as `namespace__name`, tests that the returned function call carries the original namespace, checks that plaintext arguments carry `encrypted_function_args: []`, and confirms that `agent_message` text reached the upstream request.

**Current limit:** there is no automatic capture or Magpie integration. This is an offline checker for traces you provide; a passing synthetic demo does not establish that a live gateway works. It checks a narrow Responses-style contract, not all provider protocols or tool semantics.

## Related projects

- [Magpie #130](https://github.com/yetone/magpie/issues/130) reports Codex namespace tools disappearing when served through Magpie. Its concrete `spawn_agent` shape informed the tool check.
- [Magpie #141](https://github.com/yetone/magpie/issues/141) reports a MultiAgentV2 subagent receiving no task. Its `agent_message` and plaintext argument cases informed the message check.
- [LLMConform](https://github.com/aitk-org/LLMConform) covers broad gateway compatibility. Agent Tools Check focuses on the four-stage trace of an agent delegation. No integration or affiliation is claimed.

## Test

```sh
python3 -m unittest discover -s tests -v
```

Python 3.11+, no dependencies. MIT. An alpha diagnosis tool for gateway maintainers.
