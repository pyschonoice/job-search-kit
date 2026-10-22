/* LinkedIn Easy Apply: open the dialog on the current job page (if not open), pick the resume, and walk page by page up to (not past) the Review page. Stops early on a page with unanswered required questions or errors.
ARGS: {"resume": "ai" | "fs" | "<exact PDF file name already uploaded to LinkedIn>"}
Returns: page-by-page text (country-code list and resume list collapsed), the resume picked, and where it stopped. */
async (page) => {
  const ARGS = __ARGS__;
  const P = ARGS.profile;
  const want = ARGS.resume === 'ai' ? P.resumes.ai.split('/').pop() : ARGS.resume === 'fs' ? P.resumes.fs.split('/').pop() : ARGS.resume;
  let d = page.getByRole('dialog').first();
  if (!(await d.count()) || !/Apply to/i.test(await d.innerText().catch(() => ''))) {
    await page.getByRole('button', { name: /Easy Apply/i }).first().click();
    await page.waitForTimeout(3000);
    d = page.getByRole('dialog').first();
  }
  const clean = (t) => t.replace(/\n{2,}/g, '\n').replace(/Phone country code\*[\s\S]*?Mobile/, 'Phone country code* … Mobile').replace(/(Resume\*\n[^\n]*\n)[\s\S]*?(?=Back\n|Next\n|Additional|$)/, '$1(resume list)\n');
  const pickResume = async () => {
    const radios = d.locator('input[type=radio]');
    const n = await radios.count();
    for (let k = 0; k < n; k++) {
      const lab = await radios.nth(k).evaluate((e) => { let p = e; for (let j = 0; j < 5; j++) { p = p.parentElement; if (p.innerText && p.innerText.length > 10) break; } return p.innerText.replace(/\s+/g, ' '); });
      if (lab.includes(want)) {
        if (!(await radios.nth(k).isChecked())) {
          const id = await radios.nth(k).getAttribute('id');
          const l = d.locator(`label[for="${id}"]`);
          if (await l.count()) await l.first().click({ force: true }); else await radios.nth(k).check({ force: true });
          await page.waitForTimeout(500);
        }
        return `resume: ${lab.slice(0, 70)} checked=${await radios.nth(k).isChecked()}`;
      }
    }
    return `resume: ${want} NOT FOUND in LinkedIn's list (upload it first)`;
  };
  const steps = [];
  for (let i = 0; i < 8; i++) {
    const txt = await d.innerText();
    if (/Resume\*/.test(txt) && /Select or upload a resume/.test(txt)) steps.push(await pickResume());
    steps.push(`--- page ${i}\n` + clean(txt).slice(0, 1600));
    if (/Review your application/.test(txt)) { steps.push('(on Review page)'); break; }
    const btn = d.getByRole('button', { name: /^(Next|Review|Continue to next step|Review your application)$/i });
    if (!(await btn.count())) { steps.push('(no Next button)'); break; }
    const lbl = (await btn.first().innerText()).trim();
    const unanswered = await d.locator('[role=radiogroup]').evaluateAll((gs) => gs.filter((g) => !g.querySelector('input:checked')).length);
    const emptyText = await d.locator('input[type=text]:not([readonly]), textarea').evaluateAll((es) => es.filter((e) => e.required !== false && !e.value).length);
    if (/Review/i.test(lbl) && (unanswered || emptyText)) { steps.push(`(stopped: ${unanswered} unanswered radio groups, ${emptyText} empty text fields — answer with li-answer)`); break; }
    await btn.first().click();
    await page.waitForTimeout(1800);
    const err = (await d.locator('[role=alert], .artdeco-inline-feedback--error').allInnerTexts().catch(() => [])).filter((x) => x.trim());
    if (err.length) { steps.push('ERRORS: ' + err.join(' | ') + '\n' + clean(await d.innerText()).slice(0, 1200)); break; }
  }
  return steps.join('\n');
}
