"""For each candidate domain: does it resolve, page title, MX, and any emails published on common pages."""
import re, subprocess, sys, json, urllib.request, ssl, concurrent.futures as cf
ctx = ssl.create_default_context()
PAGES = ["", "contact", "contact-us", "careers", "about", "about-us", "privacy", "privacy-policy", "terms", "jobs", "team"]
EM = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}")
def get(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        return urllib.request.urlopen(req, timeout=12, context=ctx).read(400000).decode("utf-8", "ignore")
    except Exception:
        return ""
def mx(d):
    out = subprocess.run(["dig", "+short", "MX", d], capture_output=True, text=True).stdout.split()
    return " ".join(out[1::2])[:60]
def scan(d):
    title, emails = "", set()
    for p in PAGES:
        h = get(f"https://{d}/{p}")
        if not h: continue
        if p == "":
            m = re.search(r"<title[^>]*>(.*?)</title>", h, re.S | re.I); title = (m.group(1).strip()[:70] if m else "")
        for e in EM.findall(h):
            if not e.lower().endswith((".png", ".jpg", ".webp", ".svg", ".gif")) and "sentry" not in e and "example" not in e:
                emails.add(e.lower())
    return {"domain": d, "title": title, "mx": mx(d), "emails": sorted(emails)[:12]}
doms = sys.argv[1:]
with cf.ThreadPoolExecutor(12) as ex:
    for r in ex.map(scan, doms):
        print(json.dumps(r))
