/* Workday "Application Questions" (and similar pages): list every dropdown with its real question text, and optionally answer them.
ARGS: {"answers": [{"q": "<regex on question>", "a": "<regex on option>"}], "text": [{"q": "<regex>", "a": "<text>"}], "date": "MM/DD/YYYY" (fills the first date field, e.g. earliest start), "list_only": false}
The dropdown buttons' aria-labels don't contain the question, so the question is read from the nearest ancestor with text. Follow-up questions (e.g. "If yes, 3 days per week?") appear after an answer, so the script re-scans after each pick.
Returns: every question = current answer, marking UNANSWERED ones, plus the options of unanswered ones so you can ask the user. */
async (page) => {
  const ARGS = __ARGS__;
  const scan = () => page.locator('button[aria-haspopup=listbox]').evaluateAll((bs) => bs.map((b, i) => {
    let p = b; for (let k = 0; k < 8; k++) { p = p.parentElement; if (p && p.innerText && p.innerText.length > 25) break; }
    const q = (p ? p.innerText : '').replace(/\s+/g, ' ').replace(b.innerText, '').trim();
    return { i, q: q.slice(0, 160), v: b.innerText.trim() };
  }));
  const log = [];
  if (!ARGS.list_only) {
    for (const { q, a } of ARGS.answers || []) {
      const items = await scan();
      const it = items.find((x) => new RegExp(q, 'i').test(x.q));
      if (!it) { log.push(`NO QUESTION /${q}/`); continue; }
      const b = page.locator('button[aria-haspopup=listbox]').nth(it.i);
      await b.click(); await page.waitForTimeout(700);
      const opts = page.getByRole('option'); const t = (await opts.allInnerTexts()).map((x) => x.trim());
      const k = t.findIndex((x) => new RegExp(a, 'i').test(x) && x !== 'Select One');
      if (k < 0) { await page.keyboard.press('Escape'); log.push(`NO OPTION /${a}/ for "${it.q.slice(0, 60)}" in ${t.join(' / ')}`); continue; }
      await opts.nth(k).click(); await page.waitForTimeout(500);
    }
    for (const { q, a } of ARGS.text || []) {
      const ta = page.locator('textarea, input[type=text]').filter({ hasNot: page.locator('[role=spinbutton]') });
      const n = await ta.count(); let done = false;
      for (let i = 0; i < n && !done; i++) {
        const lab = await ta.nth(i).evaluate((e) => { let p = e; for (let k = 0; k < 8; k++) { p = p.parentElement; if (p && p.innerText && p.innerText.length > 15) break; } return p ? p.innerText : ''; });
        if (new RegExp(q, 'i').test(lab)) { await ta.nth(i).fill(a); done = true; }
      }
      log.push(done ? `text /${q}/ filled` : `NO TEXT FIELD /${q}/`);
    }
    if (ARGS.date) {
      const [mm, dd, yyyy] = ARGS.date.split('/');
      const f = page.locator('[data-automation-id="dateSectionMonth-input"]').first();
      if (await f.count()) { await f.focus(); await page.keyboard.type(mm + dd + yyyy, { delay: 100 }); await page.keyboard.press('Tab'); await page.waitForTimeout(400);
        log.push('date=' + (await page.locator('[data-automation-id="dateInputWrapper"]').first().innerText()).replace(/\s+/g, '')); }
    }
  }
  const final = await scan();
  for (const x of final) {
    if (x.v === 'Select One') {
      const b = page.locator('button[aria-haspopup=listbox]').nth(x.i);
      await b.click(); await page.waitForTimeout(500);
      const t = (await page.getByRole('option').allInnerTexts()).map((y) => y.trim()).filter((y) => y !== 'Select One');
      await page.keyboard.press('Escape');
      log.push(`UNANSWERED: ${x.q} {${t.join(' / ')}}`);
    } else log.push(`${x.q} = ${x.v}`);
  }
  return log.join('\n');
}
