"""Regression tests grounded in the actual repository's source-reviewed tables."""
from __future__ import annotations
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
import csv
import json
import sys

from docx import Document
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from institutional_toolkit import rag, updates, evidence, reports


@pytest.fixture(scope='module')
def data():
    return evidence.load_data(str(ROOT / 'data'))


def test_actual_data_is_unchanged(data):
    stat = evidence.validate(data)
    assert stat['countries'] == 195
    assert stat['domains'] == 17
    assert stat['eligible_interventions'] == 72
    assert stat['source_specific_findings'] == 75


def test_index_only_citable_linked_excerpts(data):
    a = rag.audit(data, ROOT/'data')
    assert a['countries'] == 195
    assert a['countries_with_citable_excerpts'] == 26
    assert a['indexed_research_excerpts'] >= 200
    assert len(rag.corpus(data, 'Estonia', ROOT/'data')) > 0
    assert len(rag.corpus(data, 'Afghanistan', ROOT/'data')) == 0
    assert all(chunk.source_url.startswith(('http://','https://')) for chunk in rag.corpus(data,'Sweden',ROOT/'data'))
    assert all(chunk.excerpt and chunk.evidence_id.startswith('RS-') for chunk in rag.corpus(data, 'Estonia',ROOT/'data'))


def test_country_isolation(data):
    e = rag.retrieve(data,'Estonia','government traffic commission road safety programme',data_dir=ROOT/'data')
    assert e
    assert all(hit['country']=='Estonia' for hit in e)
    assert not rag.retrieve(data,'Afghanistan','Swedish road safety Vision Zero',data_dir=ROOT/'data')
    assert not rag.retrieve(data,'Nonexistentland','coordination',data_dir=ROOT/'data')
    pair=rag.retrieve_pair(data,'Estonia','Sweden','coordination action plan government membership',data_dir=ROOT/'data')
    assert set(r['country'] for r in pair) == {'Estonia','Sweden'}
    assert all(r['country'] in ('Estonia','Sweden') for r in pair)


def test_intervention_exact_filter_and_no_false_completion(data):
    hits=rag.retrieve(data,'Estonia','commission coordination programme',data_dir=ROOT/'data',matrix_id='01-4')
    assert hits and all(x['matrix_id']=='01-4' for x in hits)
    rows=evidence.checklist_prefill(data,'Estonia')
    assert len(rows)==72
    assert sum(bool(row['source_urls']) for row in rows)==3
    assert all(row['assessment_status']=='Draft, not government validated' for row in rows)
    assert not rag.retrieve(data,'Estonia','hospital emergency services',data_dir=ROOT/'data',matrix_id='01-4',domain='Health and medical services')


def test_refuse_unknown_citations(data):
    hits=rag.retrieve(data,'Estonia','coordination national programme',data_dir=ROOT/'data')
    bad={'summary':'Test','claims':[{'text':'Invented claim', 'evidence_ids':['RS-NOT-REAL']}],
         'limitations':[],'questions_for_verification':[]}
    with pytest.raises(ValueError):
        rag.verify_answer(bad,hits)
    with pytest.raises(ValueError):
        rag.verify_answer({'claims':[{'text':'Uncited claim','evidence_ids':[]}], 'limitations':[], 'questions_for_verification':[]},hits)


def test_model_output_is_always_linked_from_corpus(data):
    hits=rag.retrieve(data,'Estonia','coordination',data_dir=ROOT/'data')
    valid={'summary':'False source injected in summary https://bad-site.test',
           'claims':[{'text':'Reviewed record indicates coordinating activity', 'evidence_ids':[hits[0]['evidence_id']]}],
           'limitations':['Confirmation of actual implementation remains open'],
           'questions_for_verification':['Have you seen a current official implementation report?']}
    verified=rag.verify_answer(valid,hits)
    assert 'bad-site' not in verified['summary']
    assert verified['claims'][0]['references'][0]['url']==hits[0]['source_url']
    assert verified['status'].startswith('AI-assisted draft')


def test_no_evidence_means_no_ai_call():
    class FakeClient:
        @property
        def responses(self):
            raise AssertionError('No model call should be made with no evidence')
    output=rag.synthesis('Is there a body?',[],client=FakeClient())
    assert output['claims']==[]
    assert output['status'].startswith('Insufficient')


