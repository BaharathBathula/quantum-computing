"""Every language file must be a complete, structurally identical translation of en.json,
and the built Quantum Lab page must be up to date."""

import importlib.util
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("lab_build", ROOT / "web" / "build.py")
build = importlib.util.module_from_spec(spec)
sys.modules["lab_build"] = build
spec.loader.exec_module(build)

TRANSLATIONS = build.load_translations()


def test_english_is_the_source_of_truth():
    assert "en" in TRANSLATIONS
    assert len(TRANSLATIONS) >= 2, "at least one translation besides English"


@pytest.mark.parametrize("code", sorted(TRANSLATIONS))
def test_translation_is_complete_and_consistent(code):
    problems = [p for p in build.validate(TRANSLATIONS) if p.startswith(f"{code}:")]
    assert not problems, "\n".join(problems)


@pytest.mark.parametrize("code", sorted(c for c in TRANSLATIONS if c != "en"))
def test_translation_is_actually_translated(code):
    en, tr = TRANSLATIONS["en"], TRANSLATIONS[code]
    prose = [k for k in en if k.endswith((".intro", ".check", ".h2"))]
    untouched = [k for k in prose if tr[k] == en[k]]
    assert len(untouched) < len(prose) / 4, f"{code}: these look untranslated: {untouched}"


def test_every_template_key_exists_in_english():
    template = (ROOT / "web" / "src" / "template.html").read_text(encoding="utf-8")
    used = set(re.findall(r'data-i18n(?:-aria)?="([^"]+)"', template))
    used |= set(re.findall(r'\bt\("([a-z0-9.]+)"', template))
    used |= set(re.findall(r'(?:key:|Say\()\s*"(s\d\.[a-z0-9.]+)"', template))
    missing = sorted(k for k in used if k not in TRANSLATIONS["en"])
    assert not missing, f"keys used in the template but missing from en.json: {missing}"


def test_no_english_key_is_unused():
    template = (ROOT / "web" / "src" / "template.html").read_text(encoding="utf-8")
    unused = sorted(k for k in TRANSLATIONS["en"] if not k.startswith("_") and f'"{k}"' not in template)
    assert not unused, f"keys in en.json that the template never uses: {unused}"


def test_built_page_is_current():
    built = (ROOT / "web" / "quantum-lab.html").read_text(encoding="utf-8")
    assert built == build.render(TRANSLATIONS), "run `python web/build.py`"
