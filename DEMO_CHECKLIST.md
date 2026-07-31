# Rosetta — Hackathon Demo Video Checklist

A concise sequence for a strong demo video (target: under 3 minutes).

---

## Recommended sequence

1. **Open with the headline**
   > "One metric. Two meanings. Silent chaos."
   Explain in one sentence: two teams define `billing_amount` differently — clinical includes medication, finance subtracts discounts. Nobody notices. Reports silently diverge.

2. **Show the official data badge**
   Point to the **DEMO MODE · OFFICIAL HACKATHON SAMPLE DATA** badge in the topbar.
   State: *"This runs against the official Build-with-DataHub hackathon dataset — 55,500 synthetic patient records, no credentials required."*

3. **Run the five-agent demo**
   Click **Run the five-agent demo** and narrate each agent briefly:
   - 🧲 Harvester — reads metric definitions from the DataHub metadata graph
   - 🔍 Conflict Detector — finds silent contradictions and hidden synonyms
   - 💥 Blast-Radius Analyzer — traces every downstream asset contaminated
   - 🤝 Reconciliation Broker — proposes a canonical GlossaryTerm definition
   - ✅ Writer — generates a validated DataHub write plan (Demo Mode: not executed)

4. **Open the strongest finding**
   Show the `billing_amount` conflict: 1,215 negative billing rows, $28.48M affected transaction value in sample data.

5. **Show evidence and blast radius**
   Point to the blast-radius graph. Name the downstream assets: `mart_billing`, dashboards, ML models.

6. **Show the proposed canonical definition**
   > `SUM(base_charge) + SUM(medication) − SUM(discounts)`
   Explain: Rosetta proposes this as a DataHub GlossaryTerm that all teams agree on.

7. **Approve the plan**
   Click **Approve & Generate Write Plan**. State:
   *"Human approval is enforced in code — no function executes without an explicit approval token tied to this exact plan."*

8. **Show exact DataHub operations and the VALIDATED status**
   Point to the **VALIDATED · NOT EXECUTED** badge.
   Show the machine-readable operations panel:
   - Op 1: `upsert_glossary_term` → `urn:li:glossaryTerm:billing_amount`
   - Op 2–N: `attach_term_to_asset` → each affected dataset URN
   - Op N+1–M: `deprecate_term` → each conflicting variant URN

9. **Copy or download the JSON plan**
   Click **Copy JSON** or **Download JSON**. State:
   *"Judges can inspect the exact operations. The JSON is machine-readable and matches what Connected Mode would submit to DataHub."*

10. **Explain Connected Mode**
    > "In Connected Mode, Rosetta reads from your DataHub instance, executes only the approved operations, then re-reads every affected entity to verify the state was applied correctly. Approval is tied to the exact plan hash — it cannot be reused for a different plan."

11. **Close**
    > "Data quality tells us whether the numbers are valid.  
    > Rosetta helps ensure everyone agrees on what those numbers mean."

---

## Key accuracy reminders for the recording

- Say **"generates a validated DataHub write plan"** — not "writes to DataHub" or "executes"
- Say **"affected transaction value"** — not "cost avoided", "revenue loss", or "savings"
- Say **"official hackathon sample data"** for healthcare; retail is a supplementary scenario
- Demo Mode status is always **VALIDATED · NOT EXECUTED** — never EXECUTED
- The approval token is **plan-specific** — approval for one conflict cannot authorize another

---

*No external DataHub catalog was modified during the demo.*
