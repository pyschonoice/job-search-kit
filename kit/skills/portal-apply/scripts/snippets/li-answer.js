/* LinkedIn Easy Apply: answer the questions on the current dialog page by matching question text.
ARGS: {"answers": [{"q": "<regex, case-insensitive, matched against the question text>", "a": "<option text for radios/selects, or text for inputs>"}]}
Radios are LinkedIn's custom div[role=radio] whose aria-label is the question. Numeric-only fields ("notice period" often) reject text: pass a plain number.
Returns: every question on the page with its current answer, and any validation errors. Unmatched questions are listed as UNANSWERED. */
async (page) => {
  const ARGS = __ARGS__;
  const d = page.getByRole('dialog').first();
  const log = [];
  for (const { q, a } of ARGS.answers) {
    const re = new RegExp(q, 'i');
    let done = false;
    // radios
    const groups = d.getByRole('radiogroup');
    for (let i = 0; i < (await groups.count()) && !done; i++) {
      const g = groups.nth(i);
      const qt = (await g.locator('div[role=radio]').first().getAttribute('aria-label').catch(() => '')) || (await g.evaluate((e) => (e.closest('fieldset')?.innerText || e.parentElement?.innerText || '')));
      if (re.test(qt)) {
        await g.locator('div[role=radio]').filter({ hasText: new RegExp('^\\s*' + a.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\s*$', 'i') }).first().click();
        log.push(`radio "${qt.slice(0, 60)}" -> ${a}`); done = true;
      }
    }
    if (done) continue;
    // selects
    const sels = d.locator('select');
    for (let i = 0; i < (await sels.count()) && !done; i++) {
      const s = sels.nth(i);
      const lab = await s.evaluate((e) => (e.id && document.querySelector(`label[for="${e.id}"]`)?.innerText) || e.getAttribute('aria-label') || e.parentElement?.innerText || '');
      if (re.test(lab)) { await s.selectOption({ label: a }).catch(async () => s.selectOption(a)); log.push(`select "${lab.slice(0, 60)}" -> ${a}`); done = true; }
    }
    if (done) continue;
    // text inputs / textareas
    const tbs = d.locator('input[type=text], input[type=number], input:not([type]), textarea');
    for (let i = 0; i < (await tbs.count()) && !done; i++) {
      const t = tbs.nth(i);
      const lab = await t.evaluate((e) => (e.id && document.querySelector(`label[for="${e.id}"]`)?.innerText) || e.getAttribute('aria-label') || '');
      if (re.test(lab)) { await t.fill(String(a)); log.push(`text "${lab.slice(0, 60)}" -> ${a}`); done = true; }
    }
    if (!done) log.push(`NO MATCH for /${q}/`);
  }
  await page.waitForTimeout(500);
  // read back
  const state = await d.evaluate((root) => {
    const out = [];
    root.querySelectorAll('[role=radiogroup]').forEach((g) => {
      const q = g.querySelector('div[role=radio]')?.getAttribute('aria-label') || '';
      const c = [...g.querySelectorAll('input[type=radio]')].findIndex((x) => x.checked);
      const opts = [...g.querySelectorAll('div[role=radio]')].map((x) => x.innerText.trim());
      out.push(`${c >= 0 ? '' : 'UNANSWERED '}radio: ${q.slice(0, 80)} = ${c >= 0 ? opts[c] : '-'}`);
    });
    root.querySelectorAll('input[type=text], input[type=number], textarea, select').forEach((e) => {
      const lab = (e.id && root.querySelector(`label[for="${e.id}"]`)?.innerText) || e.getAttribute('aria-label') || '';
      const v = e.tagName === 'SELECT' ? e.options[e.selectedIndex]?.text : e.value;
      if (!/search/i.test(lab)) out.push(`${v ? '' : 'UNANSWERED '}${e.tagName.toLowerCase()}: ${lab.trim().slice(0, 80)} = ${v}`);
    });
    return out.join('\n');
  });
  const err = (await d.locator('[role=alert], .artdeco-inline-feedback--error').allInnerTexts().catch(() => [])).filter((x) => x.trim());
  return log.join('\n') + '\n--- page state\n' + state + (err.length ? '\nERRORS: ' + err.join(' | ') : '');
}
