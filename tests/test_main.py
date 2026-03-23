from pathlib import Path

from hosts_blocker.main import (
    LEGACY_MARKER_BEGIN,
    LEGACY_MARKER_END,
    MARKER_BEGIN,
    MARKER_END,
    get_all_hostnames,
    ipv4_block_entry,
    ipv6_block_entry,
    normalize_url,
    remove_existing_block,
    write_hosts_with_block,
)


def test_normalize_url_strips_scheme_www_and_path() -> None:
    assert normalize_url("https://www.example.com/path?q=1") == "example.com"


def test_get_all_hostnames_deduplicates_and_adds_www() -> None:
    assert get_all_hostnames(["example.com", "www.example.com", "news.ycombinator.com"]) == [
        "example.com",
        "news.ycombinator.com",
        "www.example.com",
        "www.news.ycombinator.com",
    ]


def test_ipv4_and_ipv6_block_entries_are_single_lines() -> None:
    assert ipv4_block_entry("example.com") == "0.0.0.0\t\texample.com\n"
    assert ipv6_block_entry("example.com") == "::1\t\texample.com\n"


def test_remove_existing_block_removes_current_and_legacy_markers() -> None:
    lines = [
        "127.0.0.1 localhost\n",
        f"{MARKER_BEGIN}\n",
        "0.0.0.0\t\texample.com\n",
        f"{MARKER_END}\n",
        f"{LEGACY_MARKER_BEGIN}\n",
        "0.0.0.0\t\tlegacy.example.com\n",
        f"{LEGACY_MARKER_END}\n",
    ]

    assert remove_existing_block(lines) == ["127.0.0.1 localhost\n"]


def test_write_hosts_with_block_replaces_legacy_block(tmp_path: Path) -> None:
    hosts_path = tmp_path / "hosts"
    hosts_path.write_text(
        "127.0.0.1 localhost\n"
        f"{LEGACY_MARKER_BEGIN}\n"
        "0.0.0.0\t\told.example.com\n"
        f"{LEGACY_MARKER_END}\n",
        encoding="utf-8",
    )

    write_hosts_with_block(["example.com"], hosts_path)

    assert hosts_path.read_text(encoding="utf-8") == (
        "127.0.0.1 localhost\n"
        "\n"
        f"{MARKER_BEGIN}\n"
        "0.0.0.0\t\texample.com\n"
        "::1\t\texample.com\n"
        "0.0.0.0\t\twww.example.com\n"
        "::1\t\twww.example.com\n"
        f"{MARKER_END}\n"
    )
