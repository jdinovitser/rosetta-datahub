# GitHub Repo Polish — About sidebar (description, website, topics)

Judges land on your GitHub repo page first. The **About** box in the top-right is the first
thing they read. This guide gives you copy-paste values for the description, the website link,
and the topic tags, plus how to set them.

---

## 1. Repository description (the one-line under the repo name)
Paste this into the **Description** field. It's under GitHub's 350-char limit and leads with
the value, not the buzzwords:

```
A linter for meaning across your DataHub graph. Rosetta is a five-agent pipeline that finds where teams silently define the same metric differently, quantifies the blast radius in dollars and downstream assets, brokers a canonical definition, and writes it back to DataHub.
```

**Shorter alternative** (if you prefer a tighter one-liner):
```
Semantic Consistency Agent for DataHub: finds conflicting metric definitions, quantifies blast radius, and writes a canonical definition back to the graph.
```

---

## 2. Website field
Put your **live demo URL** here (the deployed Replit/Render link). This makes a clickable
"try it now" link appear right in the About box for judges:
```
<PASTE YOUR LIVE DEMO URL>
```

---

## 3. Topics (the tag chips under the description)
Add these topics. GitHub topics must be lowercase and hyphenated. Paste them one at a time
(or comma-separated in the topics editor):

```
datahub
data-catalog
metadata
ai-agents
llm-agents
data-governance
semantic-layer
metrics
data-lineage
mcp-server
python
flask
hackathon
apache-2-0
data-quality
```

> Tip: the first five (`datahub`, `data-catalog`, `metadata`, `ai-agents`, `data-governance`)
> are the highest-signal ones for this hackathon's judges. If GitHub caps you, keep those.

---

## 4. How to set all of this
1. Open your repo page on GitHub.
2. Click the **gear icon** ⚙ next to **About** (top-right).
3. Paste the **Description** (section 1).
4. Paste your live demo URL in the **Website** field (section 2).
5. In **Topics**, type each tag from section 3 and press Enter/space to add it.
6. Confirm **"Use your GitHub Pages website"** is unchecked (you're using the live demo URL).
7. Click **Save changes**.

---

## 5. Verify the page looks polished (judge's-eye check)
- [ ] Repo is **Public**.
- [ ] **About** shows the description, a clickable live-demo link, and the topic chips.
- [ ] Under the description, the license reads **Apache-2.0** with a license icon.
- [ ] The README renders with the logo/hero image and clear setup instructions at the top.
- [ ] The `examples/` folder is visible in the file list.
- [ ] A green **Releases** or clean commit history, no leftover `__pycache__` or `.pytest_cache`.

---

## 6. Optional: pin the social preview image
GitHub lets you set a social/OG image (what shows when the repo link is shared):
1. **Settings → General → Social preview → Edit**.
2. Upload `assets/blast_radius_graph.png` or `assets/rosetta-logo.png`.
This makes the repo link look sharp when judges paste it into Slack or a browser preview.
