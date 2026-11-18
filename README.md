# Global Road Safety: integrated deployment package

This is a self-contained Streamlit app with the four user-supplied global HTML pages, two reorganized interactive research pages and a plain-language introduction. Its visual system matches the supplied navy/cyan public-sector reference pages. No official endorsement is asserted.

## Run or deploy

1. Extract the ZIP into one folder. Keep `app.py`, `requirements.txt`, the `.streamlit` folder, six research HTML pages, and `data/` together.
2. Create a GitHub repository; upload all extracted files, preserving names and folders.
3. In Streamlit Community Cloud, create an app pointing at `app.py` in the repository root.
4. No additional API keys are needed. The embedded pages use bundled HTML and JavaScript.
5. Check **Start here**, **Atlas**, **Taskforces**, **Existing documents**, **Bodies & strategies**, **Checklists for your task force**, **Case Studies**, and **Download data**.

To run locally: `pip install -r requirements.txt`, then `streamlit run app.py`.

## Tabs and intended use

- **Start here**: concise orientation for readers new to the research, scope, definitions and scores.
- **Atlas**: the original user-supplied interactive initiative atlas.
- **Taskforces**: the original user-supplied 195-country institution directory.
- **Existing documents**: the original publication directory, with 5 supplemental policy entries for independently reviewed countries where these were absent.
- **Bodies & strategies**: the user-supplied 195-country policy-attribution directory. Only reviewed-country records are replaced with their latest reviewed versions (21 countries had a different reviewed entry). All other countries retain supplied records.
- **Checklists for your task force**: interactive 17-domain participant checklist and 72 defined mission prompts, with a CSV export worksheet for selected items.
- **Case Studies**: comparison table for all 22 mechanisms, filters, country profiles, evidence sources and full 17-domain/85-cell tables for the seven source-audited cases.
- **Download data**: structured research data and seven country-level detailed audits.

No correction-log tab is included. Correction history is not presented as a public dashboard. The updated country evidence and scores appear directly in the relevant comparison pages.

## Coverage and limitations

- Global directories: 195 country entries, with limitations recorded per source.
- Detailed subset: 22 coordinating mechanisms across 21 countries, including separate US state mechanisms.
- Documented institutional links: 265 of 374.
- Documented exact planned tasks: 109, partial: 399, unverified: 1076, from 1584 comparisons.
- Seven cases have detailed sourced cell-level CSV audits: Croatia, Cyprus, Estonia, France, Japan, Jordan, Latvia.
- Earlier reviewed cases retain their documented reviewed summary values; gaps are not invented. A strategy or assigned task is not evidence of successful implementation or causal effects.
- The four original HTML source pages preserve their original global records, except the limited, source-backed policy alignment described above. There is no blanket re-verification of 195 countries.

## Editorial data reconciliation

The supplied directory and the latest reviewed-case pages were compared directly. 21 reviewed-country records in the body-to-policy directory were updated to their reviewed versions: Australia, Brazil, Brunei, Bulgaria, Cambodia, Canada, Chile, Costa Rica, Croatia, Cyprus, Czechia, Estonia, France, Japan, Jordan, Latvia, Sweden, Türkiye, Uganda, United Kingdom, United States. 5 newly documented items were appended to the existing-documents directory: Croatia / National Road Traffic Safety Plan 2021–2030, Estonia / Road Safety Implementation Plan 2026–2029, France / Decisions of the Interministerial Road Safety Committee, 17 July 2023, Japan / 11th Basic Traffic Safety Plan 2021–2025, Japan / 12th Basic Traffic Safety Plan 2026–2030. Existing records for non-reviewed countries were not rescored or rewritten. This reconciliation is documented here for maintainers, not displayed as a public correction log.

## Hosting note

Deploy to a new Streamlit application or replace the existing `app.py` and add the bundled HTML/data assets to the original Atlas repository if you wish to use this as the consolidated version. Keep a backup of the repository before replacing an existing application. A deployed page is not automatically editable: edits to HTML or datasets require updating the repository and redeploying.

## Current public research tabs (November 2026)

1. Start here
2. Atlas
3. Taskforces
4. Existing documents
5. Bodies & strategies
6. Checklists for your task force
7. Case Studies
8. Download data

The earlier comparison and detailed assessment HTML are retained under `reference_source_pages/` for maintenance only, not as dashboard tabs. There is no correction-log tab. The case study comparison counts are drawn from the same reviewed 22-mechanism dataset as the detailed case cards. The checklists are independent user planning tools; selecting a checkbox does not change evidence scores.
