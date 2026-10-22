/* Workday step "My Experience": replace the parser's mangled work history with profile.jobs (4 jobs), set dates, languages (English 5 - Fluent), websites, and try the school.
ARGS: {"school_query": "<your university name>", "drop_education_if_missing": true}
Dates: Workday's month/year spinbuttons ignore fill(); click the month segment and type digits ("4", then year). Pre-filled segments are overwritten by typing.
Education is optional on most tenants; when the school isn't in the list (<your university> usually isn't) the half-filled entry blocks Next, so it's deleted when drop_education_if_missing is true. Report that to the user.
Returns: job titles and dates as Workday now shows them, language levels, websites, education result. */
async (page) => {
  const ARGS = __ARGS__;
  const P = ARGS.profile;
  const log = [];
  const close = async () => { await page.mouse.click(5, 5); await page.waitForTimeout(300); };
  // --- jobs
  for (let i = 0; i < P.jobs.length; i++) {
    const j = P.jobs[i];
    if ((await page.getByRole('textbox', { name: 'Job Title' }).count()) <= i) {
      await page.getByRole('button', { name: 'Add Another' }).first().click(); await page.waitForTimeout(1200);
    }
    const tb = (n) => page.getByRole('textbox', { name: n }).nth(i);
    await tb('Job Title').fill(j.title); await tb('Company').fill(j.company); await tb('Location').fill(j.location);
    const cb = page.getByRole('checkbox', { name: 'I currently work here' }).nth(i);
    if ((await cb.isChecked()) !== j.current) { await cb.click(); await page.waitForTimeout(500); }
    await tb('Role Description').fill(j.desc);
  }
  // delete extra parsed jobs beyond profile.jobs
  while ((await page.getByRole('textbox', { name: 'Job Title' }).count()) > P.jobs.length) {
    const n = await page.getByRole('textbox', { name: 'Job Title' }).count();
    const box = page.locator('div').filter({ has: page.getByRole('textbox', { name: 'Job Title' }).nth(n - 1) }).filter({ has: page.getByRole('button', { name: /Delete/ }) }).last();
    await box.getByRole('button', { name: /Delete/ }).first().click(); await page.waitForTimeout(800);
  }
  const setDate = async (field, idx, mm, yyyy) => {
    const f = page.locator(`[data-automation-id="formField-${field}"]`).nth(idx);
    const mi = f.locator('[data-automation-id="dateSectionMonth-input"]');
    await mi.click({ force: true }).catch(() => mi.focus());
    await page.keyboard.type(String(parseInt(mm, 10)), { delay: 120 });
    const yi = f.locator('[data-automation-id="dateSectionYear-input"]');
    await yi.click({ force: true }).catch(() => yi.focus());
    await page.keyboard.type(yyyy, { delay: 100 });
    await page.keyboard.press('Tab'); await page.waitForTimeout(300);
    return (await f.innerText()).replace(/\s+/g, ' ').replace(/.*current value is /, '').slice(0, 20);
  };
  let e = 0;
  for (let i = 0; i < P.jobs.length; i++) {
    const j = P.jobs[i];
    const s = await setDate('startDate', i, j.from_mm, j.from_yyyy);
    let t = 'present';
    if (!j.current) { t = await setDate('endDate', e, j.to_mm, j.to_yyyy); e++; }
    log.push(`${j.title} @ ${j.company}: ${s} -> ${t}`);
  }
  // --- education
  const sc = page.locator('[data-automation-id="formField-school"] input').first();
  if (await sc.count()) {
    await close(); await sc.focus(); await sc.fill(ARGS.school_query || ''); await page.keyboard.press('Enter'); await page.waitForTimeout(2200);
    const po = page.locator('[data-automation-id="promptOption"]'); const t = await po.allInnerTexts();
    const i = t.findIndex((x) => (ARGS.school_query || '').toLowerCase() && x.toLowerCase().includes(ARGS.school_query.toLowerCase()));
    if (i >= 0) { await po.nth(i).click(); log.push('school=' + t[i]); }
    else if (ARGS.drop_education_if_missing !== false) {
      await sc.fill(''); await close();
      const box = page.locator('div').filter({ has: page.locator('[data-automation-id="formField-school"]') }).filter({ has: page.getByRole('button', { name: /Delete/ }) }).last();
      await box.getByRole('button', { name: /Delete/ }).first().click(); await page.waitForTimeout(800);
      log.push('education: school not in list -> entry deleted (tell the user)');
    } else log.push('education: school not found, left for the user');
  }
  // --- languages
  for (const k of ['Comprehension', 'Overall', 'Reading', 'Speaking', 'Writing']) {
    const b = page.locator(`button[aria-label*="${k}"]`).first();
    if (!(await b.count())) continue;
    await b.click(); await page.waitForTimeout(600);
    await page.getByRole('option', { name: P.languages[0].level5, exact: true }).click().catch(() => page.keyboard.press('Escape'));
    await page.waitForTimeout(300);
  }
  const fl = page.getByRole('checkbox', { name: 'I am fluent in this language.' });
  if ((await fl.count()) && !(await fl.isChecked())) await fl.click();
  log.push('languages: ' + (await page.locator('button[aria-haspopup=listbox]').evaluateAll((b) => b.map((x) => x.getAttribute('aria-label')).filter((l) => /Comprehension|Overall|Reading|Speaking|Writing/.test(l || '')).join(' | '))));
  // --- websites (the "Add" under Websites is the LAST plain "Add" button; Certifications has one too)
  const urls = await page.getByRole('textbox', { name: /^URL/ }).evaluateAll((x) => x.map((y) => y.value));
  for (const u of [P.linkedin, P.github]) {
    if (urls.includes(u)) continue;
    const before = await page.getByRole('textbox', { name: /^URL/ }).count();
    const btn = before ? page.getByRole('button', { name: 'Add Another' }).last() : page.getByRole('button', { name: 'Add', exact: true }).last();
    await btn.click(); await page.waitForTimeout(800);
    const tbs = page.getByRole('textbox', { name: /^URL/ });
    if ((await tbs.count()) > before) await tbs.nth(before).fill(u); else log.push('websites: Add did not create a URL field (check Certifications got no empty entry)');
  }
  log.push('websites: ' + (await page.getByRole('textbox', { name: /^URL/ }).evaluateAll((x) => x.map((y) => y.value).join(', '))));
  log.push('certification entries (should be 0): ' + (await page.locator('[data-automation-id="formField-certification"]').count()));
  return log.join('\n');
}
