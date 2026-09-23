# Runtime Compatibility — Install, Authenticate, Verify, Use

MANGO’s canonical Employee/Skill layer is runtime-independent.

A **Runtime** is the external execution surface that receives the Runtime Package.

You do not need a live runtime to start. Use **prepare** first.

## Step 0 — verify MANGO before any runtime

~~~bash
mango --version
mango validate reference-employees/mango-chief-of-staff
mango test reference-employees/mango-chief-of-staff
mango security reference-employees/mango-chief-of-staff
~~~

## Built-in runtime: prepare

Prerequisites:

- MANGO installed;
- no external model CLI;
- no model account;
- no API key.

Example:

~~~bash
mango run reference-employees/mango-chief-of-staff \
  --skill pre-meeting-brief \
  --task "Prepare a fictional brief" \
  --runtime prepare
~~~

Use prepare for:

- first setup;
- debugging Skill assignment;
- inspecting package/prompt;
- offline tests;
- safer upgrade smoke tests.

## What mango doctor does

~~~bash
mango doctor
~~~

doctor checks whether these binary names are in PATH:

- codex;
- claude;
- gemini;
- hermes;
- openclaw.

FOUND means “the executable is discoverable”.

FOUND does **not** guarantee:

- authentication;
- model entitlement;
- provider/API configuration;
- billing/quota;
- network;
- compatibility with every upstream version.

Always verify a runtime directly before using it through MANGO.

---

# Codex CLI

## What it is

Codex CLI is OpenAI’s terminal coding/agent client.

## Prerequisites

For the npm installation path:

- Node.js/npm installed;
- internet access;
- OpenAI/ChatGPT account or other supported authentication.

Official current references:

- https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan
- https://help.openai.com/en/articles/11096431

## Install

~~~bash
npm install -g @openai/codex
~~~

## Verify

~~~bash
codex --version
~~~

Current Codex builds also expose diagnostics such as:

~~~bash
codex doctor
~~~

when supported by the installed version.

## Authenticate

Launch Codex and follow its sign-in flow:

~~~bash
codex
~~~

Current OpenAI guidance supports signing in with ChatGPT in Codex clients. Some environments can also use supported API/provider credentials.

## Verify outside MANGO

Run one harmless prompt directly in Codex before blaming MANGO for an authentication issue.

## Verify MANGO discovery

~~~bash
mango doctor
~~~

## MANGO adapter

MANGO currently invokes:

~~~text
codex exec --ephemeral --sandbox read-only ... -
~~~

This is intentionally restrictive.

Example:

~~~bash
mango run EMPLOYEE --skill SKILL_ID --task "Describe the task" --runtime codex
~~~

---

# Claude Code

## Prerequisites

Anthropic’s current npm installation documentation lists:

- Node.js 18+;
- supported OS/shell;
- internet access;
- Claude/Anthropic authentication.

Official setup:

https://docs.anthropic.com/en/docs/claude-code/getting-started

## Install with npm

~~~bash
npm install -g @anthropic-ai/claude-code
~~~

Anthropic recommends not using sudo for the global npm installation.

## Verify

~~~bash
claude --version
claude doctor
~~~

## Authenticate

Launch:

~~~bash
claude
~~~

Follow the provider/account prompts.

## MANGO discovery

~~~bash
mango doctor
~~~

## MANGO adapter

MANGO invokes Claude in print mode and denies common mutation tools:

~~~text
claude -p --disallowedTools Bash Edit Write
~~~

Optional --model is passed through by MANGO.

Example:

~~~bash
mango run EMPLOYEE --skill SKILL_ID --task "Describe the task" --runtime claude
~~~

---

# Google Gemini CLI

## Prerequisites

Current Google guidance requires Node.js 20+ for local npm installation.

Official references:

- https://codelabs.developers.google.com/codelabs/quick-guide-to-gemini-cli
- https://github.com/google-gemini/gemini-cli

## Install

~~~bash
npm install -g @google/gemini-cli
~~~

Alternative current Google guidance may offer npx or Homebrew.

## Verify

