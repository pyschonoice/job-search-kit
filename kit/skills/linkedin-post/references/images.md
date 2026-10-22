# Images: when, which, how

A post gets **1–3 images when they show something real**. An image almost always beats plain text: about twice the likes, and images get the most comments of any format. But a stock or decorative image adds nothing. When the post has nothing real to show, post plain text.

## Which image for which post

| Post type | Best image | Count |
|---|---|---|
| A. Production lesson | Before/after diagram card (e.g. "4,000 tokens → 6 fields") | 1, or 2 (before and after as separate cards) |
| B. How I built X | Architecture diagram card, or a code snippet card of the key 10–15 lines | 1–2. For 4+ steps, use a PDF carousel instead |
| C. Opinion | A text card with the one line, or nothing | 0–1 |
| D. Build in public | Real product screenshot, cropped and framed | 1–3 |
| E. Checklist | PDF carousel (one item per slide) or one checklist card | 1 PDF, or 1 card |
| F. Human | **Real photo of the user** (hackathon, team, desk) | 1–3 |

## The four kinds

1. **Photos of the user.** Only the user can supply these. Ask them for them; never make them up or generate them. Before using a group photo, ask whether everyone in it is OK being posted.
2. **Product screenshots.**
   - Only from their own products (projects in `my-profile` that are free of employer or client data).
   - Take them with the Playwright browser, at 1080 px wide or more.
   - Crop to the interesting part.
   - Remove any personal data: emails, names, phone numbers, API keys, wallet balances of real users.
   - Then wrap the screenshot in the `frame` card so it looks deliberate.
3. **Diagram and code cards.** Make these with `templates/card.html` and `scripts/render.sh`. Draw flows with boxes and arrows in HTML/CSS. Use real code from their repos, shortened, with secrets and client names removed.
4. **PDF carousel (a document post).**
   - 6–10 slides at 1080×1350.
   - Render each slide with the card template.
   - Combine them into one PDF (see below).
   - Slide 1 is the hook. The last slide is "What would you add?" plus their name.

**Never:** screenshots of <employer>'s internal tools, dashboards, transcripts or client prompts; AI-generated people or scenes; stock photos; memes; screenshots of other people's posts or DMs.

## Specs

- **Single image:** 1080×1350 (4:5 portrait, the most space in the mobile feed). Use 1080×1080 when the content is square.
- **Several images in one post:** all the same size and orientation, up to 3.
- **Format:** PNG under 5 MB.
- **Legibility:**
  - Body text at least 34 px and titles at least 64 px at 1080 width, so they read on a phone without zooming.
  - At most about 40 words on a card.
- **Alt text:** write one line for every image, describing what it shows, not "image".

## Making a card

1. Copy `templates/card.html` to `linkedin-posts/posts/<folder>/img1.html`.
2. Pick a layout class on `<body>`:
   - `diagram`: title, then a flow of boxes
   - `code`: title plus a code block
   - `statement`: one big line
   - `checklist`
   - `frame`: wraps a screenshot (`<img src="shot.png">`)
3. Edit the content inside `<main>`. Keep the footer with their name and handle; it identifies them when the image is shared.
4. Render it:
   ```bash
   .claude/skills/linkedin-post/scripts/render.sh linkedin-posts/posts/<folder>/img1.html            # 1080x1350
   .claude/skills/linkedin-post/scripts/render.sh linkedin-posts/posts/<folder>/img1.html 1080 1080  # square
   ```
   This writes `img1.png` next to the HTML.
5. Look at the PNG with Read before showing it to the user. Fix any overflow, tiny text or empty space.

## Making a PDF carousel

Render every slide (`slide1.html` … `slideN.html`), then combine them:
```bash
python3 -c "
import sys,glob
from PIL import Image
f=sorted(glob.glob(sys.argv[1]+'/slide*.png'), key=lambda p:int(''.join(c for c in p.split('slide')[-1] if c.isdigit())))
ims=[Image.open(p).convert('RGB') for p in f]; ims[0].save(sys.argv[1]+'/carousel.pdf', save_all=True, append_images=ims[1:])
" linkedin-posts/posts/<folder>
```
If PIL is missing, run `pip3 install pillow` (ask first). On LinkedIn the PDF is uploaded as a "document", and its title shows on top of it, so give it a short title.
