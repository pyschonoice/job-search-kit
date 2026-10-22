/* LinkedIn Easy Apply: from the current page, click Next/Review up to the Review page, check it, then submit. Only for Easy Apply (the user's standing rule).
ARGS: {"resume": "ai" | "fs" | "<file name>", "dry": false}
Refuses to submit when: the Review page shows a different resume, any answer is empty, or there's a validation error. "dry": true stops on Review and returns its text.
Returns: the Review page text and the confirmation ("Your application was sent to ...") or the reason it refused. */
async (page) => {
  const ARGS = __ARGS__;
  const P = ARGS.profile;
  const want = ARGS.resume === 'ai' ? P.resumes.ai.split('/').pop() : ARGS.resume === 'fs' ? P.resumes.fs.split('/').pop() : ARGS.resume;
  const d = page.getByRole('dialog').first();
  for (let i = 0; i < 6; i++) {
    const t = await d.innerText();
    if (/Review your application/.test(t)) break;
    const btn = d.getByRole('button', { name: /^(Next|Review)$/i });
    if (!(await btn.count())) return 'REFUSED: no Next/Review button\n' + t.slice(0, 800);
    await btn.first().click();
    await page.waitForTimeout(1800);
    const err = (await d.locator('[role=alert], .artdeco-inline-feedback--error').allInnerTexts().catch(() => [])).filter((x) => x.trim());
    if (err.length) return 'REFUSED: validation errors: ' + err.join(' | ');
  }
  const review = (await d.innerText()).replace(/\n{2,}/g, '\n').replace(/Phone country code[\s\S]*?Mobile/, '…Mobile');
  if (!/Review your application/.test(review)) return 'REFUSED: never reached Review\n' + review.slice(0, 800);
  if (want && !review.includes(want)) return `REFUSED: Review shows a different resume (wanted ${want})\n` + review.slice(0, 1500);
  if (ARGS.dry) return 'DRY RUN, on Review:\n' + review.slice(0, 2000);
  await d.getByRole('button', { name: 'Submit application', exact: true }).click();
  await page.waitForTimeout(3500);
  const conf = await page.getByRole('dialog').first().innerText().catch(() => '');
  return (/application was sent/i.test(conf) ? 'SUBMITTED. ' : 'UNCLEAR, check the tab. ') + conf.replace(/\n{2,}/g, '\n').slice(0, 200) + '\n--- review was:\n' + review.slice(0, 1500);
}
