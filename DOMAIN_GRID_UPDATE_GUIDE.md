# Road Safety Toolkit: compact comparison grid and membership-display update

## What changed

- Removed the repeated **Membership: Not verified** field from the *Explore country findings* institutional-domain evidence display and from the *Institutional comparison by domain* view.
- Removed the same field from the **Country findings** and **Pairwise comparison** Word reports, so printed results match what readers see.
- Replaced 17 stacked full-width comparison expanders with **four compact domain cards per row**, each showing only the presence or absence of linked source records for the two selected countries. Selecting a card displays a full-width, two-country evidence table beneath the grid.
- Retained the original `formal_membership` records and the separately selectable membership topic in controlled RAG for future targeted verification. No research data were deleted or reclassified.
- Kept the light background, readable contrast, source links and country-specific selection behavior.

## Install on GitHub

1. Download and **extract** `Road_Safety_Toolkit_Domain_Grid_Patch.zip`.
2. Open https://github.com/maleknaz/roadsafety_toolkit and choose **Add file > Upload files**.
3. Upload these extracted files, keeping their relative folders:
   - `institutional_toolkit/ui.py`
   - `institutional_toolkit/reports.py`
   - `tests/test_domain_grid.py` (optional regression tests)
4. Commit the changes. Streamlit should redeploy if the app is linked to this branch.
5. Open `Road Safety Institutional Toolkit` > `Compare with another country`, select Estonia and Sweden, and confirm the 17 domains display as four cards per row, with a full-width comparison table appearing for the selected card.
6. Check `Explore country findings` and the generated Word reports to confirm the repeated Membership field is no longer displayed.

The patch does **not** contain or change `app.py`, `data/`, `planner.py`, the existing HTML files, or Streamlit light-theme configuration.

## Validation

- `python -m compileall institutional_toolkit/`
- `PYTHONPATH=. pytest -q tests` -> **34 tests passed**, including new grid layout, click-to-select behavior, country pair isolation, report output and escaped HTML content.

These are local tests using the actual repository dataset and simulated Streamlit widget behavior. The hosted Streamlit page must be checked after deployment.
