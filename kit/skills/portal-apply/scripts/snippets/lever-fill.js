/* Lever (jobs.lever.co/<co>/<id>/apply): fill the standard fields, upload the resume, pick the location from Lever's autocomplete, and answer custom questions by text.
ARGS: {"resume": "ai" | "fs" | "<absolute pdf path>", "cards": [{"q": "<regex on question text>", "a": "<answer>"}], "location": "<your city>"}
Order matters: Lever re-parses the resume on upload and can clear "Current location", so the resume goes first and location last.
Never touches the consent/marketing checkbox or the Submit button. If the user's submit later fails with "There was an error verifying your application", that's Lever's bot check: the page reloads and drops the file; re-run with just the resume.
Returns: every field's value, the uploaded file name, and any unanswered required question. */
async (page) => {
  const ARGS = __ARGS__;
  const P = ARGS.profile;
  const pdf = ARGS.resume === 'ai' ? P.resumes.ai : ARGS.resume === 'fs' ? P.resumes.fs : ARGS.resume;
  const log = [];
  if (pdf) { await page.locator('input[type=file][name=resume], input[type=file]').first().setInputFiles(pdf); await page.waitForTimeout(3500); }
  const set = async (sel, v) => { const l = page.locator(sel).first(); if (await l.count()) { await l.fill(v); } };
  await set('input[name=name]', P.full);
  await set('input[name=email]', P.email);
  await set('input[name=phone]', P.phone_intl);
  await set('input[name=org]', P.current_employer);
  await set('input[name="urls[LinkedIn]"]', P.linkedin);
  await set('input[name="urls[GitHub]"]', P.github);
  // custom question cards: label text sits in the enclosing <li>
  for (const { q, a } of ARGS.cards || []) {
    const re = new RegExp(q, 'i'); let done = false;
    const inputs = page.locator('textarea[name^="cards["], input[type=text][name^="cards["]');
    for (let i = 0; i < (await inputs.count()) && !done; i++) {
      const lab = await inputs.nth(i).evaluate((e) => (e.closest('li')?.innerText || e.parentElement?.parentElement?.innerText || '').trim());
      if (re.test(lab)) { await inputs.nth(i).fill(a); done = true; }
    }
    if (!done) { // radio/checkbox/select cards
      const lis = page.locator('li').filter({ hasText: re });
      if (await lis.count()) {
        const li = lis.last();
        const opt = li.locator('label').filter({ hasText: new RegExp('^\\s*' + a + '\\s*$', 'i') });
        if (await opt.count()) { await opt.first().click(); done = true; }
        else if (await li.locator('select').count()) { await li.locator('select').first().selectOption({ label: a }); done = true; }
      }
    }
    log.push(`${done ? 'ok' : 'NO MATCH'} /${q}/`);
  }
  // location autocomplete last
  const loc = page.locator('input[name=location], #location-input').first();
  if (await loc.count()) {
    await loc.fill(''); await loc.pressSequentially(ARGS.location || P.address.city, { delay: 60 }); await page.waitForTimeout(1500);
    const opt = page.getByText(/^<City>, <District>, <State>, <CTRY>$/).first();
    if (await opt.count()) await opt.click(); else { const any = page.locator('.dropdown-results div').first(); if (await any.count()) await any.click(); }
    await page.waitForTimeout(500);
  }
  const state = await page.evaluate(() => {
    const r = [...document.querySelectorAll('input:not([type=hidden]):not([type=file]), textarea')].filter((e) => e.offsetParent).map((e) => `${(e.name || '').slice(-24)} = ${e.type === 'checkbox' || e.type === 'radio' ? e.checked : (e.value || '').slice(0, 50)}`);
    const f = [...document.querySelectorAll('input[type=file]')].map((x) => [...x.files].map((y) => y.name).join(',')).join(' ');
    const ok = /Success!/.test(document.body.innerText);
    const req = [...document.querySelectorAll('li')].filter((li) => /✱/.test(li.innerText) && li.querySelector('textarea, input[type=text]') && !li.querySelector('textarea, input[type=text]').value).map((li) => 'EMPTY REQUIRED: ' + li.innerText.split('\n')[0].slice(0, 80));
    return r.concat([`FILE: ${f} upload-success=${ok}`], req).join('\n');
  });
  return log.join('\n') + '\n--- state\n' + state;
}