def test_model_with_mocked_response_validation(data):
    hits=rag.retrieve(data,'Estonia','coordination',data_dir=ROOT/'data')
    class FakeResponses:
        def create(self,**kwargs):
            assert kwargs['store'] is False
            assert kwargs['text']['format']['strict'] is True
            assert 'tools' not in kwargs
            return SimpleNamespace(output_text=json.dumps({
                'summary':'Estonia status','claims':[{'text':'Documented in research', 'evidence_ids':[hits[0]['evidence_id']]}],
                'limitations':[], 'questions_for_verification':[]}))
    fake=SimpleNamespace(responses=FakeResponses())
    result=rag.synthesis('coordination',hits,client=fake)
    assert len(result['claims'])==1
    assert result['claims'][0]['references'][0]['evidence_id']==hits[0]['evidence_id']


def test_curated_manifest_allows_docs_but_no_traversal(tmp_path,data):
    base=tmp_path/'knowledge_documents'
    base.mkdir()
    (base/'current.txt').write_text('Official demonstration document about a transport coordination programme.',encoding='utf-8')
    (tmp_path/'outside.txt').write_text('secret text',encoding='utf-8')
    with (tmp_path/'knowledge_documents.csv').open('w',newline='',encoding='utf-8') as fp:
        w=csv.DictWriter(fp,fieldnames=['country','relative_path','source_url','title','published_on'])
        w.writeheader()
        w.writerow({'country':'Estonia','relative_path':'current.txt','source_url':'https://example.org/public','title':'Demonstration','published_on':'2026-01-01'})
        w.writerow({'country':'Estonia','relative_path':'../outside.txt','source_url':'https://example.org/private','title':'Forbidden','published_on':'2026-01-01'})
        w.writerow({'country':'Sweden','relative_path':'current.txt','source_url':'https://example.org/cross','title':'Wrong country','published_on':'2026-01-01'})
    docs=rag.curated_documents(tmp_path,'Estonia')
    assert len(docs)==1
    assert 'public' in docs[0].source_url
    assert 'secret' not in docs[0].excerpt
    assert all(d.country=='Estonia' for d in docs)


def test_trusted_update_domain_lock(data):
    links=[s['url'] for s in evidence.sources_for(evidence.country_context(data,'Estonia'))]
    allowed=updates.trusted_domains(links)
    assert allowed
    assert updates.domain_permitted('https://transpordiamet.ee/new',allowed)
    assert not updates.domain_permitted('https://transpordiamet.ee.evil.test/new',allowed)
    assert not updates.domain_permitted('http://transpordiamet.ee/new',allowed)
    assert not updates.domain_permitted('https://fake.gov.example/new',allowed)
    rows=[{'claim':'Real prospective lead','url':'https://transpordiamet.ee/new','date':'2026-11-01'},
          {'claim':'Invented off-domain','url':'https://fraud.test/new','date':'2026-11-01'},
          {'claim':'Uncited allowed domain','url':'https://transpordiamet.ee/unknown','date':'2026-11-01'}]
    result=updates.filter_candidate_updates(rows,['https://transpordiamet.ee/new'],allowed)
    assert len(result)==1
    assert result[0]['review_status'].startswith('Candidate')


def test_no_trusted_source_means_no_web_search(monkeypatch):
    monkeypatch.setattr(updates,'_perform',lambda *args: (_ for _ in ()).throw(AssertionError('Cannot search without allowlist')))
    res=updates.check_updates('Unknown country',[], 'new law')
    assert res['status'].startswith('Not checked')
    assert res['sources']==[]


def test_rag_report_generates_source_bibliography(data):
    hits=rag.retrieve(data,'Estonia','road safety commission',data_dir=ROOT/'data',limit=3)
    result=rag.verify_answer({'summary':'Test','claims':[{'text':'A source-backed finding','evidence_ids':[hits[0]['evidence_id']]}],
                              'limitations':['Need independent verification'], 'questions_for_verification':[]},hits)
    binary=reports.word_rag('Estonia','What is the mandate?',hits,result)
    doc=Document(BytesIO(binary))
    paragraphs='\n'.join(p.text for p in doc.paragraphs)
    assert hits[0]['source_url'] in paragraphs
    assert hits[0]['evidence_id'] in paragraphs
    assert 'source' in paragraphs.casefold()
