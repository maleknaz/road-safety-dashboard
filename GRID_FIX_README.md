# Road Safety Toolkit: verified four-column comparison grid

## Why this release

The previous update was not sufficient: the original grid check only asserted that the Python code called `st.columns(4)` and never verified the page's rendered visual layout. The user still saw a 17-item vertical list.

This revision replaces **Institutional comparison by domain** with a **single self-contained CSS grid** of 17 interactive cards. The layout no longer depends on Streamlit column arrangements or the global CSS rules applied by other tabs.

## What you will see

- Desktop: **four cards per row** (five rows for 17 domains).
- Intermediate widths: three or two cards per row.
- Narrow phone screens: one per row for readability.
- Click any card to highlight it and open the corresponding full-width Estonia/Sweden (or other country pair) comparison table below the grid.
- Each card shows whether each country's domain has a linked source in the reviewed subset, **not a ranking of performance**.
- The comparison table retains the original evidence, institution, function, implementation, qualification and cited source link fields.
- The repeated **Membership: Not verified** item is **not** displayed.
- The informative navy **Road Safety Institutional Toolkit** header from the latest previous patch is retained.

## GitHub installation, one file

1. Download and **extract** `Road_Safety_Toolkit_Verified_Grid_Patch.zip`.
2. In your GitHub repository (https://github.com/maleknaz/roadsafety_toolkit), find the existing `institutional_toolkit` folder.
3. Replace **`institutional_toolkit/ui.py`** with the new version in the patch, preserving its exact folder path. GitHub's `Add file > Upload files` will show the replacement in the commit summary.
4. Commit. The connected Streamlit Community Cloud deployment should rebuild.
5. Open **Road Safety Institutional Toolkit > Compare with another country**. Select Estonia and Sweden. Scroll to **Institutional comparison by domain** and confirm four domain cards in each desktop row. Click a domain to see its complete detail table. Try changing the country pair, too.
6. If the old accordions persist, inspect the GitHub `institutional_toolkit/ui.py` file after committing and search for `_domain_grid_html`. If that function is absent, the new file was not uploaded to the correct path. Refresh the deployed page after Streamlit finishes rebuilding.

This patch is based on the **most recent Toolkit header release**. Do not re-upload the older `Domain_Grid_Patch` or `Header_Update_Patch` after this one, or you may overwrite the correction.

## Validation

- 41 repository regression tests passed.
- Live Chromium DOM layout tested at 1440 px (four columns), 960 px (three), 680 px (two) and 390 px (one).
- 17 interactive domain cards displayed for Estonia vs Sweden.
- Clicking a card changed the detailed side-by-side table and preserved one selected card.
- Display escaping and absence of the repeated Membership field were checked.
- Other tabs, country data, source links, RAG pipeline, and export logic were not changed.

Browser tests were run on the component HTML outside the hosted Streamlit site; final deployment must still be checked on the live app. The bundle intentionally does not include API secrets.
