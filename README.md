# Basket Case Labels — Web

A small web app that lets anyone on your team build a Basket Case Grocer
prepared-foods label sheet by filling in three fields — product, ingredients,
price — and clicking a button. Same calibrated PDF output as the desktop kit
(the actual `build_label_sheet.py` runs server-side).

## What's in here

```
basket-case-labels-web/
├── index.html             — the form your team uses
├── api/
│   └── build.py           — Vercel Python serverless function
├── lib/
│   └── label_renderer.py  — the calibrated PDF generator
├── assets/
│   ├── basket_case_logo.png
│   └── Faraz-Regular.ttf
├── requirements.txt       — Python deps (reportlab)
├── vercel.json            — Vercel config
└── README.md              — this file
```

## Deploy to Vercel (recommended)

You'll get a public URL like `https://basket-case-labels.vercel.app` that
anyone with the link can use — no signin, no Claude required.

### One-time setup (5 minutes)

1. **Create a free Vercel account** at [vercel.com](https://vercel.com) — sign in with GitHub, GitLab, or email.
2. **Install the Vercel CLI** if you don't have it:
   ```bash
   npm install -g vercel
   ```
   (You'll need Node.js — install from [nodejs.org](https://nodejs.org) if you don't have it.)
3. **Deploy** from this folder:
   ```bash
   cd basket-case-labels-web
   vercel
   ```
   The CLI will ask a few questions:
   - "Set up and deploy?" → **Yes**
   - "Which scope?" → your own account
   - "Link to existing project?" → **No**
   - "Project name?" → e.g. `basket-case-labels`
   - "Directory?" → just press Enter (current directory)
   - "Override settings?" → **No**

   Vercel detects the Python function and HTML automatically. After ~30
   seconds it prints a URL like `https://basket-case-labels-xyz.vercel.app`.

4. **Promote to production** when you're happy:
   ```bash
   vercel --prod
   ```
   This gives you the stable URL (without the `-xyz` suffix) you can share
   with your team. Bookmark it on the kitchen iPad.

### Custom domain (optional)

In the Vercel dashboard for the project: **Settings → Domains → Add**.
Point a domain like `labels.basketcasegrocer.com` at it. Vercel handles
SSL automatically.

## Deploy without the CLI

Don't want to install Node? Use the web UI:

1. Push this folder to a new GitHub repo (free).
2. In Vercel: **Add New → Project → Import Git Repository → pick your repo**.
3. Click **Deploy**.

Same result — public URL, auto-redeployed on every push to GitHub.

## Updating

To change calibration knobs, the brand font, or the logo:

- **Knobs / layout / business logic** — edit `lib/label_renderer.py`
- **Font** — replace `assets/Faraz-Regular.ttf`
- **Logo** — replace `assets/basket_case_logo.png`
- **Form** — edit `index.html`

Then `vercel --prod` (or push to GitHub if you used the Git path) to redeploy.

## Run locally before deploying

```bash
cd basket-case-labels-web
pip install -r requirements.txt
python3 -m http.server 3000  # serves index.html
# In another shell, run the API handler manually if needed
```

For full local Vercel emulation use `vercel dev` (hits the real serverless
function locally on port 3000).

## How the team uses it

1. Open the URL on any device — phone, tablet, kitchen iPad, computer.
2. Type product name, ingredients, price.
3. Click **Build & Download PDF**.
4. Open the PDF. Print at **Actual Size / 100%** (NEVER "Fit to Page").

That's it. No Claude, no Python, no script-editing. Self-serve.
