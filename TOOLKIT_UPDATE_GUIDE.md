# Road Safety Institutional Toolkit: Checklist-tab integration

This update is built against the supplied `maleknaz/roadsafety_toolkit` repository ZIP of November 23, 2026. The six existing HTML pages and all five existing data files have been preserved **byte for byte**.

## What changed

- In `app.py`, the final navigation tab is now named **Road Safety Institutional Toolkit** and calls `institutional_toolkit.render()` in place of the previous `planner.render()` call. Shared CSS now styles both the new interface and the original planner correctly, without affecting the six HTML tabs.
- New `institutional_toolkit/` Python package implements findings, evidence coverage benchmarking, conditional country-pair comparison, a question-first checklist, recorded user responses, source-aware guidance, export helpers, and optional AI assistance.
- In `requirements.txt`, the OpenAI SDK is included so the app can perform the optional targeted update check. **A working OpenAI API key is not included.**
- Original `planner.py` remains **unchanged**, and is accessible from **Generate my institutional checklist → Open the original detailed action planner** for detailed manual assessment, Word/Excel export, and action tracking.

## How to put this on GitHub

The easiest approach is to upload the *changed files*, not the ZIP itself.

1. Download `Road_Safety_Toolkit_GitHub_Update.zip`, and extract it on your computer.
2. Open `https://github.com/maleknaz/roadsafety_toolkit` and navigate to the default branch.
3. Click **Add file → Upload files**.
4. Drag the extracted `app.py`, `requirements.txt`, and the **entire `institutional_toolkit` folder** into GitHub's upload area. Confirm the upload list shows:

   ```text
   app.py
   requirements.txt
   institutional_toolkit/__init__.py
   institutional_toolkit/evidence.py
   institutional_toolkit/reports.py
   institutional_toolkit/updates.py
   institutional_toolkit/ui.py
   ```

5. Click **Commit changes**. If your browser does not support uploading a folder, use GitHub Desktop to copy these files into a local checkout and commit/sync them, or ask for a step-by-step file-by-file web upload.
6. Allow the existing Streamlit Cloud deployment to rebuild. The deployment command and app entrypoint remain `app.py`.
7. Go to `https://roadsafetytoolkit.streamlit.app/` and open the new last tab.

For a complete backup/reference repository, the separate `Road_Safety_Toolkit_Updated_Repository.zip` includes **all** original assets and data, plus the update. Do not upload that ZIP as a single file to GitHub; GitHub and Streamlit will not automatically unzip it.

## Test the app after deployment

- Open Estonia → **Explore country findings**. Expected detailed review profile: Government Traffic Commission (Liikluskomisjon).
- Select **Benchmark internationally**. The table has 195 countries, but only 26 have mechanisms in the detailed reviewed subset. A zero means **not reviewed in that subset**, not absence of a commission.
- Select **Compare with another country**. The comparison country selector should appear now, not on the other screens. Choose Sweden, review the 17 domains, and export the detailed Word dossier.
- Select **Generate my institutional checklist**. Answer or skip eight optional questions. Click **Generate my prefilled checklist**. Check the 72 items, source links, user input, and proposed verification steps. Download Word/Excel files.
- If needed, open the original detailed planner from inside that same checklist workflow.
- Confirm the **Atlas**, **Taskforces**, **Existing documents**, **Bodies & strategies**, and **Country case studies** HTML tabs look unchanged.

## Optional short update searches and AI-grounded summaries

To enable OpenAI, go to the existing Streamlit Community Cloud app → **Settings → Secrets**, and enter:

```toml
OPENAI_API_KEY = "your-own-API-key"
```

Do not commit an API key or the `secrets.toml` file to GitHub. The code retrieves the key from Streamlit Secrets or the environment.

With the key present, the toolkit can (1) create AI-assisted syntheses from retrieved, source-linked excerpts and (2) do **limited on-demand official update searches**. Checklist generation offers an opt-in checkbox, checked by default when a key is configured, to look for recent updates. New results are held as **unverified candidates**, shown separately and attached to exports; they do **not** silently change official research classifications. This avoids confusing unreviewed web results with validated data.

The short update operation has a roughly 20-second client timeout; actual provider latency, availability and charges depend on the configured API. We have not executed billable API tests with your key.

## Implementation boundary

This is an integrated, functional **first milestone**, not a production-grade autonomous RAG database. The current source retrieval is country-filtered, lexical (keyword) search over the repository's source-linked research records; optional AI synthesis uses only those retrieved excerpts. A persistent vector index, full-text document parsing of the HTML reports, source-change scheduler, authentication, persistent multi-user drafts and official review/approval workflows are future work. Recommendations are evidence-aware prompts for verification and next action; they are not an independently validated government performance audit.

All existing country research data remain unchanged and are *not* overwritten by users' form answers. The app uses Streamlit session state for temporary answers, so users must download their outputs before closing the session.

## Dataset verified for this build

- 195 countries in the country selector
- 17 institutional domains
- 72 eligible checklist interventions
- 27 researched institutional mechanisms in 26 countries
- 459 institutional evidence records
- 2,295 research matrix rows, including 13 ineligible items per reviewed mechanism
- 75 additional source-specific intervention findings
- Estonia: 1 mechanism, 13 institutional domains with linked sources, 3 source-specific intervention requirements with links
- Sweden: 1 mechanism, 6 institutional domains with linked sources, 3 source-specific intervention requirements with links

These numbers describe repository coverage, not institutional effectiveness. They have not been verified against live government websites in this delivery.

## Local verification

From the full repository folder, use:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Unit/integration tests from this delivery passed 7/7 against the uploaded repository's actual data; Word output was rendered and inspected. No live Streamlit deployment or real OpenAI API search was executed within this development environment.