~~~bash
gemini --version
~~~

## Authenticate

Launch:

~~~bash
gemini
~~~

Follow the authentication flow. Depending on configuration, Gemini CLI can use Google account/API/Google Cloud paths supported by the upstream client.

## MANGO discovery

~~~bash
mango doctor
~~~

## MANGO adapter

MANGO sends the Runtime Package through stdin to:

~~~text
gemini
~~~

and adds --model when specified.

Example:

~~~bash
mango run EMPLOYEE --skill SKILL_ID --task "Describe the task" --runtime gemini
~~~

---

# Hermes Agent

## Prerequisites

Hermes installation is managed by the Hermes project. Current official documentation supports Linux/macOS/WSL2 and native Windows installation paths.

Official project:

https://github.com/NousResearch/hermes-agent

## Install — Linux/macOS/WSL2

Current official quick install:

~~~bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
~~~

Reload your shell if instructed.

## Install — Windows PowerShell

Current official path:

~~~powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
~~~

Open a new terminal if PATH was changed.

## Configure provider/model

General setup:

~~~bash
hermes setup
~~~

Current Hermes documentation also describes:

~~~bash
hermes setup --portal
~~~

for Nous Portal configuration.

## Verify

~~~bash
hermes --help
hermes doctor
~~~

when doctor is supported by the installed build.

## MANGO discovery

~~~bash
mango doctor
~~~

## MANGO adapter

MANGO uses the Hermes query-file/stdin interface:

~~~text
hermes chat --query-file -
~~~

Current Hermes upstream source/docs include --query-file support for programmatic/untrusted message bodies.

Example:

~~~bash
mango run EMPLOYEE --skill SKILL_ID --task "Describe the task" --runtime hermes
~~~

---

# OpenClaw

## Prerequisites

OpenClaw’s current install documentation lists modern Node requirements for direct package installation and also offers an installer that manages a local prefix.

Official install:

https://docs.openclaw.ai/install

Official CLI:

https://docs.openclaw.ai/cli

## Install — local-prefix installer on macOS/Linux

Current documented option:

~~~bash
curl -fsSL https://openclaw.ai/install-cli.sh | bash
~~~

Follow the installer/onboarding prompts.

## Setup

~~~bash
openclaw setup
~~~

Use the upstream setup/configuration flow to establish model/provider access.

## Verify

~~~bash
openclaw --version
openclaw doctor
~~~

if doctor is available in the installed build.

## MANGO discovery

~~~bash
mango doctor
~~~

## MANGO adapter

MANGO invokes the headless agent-exec path:

~~~text
openclaw agent exec --message-file - --isolated
~~~

and passes --model when specified.

OpenClaw documents agent exec as its headless/CI-oriented single-turn path.

Example:

~~~bash
mango run EMPLOYEE --skill SKILL_ID --task "Describe the task" --runtime openclaw
~~~

Because MANGO uses --isolated, verify your provider/auth configuration works with the installed OpenClaw version and the way it resolves credentials in isolated execution.

---

# Runtime selection guidance

For a first live setup:

1. choose one runtime;
2. install it;
3. authenticate it;
4. verify it directly;
5. run mango doctor;
6. use mango run with a low-risk Skill;
7. inspect the output;
8. only then add more runtimes.

## Runtime troubleshooting checklist

If prepare succeeds but live execution fails:

1. mango doctor;
2. runtime --version;
3. upstream runtime direct prompt;
4. account/authentication;
5. quota/billing/model access;
6. network;
7. model override syntax;
8. then MANGO adapter compatibility.

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Verification levels

- **Package verified** — MANGO can build the package/prompt.
- **Binary detected** — mango doctor finds the runtime executable.
- **Direct runtime verified** — the runtime itself can complete a harmless prompt.
- **MANGO live verified** — mango run succeeds through that runtime.

Do not call a runtime “live verified” merely because mango doctor prints FOUND.

## Last reviewed

Runtime installation notes on this page were reviewed against upstream public documentation on **2026-09-22**. Third-party installation/authentication steps can change; when in doubt, prefer the linked upstream docs.
