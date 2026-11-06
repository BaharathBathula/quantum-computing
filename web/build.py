"""
Build web/quantum-lab.html from web/src/template.html + web/i18n/*.json.

    python web/build.py                    # rebuild web/quantum-lab.html (standalone page)
    python web/build.py --check            # CI: translations complete + built page current (exit 1 otherwise)
    python web/build.py --fragment out.html  # content-only build for hosts that add their own <html> skeleton

Translation files are validated against en.json: same keys, no empty strings,
the same {placeholders} and the same inline HTML tags in every value.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent
TEMPLATE = WEB / "src" / "template.html"
I18N_DIR = WEB / "i18n"
OUTPUT = WEB / "quantum-lab.html"
MARKER = "/*__I18N__*/{}"

PLACEHOLDER = re.compile(r"\{(\w+)\}")
TAG = re.compile(r"<(/?)([a-z0-9]+)[^>]*>")


def load_translations() -> dict[str, dict[str, str]]:
    files = sorted(I18N_DIR.glob("*.json"), key=lambda p: (p.stem != "en", p.stem))
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in files}


def validate(translations: dict[str, dict[str, str]]) -> list[str]:
    """Return a list of problems (empty when everything is consistent)."""
    problems: list[str] = []
    en = translations.get("en")
    if en is None:
        return ["web/i18n/en.json is missing"]
    en_keys = {k for k in en if not k.startswith("_")}
    for code, tr in translations.items():
        meta = tr.get("_meta", {})
        if not isinstance(meta, dict) or not meta.get("name") or meta.get("dir") not in ("ltr", "rtl"):
            problems.append(f'{code}: _meta must be {{"name": ..., "dir": "ltr"|"rtl"}}')
        keys = {k for k in tr if not k.startswith("_")}
        for k in sorted(en_keys - keys):
            problems.append(f"{code}: missing key {k}")
        for k in sorted(keys - en_keys):
            problems.append(f"{code}: unknown key {k} (not in en.json)")
        for k in sorted(keys & en_keys):
            v = tr[k]
            if not isinstance(v, str) or not v.strip():
                problems.append(f"{code}: {k} is empty")
                continue
            if set(PLACEHOLDER.findall(v)) != set(PLACEHOLDER.findall(en[k])):
                problems.append(f"{code}: {k} placeholders differ from en ({PLACEHOLDER.findall(en[k])})")
            if sorted(TAG.findall(v)) != sorted(TAG.findall(en[k])):
                problems.append(f"{code}: {k} inline HTML tags differ from en")
    return problems


BODY_MARKER = "<!--__BODY__-->"
SKELETON_HEAD = (
    "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    '<meta name="description" content="Nine interactive quantum computing experiments on an in-browser '
    'simulator: qubits, superposition, entanglement, gates, Grover, circuits, hardware noise, error '
    'correction and quantum advantage. Eight languages, works offline.">\n'
    "<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>\n"
)


def render(translations: dict[str, dict[str, str]], fragment: bool = False) -> str:
    """Full standalone document by default (GitHub Pages, file://).

    fragment=True returns only the page content, for hosts that wrap it in their own
    <html>/<head>/<body> skeleton (the claude.ai artifact viewer does)."""
    template = TEMPLATE.read_text(encoding="utf-8")
    for marker in (MARKER, BODY_MARKER):
        if marker not in template:
            raise SystemExit(f"template is missing the marker {marker}")
    bundle = json.dumps(translations, ensure_ascii=False, separators=(",", ":"))
    bundle = bundle.replace("</script", "<\\/script")  # never close the page's own script tag
    page = template.replace(MARKER, "/*__I18N__*/" + bundle)
    head, body = page.split(BODY_MARKER, 1)
    if fragment:
        return head + body
    return SKELETON_HEAD + head.strip() + "\n</head>\n<body>" + body.rstrip() + "\n</body>\n</html>\n"


def main(argv: list[str]) -> int:
    translations = load_translations()
    problems = validate(translations)
    if problems:
        print("\n".join(problems))
        return 1
    if "--fragment" in argv:  # --fragment OUT.html: content-only build for wrapping hosts
        out = Path(argv[argv.index("--fragment") + 1])
        out.write_text(render(translations, fragment=True), encoding="utf-8")
        print(f"wrote fragment {out}")
        return 0
    html = render(translations)
    if "--check" in argv:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != html:
            print(f"{OUTPUT.relative_to(WEB.parent)} is out of date: run `python web/build.py`")
            return 1
        print(f"ok: {len(translations)} languages, {OUTPUT.name} is current")
        return 0
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"built {OUTPUT.relative_to(WEB.parent)} ({len(html) // 1024} KB, {', '.join(translations)})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
