# NFP AI Use-Case Tracker

A searchable register of named Australian not-for-profits using, piloting or funding AI. Each case has a source link and a quote taken word-for-word from that source.

This is the **static** version: a plain website plus a JSON database, hosted free on GitHub Pages. Nothing updates automatically. The site shows whatever is in `data/cases.json`, and you add or edit cases yourself.

**Data as of 29 October 2026:** 54 cases. 35 are verified and 19 are not yet verified.

---

## What's in the repo

| File | What it is |
|---|---|
| `index.html` | The website: search, filters, verified / not-yet-verified tabs, and CSV download. It reads the database and has no other dependencies. |
| `data/cases.json` | **The database.** Every case, as JSON. |
| `data/schema.json` | The rules for the database: required fields, allowed values and the id format. |
| `data/cases.csv` | The same data as a spreadsheet. Regenerate it with `scripts/to_csv.py`. |
| `scripts/validate.py` | Checks the database for mistakes before you commit. |
| `scripts/to_csv.py` | Exports the database to CSV. |
| `.github/workflows/validate.yml` | Runs the checker automatically whenever the data changes, and flags errors with a red cross. It never edits anything. |
| `.nojekyll` | Tells GitHub Pages to serve the files as they are. |

---

## Put it online (about 5 minutes)

1. Create a new repository on github.com. It must be **Public** for free GitHub Pages.
2. Upload everything in this folder. On a Mac, press Cmd + Shift + . in Finder to show the hidden `.github` folder and `.nojekyll` file, and include them.
3. Go to **Settings → Pages**. Under *Build and deployment*, choose **Deploy from a branch**, then branch **main**, folder **/ (root)**, and click **Save**.
4. After a minute or two the site is live at `https://<your-username>.github.io/<repo-name>/`.

**To preview on your own computer:** opening `index.html` directly won't load the data, because browsers block that. In this folder, run:

```bash
python -m http.server
```

Then open http://localhost:8000.

---

## The database (`data/cases.json`)

```json
{
  "meta": { "name": "NFP AI Use-Case Tracker", "last_updated": "2026-10-29", ... },
  "cases": [
    {
      "id": "wombat-housing--client-facing-chatbot",
      "status": "tracker",
      "organisation": "Wombat Housing",
      "org_type": "Charity",
      "state": "VIC",
      "cause_area": "homelessness, youth",
      "category": "client-facing chatbot or assistant",
      "use_case": "'WomBot' chatbot gives young people at risk of homelessness support information within strict guardrails.",
      "partner": "",
      "stage": "deployed",
      "quote": "employs strict guardrails on the information it uses to help young people at risk of homelessness",
      "sources": [ { "title": "Institute of Community Directors Australia (18 Sep 2025)", "url": "https://..." } ],
      "first_seen": "2026-09-30",
      "last_seen": "2026-09-30",
      "review_reason": ""
    }
  ]
}
```

### Fields

| Field | Required | Allowed values / format |
|---|---|---|
| `id` | yes | organisation slug + `--` + category word, e.g. `justice-connect--intake`. Must be unique. There's one id per organisation and use case, so the same use is never listed twice. |
| `status` | yes | `tracker` (verified) or `review` (not yet verified) |
| `organisation` | yes | Name as written in the source |
| `org_type` | | `Charity`, `Community legal centre`, `Community legal organisation`, `NFP`, `NFP research institute`, `Unclear` |
| `state` | | `NSW` `VIC` `QLD` `WA` `SA` `TAS` `ACT` `NT` `National`, or `""` |
| `cause_area` | | Short label, e.g. `legal help` |
| `category` | yes | `client-facing chatbot or assistant`, `intake, triage or referral`, `service delivery or decision support`, `fundraising, marketing or communications`, `grant writing or reporting`, `data analysis, research or evaluation`, `internal operations or productivity`, `advocacy, policy or legal`, `other` |
| `use_case` | yes | One sentence: what the AI does and for whom |
| `partner` | | Vendor, tool or funder |
| `stage` | yes | `deployed`, `pilot`, `funded`, `announced`, `unclear`, `discontinued` |
| `quote` | yes | A short sentence copied **word-for-word** from the source |
| `sources` | yes | List of `{ "title": "Publisher (date)", "url": "https://..." }` |
| `first_seen`, `last_seen` | yes | Dates as `YYYY-MM-DD` |
| `review_reason` | | Why a `review` case isn't verified yet. Leave it `""` for verified cases. |

---

## Updating the data

**Add a case:** copy an existing case in `data/cases.json`, paste it into the `cases` list (watch the commas between cases), change the fields, and give it a new `id`.

**Verify a case:** change its `status` from `"review"` to `"tracker"` and set `review_reason` to `""`.

**Remove a case:** delete its `{ ... }` block.

**Then, every time:**

1. Update `meta.last_updated` to today's date.
2. Run `python scripts/validate.py` and fix anything it reports. It names the case and the problem.
3. Optionally run `python scripts/to_csv.py` to refresh the CSV.
4. Commit. GitHub Pages republishes the site within a minute or two.

You can also edit `data/cases.json` directly on github.com with the pencil icon. The **Check database** action then runs the validator and shows a red cross on the commit if something is wrong.

**Copying in new cases from the live Claude tracker:** use **Export CSV** on the tracker page, or ask Claude to "export the tracker as cases.json in the static repo's format".

---

## Settings

- **Hide unverified cases from the public site:** in `index.html`, set `const SHOW_UNVERIFIED = false;`. This hides the "Not yet verified" tab and its count, and leaves them out of the CSV download.
- **Change the categories or stages:** update both `data/schema.json` and the `CATS` / `STAGES` lists near the top of the script in `index.html`.

---

## Notes

- Quotes come from public sources. Check a quote against its source before citing it. The first batch of cases (first seen 30 September 2026) came mostly from one secondary source, the Institute of Community Directors' list from September 2025.
- Choose a licence for the data before you promote the site, for example CC BY 4.0, by adding a `LICENSE` file.
