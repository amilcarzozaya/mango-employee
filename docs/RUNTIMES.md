# Runtime Compatibility

MANGO's canonical layer is runtime-independent. `mango run` builds one Runtime Package and dispatches it through an adapter.

## Codex CLI
Adapter: `codex exec --ephemeral --sandbox read-only ... -`

Use for non-interactive execution. MANGO deliberately starts read-only. Granting write access is a deployment decision outside the default adapter.

## Claude Code
Adapter: `claude -p --disallowedTools Bash Edit Write`

Print mode provides non-interactive execution. The default MANGO adapter explicitly denies common mutation tools.

## Google Gemini CLI
Adapter: `gemini` with the Runtime Package supplied through stdin.

Gemini CLI supports headless use from stdin. Host configuration still determines available tools and permissions.

## Hermes Agent
Adapter: `hermes chat --query-file -`

Hermes supports one-shot queries from stdin. MANGO does not enable extra Hermes toolsets automatically.

## OpenClaw
Adapter: `openclaw agent exec --message-file - --isolated`

`agent exec` is OpenClaw's headless/CI path. `--isolated` avoids ambient config. Model/provider can be selected with `--model`.

## Verification levels
- **Adapter verified:** command construction matches documented upstream CLI syntax.
- **Offline verified:** MANGO package generation and security tests pass without the runtime installed.
- **Live verified:** requires the actual third-party CLI, authentication and a model call on the target machine.

The repository CI performs the first two levels. It does not claim live verification for third-party CLIs that are not installed/authenticated in CI.
