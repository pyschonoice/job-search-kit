#!/usr/bin/env python3
"""Study tracker for the user's interview prep. The vault is plain .md files that Obsidian opens.

State lives in <vault>/_data/progress.csv (one row per item). Every command that changes
state also regenerates Home.md (dashboard + "where we left off"), Maps/<Track>.md
(mind-map outlines) and Maps/Study Map.canvas (Obsidian canvas).

  study.py init                      create the vault from the syllabus (safe to re-run)
  study.py sync                      add new syllabus items without touching progress
  study.py today [--new-dsa 2]       where we left off + today's plan
  study.py start <id>                mark an item in progress
  study.py done <id> --conf 1-5 [--minutes N] [--summary "..."]
  study.py review <id> --conf 1-5 [--summary "..."]
  study.py add --track T --section S --item I
  study.py find <text>               search items
  study.py status                    progress per track
  study.py note <id>                 print the note paths for an item (creating stubs if missing)
  study.py map                       regenerate Home, Maps and canvas
"""
import argparse, csv, datetime as dt, json, os, re, sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
SYLLABUS = SKILL / "references" / "syllabus.json"
VAULT = Path(os.environ.get("STUDY_VAULT", Path.cwd() / "study"))
DATA = VAULT / "_data" / "progress.csv"
FIELDS = ["id", "track", "section", "item", "note", "status", "confidence", "first_done",
          "last_reviewed", "next_review", "reviews", "minutes", "summary"]
BASE_INTERVAL = {1: 1, 2: 2, 3: 4, 4: 7, 5: 14}  # days until the first review, by confidence
TRACK_PREFIX = {"DSA": "dsa", "System Design": "sd", "AI Engineering": "ai"}


def today():
    return dt.date.today()


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def load_syllabus():
    return json.loads(SYLLABUS.read_text())


def item_id(track, item):
    return f"{TRACK_PREFIX.get(track, slug(track)[:4])}-{slug(item)}"


def note_name(track_cfg, section, item):
    return section if track_cfg.get("note_per") == "section" else item


def read_rows():
    if not DATA.exists():
        return []
    with DATA.open() as f:
        return list(csv.DictReader(f))


def write_rows(rows):
    DATA.parent.mkdir(parents=True, exist_ok=True)
    tmp = DATA.with_suffix(".tmp")
    with tmp.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    tmp.replace(DATA)


def find_row(rows, rid):
    for r in rows:
        if r["id"] == rid:
            return r
    hits = [r for r in rows if rid.lower() in r["id"] or rid.lower() in r["item"].lower()]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        sys.exit(f"No item matches '{rid}'. Try: study.py find <text>")
    sys.exit("Ambiguous, pick one:\n" + "\n".join(f"  {r['id']}  ({r['item']})" for r in hits[:15]))


def sync_rows(rows):
    have = {r["id"] for r in rows}
    added = 0
    for t in load_syllabus()["tracks"]:
        for s in t["sections"]:
            for it in s["items"]:
                rid = item_id(t["name"], it)
                if rid in have:
                    continue
                rows.append({k: "" for k in FIELDS} | {
                    "id": rid, "track": t["name"], "section": s["name"], "item": it,
                    "note": note_name(t, s["name"], it), "status": "todo", "reviews": "0", "minutes": "0"})
                have.add(rid)
                added += 1
    return added


def track_order():
    return [t["name"] for t in load_syllabus()["tracks"]]


# ---------- notes ----------

def crisp_name(note):
    return f"{note} (crisp)"


def note_paths(r):
    d = VAULT / "Detailed" / r["track"] / f"{r['note']}.md"
    c = VAULT / "Crisp" / r["track"] / f"{crisp_name(r['note'])}.md"
    return d, c


def ensure_notes(r):
    d, c = note_paths(r)
    tag = slug(r["track"])
    sec = slug(r["section"])
    if not d.exists():
        d.parent.mkdir(parents=True, exist_ok=True)
        tpl = (VAULT / "Templates" / "Detailed.md").read_text()
        d.write_text(fill_template(tpl, r, tag, sec))
    if not c.exists():
        c.parent.mkdir(parents=True, exist_ok=True)
        tpl = (VAULT / "Templates" / "Crisp.md").read_text()
        c.write_text(fill_template(tpl, r, tag, sec))
    return d, c


def fill_template(tpl, r, tag, sec):
    return (tpl.replace("{{title}}", r["note"]).replace("{{track}}", r["track"])
            .replace("{{section}}", r["section"]).replace("{{track_tag}}", tag)
            .replace("{{section_tag}}", sec).replace("{{date}}", today().isoformat()))


