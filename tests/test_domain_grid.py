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


def test_domain_grid_html_contains_all_seventeen_cards(monkeypatch):
    ui,fake=_load_ui(monkeypatch)
    data=evidence.load_data(str(ROOT/'data'))
    rows=evidence.compare(data,'Estonia','Sweden')
    html=ui._domain_grid_html(rows,'Estonia','Sweden')
    assert len(rows)==17
    assert html.count('class="domain-card"')==17
    assert 'grid-template-columns:repeat(4,minmax(0,1fr))' in html
    assert html.count('<template id="domain-template-')==17
    assert 'Membership' not in html


def test_source_html_is_escaped_in_grid(monkeypatch):
    ui,_=_load_ui(monkeypatch)
    row={'domain':'Transport <script>alert(1)</script>',
          'A': {'evidence':'Linked institutional record','responsible_institution':'<img src=x>',
                'functional_responsibility':'A & B','implementation_evidence':'<unknown>',
                'rationale':'Not stated', 'source_url':'https://example.org/?a=1&b=2'},
          'B': {'evidence':'No linked record', 'source_url':''}}
    markup=ui._domain_grid_html([row],'A','B')
    assert '<script>alert(1)</script>' not in markup
    assert '&lt;script&gt;' in markup
    assert '<img src=x' not in markup
    assert '&lt;img' in markup
    assert 'https://example.org/?a=1&amp;b=2' in markup
    assert 'Membership' not in markup


def test_country_and_comparison_word_reports_omit_repeated_membership():
    data=evidence.load_data(str(ROOT/'data'))
    for document in (reports.word_country(data,'Estonia'),
                     reports.word_country(data,'Sweden'),
                     reports.word_comparison(data,'Estonia','Sweden')):
        paragraphs='\n'.join(p.text for p in Document(BytesIO(document)).paragraphs)
        assert 'Membership:' not in paragraphs
        assert 'Institution:' in paragraphs
        assert 'Role:' in paragraphs or 'Function:' in paragraphs
