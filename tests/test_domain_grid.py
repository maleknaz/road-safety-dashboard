"""Regression tests for compact multi-column domains and membership-display removal."""
from contextlib import nullcontext
from io import BytesIO
from pathlib import Path
import importlib
import sys
import types
from html import escape

from docx import Document
from institutional_toolkit import evidence, reports

ROOT=Path(__file__).resolve().parents[1]


class FakeStreamlit(types.ModuleType):
    def __init__(self):
        super().__init__('streamlit')
        self.session_state={}
        self.layout=[]
        self.markdowns=[]
        self.buttons=[]
        self.click=None
        self.subheaders=[]
        self.captions=[]
    def columns(self,n,**kwargs):
        self.layout.append(n)
        return [nullcontext() for _ in range(n)]
    def container(self,**kwargs):
        return nullcontext()
    def markdown(self,text,**kwargs):
        self.markdowns.append(text)
    def caption(self,text):
        self.captions.append(text)
    def subheader(self,text):
        self.subheaders.append(text)
    def button(self,text,**kwargs):
        self.buttons.append((text,kwargs))
        clicked=kwargs.get('key')==self.click
        if clicked and kwargs.get('on_click'):
            kwargs['on_click'](*(kwargs.get('args') or ()))
        return clicked


def _load_ui(monkeypatch):
    fake=FakeStreamlit()
    monkeypatch.setitem(sys.modules, 'streamlit', fake)
    sys.modules.pop('institutional_toolkit.ui',None)
    ui=importlib.import_module('institutional_toolkit.ui')
    monkeypatch.setattr(ui,'st',fake)
    return ui,fake


def test_domain_grid_has_four_cards_per_row_for_seventeen_domains(monkeypatch):
    ui,fake=_load_ui(monkeypatch)
    data=evidence.load_data(str(ROOT/'data'))
    rows=evidence.compare(data,'Estonia','Sweden')
    assert len(rows)==17
    ui._render_domain_grid(rows,'Estonia','Sweden')
    assert fake.layout==[4,4,4,4,4]
    assert len(fake.buttons)==17
    assert all('rs_domain_view_Estonia_Sweden_' in item[1]['key'] for item in fake.buttons)
    assert sum('rs-domain-card-title' in text and '<div class="rs-domain-card-title">' in text
               for text in fake.markdowns)==17
    assert sum('rs-domain-comparison-table' in text and '<table' in text for text in fake.markdowns)==1
    table=next(text for text in fake.markdowns if '<table' in text)
    assert '<th scope="col">Estonia</th>' in table
    assert '<th scope="col">Sweden</th>' in table
    assert 'Membership' not in table
    assert all('Membership' not in text for text in fake.markdowns)


def test_click_domain_changes_detail_and_is_pair_specific(monkeypatch):
    ui,fake=_load_ui(monkeypatch)
    data=evidence.load_data(str(ROOT/'data'))
    rows=evidence.compare(data,'Estonia','Sweden')
    fake.click='rs_domain_view_Estonia_Sweden_8'
    ui._render_domain_grid(rows,'Estonia','Sweden')
    assert fake.session_state['rs_selected_domain_Estonia_Sweden']==rows[8]['domain']
    assert '#### '+escape(rows[8]['domain']) in fake.markdowns
    fake.click=None
    fake.markdowns.clear();fake.layout.clear();fake.buttons.clear()
    ui._render_domain_grid(evidence.compare(data,'Canada','Estonia'),'Canada','Estonia')
    assert fake.session_state['rs_selected_domain_Canada_Estonia'] in data['domains']
    assert fake.session_state['rs_selected_domain_Estonia_Sweden']==rows[8]['domain']


def test_html_escapes_source_and_institution_text(monkeypatch):
    ui,_=_load_ui(monkeypatch)
    item={'domain':'Transport <script>alert(1)</script>',
          'A': {'evidence':'Linked institutional record','responsible_institution':'<img src=x>',
                'functional_responsibility':'A & B','implementation_evidence':'<unknown>',
                'rationale':'Not stated', 'source_url':'https://example.org/?a=1&b=2'},
          'B': {'evidence':'No linked record', 'source_url':''}}
    card=ui._domain_card_html(item,'A','B')
    table=ui._domain_comparison_table(item,'A','B')
    assert '<script>' not in card
    assert '&lt;script&gt;' in card
    assert '<img' not in table
    assert '&lt;img' in table
    assert 'https://example.org/?a=1&amp;b=2' in table
    assert 'Membership' not in table


def test_country_and_comparison_word_reports_omit_repeated_membership():
    data=evidence.load_data(str(ROOT/'data'))
    for document in (reports.word_country(data,'Estonia'),
                     reports.word_country(data,'Sweden'),
                     reports.word_comparison(data,'Estonia','Sweden')):
        paragraphs='\n'.join(p.text for p in Document(BytesIO(document)).paragraphs)
        assert 'Membership:' not in paragraphs
        assert 'Institution:' in paragraphs
        assert 'Role:' in paragraphs or 'Function:' in paragraphs
