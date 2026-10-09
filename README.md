# Agent Tools Check

## New: MCP tool name length preflight

**“My MCP server connects, but an agent rejects a long tool name.”** `python3 tool_name_budget.py demo --lang en` shows a synthetic 71-character name over a 64-character limit. Check a saved `tools/list` response or a `tools` array with `python3 tool_name_budget.py check --catalog tools.json --limit 64 --lang en`. Output gives names, character counts, UTF-8 byte counts and positions. It never renames tools; aliases must be applied consistently by the gateway and client. Review catalogs before sharing their names.

**Related projects:** [Magpie #1393](https://github.com/yetone/magpie/issues/1393) reports Kiro rejecting a long MCP name and discusses bidirectional aliases; [Magpie](https://github.com/yetone/magpie) is a neighboring configuration router. This is an independent offline preflight, with no Magpie or Kiro integration or affiliation.

## New: find MCP tokens copied into agent configurations

`python3 mcp_secret_map.py demo --lang en` shows one **synthetic** authentication value copied into a Magpie library and three agent configurations. A successful demo exits 0. Inspect files you control without changing them:

```sh
python3 mcp_secret_map.py scan --magpie library.json --codex config.toml --claude claude.json --opencode opencode.json --lang en
```

The checker reads Magpie's `mcp` array, Codex `mcp_servers` TOML, Claude `mcpServers` and OpenCode `mcp`. It checks remote MCP authentication headers only. The report gives counts and server positions; **neither text nor JSON output contains a value, URL or fingerprint**. Exit codes: 0 no literal found in supplied MCP entries, 2 possible literal found, 1 invalid input. A literal can be a test value; a clean result does not scan other files or prove a running agent is safe. Environment references such as Codex `bearer_token_env_var`, Claude `${VAR}` and OpenCode `{env:VAR}` are recognized but not rewritten; Magpie support depends on its version.

**Related projects:** [Magpie #1250](https://github.com/yetone/magpie/issues/1250) reports a token copied into generated agent settings and requests variable references. [cc-switch](https://github.com/farion1231/cc-switch) is cited there as a neighboring configuration manager. This checker is independent and has no integration or affiliation with either project.

## New: find MCP servers stranded after a Pi sync

`python3 pi_mcp.py pi-demo --lang en` shows two servers moving from Pi's native `mcp.json` into an adapter file that the active Pi setup does not read. A successful demo exits 0. Compare **copies** of your configuration before and after a sync:

```sh
python3 pi_mcp.py pi-compare BEFORE_DIR AFTER_DIR --pi-version 1.0.3 --lang en
```

If you have only the current directory, run `python3 pi_mcp.py pi-scan AGENT_DIR --pi-version 1.0.3 --lang en`. Exit 2 then means a server is **suspected** to be unread from its file placement; a before snapshot is required to confirm a loss.

Each directory contains the available `settings.json`, `mcp.json`, `mcp-adapter.json` and, if present, `npm/node_modules/pi-mcp-adapter/`. The checker reads JSON or JSONC, reports server **names only**, and never edits files or prints commands, URLs, headers, or credentials. Exit codes: 0 no confirmed loss, 2 servers no longer on the expected native path, 3 reader unknown, 1 invalid capture. It assumes Pi 0.99+ uses native MCP unless the adapter is declared in settings or present under `extensions/`; a leftover npm directory alone is not proof it is loaded. Loaded adapter and legacy configurations remain inconclusive because adapter versions differ. This checks file placement, not actual runtime tool visibility; use `doctor.py compare` with captured tool catalogs for that separate boundary.

**Related projects:** [Magpie #1097](https://github.com/yetone/magpie/issues/1097) reports this configuration migration and a maintainer-confirmed stale-adapter detection path; [Pi's native MCP support](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/mcp.md) supplies the reader. This tool is independent and does not modify either project.

**Your MCP server is connected, but your agent cannot see its tools?** Compare the tool catalogs to find the first missing boundary. A second command checks whether a model gateway preserved tool calls and task messages.

[Français](README.fr.md) · English · [Español](README.es.md)

## Related projects

- [Codex #49758](https://github.com/openai/codex/issues/49758) reports an MCP server at READY whose tools are unavailable to the agent. The new doctor distinguishes a confirmed absence from an untested deferred search.
- [Codex #50201](https://github.com/openai/codex/issues/50201) reports a configured STDIO server visible directly but missing in a delegated local task; `compare` checks two supplied captures of that boundary.
- [MCP Extensions #28](https://github.com/openai/mcp-extensions/issues/28) and [#29](https://github.com/openai/mcp-extensions/issues/29) report a fullscreen mode mismatch and a listed entrypoint without an observed `tools/call`. `entrypoint.py` checks supplied host traces, without a live host integration.
- [Magpie #404](https://github.com/yetone/magpie/issues/404) describes `namespace` functions dropped before Grok sees them; our reconstructed example checks that boundary. [Magpie #130](https://github.com/yetone/magpie/issues/130) reports a related gateway problem.
- [LLMConform](https://github.com/aitk-org/LLMConform) covers broad gateway compatibility. This repository compares a small, captured tool surface. These links do not imply integration or affiliation.

## See it in 10 seconds

```sh
python3 doctor.py demo
python3 check.py demo
```

The first demo shows a missing tool, an inconclusive deferred search and a visible tool. The second shows a broken gateway failing three checks, then passing after repair. Both run without a model, account, API key or network. They use **synthetic or reconstructed protocol fixtures**; neither is a live test of Codex, Magpie or another gateway.

## Compare direct and delegated tasks

```sh
python3 doctor.py compare examples/working-visibility.json examples/delegated-missing.json --lang en
```

The synthetic example reports `find_page` visible only in the direct session. Exit codes: `2` confirmed loss, `3` deferred search not captured, `0` no confirmed loss, `1` invalid input. The command reads two local captured catalogs. It does not collect a live Codex task or identify the host defect. [Codex #50201](https://github.com/openai/codex/issues/50201) is the related direct/delegated report.

## Compare renamed tool captures

Run `python3 doctor.py compare examples/renamed-direct.json examples/renamed-delegated.json --lang en`. The synthetic direct capture explicitly maps `find_page` to `spaces__find_page`; the delegated capture lacks both names. The result is a confirmed visibility loss, not a claim about why a host omitted the tool.

## Check a captured exchange

```sh
python3 check.py check examples/working-trace.json
python3 check.py check examples/broken-trace.json --json
```

Exit codes: `0` preserved, `2` lost capability, `1` invalid trace. The JSON file must contain `client_request`, `upstream_request`, `upstream_response` and `client_response`. These are the four surfaces to capture while debugging your own gateway. See [trace format](docs/trace-format.md). The checker accepts a namespaced tool forwarded as `namespace__name`, tests that the returned function call carries the original namespace, checks that plaintext arguments carry `encrypted_function_args: []`, and confirms that `agent_message` text reached the upstream request.

**Current limit:** there is no automatic capture or Magpie integration. This is an offline checker for traces you provide; a passing synthetic demo does not establish that a live gateway works. It checks a narrow Responses-style contract, not all provider protocols or tool semantics.

## Check a plugin entrypoint trace

```sh
python3 entrypoint.py demo --lang en
python3 entrypoint.py check fixtures/host-trace.json --lang en
```

The capture format contains `declared_modes`, `host_modes`, `entrypoint_listed`, `trace_complete`, and `call_observed`. The checker distinguishes a confirmed mismatch from incomplete evidence. The fixture is synthetic. It does not open a ChatGPT plugin or diagnose the host root cause.

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
