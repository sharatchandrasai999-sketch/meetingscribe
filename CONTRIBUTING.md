# Contributing

Thanks for helping. Turn a plain-text meeting transcript into a summary and action items. This is a small, personal project, so keep changes small and easy to review.

## Before you send a change

- Run the tests from any folder: `pytest -q` (tests must not depend on the current working directory)
- Keep the offline path working: it must work on a local transcript file, no API key and no download.
- If you add an extraction rule, ship a sample transcript line that exercises it.

## Reporting a problem

Open an issue and include:

- The exact command you ran
- The input file, if it is about one
- What happened, and what you expected instead

Do not include API keys, private documents, or personal details.
