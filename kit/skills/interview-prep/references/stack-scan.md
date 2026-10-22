# Reading a company's public front-end for stack signals

A single-page app ships its whole client bundle to every visitor. Provider names, route names and constants in it tell you more about the real stack than the marketing page does. For example, a scan can surface a self-hosted component or a specific vendor stack the marketing page never names.

## Allowed vs off-limits
- ✅ Reading the HTML/JS/CSS the public site already serves to any visitor, in the browser you have open.
- ✅ Reading their public docs, GitHub org (public repos only), job posts, LinkedIn.
- ❌ Calling their API endpoints (even "public" ones), logging in, creating accounts, fuzzing routes, port scans, or opening anything behind auth. Just list route names; never request them.
- ❌ Telling them in the interview that you read the bundle. Say "I went through your product and demo".

## Steps (Playwright MCP)
1. `browser_navigate` to the site. If WebFetch returned only a title, it's a JS app.
2. Render all text and links (scrolling triggers lazy sections):
```js
async () => { for (let y=0;y<document.body.scrollHeight;y+=600){window.scrollTo(0,y); await new Promise(r=>setTimeout(r,250));}
  const links=[...document.querySelectorAll('a')].map(a=>a.innerText.trim().slice(0,40)+' -> '+a.href);
  return document.body.innerText + '\n\nLINKS:\n' + [...new Set(links)].join('\n'); }
```
3. Click product tabs (match `button` elements by exact text) and re-read the section, since tab contents only render when selected.
4. Subpages on the same SPA: navigate to each, or load each in an iframe and read `contentDocument.body.innerText`.
5. Scan the main bundle for providers, routes and context:
```js
async () => { const s=[...document.scripts].map(s=>s.src).find(x=>/index-|main|app/.test(x));
  const t=await (await fetch(s)).text();
  const ctx=(re,n=3,w=160)=>{const r=[];let m;const g=new RegExp(re,'gi');while((m=g.exec(t))&&r.length<n){r.push(t.slice(Math.max(0,m.index-w),m.index+w).replace(/\s+/g,' '));}return r;};
  const providers='livekit|daily\\.co|agora|twilio|plivo|exotel|vobiz|knowlarity|telnyx|vonage|deepgram|assemblyai|sarvam|elevenlabs|cartesia|playht|openai|anthropic|gemini|groq|bedrock|supabase|firebase|stripe|razorpay|composio|wasender|gupshup|interakt|segment|mixpanel|posthog|sentry';
  const counts={}; for (const p of providers.split('|')) { const m=t.match(new RegExp(p,'gi')); if(m) counts[p]=m.length; }
  const routes=[...new Set(t.match(/["'`]\/[a-z0-9_\-]+\/[a-z0-9_\-\/]+["'`]/gi)||[])].slice(0,200);
  const wss=[...new Set(t.match(/wss?:\/\/[a-z0-9.\-\/]+/gi)||[])];
  return JSON.stringify({counts, wss, routes},null,1); }
```
Then run `ctx('<term>')` on interesting hits (e.g. `hitl`, `failure-groups`, `CALL_START_HOUR`, `consent`, `dlq`) to read the surrounding code and work out what each feature does.
6. Also check: `performance.getEntriesByType('resource')` hosts (CDNs, analytics), `img` alt text for "trusted by" customer logos, and any download URLs (desktop/mobile apps, cloud region in an S3 URL).

## Writing it up
- In `01 Their Architecture.md`: **✅ seen** = the literal name or route found. **🔶 inferred** = how the pieces likely connect. Never upgrade an inference to fact.
- Turn every unknown into a question in `03 Questions to Ask.md` (e.g. the STT vendor isn't in the front-end, so ask).
- Sensitive findings (e.g. an unofficial WhatsApp API): write a tactful question, never a criticism.
