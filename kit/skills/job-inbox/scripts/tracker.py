#!/usr/bin/env python3
"""the user's universal job tracker: one CSV row per opportunity.

The data lives in tracker/applications.csv at the repo root (opens in Sheets,
Excel or Numbers). This script is the safe way to change it: it validates
enums, keeps the column order, stamps last_update, and finds what's due.

  tracker.py add --company X --role Y --category company_site --platform Workday --status applied --date_applied 2026-10-05
  tracker.py update <id> --status rejected --date_closed 2026-10-06 --notes "Workday rejection"
  tracker.py find <text>            rows whose company/role/contact match
  tracker.py list [--status S] [--category C] [--open] [--closed]
  tracker.py due [--today YYYY-MM-DD]   follow-ups and next actions that are due
  tracker.py stats                  funnel and response rates
"""
import argparse
import csv
import datetime as dt
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CSV_PATH = ROOT / "tracker" / "applications.csv"

FIELDS = [
    "id", "company", "role", "category", "platform", "status", "stage",
    "date_found", "date_applied", "last_update", "date_closed",
    "next_action", "next_action_due",
    "contact", "contact_email", "job_url", "location", "work_mode",
    "resume", "ats_score", "salary", "gmail_thread", "notes",
]

CATEGORIES = {
    "linkedin_easy_apply": "Applied with LinkedIn Easy Apply",
    "company_site": "Applied on the company's careers page or ATS (Workday, Ashby, Greenhouse...)",
    "job_board": "Applied through a job board (ClanX, YC Work at a Startup, Jobgether, Wellfound, Instahyre, Naukri, Cutshort, HireFT...)",
    "recruiter_inbound": "A recruiter or company reached out first (InMail, email, call)",
    "referral": "Applied through an employee referral",
    "cold_email": "The user emailed a founder, hiring manager or recruiter directly",
    "linkedin_dm": "The user messaged someone on LinkedIn directly",
}

STATUSES = {
    "lead": "A target not contacted yet (e.g. a founder from a contacts list)",
    "saved": "A posting worth applying to; not applied yet",
    "applied": "Application sent, no response yet",
    "in_review": "They acknowledged or are actively reviewing (beyond an auto-confirmation)",
    "assessment": "Online test or take-home assigned",
    "interviewing": "Any interview round scheduled or done (put the round in stage)",
    "offer": "Offer received",
    "accepted": "Offer accepted",
    "rejected": "They said no",
    "withdrawn": "The user pulled out",
    "ghosted": "No response long after applying or following up",
    "closed": "Posting closed or dropped before applying",
    "cold_sent": "Cold email or DM sent, waiting for a reply",
    "replied": "They replied to a cold email, DM or inbound message; conversation open",
}
OPEN = {"lead", "saved", "applied", "in_review", "assessment", "interviewing", "offer", "cold_sent", "replied"}
CLOSED = set(STATUSES) - OPEN
WORK_MODES = {"", "remote", "hybrid", "onsite"}
DATE_FIELDS = {"date_found", "date_applied", "last_update", "date_closed", "next_action_due"}


def today():
    return dt.date.today().isoformat()


def load():
    if not CSV_PATH.exists():
        return []
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(rows):
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Open rows first, then closed; newest first within each group.
    rows.sort(key=lambda r: r.get("date_applied") or r.get("date_found") or "", reverse=True)
    rows.sort(key=lambda r: r["status"] in CLOSED)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})


def slug(company, role):
    s = f"{company}-{role}".lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60]


def validate(row):
    errs = []
    if row.get("category") and row["category"] not in CATEGORIES:
        errs.append(f"category must be one of {sorted(CATEGORIES)}")
    if row.get("status") and row["status"] not in STATUSES:
        errs.append(f"status must be one of {sorted(STATUSES)}")
    if row.get("work_mode", "") not in WORK_MODES:
        errs.append(f"work_mode must be one of {sorted(WORK_MODES - {''})}")
    for k in DATE_FIELDS:
        v = row.get(k, "")
        if v:
            try:
                dt.date.fromisoformat(v)
            except ValueError:
                errs.append(f"{k} must be YYYY-MM-DD, got {v!r}")
    if errs:
        sys.exit("error: " + "; ".join(errs))


def days_since(d, ref):
    if not d:
        return None
    return (dt.date.fromisoformat(ref) - dt.date.fromisoformat(d)).days


def add_field_args(p):
    for f in FIELDS:
        if f != "id":
            p.add_argument(f"--{f}", default=None)


def cmd_add(a):
    rows = load()
    vals = {f: getattr(a, f) for f in FIELDS if f != "id" and getattr(a, f) is not None}
    if not vals.get("company") or not vals.get("role"):
        sys.exit("error: --company and --role are required")
    rid = a.id or slug(vals["company"], vals["role"])
    existing = next((r for r in rows if r["id"] == rid), None)
    if existing:
        sys.exit(f"error: {rid} already exists; use `update {rid}` (or pass --id for a distinct row)")
    row = {f: "" for f in FIELDS}
    row.update(vals)
    row["id"] = rid
    row.setdefault("status", "applied")
    row["status"] = row["status"] or "applied"
    row["date_found"] = row["date_found"] or row["date_applied"] or today()
    row["last_update"] = row["last_update"] or today()
    validate(row)
    rows.append(row)
    save(rows)
    print(f"added {rid}")


