"""A leading `cd DIR &&` moves the folder a --body-file path is read from."""

from pathlib import Path

import pytest

from ship_gate.check_gate import (
    command_cwd,
    find_pr_create,
    parse_pr_flags,
    split_command,
)
from voice_guard.check_voice import (
    command_cwd as voice_command_cwd,
    extract_body,
    find_comment_command,
)


def _gate_flags(command: str, base: Path):
    tokens = split_command(command)
    start = find_pr_create(tokens)
    cwd = command_cwd(tokens, start, str(base))
    return parse_pr_flags(tokens, start, str(cwd))


def _voice_body(command: str, base: Path):
    tokens = split_command(command)
    start = find_comment_command(tokens)
    cwd = voice_command_cwd(tokens, start, str(base))
    return extract_body(tokens, start, str(cwd))


@pytest.mark.parametrize("separator", ["&&", ";"])
def test_a_leading_cd_moves_the_body_file_folder(tmp_path, separator):
    folder = tmp_path / "notes"
    folder.mkdir()
    (folder / "draft.md").write_text("body from the notes folder", encoding="utf-8")

    command = f"cd notes {separator} gh pr create --title t --body-file draft.md"

    flags = _gate_flags(command, tmp_path)
    assert flags.get("problem") is None
    assert flags["body"] == "body from the notes folder"

    body, problem = _voice_body(command, tmp_path)
    assert problem is None
    assert body == "body from the notes folder"


def test_a_quoted_folder_name_is_handled(tmp_path):
    folder = tmp_path / "notes dir"
    folder.mkdir()
    (folder / "draft.md").write_text("quoted", encoding="utf-8")

    flags = _gate_flags('cd "notes dir" && gh pr create --title t --body-file draft.md', tmp_path)

    assert flags.get("problem") is None
    assert flags["body"] == "quoted"


def test_no_cd_keeps_the_hook_cwd(tmp_path):
    (tmp_path / "draft.md").write_text("plain", encoding="utf-8")

    flags = _gate_flags("gh pr create --title t --body-file draft.md", tmp_path)

    assert flags.get("problem") is None
    assert flags["body"] == "plain"


def test_an_unreadable_file_still_stops_and_names_the_folder(tmp_path):
    flags = _gate_flags("cd notes && gh pr create --title t --body-file missing.md", tmp_path)

    assert "could not read the body file" in flags["problem"]
    assert str(tmp_path / "notes") in flags["problem"]

    body, problem = _voice_body("cd notes && gh issue comment 1 --body-file missing.md", tmp_path)
    assert body is None
    assert "could not read the body file" in problem
    assert str(tmp_path / "notes") in problem


def test_cd_without_a_separator_does_not_move_the_folder(tmp_path):
    tokens = split_command("cd notes gh pr create --title t --body-file draft.md")
    start = find_pr_create(tokens)

    assert command_cwd(tokens, start, str(tmp_path)) == tmp_path
