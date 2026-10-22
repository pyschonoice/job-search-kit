/* Wellfound: replace the profile resume (the one every Wellfound application sends) and confirm the new file name.
ARGS: {"resume": "ai" | "fs" | "<absolute pdf path>"}
Navigates the CURRENT tab to /profile/edit/resume, so run it in a spare tab, not one holding a filled panel. Uploads via the "Upload new file" chooser, then reloads, because the page keeps showing the old name until it does.
Returns: "before: <old file> -> after: <new file>". If after != the uploaded file name, the upload failed: retry once, then tell the user. */
async (page) => {
  const ARGS = __ARGS__;
  const P = ARGS.profile;
  const pdf = ARGS.resume === 'ai' ? P.resumes.ai : ARGS.resume === 'fs' ? P.resumes.fs : ARGS.resume;
  const name = async () => page.evaluate(() => [...document.querySelectorAll('h2')].map((h) => h.textContent.trim()).find((t) => /\.(pdf|docx?|txt)$/i.test(t)) || '(none)');
  await page.goto('https://wellfound.com/profile/edit/resume'); await page.waitForTimeout(2000);
  const before = await name();
  const chooser = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: /Upload new file|Upload/ }).first().click();
  await (await chooser).setFiles(pdf);
  await page.waitForTimeout(5000);
  await page.reload(); await page.waitForTimeout(2500);
  const after = await name();
  const want = pdf.split('/').pop();
  return `before: ${before} -> after: ${after}${after === want ? ' (OK)' : ' (MISMATCH: expected ' + want + ')'}`;
}
