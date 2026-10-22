/* Wellfound: open a job's apply panel, report its questions, and (unless dump-only) fill them. NEVER clicks "Send application".
ARGS: {"url": "https://wellfound.com/jobs/<id>-<slug>" (optional: uses the current page), "answers": [{"q": "<regex on the question label>", "a": "<answer>"}], "dump": false}
Status first: a "✓ Applied" button or "Your application has been sent" means it's already done, and the script stops. A missing "Apply now" usually means the job is closed or the profile is incomplete.
The panel sends the **profile** resume (see wf-resume) plus these custom questions. Typical ones: "What interests you about working for this company?" (textarea), Phone (text), sometimes a yes/no select. Jobs with no custom questions show a single "Cover Letter" textarea (name userNote): match it with q "cover letter". Phone is filled from profile.json automatically when a label matches /phone/ and no answer is given.
Returns: status, every question with its type and current value length, NO MATCH lines for answers that didn't land, and EMPTY REQUIRED for anything still blank. */
async (page) => {
  const ARGS = __ARGS__;
  const P = ARGS.profile;
  if (ARGS.url && !page.url().startsWith(ARGS.url)) { await page.goto(ARGS.url); await page.waitForTimeout(2500); }
  const btns = async () => page.evaluate(() => [...document.querySelectorAll('button')].map((b) => b.innerText.trim()));
  const sent = async () => page.evaluate(() => /application has been sent/i.test([...document.querySelectorAll('[role="dialog"]')].map((d) => d.innerText).join(' ')));
  let b = await btns();
  if (b.some((t) => /✓\s*Applied/.test(t)) || (await sent())) return 'STATUS: already applied';
  if (!b.some((t) => /^Apply now$|^Apply$/.test(t))) return 'STATUS: no Apply button (closed, or profile incomplete). Buttons: ' + JSON.stringify(b.filter((t) => t).slice(0, 15));
  const dlg = page.locator('[role="dialog"]').filter({ hasText: 'YOUR APPLICATION' });
  if (!(await dlg.count())) { await page.locator('button:has-text("Apply now")').first().click(); await page.waitForTimeout(1500); }
  const read = async () => page.evaluate(() => {
    const d = [...document.querySelectorAll('[role="dialog"]')].find((x) => /YOUR APPLICATION/.test(x.innerText));
    if (!d) return [];
    return [...d.querySelectorAll('textarea, input:not([type=hidden]), select')].filter((e) => e.offsetParent).map((e) => {
      let lab = (e.id && d.querySelector(`label[for="${CSS.escape(e.id)}"]`)?.innerText) || e.closest('label')?.innerText || '';
      if (!lab) { let p = e.parentElement; for (let i = 0; i < 4 && p && !lab; i++, p = p.parentElement) { const l = p.querySelector('label'); if (l) lab = l.innerText; } }
      // jobs without custom questions show one textarea "userNote" captioned "Cover Letter" (a sibling div, not a label)
      if (e.name === 'userNote') lab = 'Cover Letter (note to the company)';
      if (!lab) lab = e.placeholder || '';
      return { name: e.name, tag: e.tagName.toLowerCase(), type: e.type, label: lab.trim().replace(/\s+/g, ' '), required: e.required || /\*\s*$/.test(lab.trim()), len: (e.value || '').length };
    });
  });
  const log = [];
  let fields = await read();
  if (!ARGS.dump) {
    const answers = [...(ARGS.answers || [])];
    if (!answers.some((x) => /phone/i.test(x.q))) answers.push({ q: 'phone', a: P.phone_intl });
    for (const { q, a } of answers) {
      const re = new RegExp(q, 'i');
      const f = fields.find((x) => re.test(x.label));
      if (!f) { if (!/phone/i.test(q) || ARGS.answers?.some((x) => x.q === q)) log.push(`NO MATCH /${q}/`); continue; }
      const loc = page.locator(`[role="dialog"] [name="${f.name}"]`).first();
      if (f.tag === 'select') await loc.selectOption({ label: a });
      else await loc.fill(a);
      log.push(`ok /${q}/ -> ${f.name}`);
    }
    fields = await read();
  }
  const lines = fields.map((f) => `${f.required ? '*' : ' '} [${f.tag}${f.type && f.tag === 'input' ? ':' + f.type : ''}] ${f.label || f.name} = ${f.len} chars`);
  const empty = fields.filter((f) => f.required && !f.len).map((f) => 'EMPTY REQUIRED: ' + (f.label || f.name));
  return ['STATUS: panel open, NOT sent', ...log, '--- fields', ...lines, ...empty].join('\n');
}