# ---------- log ----------

def log(line, heading):
    p = VAULT / "Log" / f"{today().isoformat()}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    text = p.read_text() if p.exists() else f"---\ntags: [study-log]\n---\n# {today().isoformat()}\n\n## Done\n\n## Reviewed\n\n## Notes for next time\n"
    marker = f"## {heading}\n"
    i = text.index(marker) + len(marker)
    j = text.find("\n## ", i)
    j = len(text) if j == -1 else j
    block = text[i:j].rstrip("\n")
    block = (block + "\n" if block.strip() else "") + line + "\n"
    text = text[:i] + block + "\n" + text[j:].lstrip("\n")
    p.write_text(text)


def last_log():
    logs = sorted((VAULT / "Log").glob("*.md")) if (VAULT / "Log").exists() else []
    return logs[-1] if logs else None


# ---------- scheduling ----------

def schedule(r, conf, reviewing):
    n = int(r["reviews"] or 0) + (1 if reviewing else 0)
    days = BASE_INTERVAL[conf] * (2 ** min(n, 3)) if conf >= 3 else BASE_INTERVAL[conf]
    r["confidence"] = str(conf)
    r["reviews"] = str(n)
    r["last_reviewed"] = today().isoformat()
    r["next_review"] = (today() + dt.timedelta(days=days)).isoformat()


def due(rows):
    t = today().isoformat()
    return sorted([r for r in rows if r["status"] == "done" and r["next_review"] and r["next_review"] <= t],
                  key=lambda r: (r["next_review"], int(r["confidence"] or 0)))


def plan(rows, new_dsa=2):
    in_progress = [r for r in rows if r["status"] == "learning"]
    reviews = due(rows)[:3]
    todo = [r for r in rows if r["status"] == "todo"]
    dsa = [r for r in todo if r["track"] == "DSA"][:new_dsa]

    def ratio(track):
        rs = [r for r in rows if r["track"] == track]
        return sum(r["status"] == "done" for r in rs) / max(len(rs), 1)

    others = [t for t in track_order() if t != "DSA"]
    others.sort(key=ratio)
    topic = []
    for t in others:
        nxt = [r for r in todo if r["track"] == t]
        if nxt:
            topic = nxt[:1]
            break
    return in_progress, reviews, dsa, topic


# ---------- generated files ----------

def link(note, alias=None):
    return f"[[{note}|{alias}]]" if alias else f"[[{note}]]"


def label(r, crisp=False):
    """Link to the item's note, plus the item name when the note covers a whole section (DSA)."""
    l = link(crisp_name(r["note"]), r["note"]) if crisp else link(r["note"])
    return l if r["note"] == r["item"] else f"{l} · {r['item']}"


def bar(done, total, width=20):
    k = round(width * done / max(total, 1))
    return "█" * k + "░" * (width - k)


def render_home(rows):
    ip, rv, dsa, topic = plan(rows)
    lg = last_log()
    lines = ["---", "tags: [study-home]", "---", "# Interview Prep", "",
             f"_Updated {dt.datetime.now().strftime('%Y-%m-%d %H:%M')} by study.py. Don't edit by hand; it is regenerated._", ""]
    lines += ["## Where we left off", ""]
    if lg:
        lines.append(f"Last session: [[{lg.stem}]]")
        nxt = re.search(r"## Notes for next time\n(.*)", lg.read_text(), re.S)
        if nxt and nxt.group(1).strip():
            lines += ["", "> " + nxt.group(1).strip().replace("\n", "\n> ")]
    else:
        lines.append("No sessions yet. Say \"let's study\" to start.")
    if ip:
        lines += ["", "**Unfinished:** " + ", ".join(f"{label(r)} (`{r['id']}`)" for r in ip)]
    lines += ["", "## Today's plan (45–60 min)", ""]
    for r in rv:
        lines.append(f"- [ ] Review {label(r, crisp=True)} (conf {r['confidence']}, due {r['next_review']}) `{r['id']}`")
    for r in dsa + topic:
        lines.append(f"- [ ] New: {label(r)} `{r['id']}`")
    lines += ["", "## Progress", "", "| Track | Done | Learning | Left | |", "|---|---|---|---|---|"]
    for t in track_order():
        rs = [r for r in rows if r["track"] == t]
        d = sum(r["status"] == "done" for r in rs)
        l = sum(r["status"] == "learning" for r in rs)
        lines.append(f"| [[{t}]] | {d} | {l} | {len(rs) - d - l} | `{bar(d, len(rs))}` {round(100 * d / max(len(rs), 1))}% |")
    weak = sorted([r for r in rows if r["status"] == "done" and r["confidence"] and int(r["confidence"]) <= 2],
                  key=lambda r: r["last_reviewed"])
    if weak:
        lines += ["", "## Weak spots (confidence 1–2)", ""]
        lines += [f"- {label(r)} (conf {r['confidence']})" for r in weak[:10]]
    lines += ["", "## Maps", "", "- [[DSA]] · [[System Design]] · [[AI Engineering]]",
              "- Canvas: [[Study Map.canvas|Study Map]]", "- Mocks: `Mocks/`  ·  Daily logs: `Log/`", ""]
    (VAULT / "Home.md").write_text("\n".join(lines))


