"""Toolkit masthead and descriptions: no Streamlit server/API key required."""
from __future__ import annotations
import ast
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'institutional_toolkit' / 'ui.py'

def intro_html() -> str:
    tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'TOOLKIT_INTRO_HTML' for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError('Intro HTML not found')


def test_hero_title_and_fixed_dimensions():
    text = intro_html()
    assert '<h1 id="rs-toolkit-heading">Road Safety <em>Institutional Toolkit</em></h1>' in text
    assert 'height:320px!important' in text
    assert 'height:70px!important' in text
    assert 'linear-gradient(114deg,#0c2945' in text
    assert 'max-width:1580px' in text


def test_four_modes_and_honest_intelligence_claims():
    t = intro_html()
    assert t.count('class="rs-toolkit-option"') == 4
    for label in ['Explore country findings', 'Benchmark internationally', 'Compare with another country',
                  'Generate my institutional checklist']:
        assert label in t
    assert 'not rankings of road safety performance' in t
    assert 'With AI access configured' in t
    assert 'Evidence gaps and user responses remain unverified until reviewed' in t


def test_responsive_light_theme_and_separation():
    t = intro_html()
    assert '@media(max-width:720px)' in t
    assert 'grid-template-columns:1fr' in t
    assert 'background:#ffffff!important' in t
    assert '.st-key-road_safety_toolkit .rs-toolkit-hero' in t
    assert 'unsafe_allow_html=True' in SOURCE.read_text(encoding='utf-8')
