#!/usr/bin/env python3
"""ATS check for a compiled resume PDF.

Reads the PDF's text layer the way an applicant tracking system does, then reports:
  1. parse faults (hyphen-split words, ligature glyphs, odd characters, page count)
  2. structure (standard section headers, contact details, visible profile URLs)
  3. keyword coverage against one or more keyword lists (role lists or a JD list)
  4. quantified bullets
and an overall score out of 100.

Usage:
  ats_check.py <resume.pdf> [--keywords FILE ...] [--profile FILE] [--parse-only]

Keyword file format (one keyword per line, '#' comments allowed):
  core | Tool Calling | function calling | tool use
  nice | LangGraph
The first column is the weight tier (core = 2, nice = 1), the second is the
canonical keyword, the rest are aliases that also count as a match.

Exit code: 1 if any parse FAIL was found (so build scripts can stop), else 0.
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
SWIFT_SRC = os.path.join(HERE, "pdftext.swift")
BIN = os.path.join(tempfile.gettempdir(), "ats_pdftext_bin")

STANDARD_SECTIONS = ["SUMMARY", "SKILLS", "EXPERIENCE", "PROJECTS", "EDUCATION"]
OPTIONAL_SECTIONS = ["ACHIEVEMENTS", "OPEN SOURCE", "CERTIFICATIONS", "HACKATHONS", "PUBLICATIONS"]
# Characters that parse fine; anything else outside ASCII gets flagged.
ALLOWED_NON_ASCII = set("•–—’‘“”·…")


def extract(pdf):
    import shutil
    if shutil.which("swiftc"):  # macOS: PDFKit
        if not os.path.exists(BIN) or os.path.getmtime(BIN) < os.path.getmtime(SWIFT_SRC):
            subprocess.run(["swiftc", "-O", SWIFT_SRC, "-o", BIN], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        out = subprocess.run([BIN, pdf], check=True, capture_output=True, text=True).stdout
        first, _, text = out.partition("\n")
        pages = int(first.split()[-1]) if first.startswith("PAGES:") else 0
        return pages, text
    if shutil.which("pdftotext"):  # Linux / no Swift: poppler (apt install poppler-utils)
        text = subprocess.run(["pdftotext", "-layout", pdf, "-"], check=True,
                              capture_output=True, text=True).stdout
        return text.count("\f") or 1, text
    sys.exit("ats_check needs swiftc (macOS) or pdftotext (poppler-utils).")


def split_sections(lines):
    """Map section name -> its lines, using all-caps header lines."""
    known = STANDARD_SECTIONS + OPTIONAL_SECTIONS
    sections, current = {"HEADER": []}, "HEADER"
    first = next((i for i, l in enumerate(lines) if l.strip()), 0)  # the name line
    for i, ln in enumerate(lines):
        s = ln.strip()
        if i > first and s and s.isupper() and len(s) < 40 and not s.startswith("•") and re.fullmatch(r"[A-Z &/]+", s):
            current = s
            sections[current] = []
        else:
            sections.setdefault(current, []).append(ln)
    return sections, known


def load_keywords(path):
    kws = []
    with open(path) as f:
        for raw in f:
            raw = raw.split("#", 1)[0].strip()
            if not raw:
                continue
            parts = [p.strip() for p in raw.split("|") if p.strip()]
            tier, names = parts[0].lower(), parts[1:]
            if tier not in ("core", "nice") or not names:
                continue
            kws.append({"tier": tier, "name": names[0], "aliases": names, "file": os.path.basename(path)})
    return kws


def kw_regex(term):
    esc = re.escape(term.lower()).replace(r"\ ", r"[\s\-]+")
    return re.compile(r"(?<![a-z0-9])" + esc + r"(?![a-z0-9])")


def where(term_res, sections):
    hits = []
    for name, lines in sections.items():
        blob = " ".join(lines).lower()
        if any(r.search(blob) for r in term_res):
            hits.append(name.title())
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--keywords", nargs="*", default=[])
    ap.add_argument("--profile", help="my-profile SKILL.md, to label missing keywords")
    ap.add_argument("--parse-only", action="store_true")
    a = ap.parse_args()

    pages, text = extract(a.pdf)
    lines = [l for l in text.splitlines()]
    fails, warns = [], []

    # ---------- 1. Parse faults ----------
    if len(text.strip()) < 500:
        fails.append("almost no extractable text (image PDF or broken font mapping)")
    if pages != 1:
        fails.append(f"{pages} pages (must be 1)")
    for i in range(len(lines) - 1):
        m = re.search(r"([A-Za-z]+)-$", lines[i].rstrip())
        nxt = lines[i + 1].lstrip()
        if m and nxt[:1].islower():
            fails.append(f"hyphen-split word: '{m.group(1)}-' + '{nxt.split()[0]}' (ATS reads two fragments)")
    ligs = sorted({c for c in text if 0xFB00 <= ord(c) <= 0xFB06})
    if ligs:
        words = sorted({w for w in re.findall(r"\S*[ﬀ-ﬆ]\S*", text)})
        fails.append(f"ligature glyphs {''.join(ligs)} in: {', '.join(words[:8])} (keyword won't match)")
    odd = sorted({c for c in text if ord(c) > 127 and c not in ALLOWED_NON_ASCII and not (0xFB00 <= ord(c) <= 0xFB06)})
    if odd:
        warns.append("unusual characters: " + " ".join(f"{c}(U+{ord(c):04X} {unicodedata.name(c, '?')})" for c in odd))

    # ---------- 2. Structure ----------
    sections, known = split_sections(lines)
    found = [s for s in sections if s != "HEADER"]
    for s in STANDARD_SECTIONS:
        if s not in found:
            warns.append(f"missing standard section header: {s}")
    for s in found:
        if s not in known:
            warns.append(f"non-standard section header '{s}' (ATS maps standard names best)")
    header = " ".join(lines[:3])
    if not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", header):
        fails.append("no email in the first lines")
    if not re.search(r"\+?\d[\d\s-]{8,}", header):
        warns.append("no phone number in the first lines")
    for site in ("linkedin.com", "github.com"):
        if site not in header.lower():
            warns.append(f"'{site}/...' not visible as text (hyperlink-only URLs are dropped by some parsers)")

    parse_score = max(0, 25 - 8 * len(fails) - 2 * len([w for w in warns if "characters" in w]))
    struct_score = max(0, 20 - 3 * len([w for w in warns if "section" in w or ".com" in w or "phone" in w]))

    print(f"== ATS CHECK: {a.pdf}")
    print(f"pages: {pages}  chars: {len(text)}")
    print("\n-- Parse & structure")
    for f in fails:
        print("FAIL:", f)
    for w in warns:
        print("WARN:", w)
    if not fails and not warns:
        print("clean")
    print("sections:", ", ".join(found))

    if a.parse_only:
        sys.exit(1 if fails else 0)

    # ---------- 3. Quantified bullets ----------
    bullets, cur = [], None
    for ln in lines:
        if ln.lstrip().startswith("•"):
            if cur:
                bullets.append(cur)
            cur = ln
        elif cur is not None and ln.strip() and not ln.strip().isupper():
            cur += " " + ln
        else:
            if cur:
                bullets.append(cur)
            cur = None
    if cur:
        bullets.append(cur)
    quant = [b for b in bullets if re.search(r"\d", b)]
    ratio = len(quant) / len(bullets) if bullets else 0
    quant_score = round(15 * min(1, ratio / 0.6))
    print(f"\n-- Quantified bullets: {len(quant)}/{len(bullets)} ({ratio:.0%}; target 60%+)")
    for b in bullets:
        if b not in quant:
            print("  no number:", re.sub(r"\s+", " ", b.strip())[:110])

    # ---------- 4. Keywords ----------
    kw_score = None
    if a.keywords:
        profile = open(a.profile).read().lower() if a.profile else ""
        # Past applications record what was NOT claimed; don't count those mentions as evidence.
        profile = profile.split("## past applications", 1)[0]
        unverified = ""
        m = re.search(r"not verified, don't list:\*\*(.*)", profile)
        if m:
            unverified = m.group(1)
        kws = [k for f in a.keywords for k in load_keywords(f)]
        total = got = 0
        missing = []
        print("\n-- Keywords")
        for k in kws:
            w = 2 if k["tier"] == "core" else 1
            total += w
            res = [kw_regex(t) for t in k["aliases"]]
            locs = where(res, sections)
            if locs:
                got += w
                thin = " (only 1 place; aim for Skills + a bullet)" if k["tier"] == "core" and len(locs) == 1 else ""
                print(f"  HIT  [{k['tier']}] {k['name']}: {', '.join(locs)}{thin}")
            else:
                label = "?"
                if profile:
                    if any(kw_regex(t).search(unverified) for t in k["aliases"]):
                        label = "profile: NOT verified"
                    elif any(kw_regex(t).search(profile) for t in k["aliases"]):
                        label = "in profile"
                    else:
                        label = "not in profile"
                missing.append((k, label))
        for k, label in missing:
            print(f"  MISS [{k['tier']}] {k['name']}  <{label}>")
        cov = got / total if total else 0
        kw_score = round(40 * min(1, cov / 0.85))
        print(f"keyword coverage: {cov:.0%} (weighted; target 80%+, full marks at 85%)")

    print("\n-- Score")
    parts = [("parse", parse_score, 25), ("structure", struct_score, 20), ("quantified", quant_score, 15)]
    if kw_score is not None:
        parts.append(("keywords", kw_score, 40))
    for n, s, mx in parts:
        print(f"  {n:<11}{s:>3}/{mx}")
    got_pts, max_pts = sum(p[1] for p in parts), sum(p[2] for p in parts)
    print(f"ATS SCORE: {round(100 * got_pts / max_pts)}/100")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
