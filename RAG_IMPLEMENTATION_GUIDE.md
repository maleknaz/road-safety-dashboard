# Road Safety Institutional Toolkit - Controlled RAG, Milestone 2

This update changes **only** the Python Toolkit tab. It does not modify any of the six HTML pages, existing light-theme CSS, country research tables, or the original planner.

## What is in this version

- A country-filtered index of **source-linked research excerpts** from the repository's existing institutional and intervention evidence tables.
- Query retrieval with local BM25-style term scoring plus Unicode character-gram matching. Retrieval works without an AI API key.
- Metadata on each excerpt, including a stable `RS-...` evidence ID, country, jurisdiction, original URL, source title/locator when available, matrix intervention ID, research review date and evidence limitations.
- Optional, click-to-run OpenAI analysis using the Responses API. The generation call has **no browsing tools**. It receives only the retrieved excerpts, returns structured JSON, and each factual claim must cite a known evidence ID. Invalid citations make the response fail closed. AI summaries are labelled draft interpretations, not verified findings.
- Separate, optional freshness checking restricted to already reviewed **official primary-source domains** for the selected country. It looks for recent institutional changes and remains a provisional lead until independently reviewed. It never overwrites the source datasets or feeds directly into the RAG index.
- An evidence-grounded comparison workspace: independently retrieve excerpts from each selected country and optionally synthesize a cited analysis. The rest of the country comparison is preserved.
- A checklist traceability panel: retrieve evidence for a selected intervention, or clearly labelled contextual material when direct evidence is missing.
- Downloadable cited JSON and Word evidence-analysis drafts.
- Support for **manually curated original document text/PDFs**, when an approved manifest and local files are supplied. No arbitrary web scraping or user-uploaded file indexing occurs in this release.

## Important limits (read before publication)

The repository contains **195 country labels**, but detailed, source-specific reviews exist for only a subset of countries. Running the included audit against the repository dataset yielded 302 source-linked research excerpts across 26 countries. These are research-derived excerpts with original source links; they are not full-text copies of every official policy or legal document. Do not interpret the absence of a retrieved record as evidence that a country has no relevant institution.

The 72-item matrix remains the assessment framework. Unlinked matrix items are **not** indexed as factual evidence; user questionnaire answers remain unverified.

This version is an operational controlled **retrieval-augmented generation pipeline**. It does not yet implement embedding vectors, an always-on web crawler, automatic document verification, organizational accounts, or human-approved ingestion of newly found sources. The local hybrid retriever combines BM25 with character-level matching for multilingual name variants; it is not an embedding-based semantic retriever.

## GitHub update procedure

1. Download the **Road Safety Controlled RAG Patch ZIP** from ChatGPT and extract it.
2. Open <https://github.com/maleknaz/roadsafety_toolkit>.
3. Select **Add file > Upload files**.
4. Upload the extracted folder/files, preserving the repository-relative paths:
   - `institutional_toolkit/rag.py` **new**
   - `institutional_toolkit/updates.py` **replace**
   - `institutional_toolkit/ui.py` **replace**
   - `institutional_toolkit/reports.py` **replace**
   - `requirements.txt` **replace**
5. Keep your deployed `app.py`, `.streamlit/config.toml`, six HTML pages, `planner.py`, and the entire `data/` folder unchanged.
6. Commit. Your connected Streamlit deployment should rebuild. Verify the deployment from the **Road Safety Institutional Toolkit** tab.

The patch also contains this guide, an optional document manifest example, and regression tests. You may upload those too, but they are not needed for runtime.

If GitHub's browser uploader flattens a nested folder, use its folder view to confirm `institutional_toolkit/rag.py` really lives inside the existing `institutional_toolkit` directory, not in the repository root. If upload is confusing, use the full repository backup ZIP and upload the *extracted contents*, not the ZIP itself.

## How to test the app

1. **Estonia > Explore country findings:** Search for `Government Traffic Commission and the 2026–2035 Road Safety Programme`. Open each excerpt and review its exact source URL and research limitations.
2. If your OpenAI API key is configured in **Streamlit app Settings > Secrets**, click **Generate citation-checked AI synthesis**. Check that each factual claim includes an `RS-...` evidence ID linking to its original source.
3. Select **Compare with another country**, choose **Sweden**, and click **Retrieve comparable source excerpts**. Ensure that both countries have independent source excerpts, and that any AI comparison cites those excerpts.
4. **Generate my institutional checklist:** Answer or skip the questionnaire, generate the checklist, then open an intervention and expand **Trace indexed evidence for this checklist intervention**. Note the distinction between direct intervention evidence and general institutional context.
5. **Check for newer official information** is always optional and requires a configured OpenAI API key. Check the permitted domain names in the results. A new item remains a provisional lead.
6. Try a country without a detailed review, such as Afghanistan. The app should explicitly report insufficient source-linked evidence, not automatically claim the country has no coordinating body.
7. Generate and download the cited Word report. It should contain the source IDs, research limitations, and actual source URLs.

### Configuring the AI key

To enable AI synthesis and online update checking, open your deployed app in Streamlit Community Cloud and place this in your **app Secrets** (not GitHub):

```toml
OPENAI_API_KEY = "YOUR_API_KEY"
```

The model can be changed with the optional environment variable `ROAD_SAFETY_OPENAI_MODEL` (default `gpt-5-mini`). API requests require an appropriately configured OpenAI API project and incur usage costs. Model names and quotas should be checked against the current account.

### Safety of the online search

The freshness request is explicit, limited to selected country + topic, and uses the recent research-check date where present. Official domains are taken from pre-existing rows classified as official agency/government sources. Source URLs from secondary published-law transcriptions do not authorize a web-search domain. The search uses a low web-search context and bounded output, and results are cached for six hours for matching public-source requests. This limits scope and repeated expense, but is **not an exact web-tool-call count guarantee**. Results without both an allowed-domain URL and a tool citation are omitted. No new external claims automatically enter the institutional evidence tables.

### Add original curated documents later

To expand from research excerpts to original document content, create:

```text
data/
  knowledge_documents.csv
  knowledge_documents/
    estonia_strategy_2026.txt
    sweden_action_plan_2026.pdf
```

The manifest must use the following headers:

```csv
country,relative_path,source_url,title,authority,published_on,jurisdiction,domain,source_locator
```

Each manifest row should be manually checked by a curator. Only files inside `data/knowledge_documents/` are opened. Supported formats are UTF-8 `.txt`, `.md`, and `.pdf`. The index rejects absolute path escapes, oversized files, unapproved schemes, and unlisted document files. PDF reading is capped at 35 pages per document and 80,000 characters. The underlying RAG citations retain each document's declared original URL and local segment number. A curated excerpt is *not proof of implementation*.

Private internal government documents should **not** be added to the public GitHub repository. A future authenticated, private storage and review workflow is needed for such materials.

## Automated testing

```bash
python -m pip install -r requirements.txt
python -m pip install pytest
python -m pytest -q tests/test_controlled_rag.py
```

The tests cover existing-data counts, Estonia/Sweden retrieval, country isolation, strict citations, unsafe domains, missing-country behavior, optional-document path security, no-model-call fallbacks, and Word document traceability. The OpenAI integration is mock-tested; no live API call has been made during this development.
