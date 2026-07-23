# Deployment Guide — get your Repo URL and Live Demo URL

> **Recommended host: Render (free, no credit card).** For step-by-step Render
> instructions see `docs/RENDER_DEPLOYMENT.md`. The Replit steps below are kept as an
> alternative option only.

You need three URLs for the Devpost form. This guide gets you the first two:
1. **Public GitHub repo URL** (with Apache-2.0 visible in the About sidebar)
2. **Live hosted demo URL** (Render recommended; Replit optional)
3. Video URL — see `docs/VIDEO_VOICEOVER_SCRIPT.md`

Do Part A, then Part B. Total time: ~15 minutes.

---

## Part A — Push to a public GitHub repo

### A1. Unzip the package
Unzip `rosetta-datahub.zip`. You'll get a `rosetta/` folder containing all source, docs,
assets, and the `LICENSE` file.

### A2. Create the repo on GitHub
1. Go to https://github.com/new
2. Repository name: `rosetta-datahub` (or anything you like)
3. Visibility: **Public** (required by the rules)
4. Do **not** add a README, .gitignore, or license, the zip already includes them.
5. Click **Create repository**.

### A3. Push the code (run these in a terminal, inside the unzipped `rosetta/` folder)
```bash
cd rosetta
git init
git add .
git commit -m "Rosetta — Semantic Consistency Agent for DataHub"
git branch -M main
git remote add origin https://github.com/<YOUR-USERNAME>/rosetta-datahub.git
git push -u origin main
```

### A4. Confirm the Apache-2.0 license shows in the About sidebar (required)
1. Open your repo page on GitHub.
2. Look at the **About** box on the right. It should read **"Apache-2.0"** with a license icon.
3. If it doesn't appear immediately, click the gear/pencil in About and verify GitHub detected
   the `LICENSE` file. It's a standard Apache-2.0 file at the repo root, so GitHub will detect it.

**Your Repo URL** is: `https://github.com/<YOUR-USERNAME>/rosetta-datahub`

---

## Part B — Deploy the live demo on Replit

### B1. Import from GitHub
1. Go to https://replit.com and log in.
2. Click **Create Repl** → **Import from GitHub**.
3. Paste your repo URL from Part A. Replit imports it. The included `.replit` and `replit.nix`
   files are already configured.

### B2. Install dependencies
In the Replit **Shell** tab:
```bash
pip install -r requirements-demo.txt
```

### B3. Run it
- Click the big green **Run** button. The included `.replit` launches `python webapp/app.py`.
- A webview panel opens showing the Rosetta app. Click **Run the five-agent demo** to confirm
  the pipeline, counters, and blast-radius graph all work.

### B4. Get a stable public URL (Deploy)
1. Click **Deploy** (top right).
2. Choose **Autoscale** (cheapest) or **Reserved VM**.
3. Replit gives you a public URL like `https://rosetta-datahub.<username>.repl.co`.
4. **Test it in an incognito window** to be sure it's public and the demo button works with no login.

**Your Live Demo URL** is the deployed Replit URL.

> Alternatives if you prefer: `render.yaml` is preconfigured for Render Blueprints, and a
> `Dockerfile` is included (`docker build -t rosetta . && docker run -p 5000:5000 rosetta`).

---

## Part C — Fill the three placeholders
Open `docs/SUBMISSION.md` and replace:
- `<PASTE YOUR DEPLOYED URL>` → your Replit deploy URL (Part B4)
- `<PASTE YOUR REPO URL>` → your GitHub URL (Part A4)
- `<PASTE YOUR YOUTUBE/VIMEO URL>` → your video URL

Then follow `docs/DEVPOST_SUBMISSION_WALKTHROUGH.md` to paste everything into the form.

---

## Troubleshooting
| Problem | Fix |
|---|---|
| About sidebar doesn't show Apache-2.0 | Confirm `LICENSE` is at the repo root (not inside a subfolder). Refresh the page. |
| Replit "module not found" | Re-run `pip install -r requirements-demo.txt` in the Shell. |
| Demo works locally but not on the deploy URL | Make sure the app binds `0.0.0.0` and uses `$PORT`; the included Procfile/`.replit` already do this. |
| Incognito test asks for login | You opened the editor URL, not the **Deploy** URL. Use the deployed `.repl.co` link. |
