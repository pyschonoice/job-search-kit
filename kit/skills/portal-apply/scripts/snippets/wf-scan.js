/* Wellfound: scan role listing pages (logged in) and return one compact row per job, already filtered for the user.
ARGS: {"pages": ["https://wellfound.com/role/l/ai-engineer/bangalore", ".../software-engineer/bangalore?page=2"], "maxYears": 3, "maxAgeDays": 31, "drop": "<regex on title, optional; defaults below>"}
Fetches each page with the browser's session (no navigation, so open tabs are safe) and parses the HTML. Meta is read node by node, because the raw text glues fields together ("<your city>+2" + "2 years" = "<your city>+22 years").
Keeps rows whose years-of-exp is unknown or <= maxYears and whose age is <= maxAgeDays. Default drop: senior/staff/lead/principal/head/manager/architect/intern/ios/android/frontend/qa/sdet/devops/sre/designer/sales/java.
Returns: "KEPT n / seen m" then one line per job: age | company (size) | title | years | salary | location | url, plus a DROPPED summary by reason. */
async (page) => {
  const ARGS = __ARGS__;
  return await page.evaluate(async (A) => {
    const drop = new RegExp(A.drop || '\\b(senior|sr\\.?|staff|lead|principal|head|manager|architect|director|vp|intern|internship|ios|android|react native|frontend|front-end|qa|sdet|devops|sre|designer|sales|marketing|java|\\.net|golang)\\b', 'i');
    const maxY = A.maxYears ?? 3, maxAge = A.maxAgeDays ?? 31;
    const ageDays = (s) => {
      if (/today|hour|minute/i.test(s)) return 0;
      if (/yesterday/i.test(s)) return 1;
      const m = s.match(/(\d+)\s+(day|week|month|year)s?\s+ago/i);
      if (!m) return null;
      return +m[1] * { day: 1, week: 7, month: 30, year: 365 }[m[2].toLowerCase()];
    };
    const nodes = (el) => { const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); const out = []; let n; while ((n = w.nextNode())) { const t = n.textContent.trim(); if (t) out.push(t); } return out; };
    const seen = new Map(), dropped = {};
    for (const url of A.pages) {
      let html;
      try { html = await (await fetch(url, { credentials: 'include' })).text(); } catch (e) { dropped['fetch error ' + url] = 1; continue; }
      const d = new DOMParser().parseFromString(html, 'text/html');
      for (const a of d.querySelectorAll('a[href^="/jobs/"]')) {
        const href = a.getAttribute('href');
        if (!/^\/jobs\/\d+/.test(href) || seen.has(href)) continue;
        // job row: nearest ancestor that also holds the "posted" text
        let row = a; while (row && !/(ago|today|yesterday)\b/i.test(row.textContent)) row = row.parentElement;
        let card = a; while (card && !card.querySelector('a[href^="/company/"]')) card = card.parentElement;
        const compA = card ? [...card.querySelectorAll('a[href^="/company/"]')].find((x) => x.textContent.trim()) : null;
        const parts = row ? nodes(row) : [a.textContent.trim()];
        const title = a.textContent.trim().split('\n')[0];
        // years render as separate nodes: "+", "2" (extra cities), "2", "years", " of exp"
        const yi = parts.findIndex((p, i) => /^years?$/i.test(p) && /of exp/i.test(parts[i + 1] || ''));
        const years = yi > 0 && /^\d+$/.test(parts[yi - 1]) ? parts[yi - 1] : (parts.join(' ').match(/(\d+)\s+years?\s+of\s+exp/i) || [])[1];
        const posted = parts.find((p) => /(ago|today|yesterday)$/i.test(p)) || '';
        const salary = parts.find((p) => /[₹$€£]\s?\d/.test(p)) || '';
        const loc = parts.find((p) => /•|Remote|<your city>|<your city>|India|Everywhere/i.test(p) && !/[₹$]/.test(p)) || '';
        const size = card ? ((card.textContent.match(/\d[\d,]*-?\d*\+? Employees/) || [''])[0]) : '';
        seen.set(href, { url: 'https://wellfound.com' + href.split('?')[0], title, company: compA ? compA.textContent.trim() : '?', size, years: years ? +years : null, age: ageDays(posted), posted, salary, loc });
      }
    }
    const kept = [];
    for (const r of seen.values()) {
      const why = drop.test(r.title) ? 'title' : (r.years != null && r.years > maxY) ? `years>${maxY}` : (r.age != null && r.age > maxAge) ? `older than ${maxAge}d` : null;
      if (why) { dropped[why] = (dropped[why] || 0) + 1; continue; }
      kept.push(r);
    }
    kept.sort((x, y) => (x.age ?? 999) - (y.age ?? 999));
    const lines = kept.map((r) => `${r.posted || '?'} | ${r.company} (${r.size || '?'}) | ${r.title} | ${r.years ?? '?'}y | ${r.salary} | ${r.loc} | ${r.url}`);
    return `KEPT ${kept.length} / seen ${seen.size}\n` + lines.join('\n') + '\nDROPPED ' + JSON.stringify(dropped);
  }, ARGS);
}
