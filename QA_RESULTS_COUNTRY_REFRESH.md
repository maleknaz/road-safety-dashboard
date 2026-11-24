# Road Safety Toolkit country-refresh QA results

**Code base:** Last supplied controlled-RAG repository archive, updated 24 November 2026.

**Result:** 30 automated checks passed locally. No failed assertions in the final run.

### Tested successfully

- App code syntax and seven-tab integration, including six HTML pages and the Toolkit fragment.
- Main browser title and all six HTML metadata titles set to Road Safety Toolkit; landing-page visible heading updated.
- Country changes in five interactive HTML pages: Sweden, Estonia, Canada, return to Sweden; source cards and counts updated.
- Country and status/filter reset actions on embedded HTML pages.
- No JavaScript exceptions during those headless Chromium scenarios.
- Mobile viewport (390 × 844) inputs and country-selection interactions across the five interactive HTML pages.
- Streamlit Toolkit widget rerender contract simulated for Estonia/Sweden and workflow switches.
- Peer-country validation after a primary-country change; no accidental self-comparison.
- Country-isolated controlled RAG, index and citation restrictions, bounded domain allowlist rules, synthetic mocked model output verification.
- Estonia, Sweden, Canada and Afghanistan source coverage and 72-item checklist prefill.
- Word country briefs and country-pair reports generated and parsed.
- International benchmarking Excel workbook generated as valid ZIP-based XLSX with 195 country rows plus header.
- Country research files, controlled RAG engine, report logic and light-theme configuration unchanged.

### Tested visually

The Start Here HTML page was rendered in headless Chromium at 1280 × 820 and 390 × 850. The title was visible, content rendered, and there was no horizontal overflow at these viewports. The Existing documents page was also checked at mobile width after selecting Sweden, with no horizontal overflow.

### Cannot validate until deployment

Streamlit's real websocket/frontend lifecycle is not running in this isolated QA environment. Remote Streamlit Cloud behavior, API credentials, and online update searches were not exercised against a live instance. The expected fix uses Streamlit's documented `@st.fragment` independent rerun behavior.