def cmd_update(a):
    rows = load()
    row = next((r for r in rows if r["id"] == a.id), None)
    if not row:
        sys.exit(f"error: no row with id {a.id}; try `find`")
    for f in FIELDS:
        v = getattr(a, f, None)
        if f != "id" and v is not None:
            if f == "notes" and row["notes"] and not a.replace_notes:
                row["notes"] = f"{row['notes']} | {v}"
            else:
                row[f] = v
    if a.last_update is None:
        row["last_update"] = today()
    if row["status"] in CLOSED and not row["date_closed"]:
        row["date_closed"] = row["last_update"]
    validate(row)
    save(rows)
    print(f"updated {a.id}: status={row['status']}")


def show(rows, cols=("id", "status", "category", "company", "role", "date_applied", "last_update", "next_action")):
    if not rows:
        print("(none)")
        return
    # Never truncate id: it's what `update` takes.
    widths = {c: max(len(c), *(len(r.get(c, "")) for r in rows)) if c == "id" else min(max(len(c), *(len(r.get(c, "")) for r in rows)), 40) for c in cols}
    print("  ".join(c.ljust(widths[c]) for c in cols))
    for r in rows:
        print("  ".join(r.get(c, "")[: widths[c]].ljust(widths[c]) for c in cols))


def cmd_find(a):
    q = a.text.lower()
    show([r for r in load() if any(q in r.get(k, "").lower() for k in ("id", "company", "role", "contact", "contact_email", "platform"))])


def cmd_list(a):
    rows = load()
    if a.status:
        rows = [r for r in rows if r["status"] == a.status]
    if a.category:
        rows = [r for r in rows if r["category"] == a.category]
    if a.open:
        rows = [r for r in rows if r["status"] in OPEN]
    if a.closed:
        rows = [r for r in rows if r["status"] in CLOSED]
    show(rows)


def due_reason(r, ref):
    s = r["status"]
    since_update = days_since(r["last_update"], ref) or 0
    if r["next_action_due"] and r["next_action_due"] <= ref:
        return f"due {r['next_action_due']}: {r['next_action'] or 'next action'}"
    if s == "saved" and since_update >= 7:
        return f"saved {since_update}d ago: apply or close it"
    if s == "cold_sent":
        if since_update >= 14:
            return f"no reply in {since_update}d: mark ghosted"
        if since_update >= 5:
            return f"no reply in {since_update}d: send one short follow-up"
    if s in {"applied", "in_review"}:
        if since_update >= 30:
            return f"silent {since_update}d: mark ghosted"
        if since_update >= 14 and r["category"] in {"referral", "recruiter_inbound", "job_board"}:
            return f"silent {since_update}d: nudge the contact"
    if s in {"interviewing", "assessment", "replied"} and since_update >= 5:
        return f"{s}, quiet for {since_update}d: follow up"
    if s == "offer" and since_update >= 2:
        return "offer pending: decide or negotiate"
    return None


def cmd_due(a):
    ref = a.today or today()
    hits = []
    for r in load():
        if r["status"] not in OPEN or r["status"] == "lead":
            continue
        why = due_reason(r, ref)
        if why:
            hits.append({**r, "why": why})
    show(hits, cols=("id", "status", "company", "role", "why"))
    leads = [r for r in load() if r["status"] == "lead"]
    if leads:
        print(f"\n{len(leads)} cold-email leads not contacted yet (`list --status lead`).")


def cmd_stats(a):
    rows = load()
    by_status, by_cat = {}, {}
    for r in rows:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
        by_cat.setdefault(r["category"], {"total": 0, "responded": 0, "positive": 0})
        c = by_cat[r["category"]]
        if r["status"] in {"lead", "saved", "closed"}:
            continue
        c["total"] += 1
        if r["status"] not in {"applied", "cold_sent", "ghosted"}:
            c["responded"] += 1
        if r["status"] in {"in_review", "assessment", "interviewing", "offer", "accepted", "replied"}:
            c["positive"] += 1
    print("By status:")
    for s in STATUSES:
        if by_status.get(s):
            print(f"  {s:13} {by_status[s]}")
    print("\nBy channel (excluding leads, saved and closed):")
    print(f"  {'category':20} {'sent':>5} {'any reply':>10} {'positive':>9}")
    for k, c in sorted(by_cat.items(), key=lambda kv: -kv[1]["total"]):
        if c["total"]:
            print(f"  {k:20} {c['total']:>5} {c['responded']:>10} {c['positive']:>9}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("add")
    pa.add_argument("--id", default=None)
    add_field_args(pa)
    pa.set_defaults(fn=cmd_add)

    pu = sub.add_parser("update")
    pu.add_argument("id")
    pu.add_argument("--replace-notes", action="store_true", help="overwrite notes instead of appending")
    add_field_args(pu)
    pu.set_defaults(fn=cmd_update)

    pf = sub.add_parser("find")
    pf.add_argument("text")
    pf.set_defaults(fn=cmd_find)

    pl = sub.add_parser("list")
    pl.add_argument("--status")
    pl.add_argument("--category")
    pl.add_argument("--open", action="store_true")
    pl.add_argument("--closed", action="store_true")
    pl.set_defaults(fn=cmd_list)

    pd = sub.add_parser("due")
    pd.add_argument("--today")
    pd.set_defaults(fn=cmd_due)

    ps = sub.add_parser("stats")
    ps.set_defaults(fn=cmd_stats)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
