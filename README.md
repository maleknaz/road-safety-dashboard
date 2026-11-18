# Global Road Safety Atlas, unified governance dashboard (November 18, 2026)

## Included
Eight-tab Streamlit dashboard preserving the earlier navigation concept: Start here, Atlas, Taskforces, Existing documents, Bodies & strategies, Checklists for your taskforce, Country case studies, Download data.

- 195-country original directory; 290 entity rows; all records retained without replacing unrelated countries.
- 27 separately analyzed mechanisms in 26 countries, reflecting two distinct US state mechanisms.
- User's *exact* 85-cell COFOG/ISIC evidence matrix is the governing ideal framework, with 72 populated interventions and 13 undefined X cells.
- Seven reviewed case audits (Croatia, Cyprus, Estonia, France, Japan, Jordan, Latvia) have their prior cell codes and institutional classifications retained, including their original count totals.
- Fifteen legacy case-study profiles have historical aggregate counts only, not invented cell allocations.
- Five recent case-study profiles (Mexico, Poland, Qatar, Romania, Serbia) provide targeted provisional evidence matches with N/A for unverified cells. Full detailed audits are NOT completed.
- All source records distinguish formal strategy approval, drafting, technical coordination, project execution and outcome verification.

## Where numbers come from
The 195-country policy and entity information comes from the three supplied HTML directories. Country map comes from the supplied Atlas HTML. Country case summaries and seven reviewed cell-code sequences are retained from previous Case_Studies research snapshot in Project Library; the 20 non-audited profiles do NOT receive new fully verified scores. The framework comes directly from `road_safety_evidence_matrix(1)(1).xlsx` supplied in this conversation.

## Evidence boundary
A = exact planned responsibility, P = partial, N/A = no adequate cell-specific verification. Formal membership F, functional P, and unverified N/A are kept distinct. A/P do not prove implementation. A government national strategy is not automatically a council-authored strategy. In the latest five profiles, some provisional A/P examples are shown, but no unsupported overall scores are produced.

## Install / deploy
1. Unzip the full package and commit its contents at the ROOT of your Streamlit application GitHub repository, retaining the directory structure including `.streamlit` and `data/`.
2. Set the app entrypoint to `app.py` in Streamlit Community Cloud, or run locally: `pip install -r requirements.txt` and `streamlit run app.py`.
3. Confirm each tab loads, including the embedded global Atlas and case study. Clear app cache/reboot if Cloud displays old pages.
4. Do not create a separate Streamlit app: deploy into the GitHub repository already attached to https://global-road-safety-atlas.streamlit.app/.

**Important:** This ZIP does not itself upload to GitHub or redeploy the live Streamlit site. The assistant has no authenticated repository-deployment connection in this environment.

## Research completion
`data/Evidence_Review_Queue.csv` contains defined intervention cells for 20 profiles without a completed source-level audit. The earlier case counts are historical and should not be republished as independently reviewed comparative rankings. Do not mistake N/A for absence of national road safety activity. Update each reviewed cell only against direct, attributable national or local evidence and record the responsible institution and source.

## Generated files
- `data/Country_Master_195.csv`: merged country-level reference overview.
- `data/Global_Taskforce_Directory_290.csv`: 290 entity records.
- `data/Global_Document_Catalogue.csv`: country document catalogue.
- `data/Global_Bodies_and_Attributed_Documents.csv`: entity-document attribution records.
- `data/Institutional_17_Domains_27_Mechanisms.csv`: 459 domain classification rows.
- `data/Interventions_85_Cells_27_Mechanisms.csv`: 2,295 intersection rows.
- `data/Ideal_Framework_85_Cells.csv`: exact framework.
- `data/Country_Mechanism_Review_Status.csv`: case maturity and legacy counts.
- `data/Evidence_Review_Queue.csv`: outstanding source verification tasks.

## Versioning
Prepared 2026-11-18. Research contents must be treated as a living evidence catalogue; recheck official laws, new programme adoption, institutional appointments, interventions, dates and links periodically. No formal UN/UNITAR endorsement is implied.
