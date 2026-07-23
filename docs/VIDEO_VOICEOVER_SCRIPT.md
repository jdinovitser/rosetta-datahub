# Rosetta — Word-for-Word Video Voiceover Script (under 3:00)

Read this exactly. It is timed to land at ~2:48, leaving buffer under the 3:00 hard cap.
Numbers here match the current build: **3 conflicts, 24 downstream assets, $1,080 and 12
analyst-hours avoided, 32 passing tests.** Record at 1080p, set the YouTube video to **Public**.

Legend: **[VO]** = what you say. *(SCREEN)* = what is on screen.

---

## [0:00–0:18] Cold open — the silent failure
**[VO]**
> "Here are two executive dashboards. Same company, same month. Finance says two
> point one million monthly active users. Marketing says three point four million.
> Both are 'correct.' Both are wrong to somebody. This is the silent failure that
> breaks every talk-to-data agent, and nobody's fixed it in open source."

*(SCREEN: two dashboards side by side showing 2.1M vs 3.4M "active users.")*

---

## [0:18–0:40] What Rosetta is
**[VO]**
> "Rosetta is a linter for meaning across your DataHub graph. It reads glossary
> terms, column descriptions, ownership, lineage, and the actual definitions behind
> each metric, then finds where two teams silently mean different things by the same
> name."

*(SCREEN: open the Rosetta web app on the landing view. Cursor hovers the "Run the
five-agent demo" button.)*

---

## [0:40–1:20] The scan and the blast radius
**[VO]**
> "One click runs a five-agent pipeline. It found three conflicts. The worst:
> 'active user' is defined two different ways, and that fork feeds twelve downstream
> assets, seven dashboards and one machine-learning model. Rosetta ranks by blast
> radius, because a conflict on your board deck matters more than one on a scratch
> table."

*(SCREEN: click **Run the five-agent demo**. Counters animate to 3 Conflicts, 1 High,
24 Assets, and the green **$1,080 Cost Avoided** stat. The interactive blast-radius graph
draws itself; the red ML-model node pulses.)*

---

## [1:20–1:45] The dollars
**[VO]**
> "And it quantifies the damage. Across the portfolio, these conflicts put
> twenty-four downstream assets at risk and about one thousand eighty dollars and
> twelve analyst-hours of avoidable rework on the table. That's the language a
> platform team actually acts on."

*(SCREEN: hover the risk banner on the top conflict showing the cost-if-unreconciled
line.)*

---

## [1:45–2:15] Reconciliation — a human stays in the loop
**[VO]**
> "Rosetta drafts one canonical definition from the highest-coverage variant, shows a
> clean before-and-after diff, and routes it to the real owners it pulled straight from
> DataHub ownership metadata. A human approves. Nothing is ever silently overwritten."

*(SCREEN: click **Reconcile** on the top conflict. The before, two orange definitions,
resolves into a single green canonical term tagged "canonical.")*

---

## [2:15–2:40] The write-back loop — the part that matters
**[VO]**
> "On approval, Rosetta writes back: it upserts the canonical glossary term, links it to
> all twelve affected assets, and deprecates the losing definition without deleting
> history. The graph is now permanently smarter, and the next analyst, and the next
> agent, inherit one agreed answer."

*(SCREEN: the Writer step confirms upsert + link + deprecate. Click an **Export** chip to
download the HTML report, proof of a real artifact.)*

---

## [2:40–2:48] Proof and tagline
**[VO]**
> "Five agents, thirty-two passing tests, Apache 2.0, and it ships as a reusable DataHub
> Skill any agent can call. Rosetta doesn't just answer questions. It makes sure your
> whole company is asking the same one."

*(SCREEN: terminal shows `pytest -q` → 32 passed. Cut to the skill file, then an end card
with the repo URL and "Built on DataHub".)*

---

## Recording checklist
- [ ] Browser full-screen, 1080p, clean desktop.
- [ ] Web app running (`python webapp/app.py`) or your deployed URL open.
- [ ] `pytest -q` pre-run once so it's fast on camera.
- [ ] Total length **under 2:50** to be safe.
- [ ] Upload to YouTube/Vimeo, set visibility to **Public**.
- [ ] Paste the link into `docs/SUBMISSION.md` and the Devpost "Video demo" field.
