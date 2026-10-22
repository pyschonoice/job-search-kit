/* Wellfound: read full job pages without navigating (fetch with the session) and return what fit-checking needs.
ARGS: {"urls": ["https://wellfound.com/jobs/4824688-voice-ai-engineer", ...], "chars": 3500}
Per job: title and company (from <title>), company size and stage, salary, the sidebar facts (Location, Remote work policy, Hires remotely in, Experience, Relocation, Visa), the hiring contact / team names, every "N years" phrase in the JD, and the JD text (first `chars` characters after the Apply button).
Returns: one block per URL, separated by =====. */
async (page) => {
  const ARGS = __ARGS__;
  return await page.evaluate(async (A) => {
    const out = [];
    for (const u of A.urls) {
      try {
        const h = await (await fetch(u, { credentials: 'include' })).text();
        const d = new DOMParser().parseFromString(h, 'text/html');
        const title = d.title.replace(/\s*\|\s*Wellfound\s*$/, '');
        d.querySelectorAll('script,style,noscript').forEach((e) => e.remove());
        const w = d.createTreeWalker(d.body, NodeFilter.SHOW_TEXT); const parts = []; let n;
        while ((n = w.nextNode())) { const t = n.textContent.trim(); if (t) parts.push(t); }
        const t = parts.join(' | ');
        // sidebar value can be split ("2", "+ years"): join nodes until the next known label
        const LABELS = ['Location', 'Remote work policy', 'Hires remotely in', 'Job type', 'Experience', 'Relocation', 'Visa sponsorship', 'Skills', 'Meet your team', 'Hiring contact'];
        const after = (label) => { const i = parts.findIndex((p) => p === label); if (i < 0) return ''; const v = []; for (let j = i + 1; j < parts.length && j < i + 6 && !LABELS.includes(parts[j].replace(/\s+/g, ' ')); j++) v.push(parts[j]); return v.join(' ').replace(/\s+\+/g, '+'); };
        const facts = ['Location', 'Remote work policy', 'Hires remotely in', 'Job type', 'Experience', 'Relocation', 'Visa sponsorship'].map((k) => `${k}: ${after(k)}`).filter((x) => !/: $/.test(x)).join(' · ');
        const size = (t.match(/\d[\d,]*-?\d*\+? Employees/) || [''])[0];
        const stage = (t.match(/\b(Seed|Early|Growth|Scale|Public) Stage\b/) || [''])[0];
        const salary = parts.find((p) => /[₹$€£]\s?\d.*[–-]/.test(p)) || '';
        const contact = (t.match(/Hiring contact \| ([^|]+)/) || [])[1] || '';
        const team = (t.match(/Meet your team[^]*?People you would work with in this role \| ([^|]+ \| [^|]+)/) || [])[1] || '';
        const yrs = [...new Set((t.match(/[^|.]{0,40}\b\d+\s*(?:[-–to]+\s*\d+\s*)?\+?\s*years?\b[^|.]{0,50}/gi) || []).map((s) => s.trim()))].slice(0, 6);
        const start = Math.max(parts.findIndex((p) => /^Apply now$|^Save$/.test(p)), 0);
        const body = parts.slice(start + 1).join(' ').replace(/\sApply now\s[^]*$/, '');
        out.push(`===== ${title}\n${u}\nsize: ${size} ${stage} · salary: ${salary}\n${facts}\ncontact: ${contact || '-'} · team: ${team || '-'}\nyears mentioned: ${yrs.join(' || ') || '-'}\n--- JD\n${body.slice(0, A.chars || 3500)}`);
      } catch (e) { out.push(`===== ${u}\nERROR ${e}`); }
    }
    return out.join('\n');
  }, ARGS);
}
