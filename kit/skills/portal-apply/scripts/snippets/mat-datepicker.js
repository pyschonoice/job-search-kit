/* Angular Material date picker (read-only input; Infosys DOB, other Angular portals): open the calendar, go to year -> month -> day.
ARGS: {"input": "<css selector of the date input, e.g. input#mat-input-0 or input[formcontrolname=dob]>", "yyyy": "2000", "mon": "JAN", "dd": "1"}  (pass the user's DOB from answers.md; defaults to the first datepicker input)
Returns: the input's value afterwards (Infosys shows DD/MM/YYYY). */
async (page) => {
  const ARGS = __ARGS__;
  const P = ARGS.profile;
  const mons = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
  const yyyy = ARGS.yyyy || P.dob.yyyy;
  const mon = ARGS.mon || mons[parseInt(P.dob.mm, 10) - 1];
  const dd = String(parseInt(ARGS.dd || P.dob.dd, 10));
  const input = page.locator(ARGS.input || 'input.mat-datepicker-input').first();
  const tog = input.locator('xpath=ancestor::mat-form-field[1]').locator('mat-datepicker-toggle button');
  if (await tog.count()) await tog.first().click(); else await input.click();
  await page.waitForTimeout(800);
  await page.locator('.mat-calendar-period-button').click(); await page.waitForTimeout(500);
  const cell = (re) => page.locator('.mat-calendar-body-cell').filter({ hasText: re });
  for (let k = 0; k < 6 && !(await cell(new RegExp(`^\\s*${yyyy}\\s*$`)).count()); k++) {
    const range = await page.locator('.mat-calendar-period-button').innerText();
    const lo = parseInt(range, 10);
    await page.locator(lo > parseInt(yyyy, 10) ? '.mat-calendar-previous-button' : '.mat-calendar-next-button').click();
    await page.waitForTimeout(400);
  }
  await cell(new RegExp(`^\\s*${yyyy}\\s*$`)).click(); await page.waitForTimeout(400);
  await cell(new RegExp(`^\\s*${mon}\\s*$`, 'i')).click(); await page.waitForTimeout(400);
  await cell(new RegExp(`^\\s*${dd}\\s*$`)).first().click(); await page.waitForTimeout(500);
  return 'value=' + (await input.inputValue());
}
