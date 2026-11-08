# meetingscribe

Turn a plain-text meeting transcript (`.txt`, no audio) into a short
summary and a list of action items with owners and due dates.

## No LLM involved

This is plain string matching, not a model: action lines are found by
action words ("will", "needs to", "TODO", "action:", ...), owners by a
name at the start of the line, and due dates by a small date regex.
The summary is extractive — the first three sentences of the
transcript, copied verbatim. Nothing is generated or paraphrased, and
no API key is needed.

## Install

```bash
pip install -e .
```

## Usage

```bash
meetingscribe examples/sample_meeting.txt
meetingscribe examples/sample_meeting.txt --format json
```

## Example output

```
$ meetingscribe examples/sample_meeting.txt
Summary
-------
We reviewed the pricing bug from last week and agreed the warning fix is the priority. ...

Action Items
------------
1. [Owner: Sarah] Sarah will send the updated budget spreadsheet by Friday. [Due: by Friday]
2. [Owner: Mike] Mike needs to finish the extracteval test suite by 2026-11-12. [Due: 2026-11-12]
3. [Owner: Priya] Priya will draft the release notes for v0.2.0 next Monday. [Due: next Monday]
4. [Owner: Sarah] Sarah to confirm the PyPI publisher setup with the team.
5. [Owner: Mike] Mike to review the pull request for the token counter by March 5. [Due: March 5]
```

JSON output is `{"summary": ..., "action_items": [{"owner", "task", "due"}]}`,
with `"due": null` when no date is stated.

## Tests

```bash
python -m pytest
```

## License

MIT — see `LICENSE`.
