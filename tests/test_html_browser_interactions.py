"""Browser regression tests for the five interactive embedded country pages.

These HTML files are rendered directly in headless Chromium so this test does
not require the Streamlit websocket backend. The separate Streamlit fragment
rerender contract is verified by test_ui_country_switch.py.
"""
from __future__ import annotations
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
playwright = pytest.importorskip('playwright.sync_api')


@pytest.fixture(scope='module')
def browser():
    with playwright.sync_playwright() as ctx:
        browser = ctx.chromium.launch(
            executable_path='/usr/bin/chromium',headless=True,
            args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
        yield browser
        browser.close()


def _page(browser,name):
    pg=browser.new_page(viewport={'width':1280,'height':900})
    errors=[]
    pg.on('pageerror',lambda err: errors.append(str(err)))
    pg.set_content((ROOT/name).read_text(encoding='utf-8'), wait_until='domcontentloaded',timeout=40000)
    pg.wait_for_timeout(120)
    return pg,errors


def test_existing_documents_country_select(browser):
    pg,errors=_page(browser,'Existing_road_safety_documents.html')
    try:
        for country in ['Sweden','Estonia','Canada','Sweden']:
            pg.locator('#countryPick').select_option(country)
            assert pg.locator('.country').count()==1
            assert country in pg.locator('.country').first.inner_text()
        pg.locator('#reset').click()
        assert pg.locator('#countryPick').input_value()==''
        assert pg.locator('.country').count()>1
        assert not errors
    finally:pg.close()


def test_atlas_search_country_switch_and_reset(browser):
    pg,errors=_page(browser,'road_safety_atlas.html')
    try:
        for country in ['Sweden','Estonia','Sweden']:
            pg.locator('#textFilter').fill(country)
            assert '1 country sections' in pg.locator('#searchCount').inner_text()
            assert country in pg.locator('#countryRows').inner_text()
        pg.locator('#resetSearch').click()
        assert pg.locator('#textFilter').input_value()==''
        assert '1 country sections' not in pg.locator('#searchCount').inner_text()
        assert not errors
    finally:pg.close()


def test_taskforce_country_search(browser):
    pg,errors=_page(browser,'who_has_task_forces.html')
    try:
        for country in ['Sweden','Estonia','Canada','Sweden']:
            pg.locator('#search').fill(country)
            assert pg.locator('button[data-country]:visible').count()==1
            assert country in pg.locator('button[data-country]:visible').first.inner_text()
        pg.locator('#clear-search').click()
        assert pg.locator('#search').input_value()==''
        assert pg.locator('button[data-country]:visible').count()>1
        assert not errors
    finally:pg.close()


def test_case_studies_search_and_institution_selector(browser):
    pg,errors=_page(browser,'Case_Studies.html')
    try:
        for country in ['Sweden','Estonia','Canada','Sweden']:
            pg.locator('#country-search').fill(country)
            assert pg.locator('#cards button.tile').count()>=1
            assert country in pg.locator('#cards').inner_text()
        opts=pg.locator('#institution-case-pick option').count()
        assert opts>2
        for idx in [0,1,2,0]:
            pg.locator('#institution-case-pick').select_option(index=idx)
            assert pg.locator('#institution-evidence-table .institution-record:visible').count()>0
        assert not errors
    finally:pg.close()


def test_body_strategy_country_search_and_reset(browser):
    pg,errors=_page(browser,'Bodies_Their_Road_Safety_Strategies.html')
    try:
        for country in ['Sweden','Estonia','Canada','Sweden']:
            pg.locator('#search').fill(country)
            assert '1 of 195' in pg.locator('#showing').inner_text()
            assert pg.locator('.country-tile').count()==1
            assert country in pg.locator('.country-tile').first.inner_text()
        pg.locator('#reset').click()
        assert pg.locator('#search').input_value()==''
        assert pg.locator('.country-tile').count()>1
        assert not errors
    finally:pg.close()


def test_product_title_and_all_embedded_pages():
    from bs4 import BeautifulSoup
    assert 'page_title="Road Safety Toolkit"' in (ROOT/'app.py').read_text(encoding='utf-8')
    app=(ROOT/'app.py').read_text(encoding='utf-8')
    assert '@st.fragment' in app
    assert '_show_institutional_toolkit()' in app
    files=['Dashboard_Overview.html','road_safety_atlas.html',
           'who_has_task_forces.html','Existing_road_safety_documents.html',
           'Bodies_Their_Road_Safety_Strategies.html','Case_Studies.html']
    for name in files:
        soup=BeautifulSoup((ROOT/name).read_text(encoding='utf-8'),'html.parser')
        assert soup.title.text.startswith('Road Safety Toolkit')
        assert soup.h1 is not None
    first=BeautifulSoup((ROOT/files[0]).read_text(encoding='utf-8'),'html.parser')
    assert first.h1.get_text(' ',strip=True)=='Road Safety Toolkit'

@pytest.mark.parametrize('name,css,setting,target',[
    ('Existing_road_safety_documents.html','#countryPick','Sweden','.country'),
    ('road_safety_atlas.html','#textFilter','Sweden','#countryRows'),
    ('who_has_task_forces.html','#search','Sweden','button[data-country]:visible'),
    ('Case_Studies.html','#country-search','Sweden','#cards button.tile'),
    ('Bodies_Their_Road_Safety_Strategies.html','#search','Sweden','.country-tile'),
])
def test_mobile_country_controls_still_work(browser,name,css,setting,target):
    page,errors=_page(browser,name)
    try:
        page.set_viewport_size({'width':390,'height':844})
        field=page.locator(css)
        assert field.is_visible()
        if field.evaluate('(el) => el.tagName')=='SELECT':
            field.select_option(setting)
        else:
            field.fill(setting)
        assert page.locator(target).count()>0
        assert not errors
    finally:page.close()
