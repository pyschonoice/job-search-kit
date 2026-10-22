/* Workday step "My Information": overwrite the parser's values (names come back in CAPITALS) with profile data, and set source, previous-worker, state and phone type.
ARGS: {"source": "LinkedIn" (search term for How Did You Hear; picks the first option containing it, e.g. "LinkedIn Applied" or "Job Board > Linkedin"), "previous_worker": "No"}
Returns: each field and the value it now holds. Run on the My Information page, then click Next yourself. */
async (page) => {
  const ARGS = __ARGS__;
  const P = ARGS.profile;
  const log = [];
  const inp = (s) => page.locator(`[data-automation-id="formField-${s}"] input`).first();
  const fill = async (s, v) => { const l = inp(s); if (!(await l.count())) return log.push(`${s}: (no field)`); await l.fill(''); await l.fill(v); await l.press('Tab'); log.push(`${s}=${await l.inputValue()}`); };
  await fill('legalName--firstName', P.first);
  await fill('legalName--lastName', P.last);
  await fill('addressLine1', P.address.line1);
  await fill('addressLine2', P.address.line2);
  await fill('city', P.address.city);
  await fill('postalCode', P.address.pin);
  await fill('phoneNumber', P.phone10);
  // previous worker
  const pw = page.locator('[data-automation-id="formField-candidateIsPreviousWorker"]');
  if (await pw.count()) { await pw.getByText(ARGS.previous_worker || 'No', { exact: true }).click(); log.push('previous worker=' + (ARGS.previous_worker || 'No')); }
  // listbox picker: open, choose option whose text matches re (accent-insensitive: Workday spells Karnātaka)
  const norm = (s) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').trim().toLowerCase();
  const pick = async (field, want) => {
    const b = page.locator(`[data-automation-id="formField-${field}"] button`).first();
    if (!(await b.count())) return log.push(`${field}: (no field)`);
    await b.click(); await page.waitForTimeout(700);
    const opts = page.getByRole('option'); const txt = await opts.allInnerTexts();
    const i = txt.findIndex((t) => norm(t) === norm(want));
    if (i < 0) { await page.keyboard.press('Escape'); return log.push(`${field}: no option "${want}" in ${txt.slice(0, 12).join('/')}`); }
    await opts.nth(i).click(); await page.waitForTimeout(400); log.push(`${field}=${await b.innerText()}`);
  };
  await pick('countryRegion', P.address.state);
  await pick('phoneType', 'Mobile');
  // source: multiselect prompt with search
  const src = page.locator('[data-automation-id="formField-source"] input').first();
  if (await src.count()) {
    await src.click(); await src.fill(ARGS.source || 'LinkedIn'); await src.press('Enter'); await page.waitForTimeout(1800);
    const po = page.locator('[data-automation-id="promptOption"]'); const t = await po.allInnerTexts();
    const i = t.findIndex((x) => /linkedin/i.test(x) && !/sourced/i.test(x));
    if (i >= 0) { await po.nth(i).click(); await page.waitForTimeout(600); }
    await page.mouse.click(5, 5);
    log.push('source=' + (await page.locator('[data-automation-id="formField-source"]').innerText()).replace(/\s+/g, ' ').replace('How Did You Hear About Us?*', '').trim().slice(0, 60) + `  (options were: ${t.join(' / ')})`);
  }
  log.push('email=' + (await inp('emailAddress').inputValue().catch(() => '?')));
  return log.join('\n');
}
