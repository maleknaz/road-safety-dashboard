"""Real Chromium DOM checks for four-column layout and live card changes.

Run with `PYTHONPATH=. pytest tests/test_domain_grid_browser.py -q`.
This is the missing behavioral coverage in the earlier patch.
"""
import importlib
import sys
import types
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright
from institutional_toolkit import evidence

ROOT = Path(__file__).resolve().parents[1]


def get_html(monkeypatch, country='Estonia', peer='Sweden'):
    fake = types.ModuleType('streamlit')
    fake.session_state = {}
    monkeypatch.setitem(sys.modules, 'streamlit', fake)
    sys.modules.pop('institutional_toolkit.ui', None)
    ui = importlib.import_module('institutional_toolkit.ui')
    data = evidence.load_data(str(ROOT / 'data'))
    rows = evidence.compare(data, country, peer)
    assert len(rows) == 17
    return ui._domain_grid_html(rows, country, peer)


def test_four_columns_on_desktop_and_click_changes_comparison(monkeypatch, tmp_path):
    markup = get_html(monkeypatch)
    page_path = tmp_path / 'grid.html'
    page_path.write_text(markup, encoding='utf-8')
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'], headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 1200}, device_scale_factor=1)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content(markup)
        assert page.locator('.domain-card').count() == 17
        assert page.locator('.domain-card[aria-pressed="true"]').count() == 1
        cols = page.locator('.domain-grid').evaluate('el=>getComputedStyle(el).gridTemplateColumns.split(" ").length')
        assert cols == 4
        first_row = page.locator('.domain-card').all()[:4]
        ys = [round(c.bounding_box()['y']) for c in first_row]
        assert len(set(ys)) == 1, f'First four domain cards are not in same row: {ys}'
        assert page.locator('#domain-detail table').count() == 1
        first_title = page.locator('#domain-detail h3').inner_text()
        page.locator('.domain-card').nth(8).click()
        new_title = page.locator('.domain-card').nth(8).locator('.card-heading').inner_text()
        assert page.locator('#domain-detail h3').inner_text() == new_title
        assert page.locator('.domain-card').nth(8).get_attribute('aria-pressed') == 'true'
        assert page.locator('.domain-card[aria-pressed="true"]').count() == 1
        assert page.locator('#domain-detail table').count() == 1
        assert 'Membership' not in page.locator('#domain-detail').inner_text()
        assert not errors
        page.screenshot(path=str(ROOT/'tests'/'domain_grid_desktop.png'),full_page=True)
        browser.close()


@pytest.mark.parametrize('width,expected_cols',[(960,3),(680,2),(390,1)])
def test_responsive_grid_card_width(monkeypatch,tmp_path,width,expected_cols):
    page_path = tmp_path / 'grid.html'
    page_path.write_text(get_html(monkeypatch), encoding='utf-8')
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'], headless=True)
        page = browser.new_page(viewport={'width': width, 'height': 950}, device_scale_factor=1)
        page.set_content(page_path.read_text(encoding='utf-8'))
        count = page.locator('.domain-grid').evaluate('el=>getComputedStyle(el).gridTemplateColumns.split(" ").length')
        assert count==expected_cols
        assert page.locator('.domain-card').count() == 17
        assert page.locator('body').evaluate('el=>el.scrollWidth') <= width + 1
        if width==390:
            page.screenshot(path=str(ROOT/'tests'/'domain_grid_mobile.png'),full_page=True)
        browser.close()


def test_source_html_is_escaped(monkeypatch):
    fake=types.ModuleType('streamlit')
    fake.session_state={}
    monkeypatch.setitem(sys.modules, 'streamlit', fake)
    sys.modules.pop('institutional_toolkit.ui',None)
    ui=importlib.import_module('institutional_toolkit.ui')
    row={'domain':'<script>alert(1)</script>','A':{
         'source_url':'https://example.org?x=1&y=2','responsible_institution':'<img src=x onerror=alert(1)>',
         'evidence':'Linked record'},'B':{'source_url':''}}
    html=ui._domain_grid_html([row],'A','B')
    assert '<script>alert(1)</script>' not in html
    assert '&lt;script&gt;' in html
    assert '<img src=x' not in html
    assert '&lt;img' in html