def status_box(r):
    return {"done": "x", "learning": "/"}.get(r["status"], " ")


def render_maps(rows):
    maps = VAULT / "Maps"
    maps.mkdir(parents=True, exist_ok=True)
    for t in load_syllabus()["tracks"]:
        lines = ["---", f"tags: [map, {slug(t['name'])}]", "---", f"# {t['name']}", "",
                 "_Generated outline. Open it with the Mind Map / Markmap plugin, or use graph view._", ""]
        for s in t["sections"]:
            rs = [r for r in rows if r["track"] == t["name"] and r["section"] == s["name"]]
            d = sum(r["status"] == "done" for r in rs)
            if t.get("note_per") == "section":
                lines.append(f"## {link(s['name'])} · {link(crisp_name(s['name']), 'crisp')} ({d}/{len(rs)})")
                lines += [f"- [{status_box(r)}] {r['item']}" for r in rs]
            else:
                lines.append(f"## {s['name']} ({d}/{len(rs)})")
                lines += [f"- [{status_box(r)}] {link(r['note'])} · {link(crisp_name(r['note']), 'crisp')}" for r in rs]
            lines.append("")
        (maps / f"{t['name']}.md").write_text("\n".join(lines))
    render_canvas(rows)


def render_canvas(rows):
    nodes, edges = [], []
    color = lambda d, n, l: "4" if n and d == n else ("3" if d or l else "")
    nodes.append({"id": "root", "type": "text", "text": "# Interview Prep\n[[Home]]", "x": 0, "y": -500, "width": 260, "height": 100, "color": "6"})
    tracks = load_syllabus()["tracks"]
    col_w = 900
    for ti, t in enumerate(tracks):
        tx = (ti - (len(tracks) - 1) / 2) * col_w
        tid = f"t{ti}"
        nodes.append({"id": tid, "type": "file", "file": f"Maps/{t['name']}.md", "x": tx - 150, "y": -300, "width": 300, "height": 90, "color": "5"})
        edges.append({"id": f"e-root-{tid}", "fromNode": "root", "fromSide": "bottom", "toNode": tid, "toSide": "top"})
        for si, s in enumerate(t["sections"]):
            rs = [r for r in rows if r["track"] == t["name"] and r["section"] == s["name"]]
            d = sum(r["status"] == "done" for r in rs)
            l = sum(r["status"] == "learning" for r in rs)
            if t.get("note_per") == "section":
                body = f"## [[{s['name']}]]\n{d}/{len(rs)} problems · [[{crisp_name(s['name'])}|crisp]]"
                h = 110
            else:
                body = f"## {s['name']}  ({d}/{len(rs)})\n" + "\n".join(
                    f"- {'✅' if r['status'] == 'done' else ('🟡' if r['status'] == 'learning' else '⬜')} [[{r['note']}]]" for r in rs)
                h = 70 + 30 * len(rs)
            col = si % 2
            y = -120 + sum((110 if t.get("note_per") == "section" else 70 + 30 * len(x["items"])) + 40
                           for k, x in enumerate(t["sections"][:si]) if k % 2 == col)
            sid = f"t{ti}s{si}"
            node = {"id": sid, "type": "text", "text": body, "x": tx - 420 + col * 430, "y": y, "width": 400, "height": h}
            c = color(d, len(rs), l)
            if c:
                node["color"] = c
            nodes.append(node)
            edges.append({"id": f"e-{tid}-{sid}", "fromNode": tid, "fromSide": "bottom", "toNode": sid, "toSide": "top"})
    (VAULT / "Maps" / "Study Map.canvas").write_text(json.dumps({"nodes": nodes, "edges": edges}, indent=1))


