# Deploying Rosetta on Render (free, no credit card)

Rosetta is already configured for Render. Your repo includes `render.yaml`, a `Procfile`
and a `/health` endpoint, so this is a connect-and-go deploy. Follow these steps once and
you will have a permanent public URL to put on your Devpost submission.

Estimated time: about 10 minutes.

---

## Before you start
- Your code is on GitHub at: https://github.com/jdinovitser/rosetta-datahub
- You do NOT need a credit card for Render's free web service.

---

## Step 1 — Create a Render account
1. Go to https://render.com
2. Click **Get Started** (top right).
3. Choose **Sign up with GitHub**. This is the easiest path because Render can then see
   your repo directly.
4. When GitHub asks to authorize Render, click **Authorize Render**.

## Step 2 — Create a new Web Service
1. On the Render dashboard, click the **New +** button (top right).
2. Choose **Web Service**.
3. Under "Connect a repository," find **rosetta-datahub** and click **Connect**.
   - If you do not see it, click **Configure account** / **Configure GitHub App**, grant
     Render access to the `rosetta-datahub` repo, then come back.

## Step 3 — Confirm the settings
Render reads your `render.yaml` automatically, so most fields fill themselves in. Confirm:

| Field           | Value                                                              |
|-----------------|--------------------------------------------------------------------|
| **Name**        | `rosetta-datahub` (this becomes your URL)                          |
| **Region**      | Pick the one closest to you (e.g. Oregon / Frankfurt)              |
| **Branch**      | `main`                                                             |
| **Runtime**     | Python                                                             |
| **Build Command** | `pip install -r requirements-demo.txt gunicorn`                  |
| **Start Command** | `gunicorn --chdir webapp app:app --bind 0.0.0.0:$PORT`           |
| **Instance Type** | **Free**                                                         |

You do NOT need to set any environment variables for the demo (it runs on the bundled
sample data). Leave the DataHub variables blank.

## Step 4 — Deploy
1. Click **Create Web Service** (bottom of the page).
2. Watch the log stream. You will see it install packages, then a line like
   `Booting worker with pid ...` and finally **"Your service is live."**
3. First build takes 2 to 4 minutes.

## Step 5 — Get your public URL
At the top of the service page Render shows your live URL, something like:
```
https://rosetta-datahub.onrender.com
```
Click it. You should see the Rosetta home page. Click the demo/scan button to confirm the
five-agent pipeline runs and shows the 3 conflicts.

Test it in a private/incognito window too, to make sure judges do not hit a login wall.

---

## One thing to know: the free-tier "cold start"
Render's free web service goes to sleep after 15 minutes of no traffic. The next visitor
then waits about 30 to 60 seconds while it wakes up. This is normal and fine for judging,
but here is how to make the judge's experience smooth:

- **Warm it up right before you submit and before judging opens.** Just visit the URL once
  so it is awake.
- **Add a friendly note on Devpost** (optional): "First load may take ~30s while the free
  host wakes up, then it is instant."
- **Optional free keep-alive:** create a free monitor at https://uptimerobot.com that pings
  `https://rosetta-datahub.onrender.com/health` every 5 minutes. That keeps the app awake
  around the clock at no cost. (Set the monitor type to HTTP(s), interval 5 minutes.)

---

## Updating the app later
Any time you push new commits to the `main` branch on GitHub, Render automatically
rebuilds and redeploys. No extra steps.

---

## Where to put the URL
1. **Devpost "Try it out" link:** paste your `https://rosetta-datahub.onrender.com` URL.
2. **GitHub repo "Website" field:** open the repo, click the gear next to "About," paste the
   same URL in the Website box, Save.
3. Anywhere the old Replit URL appeared, replace it with the new Render URL.
