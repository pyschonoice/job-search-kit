/* li-posts: LinkedIn content search -> compact, pre-filtered hiring posts.
ARGS: {"feed": false (true = scroll the home feed instead of searching), "queries": ["hiring SDE 1 bangalore", ...], "hours": 24 | 168, "scrolls": 5, "maxMinYears": 4, "seen": ["<key>", ...], "full": false}
Splits results on the "Feed post" marker (class names are random; the marker is stable), expands "…more",
then drops: no hiring words, aggregator lists (3+ "Company:"), min experience > maxMinYears, senior/lead/manager titles,
interns/freshers, wrong stacks (.NET, Java-only, SAP, QA/Playwright testing, Salesforce, Android/iOS), keys in ARGS.seen.
Returns {kept: [{key, who, age, head, yrs, loc, emails, links}], dropped: {reason: n}}. head = first ~300 chars of the post;
"full": true adds the whole text (≤1500). links are decoded (no linkedin.com/safety/go wrappers, no nav links). */
async (page) => {
  const A = __ARGS__;
  const date = (A.hours || 24) <= 24 ? '%22past-24h%22' : '%22past-week%22';
  const seen = new Set(A.seen || []);
  const maxMin = A.maxMinYears ?? 4;
  const p = await page.context().newPage();
  const out = new Map(); const dropped = {};
  const drop = r => { dropped[r] = (dropped[r] || 0) + 1; };
  for (const q of (A.feed ? ['(feed)'] : (A.queries || ['hiring "AI engineer" bangalore']))) {
    await p.goto(A.feed ? 'https://www.linkedin.com/feed/' : 'https://www.linkedin.com/search/results/content/?keywords=' + encodeURIComponent(q) + '&datePosted=' + date + '&sortBy=%22date_posted%22');
    await p.waitForTimeout(4000);
    if (/login|authwall|checkpoint/.test(p.url())) { await p.close(); return 'NOT LOGGED IN: ask the user to log in to LinkedIn in the Playwright window'; }
    const grab = () => p.evaluate(() => {
      [...document.querySelectorAll('button')].filter(b => /…\s*more|see more/i.test(b.innerText)).forEach(b => b.click());
      const isMark = e => e.childElementCount === 0 && e.innerText?.trim() === 'Feed post';
      const marks = [...document.querySelectorAll('h2,span,div')].filter(isMark);
      const nav = /linkedin\.com\/(in|company|search|feed\/hashtag|school|mynetwork|jobs\/?$|messaging|notifications|groups|ad\/|mobile|accessibility)|about\.linkedin|licdn|\/help\/|whatsapp\.com\/channel/;
      return marks.map(m => {
        let c = m;
        while (c.parentElement && [...c.parentElement.querySelectorAll('h2,span,div')].filter(isMark).length === 1 && !/Skip to main content/.test(c.parentElement.innerText)) c = c.parentElement;
        const t = c.innerText.slice(c.innerText.indexOf('Feed post')).replace(/\n{2,}/g, '\n').trim();
        const a = c.querySelector('a[href*="/in/"],a[href*="/company/"]');
        const links = [...new Set([...c.querySelectorAll('a[href]')].map(x => {
          try { const u = new URL(x.href); return u.pathname.startsWith('/safety/go') ? u.searchParams.get('url') : x.href; } catch (e) { return x.href; }
        }).concat(t.match(/https?:\/\/[^\s)]+/g) || []).filter(u => u && !u.startsWith('mailto:') && !nav.test(u) && !/^https?:\/\/[A-Za-z]+\.[A-Z][a-z]+$/.test(u)))];
        return { t, who: (t.split('\n')[1] || '').trim() + (a ? ' ' + a.href.split('?')[0] : ''), links,
          emails: [...new Set((t.match(/[\w.+-]+@[\w-]+(\.[\w-]+)+/g) || []).map(e => e.replace(/\.$/, '')))] };
      });
    });
    // The feed unmounts old posts while scrolling, so collect at every step.
    const raw = new Map();
    for (let i = 0; i <= (A.scrolls || 5); i++) {
      for (const x of await grab()) raw.set(x.t.slice(0, 160), x);
      // LinkedIn scrolls inside <main>, not the document; End needs the tab in front.
      await p.bringToFront(); await p.keyboard.press('End');
      await p.evaluate(() => { const m = document.querySelector('main'); if (m) m.scrollTop = m.scrollHeight; });
      await p.waitForTimeout(1800);
    }
    const posts = [...raw.values()];
    for (const x of posts) {
      const t = x.t, fi = t.search(/\n(Follow|Join|Connect)\n/), body = fi > 0 ? t.slice(fi).split('\n').slice(2).join('\n') : t.split('\n').slice(3).join('\n');
      if (!/hiring|we're looking|we are looking|join (our|us)|open role|opening|send (your )?(cv|resume)|apply/i.test(body)) { drop('not hiring'); continue; }
      if ((body.match(/Company\s*:/gi) || []).length >= 3 || /\d+ (fresh )?job openings|off campus|today's job openings/i.test(body)) { drop('aggregator list'); continue; }
      if (/\bintern(ship)?\b|fresher|stipend/i.test(body.slice(0, 400))) { drop('intern/fresher'); continue; }
      if (/\bPromoted\b|starting a new position|part-time|tutor|freelance platforms|referral link/i.test(t.slice(0, 600))) { drop('ad/noise'); continue; }
      if (/product manager|frontend developer|front-end developer|customer support|sales operations|founder's office|business analyst|data analyst/i.test(body.slice(0, 300))) { drop('role'); continue; }
      const ym = body.match(/(\d{1,2})\s*(?:\+|–|-|to)?\s*(\d{1,2})?\s*\+?\s*(?:years|yrs|year)/i);
      const minY = ym ? +ym[1] : null;
      if (minY !== null && minY > maxMin) { drop('experience'); continue; }
      const title = body.split('\n').slice(0, 4).join(' ');
      if (/\b(senior|sr\.|lead|principal|staff engineer|manager|director|head of|architect|leadership|VP)\b/i.test(title)) { drop('seniority'); continue; }
      if (/\.net|c#|\bsap\b|salesforce|playwright automation|\bQA\b|SDET|test(ing)? engineer|android|\bios\b|java (developer|engineer)|spring boot developer/i.test(title)) { drop('stack'); continue; }
      const key = (x.who.split(' http')[0] + '|' + body.replace(/\s+/g, ' ').slice(0, 60)).toLowerCase();
      if (seen.has(key) || out.has(key)) { drop('seen'); continue; }
      const loc = (body.match(/(?:location|📍)\s*:?\s*([^\n]{2,60})/i) || [])[1] || '';
      const row = { key, q, who: x.who, age: (t.match(/\n(\d+[mhdw])\b/) || [])[1] || '', head: body.replace(/\s+/g, ' ').slice(0, 300),
        yrs: ym ? ym[0] : '', loc: loc.trim(), emails: x.emails, links: x.links.slice(0, 6) };
      if (A.full) row.text = body.slice(0, 1500);
      out.set(key, row);
    }
  }
  await p.close();
  return JSON.stringify({ kept: [...out.values()], dropped });
}