def regen(rows):
    render_home(rows)
    render_maps(rows)


# ---------- templates ----------

CRISP_TPL = """---
tags: [crisp, {{track_tag}}, {{section_tag}}]
track: {{track}}
section: {{section}}
created: {{date}}
---
# {{title}} (crisp)

> One line: what it is / when to reach for it.

**Key points**
-
-
-

**Pattern / formula**
-

**Gotchas**
-

**Say it in an interview (30 s)**
-

Detailed: [[{{title}}]] · Map: [[{{track}}]]
"""

DETAILED_TPL = """---
tags: [detailed, {{track_tag}}, {{section_tag}}]
track: {{track}}
section: {{section}}
created: {{date}}
---
# {{title}}

Crisp: [[{{title}} (crisp)]] · Map: [[{{track}}]]

## Intuition

## How it works

## Code / diagram

## Trade-offs and alternatives

## Interview angle
How I'd explain it, the follow-ups they ask, and what a strong answer includes.

## From my work
Only verified facts from my-profile.

## Practice
<!-- DSA: one line per problem solved: name, key insight, complexity, date -->

## Related
"""


def cmd_init(a):
    for d in ["Crisp", "Detailed", "Maps", "Log", "Mocks", "Templates", "_data"]:
        (VAULT / d).mkdir(parents=True, exist_ok=True)
    for name, tpl in [("Crisp.md", CRISP_TPL), ("Detailed.md", DETAILED_TPL)]:
        p = VAULT / "Templates" / name
        if not p.exists():
            p.write_text(tpl)
    obs = VAULT / ".obsidian"
    obs.mkdir(exist_ok=True)
    for name, cfg in [("app.json", {"newFileLocation": "folder", "newFileFolderPath": "Detailed", "userIgnoreFilters": ["_data/"]}),
                      ("templates.json", {"folder": "Templates"}),
                      ("core-plugins.json", ["file-explorer", "global-search", "graph", "backlink", "outgoing-link",
                                             "tag-pane", "page-preview", "templates", "canvas", "daily-notes", "outline"]),
                      ("daily-notes.json", {"folder": "Log", "format": "YYYY-MM-DD"})]:
        p = obs / name
        if not p.exists():
            p.write_text(json.dumps(cfg, indent=2))
    rows = read_rows()
    n = sync_rows(rows)
    write_rows(rows)
    regen(rows)
    print(f"Vault ready at {VAULT} ({len(rows)} items, {n} new). Open this folder as a vault in Obsidian.")


def cmd_sync(a):
    rows = read_rows()
    n = sync_rows(rows)
    write_rows(rows)
    regen(rows)
    print(f"{n} new items added; {len(rows)} total.")


def cmd_today(a):
    rows = read_rows()
    ip, rv, dsa, topic = plan(rows, a.new_dsa)
    lg = last_log()
    print(f"# Study plan {today().isoformat()}")
    if lg:
        print(f"Last session: {lg.stem}")
        m = re.search(r"## Notes for next time\n(.*)", lg.read_text(), re.S)
        if m and m.group(1).strip():
            print("Left for next time:\n  " + m.group(1).strip().replace("\n", "\n  "))
    else:
        print("No sessions yet.")
    fmt = lambda r: f"  {r['id']:<55} {r['track']} › {r['section']} › {r['item']}"
    if ip:
        print("\nUnfinished (finish first):"); [print(fmt(r)) for r in ip]
    if rv:
        print(f"\nReviews due ({len(due(rows))} total, top 3):")
        [print(fmt(r) + f"  [conf {r['confidence']}, due {r['next_review']}]") for r in rv]
    print("\nNew today:"); [print(fmt(r)) for r in dsa + topic]
    regen(rows)


def cmd_start(a):
    rows = read_rows()
    r = find_row(rows, a.id)
    if r["status"] == "todo":
        r["status"] = "learning"
    write_rows(rows)
    d, c = ensure_notes(r)
    regen(rows)
    print(f"Started {r['id']}\n  detailed: {d}\n  crisp:    {c}")


def cmd_done(a):
    rows = read_rows()
    r = find_row(rows, a.id)
    first = r["status"] != "done"
    r["status"] = "done"
    if first:
        r["first_done"] = today().isoformat()
    schedule(r, a.conf, reviewing=not first)
    r["minutes"] = str(int(r["minutes"] or 0) + (a.minutes or 0))
    if a.summary:
        r["summary"] = a.summary
    write_rows(rows)
    ensure_notes(r)
    t = dt.datetime.now().strftime("%H:%M")
    log(f"- {t} [[{r['note']}]] · {r['item']} — conf {a.conf}" + (f" — {a.minutes} min" if a.minutes else "")
        + (f" — {a.summary}" if a.summary else "") + f" · next review {r['next_review']}", "Done")
    regen(rows)
    print(f"Done {r['id']} (conf {a.conf}); next review {r['next_review']}")


