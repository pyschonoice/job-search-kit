/* Zoho Recruit (<co>.zohorecruit.in/jobs/Careers/<id>): click "I'm interested", then fill the application form that loads in an iframe.
ARGS: {"resume": "ai" | "fs" | "<path>", "skills": ["Python", "Generative AI", ...], "dropdowns": [{"label": "<regex on field label>", "value": "<exact option text>"}], "text": [{"label": "<regex>", "value": "<text>"}]}
Defaults filled from profile: First/Last Name, Mobile, Email, City, Current/Expected Salary (rupees), Current Work location, LinkedIn.
Zoho quirks: everything is inside a frame; dropdowns are <lyte-dropdown> (click the box, then click lyte-drop-item); skills are typed into "Search and add skills" + Enter; the resume goes in the LAST file input (the first one is "Autofill", which overwrites fields); LWD (MM/DD/YYYY) is often mandatory even when not serving notice (answers.md: today + 60 days); CAPTCHA is left for the user.
Returns: every text value and dropdown value in the form. */
async (page) => {
  const ARGS = __ARGS__;
  const P = ARGS.profile;
  const log = [];
  const btn = page.getByRole('button', { name: /I'm interested/i }).first();
  if (await btn.count()) { await page.getByRole('button', { name: 'Decline non-essential' }).click().catch(() => {}); await btn.click(); await page.waitForTimeout(4000); }
  const fr = page.frames().find((f) => /zohorecruit/.test(f.url()) && f !== page.mainFrame()) || page.mainFrame();
  // map label text -> control within the frame
  const fieldBy = async (re, sel) => {
    const boxes = fr.locator('div').filter({ hasText: re }).filter({ has: fr.locator(sel) });
    const n = await boxes.count();
    return n ? boxes.nth(n - 1).locator(sel).first() : null; // innermost match
  };
  const text = [
    [/^\s*First Name/, P.first], [/^\s*Last Name/, P.last], [/^\s*Mobile/, P.phone10], [/^\s*Email/, P.email],
    [/Current Salary/, String(P.ctc.current_rupees)], [/Expected Salary/, String(P.ctc.expected_rupees)],
    [/Current Work location/, P.address.city], [/LinkedIn/, P.linkedin],
    ...(ARGS.text || []).map((t) => [new RegExp(t.label, 'i'), t.value]),
  ];
  for (const [re, v] of text) {
    const l = await fieldBy(re, 'input[type=text]');
    if (l) { await l.fill(v); log.push(`${re.source.replace(/\\s\*|\^/g, '')} = ${v}`); } else log.push(`no field ${re}`);
  }
  for (const { label, value } of ARGS.dropdowns || []) {
    const dd = await fieldBy(new RegExp(label, 'i'), 'lyte-dropdown');
    if (!dd) { log.push(`no dropdown /${label}/`); continue; }
    await dd.locator('.lyteDummyEventContainer, lyte-drop-button').first().click(); await page.waitForTimeout(700);
    const it = fr.locator('lyte-drop-box:visible lyte-drop-item').filter({ hasText: new RegExp('^\\s*' + value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\s*$') }).first();
    if (await it.count()) { await it.click(); log.push(`${label} -> ${value}`); } else { await page.keyboard.press('Escape'); log.push(`NO OPTION ${value} for /${label}/`); }
    await page.waitForTimeout(400);
  }
  const sk = fr.getByRole('textbox', { name: 'Search and add skills' });
  for (const s of ARGS.skills || []) { if (await sk.count()) { await sk.click(); await sk.fill(''); await sk.pressSequentially(s, { delay: 50 }); await page.waitForTimeout(900); await sk.press('Enter'); await page.waitForTimeout(400); } }
  const pdf = ARGS.resume === 'ai' ? P.resumes.ai : ARGS.resume === 'fs' ? P.resumes.fs : ARGS.resume;
  if (pdf) { const fi = fr.locator('input[type=file]'); await fi.nth((await fi.count()) - 1).setInputFiles(pdf); await page.waitForTimeout(2500); }
  const state = await fr.evaluate(() => [
    ...[...document.querySelectorAll('input[type=text]')].filter((e) => e.offsetParent).map((e) => 'text: ' + e.value),
    'dropdowns: ' + [...document.querySelectorAll('lyte-dropdown')].map((d) => d.innerText.trim().split('\n')[0]).join(' | '),
    'resume: ' + ((document.body.innerText.match(/First_Last[^\n]*/g) || []).join(', ') || 'none'),
  ].join('\n'));
  return log.join('\n') + '\n--- state\n' + state;
}
