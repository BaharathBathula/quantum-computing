# Contributing

Thanks for helping make this useful to more people. Three kinds of contribution are
especially welcome, and each has a checklist below.

## Setup

```bash
git clone https://github.com/BaharathBathula/quantum-computing.git && cd quantum-computing
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest                                   # project tests (~15 s)
QLAB_SOLUTIONS=1 pytest -m exercises     # autograder against the reference solutions
ruff check . && ruff format --check .    # lint
python web/build.py --check              # translations complete, built page current
```

CI runs exactly these commands on Python 3.11, 3.12 and 3.13.

## 1. Add or improve a language in the Quantum Lab

Translations live in `web/i18n/<code>.json`, one file per language. The page itself
is built from `web/src/template.html`; never edit `web/quantum-lab.html` by hand.

1. Copy `web/i18n/en.json` to `web/i18n/<code>.json` (use a BCP-47 code: `it`, `ko`, `ar`, `pt-BR`).
2. Translate every value. Keep the `{placeholders}` and the inline HTML tags
   (`<em>`, `<b>`, `<code>`, `<a>`) exactly as they are; the test-suite checks both.
3. Set `"_meta": {"name": "<language name in that language>", "dir": "ltr"}` (`"rtl"` for Arabic, Hebrew, Persian).
4. Run `python web/build.py` to rebuild `web/quantum-lab.html`, then `pytest tests/test_i18n.py`.
5. Open the built page, switch to your language, and click through all nine panels.

Native speakers improving an existing translation: edit the JSON file, rebuild, open a PR.
Physics terms should follow the usage in that language's university textbooks.

## 2. Add an exercise

Exercises are what hiring managers and instructors use most, so keep the bar high.

- Put the stub in `exercises/exNN_<topic>.py` with the task in the module docstring:
  difficulty (★ to ★★★), estimated time, what to implement, and hints that narrow
  the search without giving the answer. Stubs raise `NotImplementedError`.
- Put the reference solution in `exercises/solutions/exNN_<topic>.py` with the same
  function names.
- Put tests in `tests/takehome/test_exNN.py`, marked `@pytest.mark.exercises`, importing
  through `exercises.loader.load("exNN_<topic>")`. Tests must pass against the solution
  and fail against the stub (CI checks both directions).
- Add a row to the table in `INTERVIEW_GUIDE.md` with the skill the exercise probes.

## 3. Fix or extend a concept module

- Every claim a module prints should be asserted somewhere in `tests/test_concepts.py`.
- Run circuits at `optimization_level=0` unless compilation is the point, so the
  transpiler cannot cancel the gates the demo is about.
- Keep seeds fixed. The same command must print the same numbers.
- If you correct something the infographic says, add it to `CORRECTIONS.md` with the
  evidence (a test in `tests/test_infographic_claims.py` is ideal).

## Style

- `ruff` is the formatter and linter; its config is in `pyproject.toml`.
- Teaching code is read far more than it is run: prefer a clear 10-line function
  over a clever 3-line one, and explain the physics in a docstring, not a comment.