def cmd_review(a):
    rows = read_rows()
    r = find_row(rows, a.id)
    if r["status"] != "done":
        sys.exit(f"{r['id']} isn't done yet; use `done`.")
    schedule(r, a.conf, reviewing=True)
    if a.summary:
        r["summary"] = a.summary
    write_rows(rows)
    t = dt.datetime.now().strftime("%H:%M")
    log(f"- {t} [[{crisp_name(r['note'])}|{r['note']}]] · {r['item']} — conf {a.conf}"
        + (f" — {a.summary}" if a.summary else "") + f" · next {r['next_review']}", "Reviewed")
    regen(rows)
    print(f"Reviewed {r['id']} (conf {a.conf}); next review {r['next_review']}")


def cmd_next_time(a):
    log(f"- {a.text}", "Notes for next time")
    regen(read_rows())
    print("Saved.")


def cmd_add(a):
    rows = read_rows()
    tracks = {t["name"]: t for t in load_syllabus()["tracks"]}
    t = tracks.get(a.track, {"name": a.track, "note_per": "item"})
    rid = item_id(a.track, a.item)
    if any(r["id"] == rid for r in rows):
        sys.exit(f"{rid} already exists.")
    rows.append({k: "" for k in FIELDS} | {"id": rid, "track": a.track, "section": a.section, "item": a.item,
                                           "note": note_name(t, a.section, a.item), "status": "todo", "reviews": "0", "minutes": "0"})
    write_rows(rows)
    regen(rows)
    print(f"Added {rid}. Also add it to references/syllabus.json so maps include it.")


def cmd_find(a):
    q = a.text.lower()
    for r in read_rows():
        if q in (r["id"] + r["item"] + r["section"]).lower():
            print(f"{r['id']:<55} {r['status']:<9} conf {r['confidence'] or '-'}  {r['track']} › {r['section']} › {r['item']}")


def cmd_status(a):
    rows = read_rows()
    for t in track_order():
        rs = [r for r in rows if r["track"] == t]
        d = sum(r["status"] == "done" for r in rs)
        print(f"{t:<16} {bar(d, len(rs))} {d}/{len(rs)}")
        for s in dict.fromkeys(r["section"] for r in rs):
            ss = [r for r in rs if r["section"] == s]
            sd = sum(r["status"] == "done" for r in ss)
            if sd or any(r["status"] == "learning" for r in ss):
                print(f"    {s:<40} {sd}/{len(ss)}")
    print(f"Reviews due: {len(due(rows))}   Minutes logged: {sum(int(r['minutes'] or 0) for r in rows)}")


def cmd_note(a):
    rows = read_rows()
    r = find_row(rows, a.id)
    d, c = ensure_notes(r)
    print(f"detailed: {d}\ncrisp:    {c}")


def cmd_map(a):
    regen(read_rows())
    print("Regenerated Home.md, Maps/ and the canvas.")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    sp.add_parser("init"); sp.add_parser("sync"); sp.add_parser("status"); sp.add_parser("map")
    x = sp.add_parser("today"); x.add_argument("--new-dsa", type=int, default=2)
    x = sp.add_parser("start"); x.add_argument("id")
    x = sp.add_parser("note"); x.add_argument("id")
    for name in ["done", "review"]:
        x = sp.add_parser(name); x.add_argument("id")
        x.add_argument("--conf", type=int, required=True, choices=range(1, 6))
        x.add_argument("--summary")
        if name == "done":
            x.add_argument("--minutes", type=int)
    x = sp.add_parser("next-time", help="note for the next session"); x.add_argument("text")
    x = sp.add_parser("add"); x.add_argument("--track", required=True); x.add_argument("--section", required=True); x.add_argument("--item", required=True)
    x = sp.add_parser("find"); x.add_argument("text")
    a = p.parse_args()
    {"init": cmd_init, "sync": cmd_sync, "today": cmd_today, "start": cmd_start, "done": cmd_done,
     "review": cmd_review, "next-time": cmd_next_time, "add": cmd_add, "find": cmd_find,
     "status": cmd_status, "note": cmd_note, "map": cmd_map}[a.cmd](a)


if __name__ == "__main__":
    main()
