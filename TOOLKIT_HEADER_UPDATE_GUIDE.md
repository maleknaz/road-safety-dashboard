# Road Safety Institutional Toolkit | Header update

## What changed

**Only** the `institutional_toolkit/ui.py` application code changes in this patch. The existing country evidence, reports, retrieval engine, other tabs, and light-theme configuration are preserved.

- New full-width, Atlas-style header with matching **70 px white label strip** and **fixed 320 px navy hero** on desktop.
- Readable mobile layout with automatic height expansion to avoid clipped text.
- Concise descriptions of all four available workflows below the hero.
- Explicit explanation of the controlled research retrieval and optional AI features, without suggesting that missing evidence has been verified.

## Install in GitHub

1. Extract `Road_Safety_Toolkit_Header_Update_Patch.zip` on your computer.
2. Open <https://github.com/maleknaz/roadsafety_toolkit>.
3. Use **Add file → Upload files** to upload the extracted `institutional_toolkit` folder, maintaining its internal path.
4. Commit the change and wait for the existing Streamlit deployment to rebuild.
5. Open the **Road Safety Institutional Toolkit** tab and verify its header at desktop and mobile width.

Do not upload the ZIP itself, and do not overwrite the complete repository with the patch.

## Verification performed

- `python -m pytest -q tests`: **37 tests passed**, including three header-specific checks.
- Browser layout preview rendered at 1440 px desktop, 1024 px tablet, and 390 px mobile.
- Measured 70 px top strip and 320 px hero at desktop/tablet sizes.
- Confirmed no horizontal overflow in the tested widths and readable light-on-dark hero text.
- No real Streamlit server or live GitHub deployment was exercised in this environment.
