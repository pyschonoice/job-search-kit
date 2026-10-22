# Darwinbox (`<company>.darwinbox.in/ms/candidatev2/...`)

Medium difficulty. The JD is public, but **Apply Now redirects to `/auth/login`** (Google, LinkedIn or email sign-in, sometimes an OTP). The user logs in themself; never create an account. First seen: Go Digit, 2026-10-13.

## Layout
- One page of steps with a pill bar and a yellow **Save & Continue** at top right. Order: Resume, Biographical, Contact, Address, Job, Personal Documents, Work Experience, Education, Last Salary, Misc, Pre-Offer, Internships, Language, Campus Fields. On the last step the button becomes **Submit** (the user clicks it).
- A pill shows a red "!" until its required fields are valid. Save & Continue still advances past a step with empty required fields, but the pill stays red.

## Resume and auto-fill
- `input[type=file]` → `setInputFiles`. A modal "Auto-fill the Application" appears; click `getByText('Yes, Auto-fill')`.
- Auto-fill sets names (UPPERCASED, so retype them), email, phone, work and education. It leaves LinkedIn, address, DOB and gender empty. Check the work dates and titles it parsed.

## Reading and writing fields
- Web components with Angular `dbx-*` wrappers. `innerText` and `querySelector` don't show values, so read them with Playwright locators or a screenshot.
- Text: `getByTestId('application-form-dynamic-form-desktop-question-<key>-<key>-text-input-input').fill(...)`. The testid without the trailing `-input` is the wrapper, and fill() on it fails. Keys: firstname, lastname, linkedin, phone, current_flat, current_street, current_landmark, current_pincode, fixed_pay, variable_pay, total_ctc. Arrays (work, education) use the `array-desktop-question-` prefix.
- Dropdowns are Choices.js. The search input is hidden, so click the visible box (page.mouse.click at CSS coords = screenshot px / 1.667), then pick `.choices__list--dropdown .choices__item:visible` with hasText. Typing filters the list. After an error clears, the layout shifts, so recompute the coordinates.
- Date pickers are readonly: click the input → header "Month YYYY" (month view) → again (year range) → prev arrow for the decade → year → month → day. Shown as DD-MM-YYYY.
- Checkboxes: `click({force:true})`. "Same as current address" copies the address automatically.

## Questions seen (Go Digit)
- "Years of Experience as per your current role": bands; pick the band that contains the saved experience (answers.md).
- Last Salary: full rupees, with no unit (e.g. 800000).
- Education "Institute Location" (required), Misc "ID Verification Type" (Experienced / Fresher, required), Pre-Offer "I Acknowledge" (health/safety), privacy consent: these are ASKs for the user.
- Language levels: Elementary / Limited working / Professional working / Fully professional / Native.
