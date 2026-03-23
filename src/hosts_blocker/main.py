from __future__ import annotations

import ctypes
import os
import platform
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Final

MARKER_BEGIN: Final = "# hosts-blocker BEGIN"
MARKER_END: Final = "# hosts-blocker END"
LEGACY_MARKER_BEGIN: Final = "# hosts-page-blocker BEGIN"
LEGACY_MARKER_END: Final = "# hosts-page-blocker END"
URL_PREFIX_RE: Final = re.compile(r"^(?:https?://)?(?:www\.)?")


def get_os_name() -> str:
    """Get the current OS name."""
    return platform.system()


def get_hosts_path(system_name: str | None = None) -> Path:
    """Determine the path to the hosts file based on the current OS."""
    current_system = system_name or get_os_name()
    if current_system == "Windows":
        return Path(r"C:\Windows\System32\drivers\etc\hosts")
    if current_system in ("Linux", "Darwin"):
        return Path("/etc/hosts")
    raise OSError(f"Unsupported OS: {current_system}")


def prompt_for_number_of_pages() -> int:
    """Prompt for an integer."""
    while True:
        try:
            page_count = int(input("Number of pages: "))
        except ValueError:
            print("Incorrect input. Enter an integer!")
            continue

        if page_count > 0:
            return page_count

        print("Incorrect input. Enter an integer!")


def normalize_url(url: str) -> str:
    """Normalize a user-provided URL into a hostname."""
    normalized_url = URL_PREFIX_RE.sub("", url.strip())
    return normalized_url.split("/", 1)[0]


def prompt_for_url() -> str:
    """Prompt for a link and ensure it doesn't contain unnecessary prefix."""
    return normalize_url(input("Enter URL: "))


def get_all_hostnames(urls: Sequence[str]) -> list[str]:
    """
    Generate hostnames for the hosts file.

    For each URL, generate:
    - example.com
    - www.example.com (if not already www)
    """
    hostnames: set[str] = set()
    for url in urls:
        if not url:
            continue
        hostnames.add(url)
        if not url.startswith("www."):
            hostnames.add(f"www.{url}")
    return sorted(hostnames)


def ipv4_block_entry(hostname: str) -> str:
    """Generate an IPv4 block entry for a given hostname."""
    return f"0.0.0.0\t\t{hostname}\n"


def ipv6_block_entry(hostname: str) -> str:
    """Generate an IPv6 block entry for a given hostname."""
    return f"::1\t\t{hostname}\n"


def remove_marker_block(lines: list[str], marker_begin: str, marker_end: str) -> list[str]:
    """Remove a marker-delimited block if present."""
    while True:
        try:
            start_idx = lines.index(f"{marker_begin}\n")
            end_idx = lines.index(f"{marker_end}\n", start_idx)
        except ValueError:
            return lines
        lines = lines[:start_idx] + lines[end_idx + 1 :]


def remove_existing_block(lines: list[str]) -> list[str]:
    """Remove existing hosts-blocker or legacy hosts-page-blocker blocks if present."""
    cleaned_lines = list(lines)
    cleaned_lines = remove_marker_block(cleaned_lines, MARKER_BEGIN, MARKER_END)
    cleaned_lines = remove_marker_block(cleaned_lines, LEGACY_MARKER_BEGIN, LEGACY_MARKER_END)
    return cleaned_lines


def write_hosts_with_block(urls: Sequence[str], hosts_path: Path) -> None:
    """
    Idempotently update the hosts file with blocked URLs.

    Existing blocks from the current or legacy project name are replaced.
    """
    with hosts_path.open("r", encoding="utf-8") as file:
        lines = file.readlines()

    lines = remove_existing_block(lines)

    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"

    hostnames = get_all_hostnames(urls)
    block_lines = [f"{MARKER_BEGIN}\n"]
    for hostname in hostnames:
        block_lines.append(ipv4_block_entry(hostname))
        block_lines.append(ipv6_block_entry(hostname))
    block_lines.append(f"{MARKER_END}\n")

    with hosts_path.open("w", encoding="utf-8") as file:
        file.writelines(lines)
        if lines:
            file.write("\n")
        file.writelines(block_lines)

    print(f"Blocked {len(hostnames)} hostname(s)")


def check_is_admin(system_name: str) -> bool:
    """Check if the script is running with admin/root privileges."""
    if system_name in ("Linux", "Darwin"):
        return os.geteuid() == 0

    if system_name == "Windows":
        windll = getattr(ctypes, "windll", None)
        return bool(windll and windll.shell32.IsUserAnAdmin())

    return False


def main() -> None:
    """Prompt for URLs and append them to the hosts file to block them."""
    system_name = get_os_name()

    if not check_is_admin(system_name):
        raise SystemExit(
            "Error: This script requires admin/root privileges.\n"
            "  Linux/macOS: Run with 'sudo .venv/bin/hosts-blocker'\n"
            "  Windows: Run terminal as Administrator"
        )

    hosts_path = get_hosts_path(system_name)
    page_count = prompt_for_number_of_pages()
    urls = [prompt_for_url() for _ in range(page_count)]
    write_hosts_with_block(urls, hosts_path)


if __name__ == "__main__":
    main()
