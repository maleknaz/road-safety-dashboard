# Road Safety Toolkit: country refresh and title fix

Release date: 24 November 2026

## What was corrected

1. The browser tab title is now **Road Safety Toolkit**. The Start Here page heading also displays **Road Safety Toolkit**. Individual embedded HTML page titles now start with the product name.
2. The Toolkit's country and mode selectors register an explicit change callback and display a clearly identified current-country/current-workflow banner.
3. The Toolkit is wrapped in a Streamlit **fragment**. When the user switches countries or modes, Streamlit re-renders this Toolkit region, instead of rebuilding all six large embedded HTML pages. This reduces unnecessary work and prevents other HTML iframes from resetting on Toolkit widget interactions.
4. Pairwise comparison retains a valid peer country when the primary country changes. When a change would select the same country on both sides, it switches to the previous primary country when possible.
5. When comparison focus changes, an old RAG retrieval or synthesis from the previous focus is discarded instead of being presented as the new comparison. The user explicitly retrieves the new topic to control API usage.
6. The country-specific checklist drill-down controls have country-scoped keys, and form resubmission resets stale detail selectors while retaining saved user answers and research records.
7. Cached HTML reading avoids repeated disk work on full-app reruns while automatically refreshing when an HTML file's modification time changes.

## Uploading the small update package to GitHub

1. Download and extract `Road_Safety_Toolkit_Country_Refresh_Patch.zip`.
2. Open https://github.com/maleknaz/roadsafety_toolkit and select **Add file > Upload files**.
3. Upload the extracted files into the **repository root**, preserving the `institutional_toolkit/` and `tests/` paths. Do **not** upload the ZIP as a single file. All existing file names should remain the same.
4. Commit your changes. If the Streamlit app is connected to the same branch, Streamlit Community Cloud should rebuild it automatically.
5. Hard-refresh https://roadsafetytoolkit.streamlit.app/ once deployment finishes.

The updated source files are `app.py`, the six top-level HTML pages, and `institutional_toolkit/ui.py`. `tests/` and the two markdown guides are optional QA files.

The complete repository backup ZIP is offered as an alternative or safety copy. It is **not necessary** to replace the five country research datasets. Their bytes are unchanged.

## Recommended 2-minute post-deployment check

- The browser title and Start Here headline should read **Road Safety Toolkit**.
- In **Road Safety Institutional Toolkit**, choose **Explore country findings**, then Estonia and Sweden. The "Currently viewing" banner and institution findings should immediately reflect each country, with no Generate button.
- Choose **Benchmark internationally**, switch Estonia / Sweden, and confirm the summary shows the correct country's coverage.
- Choose **Compare with another country**, select Estonia and Sweden, then change Estonia to Sweden. The tool should choose a different comparison country (preferably Estonia), never Sweden against itself.
- Change the **Comparison focus** after retrieving data. The old analysis should not be presented as belonging to the new focus.
- Choose **Generate my institutional checklist**, change country, and verify the questions and generated checklist are scoped to the selected country. The checklist still requires the Generate button after the optional questionnaire, by design.
- Verify that the other six HTML tabs still open and their independent country searches respond.

## QA scope and limits

The source bundle passed 30 local automated checks (Python unit/regression, Chromium JavaScript interaction tests, 390-pixel mobile smoke tests, report generation and archive integrity). The five interactive HTML pages were exercised with repeated country changes and reset controls, with no browser JavaScript exceptions.

Important: this container does not have a running Streamlit server or external access to the deployed site. We tested the Streamlit app's navigation and country-selection behavior through isolated widget simulations and source checks, while the HTML pages were actually executed in headless Chromium. The deployed app's real Streamlit websocket rerender, remote source URLs, cloud secrets, and live OpenAI calls still require the short post-deployment acceptance test above.
