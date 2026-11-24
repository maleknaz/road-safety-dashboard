"""Test Streamlit app entrypoint's tabs and fragment integration in isolation.

This is an orchestration unit test, not a substitute for a Streamlit server E2E.
"""
from __future__ import annotations
from contextlib import nullcontext
from pathlib import Path
import importlib.util
import sys
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def test_seven_tabs_and_toolkit_fragment_are_wired(monkeypatch):
    from institutional_toolkit import render as original_render
    import institutional_toolkit
    events=[]
    st=ModuleType('streamlit')
    st.set_page_config=lambda **kwargs:events.append(('config',kwargs))
    st.markdown=lambda *args,**kwargs:None
    st.error=lambda *args,**kwargs:events.append(('error',args))
    st.tabs=lambda labels:(events.append(('tabs',labels)) or [nullcontext() for _ in labels])
    def cache_data(**opts):
        def decorate(fn):return fn
        return decorate
    st.cache_data=cache_data
    def fragment(fn):
        def wrapped(*a,**k):
            events.append(('fragment',fn.__name__))
            return fn(*a,**k)
        return wrapped
    st.fragment=fragment
    components=ModuleType('streamlit.components')
    components_v1=ModuleType('streamlit.components.v1')
    components_v1.html=lambda content,**kw:events.append(('html',len(content)))
    components.v1=components_v1
    st.components=components
    monkeypatch.setitem(sys.modules,'streamlit',st)
    monkeypatch.setitem(sys.modules,'streamlit.components',components)
    monkeypatch.setitem(sys.modules,'streamlit.components.v1',components_v1)
    monkeypatch.setattr(institutional_toolkit,'render',lambda :events.append(('toolkit','rendered')))
    spec=importlib.util.spec_from_file_location('road_safety_app_e2e_stub',ROOT/'app.py')
    module=importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        cfg=[e for e in events if e[0]=='config']
        assert len(cfg)==1
        assert cfg[0][1]['page_title']=='Road Safety Toolkit'
        tabs=[e for e in events if e[0]=='tabs']
        assert len(tabs)==1 and len(tabs[0][1])==7
        assert tabs[0][1][-1]=='Road Safety Institutional Toolkit'
        assert len([e for e in events if e[0]=='html'])==6
        assert len([e for e in events if e[0]=='toolkit'])==1
        assert len([e for e in events if e[0]=='fragment'])==1
        assert not [e for e in events if e[0]=='error']
    finally:
        monkeypatch.setattr(institutional_toolkit,'render',original_render)
