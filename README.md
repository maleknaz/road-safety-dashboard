# Reviewed Road Safety Dashboard: deployment package

This is a **standalone Streamlit dashboard** for the mechanisms reviewed through the Latvia case in November 2026. It does not need any of the older Atlas, case-study or task-force HTMLs to run. The four HTML pages are self-contained and are included beside `app.py`.

## Deploy as a separate Streamlit app

1. Extract the ZIP; keep the extracted file names and directory structure unchanged.
2. Create a **new GitHub repository**, then upload the extracted files to the repository root. Upload the hidden `.streamlit/config.toml` folder too if your file manager supports it. No Python build scripts are needed.
3. In Streamlit Community Cloud, create a new app and select this repository, its main branch and entrypoint `app.py`.
4. The app installs the single requirement in `requirements.txt`. No credentials or API keys are needed.
5. Check that the tabs **Practice vs Checklist**, **Reviewed Case Assessments**, **Correction Log**, **Bodies & Their Strategies** and **Download data** appear.

**If updating the existing Atlas instead:** do not blindly overwrite its current `app.py` because that may remove the existing Atlas and case-study tabs. Copy the four HTML files and optional CSV/JSON evidence files from this package into the existing repository, then add four tabs to the existing Streamlit application using the `components.html` approach shown in this app's source.

## File roles

- `app.py`: self-contained reviewed-country Streamlit app.
- `requirements.txt`: Streamlit dependency.
- `.streamlit/config.toml`: color theme (optional but included).
- `Practice_vs_Checklist_Reviewed_2026.html`: interactive summary, checklists and comparison.
- `Reviewed_Case_Assessments_2026.html`: country-level evidence and detailed matrices.
- `Reviewed_Case_Change_Log_2026.html`: which scores changed and why.
- `Bodies_Their_Road_Safety_Strategies_Reviewed_2026.html`: wider country policy directory, with reviewed-country annotations. **This is a 195-country reference directory, not 195 re-audited cases.**
- `Reviewed_Cases_2026_Data.json`: canonical data used for consistency checks and header metrics.
- `Reviewed_Cases_2026_Summary.csv` and `Reviewed_Cases_2026_Change_Log.csv`: structured comparisons and correction history.
- `*_2026_Domain_Gap_Audit.csv`, `*_2026_Intervention_Gap_Audit.csv`, `*_2026_Change_Log.csv`: country-specific evidence audits.
- Croatia and Cyprus standalone detailed audit HTML files are supplemental, not required by `app.py`.

## Evidence limitations

The reviewed subset includes 22 coordinating mechanisms in 21 countries (two US state mechanisms). Domain coverage = 265/374, documented planned-action matches = 109 exact, 399 partial, and 1,076 unverified out of 1,584 scored comparisons. Thirteen further ideal cells per mechanism are excluded because the ideal interventions have not been defined.

Seven recent mechanisms have source-reviewed full 85-cell audits: Croatia, Cyprus, Estonia, France, Japan, Jordan and Latvia. Earlier cases retain their previously reviewed summary scores; their formal-versus-partner splits are N/A where not independently recorded. None of the planned-action counts are claims of demonstrated effectiveness.

The directory and policy references are snapshots from the November 2026 reviewed package and can change after publication. This is a research working dashboard, not an official United Nations publication.

## Local run (optional)

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```
