# Prerequisites — Install and Verify Everything You Need

This page explains every prerequisite from zero. MANGO itself has few requirements. Third-party AI runtimes are optional.

## Required for MANGO itself

### 1. A supported operating system

MANGO is a Python CLI and is intended to work on:

- macOS;
- Linux;
- Windows.

The CI matrix tests Python 3.10, 3.11, 3.12, and 3.13.

### 2. Python 3.10 or newer

MANGO declares Python >=3.10.

Verify:

~~~bash
python --version
~~~

If that command is not found, try:

~~~bash
python3 --version
~~~

On Windows, also try:

~~~powershell
py --version
~~~

You want a result such as Python 3.10.x, 3.11.x, 3.12.x, or 3.13.x.

#### Install Python on macOS

Recommended beginner options:

- Download Python from https://www.python.org/downloads/
- Or use Homebrew if you already use it:

~~~bash
brew install python
~~~

Verify:

~~~bash
python3 --version
python3 -m pip --version
~~~

#### Install Python on Ubuntu/Debian

~~~bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
python3 --version
~~~

#### Install Python on Windows

1. Download Python from https://www.python.org/downloads/windows/
2. Run the installer.
3. If offered, enable **Add Python to PATH**.
4. Open a new PowerShell window.

Verify:

~~~powershell
py --version
py -m pip --version
~~~

### 3. pip

pip installs Python packages. It normally arrives with Python.

Verify:

~~~bash
python -m pip --version
~~~

or:

~~~bash
python3 -m pip --version
~~~

Do not install MANGO globally with administrator/root privileges unless you intentionally manage Python that way. A virtual environment is safer and easier to remove.

### 4. Git

Git is required if you clone or update the repository through Git. It is not required if you download a ZIP and never pull updates.

Verify:

~~~bash
git --version
~~~

Install sources:

- https://git-scm.com/downloads
- macOS: xcode-select --install can provide Git; Homebrew is another option.
- Ubuntu/Debian: sudo apt install git
- Windows: install Git for Windows from git-scm.com.

### 5. A terminal

Examples:

- macOS: Terminal or iTerm2.
- Linux: your normal shell terminal.
- Windows: PowerShell, Windows Terminal, Command Prompt, or WSL.

All MANGO examples assume you are running commands from a terminal.

## Strongly recommended: a Python virtual environment

A virtual environment keeps MANGO and its Python packages isolated from your global Python install.

Create one:

### macOS/Linux

~~~bash
python3 -m venv .venv
source .venv/bin/activate
~~~

### Windows PowerShell

~~~powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
~~~

If PowerShell blocks script activation, you can either adjust your local execution policy according to your organization’s rules or use Command Prompt:

~~~cmd
.venv\Scripts\activate.bat
~~~

Verify the active Python:

~~~bash
python --version
python -m pip --version
~~~

## Optional prerequisite: Node.js and npm

MANGO itself does **not** require Node.js.

Node/npm is needed by common installation paths for Codex, Claude Code, Gemini CLI, and OpenClaw.

Verify:

~~~bash
node --version
npm --version
~~~

Do not choose a Node version only for MANGO. Choose it based on the runtime you want.

Current upstream requirements can change. As of September 2026:

- Claude Code documents Node.js 18+ for npm installation.
- Gemini CLI documents Node.js 20+.
- OpenClaw documents Node 24.16+ or 26.1+, with Node 26 recommended.
- Codex can be installed from npm with @openai/codex.

If you want one Node version to cover the most demanding current runtime, use the current Node version recommended by that runtime, then verify the runtime itself.

## Optional AI runtimes

You need only one live runtime. MANGO supports:

- Codex CLI;
- Claude Code;
- Google Gemini CLI;
- Hermes Agent;
- OpenClaw;
- prepare, which is built in and makes no model call.

Read [RUNTIMES.md](RUNTIMES.md) before installing one.

## Accounts, authentication, and billing

MANGO does not provide third-party model credentials.

Depending on your runtime, you may need:

- a ChatGPT/OpenAI account or API setup;
- an Anthropic/Claude account;
- a Google account, Gemini API key, or Google Cloud setup;
- a Nous Portal/provider account;
- an OpenClaw model provider configuration.

You must authenticate the third-party runtime **before** MANGO can execute it.

MANGO doctor checks whether the binary exists in PATH. It does not prove that authentication, quota, model access, or billing is valid.

## Network requirement

Offline operations such as validate, test, security, and prepare can run without a live model connection.

Installing packages and using live AI runtimes normally requires internet access.

## Verify all required prerequisites

Before installing MANGO:

~~~bash
python --version
python -m pip --version
git --version
~~~

On systems where python means something else, use python3 or py consistently.

## Next page

Continue with [INSTALLATION.md](INSTALLATION.md).
