# hosts-blocker

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![CI](https://github.com/menzhik/hosts-blocker/actions/workflows/ci.yml/badge.svg)](https://github.com/menzhik/hosts-blocker/actions/workflows/ci.yml)

A small CLI that blocks selected websites at the OS level via your hosts file.

It is harder to bypass than browser extensions because it works through the system hosts file, not just the browser.

## Usage

After installation, run `hosts-blocker` with admin/root privileges.

```sh
# Local source checkout with uv on Linux/macOS
sudo .venv/bin/hosts-blocker

# Windows (run terminal as Administrator)
.venv\Scripts\hosts-blocker.exe
```

If you installed the package into an existing Python environment, run `hosts-blocker`
from that environment instead.

Example session:

```text
Number of pages: 1
Enter URL: example.com
```

Re-running the script is safe. It replaces the old block instead of appending duplicates, and it removes legacy `hosts-page-blocker` markers.

## Installation

Requirements:
- Python 3.11+
- Admin/root privileges to modify the hosts file
- Linux, macOS, or Windows

For a local source checkout:

```sh
git clone https://github.com/menzhik/hosts-blocker.git
cd hosts-blocker
uv sync
```

`uv sync` installs only the runtime environment. Development tools are kept separate.

Without `uv`, install the package into an existing Python environment with:

```sh
python -m pip install .
```

## How it works

The tool adds entries to your system's hosts file:

```
# hosts-blocker BEGIN
0.0.0.0        example.com
::1            example.com
0.0.0.0        www.example.com
::1            www.example.com
# hosts-blocker END
```

Examples use placeholder domains (`example.com`). Replace them locally with the domains you want to block.

## Development

```sh
uv sync --all-groups
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
```

## License

MIT License — see [LICENSE](LICENSE)
