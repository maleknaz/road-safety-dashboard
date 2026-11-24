# Road Safety Institutional Toolkit - Light theme correction

This patch fixes the unreadable dark notification panel shown in the country comparison view. The earlier stylesheet colored only Streamlit's outer notification wrapper, but Streamlit can render a dark nested BaseWeb notification surface inside it.

## What changed

- `institutional_toolkit/ui.py`: uses a light, high-contrast notice component for **all** informational, warning, and error messages across country findings, international benchmarking, pairwise comparison, and checklist generation.
- `app.py`: extends the existing scoped CSS to cover nested notification layers, form inputs, metrics, expanders, captions, and buttons. The main navigation also gets a light background with dark text.
- `.streamlit/config.toml`: explicitly selects Streamlit's light theme for widgets, data tables, and popovers, regardless of the viewer's preferred dark mode.

The Atlas/Case Studies and other existing HTML content files, evidence tables, report logic, and application routes are unchanged.

## Apply to GitHub (browser)

1. Download **Road_Safety_Toolkit_Light_Theme_Patch.zip** from the conversation and extract it on your computer.
2. In the [roadsafety_toolkit](https://github.com/maleknaz/roadsafety_toolkit) repository, use **Add file > Upload files** from the repository root.
3. Drag these extracted items into the upload area together, retaining their folders:
   - `app.py`
   - `institutional_toolkit/` directory (contains its updated `ui.py`)
   - `.streamlit/` directory (contains `config.toml`)
4. Confirm GitHub shows the intended paths before committing. If GitHub does not preserve folders, upload each file into its matching folder instead.
5. Commit as `Fix Toolkit notification colors and enforce light theme`.
6. After Streamlit completes its redeploy, refresh your app with **Ctrl+Shift+R**, go to **Road Safety Institutional Toolkit > Compare with another country**, and confirm that the previously dark message is now pale blue with dark text.

You may also use **Road_Safety_Toolkit_Full_Light_Theme_Repository.zip** as a backup, but do not upload either ZIP directly into the repository as a file. Extract its contents first.

## Validation

- Python syntax checks passed for app, toolkit UI, and original planner.
- CSS passed a standards-based parser without errors.
- A headless Chromium test recreated the nested dark Streamlit notification and confirmed the resulting computed background is `rgb(238, 246, 250)` with readable text `rgb(23, 50, 74)`.
- Contrast ratios for the notice text and light backgrounds exceed 12:1.
- Actual Streamlit deployment was not rendered in this environment. Verify the hosted app after the GitHub commit.
