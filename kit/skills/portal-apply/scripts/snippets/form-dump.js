/* Dump every visible field on the page (all frames, open dialogs included): label, type, value, options, plus error/alert text.
ARGS: {} (none)
Returns: one line per field, then ERRORS. Use for pre-flight (fill-form step 2) and verify (step 7). */
async (page) => {
  const ARGS = __ARGS__;
  const out = [];
  for (const f of page.frames()) {
    let rows = [];
    try {
      rows = await f.evaluate(() => {
        const vis = (e) => e.offsetParent !== null || e.getClientRects().length > 0;
        const labelOf = (e) => {
          if (/^cards\[/.test(e.name || '') && e.closest('li')) return e.closest('li').innerText.trim().split('\n')[0];
          if (e.id) { const l = document.querySelector(`label[for="${CSS.escape(e.id)}"]`); if (l && l.innerText.trim()) return l.innerText.trim(); }
          const a = e.getAttribute('aria-label') || e.getAttribute('placeholder') || e.getAttribute('name') || e.getAttribute('formcontrolname');
          if (a) return a;
          let p = e;
          for (let k = 0; k < 6 && p; k++) { p = p.parentElement; if (p && p.innerText && p.innerText.trim().length > 3) return p.innerText.trim().split('\n')[0]; }
          return '';
        };
        const els = [...document.querySelectorAll('input:not([type=hidden]), textarea, select, [role=combobox], [role=radiogroup], button[aria-haspopup=listbox], mat-select, lyte-dropdown')].filter(vis);
        return els.map((e) => {
          const t = e.tagName.toLowerCase();
          const type = e.type || e.getAttribute('role') || t;
          let val = e.value || '';
          if (type === 'checkbox' || type === 'radio') val = e.checked ? '[x]' : '[ ]';
          if (t === 'select') val = e.options[e.selectedIndex]?.text + ' {' + [...e.options].map((o) => o.text).slice(0, 15).join(' / ') + '}';
          if (t === 'button' || t === 'mat-select' || t === 'lyte-dropdown') val = e.innerText.trim().split('\n')[0];
          if (type === 'file') val = [...(e.files || [])].map((x) => x.name).join(',');
          return `${t}:${type} | ${labelOf(e).slice(0, 90)} = ${String(val).slice(0, 80)}`;
        }).concat([...document.querySelectorAll('[role=alert], [data-automation-id=errorMessage], .error, .error-message, .artdeco-inline-feedback--error')].filter(vis).map((e) => 'ERROR: ' + e.innerText.trim().slice(0, 150)).filter((x) => x.length > 8));
      });
    } catch (e) { continue; }
    if (rows.length) out.push(`# frame ${f.url().slice(0, 80)}`, ...rows);
  }
  return out.join('\n');
}
