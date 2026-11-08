"""Tests for meetingscribe."""

import json
from pathlib import Path

from meetingscribe.cli import main
from meetingscribe.extract import extract_action_items, find_due, find_owner, summarize

SAMPLE = Path(__file__).parents[1] / "examples" / "sample_meeting.txt"


def test_extracts_owner_task_and_due():
    items = extract_action_items("Sarah will send the updated budget by Friday")
    assert len(items) == 1
    item = items[0]
    assert item["owner"] == "Sarah"
    assert "send the updated budget" in item["task"]
    assert item["due"] == "by Friday"


def test_extracts_iso_and_month_dates():
    items = extract_action_items(
        "Mike needs to finish the test suite by 2026-11-12\n"
        "Priya will draft the release notes by March 5"
    )
    assert [i["due"] for i in items] == ["2026-11-12", "March 5"]
    assert [i["owner"] for i in items] == ["Mike", "Priya"]


def test_next_monday_due_and_todo_prefix():
    items = extract_action_items("TODO: Sarah to confirm the setup next Monday")
    assert len(items) == 1
    assert items[0]["owner"] == "Sarah"
    assert items[0]["due"] == "next Monday"
    assert not items[0]["task"].startswith("TODO")


def test_line_without_action_language_produces_no_item():
    items = extract_action_items(
        "We reviewed the pricing bug from last week.\n"
        "The roadmap for December looks reasonable.\n"
    )
    assert items == []


def test_unassigned_when_no_name():
    items = extract_action_items("The budget will be reviewed by Friday")
    assert len(items) == 1
    assert items[0]["owner"] == "Unassigned"


def test_summarize_takes_first_three_sentences():
    text = "First sentence. Second sentence! Third sentence? Fourth sentence."
    assert summarize(text) == "First sentence. Second sentence! Third sentence?"


def test_missing_input_file_errors_cleanly(capsys):
    assert main(["does-not-exist.txt"]) == 2
    assert "error:" in capsys.readouterr().err


def test_json_output_parses_and_has_right_keys(tmp_path, capsys):
    path = tmp_path / "meeting.txt"
    path.write_text("Sarah will send the updated budget by Friday.\n", encoding="utf-8")
    assert main([str(path), "--format", "json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert set(data) == {"summary", "action_items"}
    assert data["action_items"][0]["owner"] == "Sarah"
    assert set(data["action_items"][0]) == {"owner", "task", "due"}


def test_text_output_lists_action_items(tmp_path, capsys):
    path = tmp_path / "meeting.txt"
    path.write_text("Sarah will send the updated budget by Friday.\n", encoding="utf-8")
    assert main([str(path)]) == 0
    out = capsys.readouterr().out
    assert "Summary" in out
    assert "Action Items" in out
    assert "[Owner: Sarah]" in out
    assert "[Due: by Friday]" in out


def test_sample_transcript_yields_at_least_three_action_items(capsys):
    assert SAMPLE.exists()
    assert main([str(SAMPLE)]) == 0
    out = capsys.readouterr().out
    assert out.count("[Owner:") >= 3


def test_sample_transcript_owners_and_dues():
    text = SAMPLE.read_text(encoding="utf-8")
    items = extract_action_items(text)
    owners = {i["owner"] for i in items}
    assert {"Sarah", "Mike", "Priya"} <= owners
    dues = {i["due"] for i in items}
    assert "by Friday" in dues
    assert "2026-11-12" in dues
