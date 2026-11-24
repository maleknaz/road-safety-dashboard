"""Streamlit rerun-contract tests without requiring a running Streamlit server.

The deployment's code is examined under a small widget simulation because
Streamlit itself is not installed in this isolated QA environment. These tests
cover the country, mode and comparison rerender contract, not browser websocket
latency or Streamlit Community Cloud deployment behavior.
"""
from __future__ import annotations
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
from html import unescape
import importlib
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from institutional_toolkit import evidence


class FakeStreamlit:
    def __init__(self):
        self.session_state = {}
        self.selection = {}
        self.radio_choice = None
        self.markdowns = []

    def container(self, **kwargs):
        return nullcontext()

    def markdown(self, content, **kwargs):
        self.markdowns.append(content)

    def divider(self):
        pass

    def selectbox(self, label, options, index=0, key=None, on_change=None,
                  args=None, **kwargs):
        desired = self.selection.get(label)
        if desired is None:
            desired = self.session_state.get(key, options[index])
        if desired not in options:
            desired = options[index]
        old = self.session_state.get(key)
        if key is not None:
            self.session_state[key] = desired
        if old is not None and old != desired and on_change:
            on_change(*(args or ()))
        return desired

    def radio(self, label, options, key=None, on_change=None,
              args=None, **kwargs):
        desired = self.selection.get(label) or options[0]
        old = self.session_state.get(key)
        if key is not None:
            self.session_state[key] = desired
        if old is not None and old != desired and on_change:
            on_change(*(args or ()))
        return desired


def test_switch_country_and_mode_updates_view(monkeypatch):
    fake = FakeStreamlit()
    monkeypatch.setitem(sys.modules, 'streamlit', fake)
    # The actual ui module imports optional Streamlit only when loaded.
    sys.modules.pop('institutional_toolkit.ui', None)
    ui = importlib.import_module('institutional_toolkit.ui')
    monkeypatch.setattr(ui, 'st', fake)
    data = evidence.load_data(str(ROOT / 'data'))
    monkeypatch.setattr(ui.ev, 'load_data', lambda _: data)
    calls = []
    monkeypatch.setattr(ui, '_country_findings', lambda d, country: calls.append(('findings', country)))
    monkeypatch.setattr(ui, '_benchmark', lambda d, country: calls.append(('benchmark', country)))
    monkeypatch.setattr(ui, '_pairwise', lambda d, country: calls.append(('compare', country)))
    monkeypatch.setattr(ui, '_checklist', lambda d, country: calls.append(('checklist', country)))

    fake.selection = {'Select your country':'Estonia',
                      'What would you like to do?':'Explore country findings'}
    ui.render()
    assert calls[-1] == ('findings', 'Estonia')
    assert 'Currently viewing:</strong> Estonia' in fake.markdowns[-1]

    fake.selection['Select your country'] = 'Sweden'
    ui.render()
    assert calls[-1] == ('findings','Sweden')
    assert fake.session_state['rs_context_country'] == 'Sweden'
    assert 'Currently viewing:</strong> Sweden' in fake.markdowns[-1]

    fake.selection['What would you like to do?'] = 'Benchmark internationally'
    ui.render()
    assert calls[-1] == ('benchmark', 'Sweden')
    assert fake.session_state['rs_context_mode'] == 'Benchmark internationally'

    fake.selection['What would you like to do?'] = 'Generate my institutional checklist'
    fake.selection['Select your country'] = 'Estonia'
    ui.render()
    assert calls[-1] == ('checklist', 'Estonia')
    assert fake.session_state['rs_context_revision'] >= 3


def test_comparison_country_resets_when_equal_to_primary(monkeypatch):
    fake=FakeStreamlit()
    monkeypatch.setitem(sys.modules,'streamlit',fake)
    sys.modules.pop('institutional_toolkit.ui',None)
    ui=importlib.import_module('institutional_toolkit.ui')
    choices=['Afghanistan','Canada','Estonia']
    assert ui._choose_peer(choices,'Sweden','Estonia')=='Estonia'
    assert ui._choose_peer(choices,'Canada','Estonia')=='Canada'
    assert ui._choose_peer(['Estonia','Sweden'],'Estonia','Estonia')=='Estonia'
    assert ui._choose_peer(['Afghanistan','Canada'],None,None)=='Afghanistan'
    # No country should be permitted to compare with itself.
    assert 'Sweden' not in choices
