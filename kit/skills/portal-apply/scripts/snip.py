#!/usr/bin/env python3
"""Build a runnable Playwright snippet with its arguments baked in.

The Playwright MCP sandbox can't read files or env vars, so each snippet in
snippets/ declares `const ARGS = __ARGS__;` and this script substitutes JSON
(merged with profile.json as ARGS.profile) and writes the result to
.playwright-mcp/run/<name>.js. Pass that path as `filename` to
mcp__playwright__browser_run_code_unsafe.

    python3 snip.py list
    python3 snip.py li-walk '{"resume": "fs"}'
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]  # repo root (…/resume)
SNIPS = HERE / "snippets"
OUT = ROOT / ".playwright-mcp" / "run"


def header(path: pathlib.Path) -> str:
    m = re.match(r"/\*(.*?)\*/", path.read_text(), re.S)
    return (m.group(1).strip() if m else "").replace("\n", "\n    ")


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
        print(__doc__)
        sys.exit(0)
    name = sys.argv[1]
    if name == "list":
        for p in sorted(SNIPS.glob("*.js")):
            print(f"{p.stem}\n    {header(p)}\n")
        return
    src = SNIPS / f"{name}.js"
    if not src.exists():
        sys.exit(f"no snippet {name!r}; run `snip.py list`")
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    code = src.read_text()
    if "profile" in code.split("*/", 1)[-1]:
        args["profile"] = json.loads((HERE / "profile.json").read_text())
    if "__ARGS__" not in code:
        sys.exit(f"{name}.js has no __ARGS__ placeholder")
    # Drop the header comment: run_code expects the file to be a single function expression.
    code = re.sub(r"^\s*/\*.*?\*/\s*", "", code, count=1, flags=re.S)
    code = code.replace("__ARGS__", json.dumps(args, ensure_ascii=False))
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"{name}.js"
    out.write_text(code)
    print(out.relative_to(ROOT))


if __name__ == "__main__":
    main()
