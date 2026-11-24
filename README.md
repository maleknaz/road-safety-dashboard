# Global Road Safety Atlas: Data-connected Checklist MVP

## What changed

The final Streamlit tab now invokes `planner.render()` instead of embedding a standalone HTML file. It loads four CSV sources, the canonical 17-domain/72-intervention framework, and a controlled 195-country JSON list.

## Deployment

1. Copy `app.py`, `planner.py`, `requirements.txt`, and the entire `data/` directory into your Streamlit GitHub repository. Keep the six HTML pages next to `app.py` (already included in this complete ZIP).
2. Commit and redeploy in Streamlit Community Cloud, using `app.py` as the entry point. Install dependencies from `requirements.txt`.
3. Open the last tab, select a country and the relevant mechanism (if it has available research), then create a private draft.
4. Use `Research evidence` to inspect cited findings; enter independently confirmed assessments in `17 domains` and `72 interventions`.
5. Use the action tracker; export draft JSON regularly, and export Word and Excel from Reports & backup.

## Data provenance

- `data/countries_195.json`: countries controlled list from the previously supplied HTML.
- `data/checklist.csv`: canonical checklist (85 possible positions, 72 defined).
- `data/institutional_evidence.csv`: 459 institutional domain records for 27 researched mechanisms; research classifications, not approved self-assessments.
- `data/source_findings.csv`: 75 source-linked intervention findings for 27 researched mechanisms, with source URLs and boundaries.
- `data/intervention_evidence.csv`: 2,295-row country mechanism matrix and metadata; used to map country to mechanism and provide the full research registry.

## Critical limitations

- This MVP is **not** a secure shared country workspace. Edits live only in the active Streamlit browser session. Use JSON download/import to continue work between sessions. Do NOT collect confidential information in this demo.
- Do not treat source suggestions as verified government statements; users must assess and cite supporting documents.
- No registration, permissions, approval workflow, or publication to the public Atlas is enabled. The publication button is deliberately disabled.
- For production, connect to a managed PostgreSQL store with authenticated accounts, row-level authorization, versioned drafts, review and approval logs and private document storage. Avoid SQLite or localStorage for a multi-user deployment; Streamlit Community Cloud's filesystem is not suitable for reliable shared persistence.
- The 27 research mechanisms do not cover every country. The remaining countries start with a blank self-assessment, not presumed road safety gaps.

## Recommended production tables

`countries`, `jurisdictions`, `mechanisms`, `framework_domains`, `framework_interventions`, `research_evidence`, `assessments`, `assessment_collaborators`, `domain_responses`, `intervention_responses`, `actions`, `review_requests`, `review_decisions`, `published_snapshots`, `audit_log`, `attachments`.

Require authentication; enforce authorization at the database API layer; keep research evidence read-only; only publish an approved immutable version. A reviewer must not approve their own assessment. Preserve links and exact source provisions for each claimed match. Never silently merge private drafts into Atlas country profiles.

## Testing completed

Validated source counts: 195 countries, 17 domains, 72 defined interventions, 27 research mechanisms, 75 source-specific findings. Python syntax compilation passed; Word and Excel byte generation passed on a sample Serbia draft. This environment does not have Streamlit installed, so full interactive web deployment remains to be tested in Streamlit Cloud.

## Institutional Toolkit update, November 2026

The former final "Checklists for your taskforce" tab has been updated to **Road Safety Institutional Toolkit**. It adds country evidence, coverage benchmarking, conditional pairwise comparison, adaptive pre-assessment questions, and prefilled evidence-aware checklists. The original detailed `planner.py` remains available within the new checklist workflow. See [TOOLKIT_UPDATE_GUIDE.md](TOOLKIT_UPDATE_GUIDE.md) for deployment instructions, evidence limitations and optional AI configuration.
