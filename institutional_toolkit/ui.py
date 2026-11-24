"""Streamlit UI for the existing final Checklist tab only."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import json, re
from html import escape
import streamlit as st
from . import evidence as ev, reports, updates, rag

ROOT=Path(__file__).resolve().parent.parent
DATA=ROOT/'data'
RESPONSES=("Yes, with official documentation", "Yes, based on my knowledge", "Partially / needs updating",
           "I believe it does not exist", "Not applicable to this jurisdiction", "I do not know")


def _slug(country: str)->str:
    return re.sub(r'[^A-Za-z0-9]+','_',country).strip('_') or 'Country'


def _context_changed(kind: str) -> None:
    """Record a country or mode switch before Streamlit's automatic rerun.

    Each rerun derives the page from the CURRENT country and comparison
    selection. A monotonic revision makes the switch explicit and supports QA.
    Existing country-specific user drafts are intentionally preserved.
    """
    st.session_state['rs_context_revision'] = st.session_state.get('rs_context_revision', 0) + 1
    if kind == 'country':
        st.session_state['rs_previous_primary_country'] = st.session_state.get('rs_context_country')
        st.session_state['rs_context_country'] = st.session_state.get('rs_toolkit_country')
        st.session_state.pop('rs_open_legacy', None)
    elif kind == 'mode':
        st.session_state['rs_context_mode'] = st.session_state.get('rs_toolkit_mode')
    elif kind == 'comparison':
        st.session_state['rs_context_comparison'] = st.session_state.get('rs_compare_country_active')


def _choose_peer(choices: list[str], selected: str | None, previous_primary: str | None) -> str:
    """Keep the selected peer valid after changing the primary country."""
    if not choices:
        raise ValueError('Pairwise comparison requires at least two countries.')
    if selected in choices:
        return selected
    if previous_primary in choices:
        return previous_primary
    for preferred in ('Sweden', 'Estonia'):
        if preferred in choices:
            return preferred
    return choices[0]


def _link(link: str, text: str='View original source'):
    link=ev.url(link)
    if link: st.markdown(f'[{text}]({link})')


def _light_notice(message: str, kind: str = 'info') -> None:
    """Accessible, light-background notices independent of Streamlit's dark-alert internals.

    Native Streamlit alerts can include a dark BaseWeb notification child even
    when the outer stAlert element is set to a light background. This is why
    the previous CSS-only fix did not address the user's screenshot.
    """
    variants = {
        'info': ('#edf7fb', '#087e96', 'Information'),
        'warning': ('#fff9eb', '#98630d', 'Attention'),
        'error': ('#fff2f0', '#a23b36', 'Error'),
        'success': ('#eef9f3', '#197553', 'Success'),
    }
    bg, accent, heading = variants.get(kind, variants['info'])
    content = escape(str(message))
    st.markdown(
        f'<div class="rs-light-notice" role="status" '
        f'style="background-color:{bg}!important;color:#17324a!important;'
        f'border:1px solid #cbdde5;border-left:4px solid {accent};'
        f'border-radius:8px;padding:14px 17px;margin:10px 0 18px;'
        f'font-size:14px;line-height:1.58;">'
        f'<span style="font-weight:700;color:{accent}!important;">{heading}.</span> '
        f'<span style="color:#17324a!important;">{content}</span></div>',
        unsafe_allow_html=True,
    )


def _boundary():
    st.caption('Evidence and source coverage are not assessments of road safety performance. Missing information does not mean a body or intervention does not exist. User responses are not independently verified.')


def _display_grounded_result(result: dict, hits: list[dict], label: str):
    """Only link real research-record URLs, never model-authored sources."""
    st.caption('**'+result.get('status','Draft')+'**')
    if not result.get('claims'):
        _light_notice('No AI-generated factual answer is available for these retrieved records. Review the linked excerpts below, or obtain additional official evidence.', 'info')
    for item in result.get('claims',[]):
        st.write(item['text'])
        for ref in item.get('references',[]):
            _link(ref['url'], 'Evidence '+ref['evidence_id'])
    if result.get('limitations'):
        with st.expander('Limitations and unanswered evidence questions',expanded=True):
            for note in result['limitations']:st.write('• '+note)
            for note in result.get('questions_for_verification',[]):st.write('Verification question: '+note)
    st.caption('AI-assisted interpretation of indexed research, not an independently audited government finding.')
    st.download_button('Download cited evidence and analysis (JSON)',
                       json.dumps({'analysis':result,'retrieved':hits},indent=2,ensure_ascii=False),
                       file_name=_slug(label)+'_RAG_evidence_DRAFT.json',mime='application/json',
                       key='rag_json_'+_slug(label))
    if st.button('Prepare source-grounded analysis report (Word)',key='rag_word_prepare_'+_slug(label)):
        st.session_state['rag_word_'+_slug(label)]=reports.word_rag(
            title=label, question=st.session_state.get('rag_question_'+_slug(label),''),
            hits=hits,result=result)
    doc=st.session_state.get('rag_word_'+_slug(label))
    if doc:
        st.download_button('Download cited analysis (Word)',doc,
                           file_name=_slug(label)+'_cited_analysis_DRAFT.docx',
                           mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                           key='rag_word_download_'+_slug(label))


def _display_retrieved(hits: list[dict]):
    if not hits:
        _light_notice('No relevant source-linked excerpt was found in the reviewed records for this request. The system will not invent a finding.', 'warning')
        return
    for i,hit in enumerate(hits,1):
        label=f"{hit['country']} · {hit['domain'] or hit['record_type']} · {hit['evidence_id']}"
        with st.expander(f'Evidence {i} • {label}'):
            st.write(hit['excerpt'])
            st.caption('Jurisdiction: '+(hit.get('jurisdiction') or 'Not specified')+
                       ' | Source locator: '+(hit.get('locator') or 'Not supplied')+
                       ' | Review date: '+(hit.get('checked_on') or 'Not supplied'))
            if hit.get('limitations'):st.write('**Evidence limitation:** '+hit['limitations'])
            st.caption(hit['provenance'])
            _link(hit['source_url'],'Open original source')


def _official_source_records(ctx: dict) -> list[dict]:
    """Freshness search uses original records marked as official/primary sources.

    Historical secondary law transcriptions are useful research leads but must
    not expand the allowed web-search domain list.
    """
    trusted = []
    for record in ctx.get('institutional', []):
        source_type = (record.get('evidence_type') or '').lower()
        link = ev.url(record.get('source_url', ''))
        if link and 'official agency' in source_type:
            trusted.append({'url':link, 'checked_on':record.get('checked_on') or ''})
    for record in ctx.get('findings', []):
        source_type = (record.get('source_class') or '').lower()
        link = ev.url(record.get('source_url', ''))
        if link and ('government' in source_type or 'official agency' in source_type):
            trusted.append({'url':link, 'checked_on':record.get('checked_on') or ''})
    return trusted


def _update_check(country: str, ctx: dict, focus: str, key: str):
    with st.expander('Check for newer official information',expanded=False):
        st.caption('Optional, targeted freshness check. Uses known source links first and checks for changes, not a new deep search. Available with an OpenAI API key.')
        if st.button('Run limited update check',key='freshness_'+key):
            with st.spinner('Checking recent official updates...'):
                source_records=_official_source_records(ctx)
                sources=[r['url'] for r in source_records]
                checked_dates=[r['checked_on'] for r in source_records if r.get('checked_on')]
                since=max(checked_dates) if checked_dates else ''
                st.session_state['freshness_result_'+key]=updates.check_updates(country,sources,focus,since=since)
        result=st.session_state.get('freshness_result_'+key)
        if result:
            st.write('**'+result['status']+'**')
            if result.get('allowed_domains'):
                st.caption('Search restricted to: '+', '.join(result['allowed_domains']))
            st.write(result['text'])
            if result['utc']:st.caption('Checked at '+result['utc'])
            for u in result['sources']:_link(u,'Candidate update source')
            st.caption('Candidate updates do not overwrite existing data or automatically change checklist statuses.')


def _country_findings(data:dict,country:str):
    ctx=ev.country_context(data,country);m=ev.coverage(data,country)
    c1,c2,c3=st.columns(3)
    c1.metric('Reviewed coordinating mechanisms',m['Reviewed mechanisms'])
    c2.metric('Institutional domains with sources',f"{m['Institutional domains with sources']} / {m['Total domains']}")
    c3.metric('Interventions with specific sources',f"{m['Source-linked checklist items']} / {m['Total eligible interventions']}")
    _boundary()
    indexed = rag.corpus(data,country,DATA)
    distinct_links = len({r.source_url for r in indexed})
    st.caption(f'Controlled retrieval index: {len(indexed)} source-linked excerpts from {distinct_links} distinct source URL(s) for {country}. '
               'No full-document coverage is implied by these counts.')
    if not ctx['mechanisms']:
        _light_notice('This country has no detailed mechanism in the reviewed research subset. This is not evidence that it has no coordinating body. The global Atlas may contain additional findings.', 'warning')
    else:
        st.subheader('Coordinating institutions in our reviewed research')
        for p in ctx['mechanisms']:
            st.write(f"**{p['coordinating_body']}**  ")
            st.caption('Jurisdiction: '+p['jurisdiction']+' | Profile: '+p['profile_id'])
        st.subheader('Institutional information')
        linked=[r for r in ctx['institutional'] if ev.url(r.get('source_url',''))]
        if not linked:_light_notice('No institutional source-linked records in this reviewed subset.')
        for r in linked:
            with st.expander(r['domain']+' • '+(r.get('institutional_relationship') or 'Research evidence')):
                st.write('**Institution**: '+(r.get('responsible_institution') or 'Not documented'))
                st.write('**Membership**: '+(r.get('formal_membership') or 'Not verified'))
                st.write('**Responsibility**: '+(r.get('functional_responsibility') or 'Not verified'))
                st.write('**Qualification**: '+(r.get('classification_rationale') or 'Not stated'))
                _link(r.get('source_url',''))
        st.subheader('Specific interventions with documented sources')
        items=[r for r in ev.checklist_prefill(data,country) if r['source_urls']]
        if not items:_light_notice('No intervention-specific sources in the detailed research subset.')
        for r in items:
            with st.expander(r['matrix_id']+' • '+r['ideal_intervention']):
                st.write('**Classification**: '+r['research_status'])
                st.write(r['documented_action'] or 'No intervention details recorded')
                if r['evidence_note']:st.caption('Research limitation: '+r['evidence_note'])
                for u in r['source_urls']:_link(u)
    st.divider()
    st.subheader('Ask the reviewed country evidence (controlled RAG)')
    st.caption('The system retrieves source-linked research excerpts from the selected country only. '
               'It does not search the open web when answering. The current corpus contains reviewed source notes, '
               'not complete copies of every official document.')
    with st.form('research_question_form'):
        question=st.text_input('Your evidence question',placeholder='For example, what sources establish the coordinating body and its mandate?')
        submitted=st.form_submit_button('Retrieve relevant evidence')
    if submitted:
        if len(question.strip())<5:
            _light_notice('Enter a more specific question.', 'warning')
        else:
            st.session_state['toolkit_retrieval_'+country]={
                'question':question,
                'hits':rag.retrieve(data,country,question,data_dir=DATA,limit=8),
            }
            st.session_state.pop('rag_summary_'+country,None)
            st.session_state.pop('rag_word_'+_slug(country),None)
    retrieval=st.session_state.get('toolkit_retrieval_'+country)
    if retrieval:
        st.write('**Question:** '+retrieval['question'])
        hits=retrieval['hits']
        _display_retrieved(hits)
        if hits and updates.api_key() and st.button('Generate citation-checked AI synthesis',key='rag_'+country):
            with st.spinner('Synthesizing the indexed evidence...'):
                st.session_state['rag_summary_'+country]=rag.synthesis(retrieval['question'],hits)
        if hits and not updates.api_key():
            st.caption('Add an OpenAI API key in Streamlit Secrets to enable AI synthesis. Indexed evidence search works without it.')
        if st.session_state.get('rag_summary_'+country):
            st.session_state['rag_question_'+_slug(country)]=retrieval['question']
            st.subheader('Cited synthesis')
            _display_grounded_result(st.session_state['rag_summary_'+country],hits,country)
    _update_check(country,ctx,'recent changes to coordinating institutions, mandates, membership and national strategies','find_'+country)
    if st.button('Prepare printable country findings report',key='word_'+country):
        st.session_state['doc_country_'+country]=reports.word_country(data,country)
    if st.session_state.get('doc_country_'+country):
        st.download_button('Download country findings (Word)',st.session_state['doc_country_'+country],
                           file_name=_slug(country)+'_country_evidence_DRAFT.docx',mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document')


def _benchmark(data:dict,country:str):
    st.write('Compare **how much institutional evidence we have documented** across countries, without confusing documentation coverage with institutional quality.')
    table=ev.all_coverage(data)
    scope=st.radio('Country set',['All 195 countries','Countries with reviewed mechanisms'],horizontal=True)
    if scope!='All 195 countries':table=[r for r in table if r['Reviewed mechanisms']>0]
    chosen=ev.coverage(data,country)
    st.write(f"**{country}** has {chosen['Reviewed mechanisms']} mechanism(s) in the reviewed detailed dataset, "
             f"with {chosen['Institutional domains with sources']} source-linked institutional domains "
             f"and {chosen['Source-linked checklist items']} source-linked intervention requirements.")
    _light_notice('Countries with zero detailed records have not been assessed in this subset. Do not interpret zeros as lack of institutions. We cannot derive country performance rankings from these research counts.')
    table.sort(key=lambda r:(r['Country']!=country,r['Country']))
    st.dataframe(table,hide_index=True,use_container_width=True)
    if st.button('Prepare printable benchmarking brief',key='benchmark_report_'+_slug(country)):
        st.session_state['benchmark_doc_'+_slug(country)]=reports.word_benchmark(data,country,table)
    if st.session_state.get('benchmark_doc_'+_slug(country)):
        st.download_button('Download benchmarking summary (Word)',st.session_state['benchmark_doc_'+_slug(country)],
                           file_name=_slug(country)+'_benchmark_brief_DRAFT.docx',
                           mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    st.download_button('Download benchmarking table (CSV)',reports.as_csv(table),
                       file_name=_slug(country)+'_benchmark_coverage.csv',mime='text/csv')
    st.download_button('Download benchmarking table (Excel)',reports.excel_export({'Coverage':table}),
                       file_name=_slug(country)+'_benchmark_coverage.xlsx',
                       mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


def _pairwise(data:dict,country:str):
    choices=[c for c in data['countries'] if c!=country]
    # A shared comparison selector needs a valid value when the PRIMARY country
    # changes (for example Sweden -> Estonia). Reset invalid or self-comparisons.
    if st.session_state.get('rs_compare_country_active') not in choices:
        st.session_state['rs_compare_country_active'] = _choose_peer(
            choices,st.session_state.get('rs_compare_country_active'),
            st.session_state.get('rs_previous_primary_country'))
    second=st.selectbox('Select the comparison country', choices,
                        key='rs_compare_country_active',
                        on_change=_context_changed, args=('comparison',))
    st.caption(f'Active comparison: {country} versus {second}. The tables below reflect this selection.')
    a=ev.coverage(data,country);b=ev.coverage(data,second)
    st.subheader(f'{country} and {second}')
    c1,c2=st.columns(2)
    c1.metric(country+' • source-linked domains',f"{a['Institutional domains with sources']} / {a['Total domains']}")
    c2.metric(second+' • source-linked domains',f"{b['Institutional domains with sources']} / {b['Total domains']}")
    st.write(f"The reviewed dataset has {a['Source-linked checklist items']} intervention-specific source-linked items for {country} "
             f"and {b['Source-linked checklist items']} for {second}. This is **not** a ranking of road safety performance.")
    st.subheader('Institutional comparison by domain')
    rows=ev.compare(data,country,second)
    for item in rows:
        with st.expander(item['domain']):
            col1,col2=st.columns(2)
            for col,n in ((col1,country),(col2,second)):
                d=item[n]
                with col:
                    st.markdown('**'+n+'**')
                    st.caption(d['evidence'])
                    st.write('**Institution**: '+(d['responsible_institution'] or 'Not verified'))
                    st.write('**Membership**: '+(d['membership'] or 'Not verified'))
                    st.write('**Function**: '+(d['functional_responsibility'] or 'Not verified'))
                    st.write('**Implementation**: '+(d['implementation_evidence'] or 'Not verified'))
                    if d['rationale']:st.caption(d['rationale'])
                    _link(d['source_url'])
    st.subheader('Intervention-level differences in documented evidence')
    first=ev.checklist_prefill(data,country);other=ev.checklist_prefill(data,second)
    available=[(x,y) for x,y in zip(first,other) if x['source_urls'] or y['source_urls']]
    if not available:_light_notice(f'No source-linked intervention records found for {country} or {second} in this reviewed subset. This does not establish that either country lacks these interventions.')
    for x,y in available:
        with st.expander(x['matrix_id']+' • '+x['ideal_intervention']):
            cols=st.columns(2)
            for col,n,r in ((cols[0],country,x),(cols[1],second,y)):
                with col:
                    st.markdown('**'+n+'**')
                    st.write(r['research_status'])
                    st.write(r['documented_action'] or 'Not verified in reviewed source-specific data')
                    for u in r['source_urls']:_link(u)
    st.divider()
    st.subheader('Generate a source-grounded analytical comparison')
    st.caption('The retriever selects separate country-specific excerpts before any model call. '
               'Neither country borrows evidence from the other.')
    topics={
        'Coordination and mandates':'coordination national road safety institution mandate strategy government',
        'Membership and representation':'membership coordination council agencies ministry government participation',
        'Strategies and action plans':'national road safety strategy programme action plan implementation',
        'Accountability and monitoring':'coordination responsibilities implementation evidence monitoring accountability',
    }
    topic=st.selectbox('Comparison focus',list(topics),key='rag_pair_topic_'+_slug(country)+'_'+_slug(second))
    pairkey=_slug(country+'_vs_'+second)
    query=f"Compare {country} and {second} regarding {topics[topic]}, distinguishing the documented governance arrangements and evidence limitations."
    if st.button('Retrieve comparable source excerpts',key='rag_pair_retrieve_'+pairkey):
        with st.spinner('Retrieving independently from both country records...'):
            hits=rag.retrieve_pair(data,country,second,query,data_dir=DATA,per_country=5)
        st.session_state['rag_pair_'+pairkey]={'question':query,'hits':hits}
        st.session_state.pop('rag_pair_answer_'+pairkey,None)
        st.session_state.pop('rag_word_'+pairkey,None)
    retrieved_pair=st.session_state.get('rag_pair_'+pairkey)
    # Each focus requires its own retrieval. Never show an answer produced for a
    # different prompt merely because the same country pair is selected.
    if retrieved_pair and retrieved_pair.get('question')!=query:
        st.session_state.pop('rag_pair_'+pairkey,None)
        st.session_state.pop('rag_pair_answer_'+pairkey,None)
        st.session_state.pop('rag_word_'+pairkey,None)
        retrieved_pair=None
        st.caption('Comparison focus changed. Select Retrieve comparable source excerpts to update the RAG evidence.')
    if retrieved_pair:
        hits=retrieved_pair['hits']
        n1=sum(x['country']==country for x in hits)
        n2=sum(x['country']==second for x in hits)
        st.write(f'Retrieved {n1} evidence excerpts for {country} and {n2} for {second}.')
        _display_retrieved(hits)
        if n1 and n2 and updates.api_key() and st.button('Generate citation-checked pairwise analysis',key='rag_pair_generate_'+pairkey):
            with st.spinner('Preparing evidence-grounded comparison...'):
                st.session_state['rag_pair_answer_'+pairkey]=rag.synthesis(retrieved_pair['question'],hits)
        elif not n1 or not n2:
            _light_notice('This dataset cannot support a source-grounded pairwise analysis of the selected topic for both countries. Compare the available records, and gather missing evidence first.', 'warning')
        elif not updates.api_key():
            st.caption('AI comparison needs an OpenAI API key. Source retrieval and the detailed tables above work without it.')
        if st.session_state.get('rag_pair_answer_'+pairkey):
            st.session_state['rag_question_'+pairkey]=retrieved_pair['question']
            _display_grounded_result(st.session_state['rag_pair_answer_'+pairkey],hits,pairkey)
    st.caption('Adaptation of practices to a different country requires national legal, financial, institutional and operational review.')
    pairrows=[]
    for item in rows:
        pairrows.append({'Domain':item['domain'],country+' institution':item[country]['responsible_institution'],
                         country+' function':item[country]['functional_responsibility'],
                         country+' source':item[country]['source_url'],
                         second+' institution':item[second]['responsible_institution'],
                         second+' function':item[second]['functional_responsibility'],
                         second+' source':item[second]['source_url']})
    st.download_button('Export pairwise table (Excel)',reports.excel_export({'Domains':pairrows}),
                       file_name=_slug(country)+'_vs_'+_slug(second)+'_domains.xlsx',
                       mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    if st.button('Prepare detailed comparison dossier',key='make_pair_doc'):
        st.session_state['pairdoc_'+country+'_'+second]=reports.word_comparison(data,country,second)
    doc=st.session_state.get('pairdoc_'+country+'_'+second)
    if doc:
        st.download_button('Download detailed comparison (Word)',doc,file_name=_slug(country)+'_vs_'+_slug(second)+'_DRAFT.docx',
                           mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    _update_check(country,ev.country_context(data,country),'institutional changes relevant to comparison with '+second,
                  'compare_'+country+'_'+second)


def _checklist(data:dict,country:str):
    st.subheader('Step 1 • Share what you already know')
    st.write('We have already collected research evidence. Before preparing your checklist, please answer any questions where you can add current local knowledge. All questions are optional.')
    prompts=ev.questionnaire(data,country)
    key=_slug(country)
    with st.form('rs_questionnaire_'+key):
        run_freshness = st.checkbox('Check recent official updates when generating (optional API call)',
                                   value=False,
                                   help='Targeted short web search. Results are added as provisional leads and never change research classifications without review.')
        for i,r in enumerate(prompts,1):
            st.markdown(f"**{i}. {r['ideal_intervention']}**")
            st.caption('Domain: '+r['domain']+' | pillar: '+r['pillar'])
            st.radio('What do you know?',RESPONSES,index=None,key='rs_choice_'+key+'_'+r['matrix_id'],horizontal=False)
            st.text_input('Optional official link / document reference',key='rs_src_'+key+'_'+r['matrix_id'])
            st.text_input('Optional explanation',key='rs_note_'+key+'_'+r['matrix_id'])
            if i<len(prompts):st.divider()
        submitted=st.form_submit_button('Generate my prefilled checklist',type='primary')
    if submitted:
        answers={}
        for r in prompts:
            rid=r['matrix_id'];choice=st.session_state.get('rs_choice_'+key+'_'+rid)
            src=st.session_state.get('rs_src_'+key+'_'+rid,'').strip();note=st.session_state.get('rs_note_'+key+'_'+rid,'').strip()
            if choice or src or note:
                answers[rid]={'choice':choice or 'I do not know','source':src,'note':note}
        candidate_updates = {'status':'Not requested', 'text':'', 'sources':[], 'utc':''}
        if run_freshness:
            with st.spinner('Checking for recent official updates before drafting...'):
                candidate_updates=updates.check_updates(
                    country,[s['url'] for s in _official_source_records(ev.country_context(data,country))],
                    'institutional mandates, coordination, strategy and policy details relevant to checklist requirements',
                    since=max((r.get('checked_on','') for r in _official_source_records(ev.country_context(data,country))),default=''))
        st.session_state['rs_assessment_'+key]={'country':country,'answers':answers,
                    'created':datetime.now(timezone.utc).isoformat(timespec='seconds'),
                    'candidate_updates':candidate_updates,
                    'items':ev.checklist_prefill(data,country,answers)}
        # Any earlier drill-down selection must not be mistaken for the new
        # response-specific assessment after the form is resubmitted.
        st.session_state.pop('rs_checklist_item_'+key, None)
        st.session_state.pop('rs_checklist_domain_'+key, None)
    saved=st.session_state.get('rs_assessment_'+key)
    if not saved:
        st.caption('You may skip all questions and still generate a checklist using the published research records.')
    else:
        st.divider();st.subheader('Step 2 • Your prefilled checklist and recommended actions')
        items=saved['items'];cited=sum(bool(x['source_urls']) for x in items)
        x,y,z=st.columns(3)
        x.metric('Interventions',len(items));y.metric('Research-supported evidence leads',cited);z.metric('Your answered questions',len(saved['answers']))
        _light_notice('Private working draft. Source-linked plans are not proof of delivery. User answers are recorded separately and have not been approved or independently verified.', 'warning')
        update_info=saved.get('candidate_updates',{})
        if update_info.get('status') not in ('Not requested',None):
            with st.expander('New information identified during this assessment',expanded=True):
                st.write('**'+update_info['status']+'**')
                st.write(update_info.get('text') or 'No new evidence available')
                for source in update_info.get('sources',[]):_link(source,'Candidate official update')
                st.caption('New findings require human review before they can amend the original evidence or checklist status.')
        st.write('**Research-first assessment summary:** '+str(cited)+' requirements have direct source links; '+
                 str(len(items)-cited)+' requirements require source-specific verification in the present dataset. This does not establish how many interventions are actually missing.')
        domains=['All domains']+list(dict.fromkeys(r['domain'] for r in items))
        selected=st.selectbox('Filter the checklist by institutional domain',domains,
                              key='rs_checklist_domain_'+key)
        eligible=[r for r in items if selected=='All domains' or r['domain']==selected]
        st.dataframe([{'ID':r['matrix_id'],'Domain':r['domain'],'Intervention':r['ideal_intervention'],
                       'Research assessment':r['research_status'],'Your answer':r['respondent_answer']}
                      for r in eligible],hide_index=True,use_container_width=True)
        chosen=st.selectbox('View detailed evidence and recommended intervention',eligible,
                            key='rs_checklist_item_'+key,
                            format_func=lambda r:r['matrix_id']+' • '+r['ideal_intervention'])
        st.write('**Research classification:** '+chosen['research_status'])
        st.write('**Documented action:** '+(chosen['documented_action'] or 'No intervention-specific documented action in the reviewed sources'))
        if chosen['evidence_note']:st.write('**Evidence limitation:** '+chosen['evidence_note'])
        st.write('**Your response:** '+chosen['respondent_answer'])
        if chosen['respondent_note']:st.caption('Your information: '+chosen['respondent_note'])
        st.write('**Recommended verification / improvement step:** '+chosen['recommended_next_step'])
        for source in chosen['source_urls']:_link(source)
        with st.expander('Trace indexed evidence for this checklist intervention'):
            matched=rag.retrieve(data,country,chosen['ideal_intervention'],data_dir=DATA,
                                 limit=5,matrix_id=chosen['matrix_id'])
            if matched:
                st.write('**Direct requirement-specific source excerpts**')
                _display_retrieved(matched)
            else:
                st.write('No citable intervention-specific excerpt was indexed for this requirement.')
                related=rag.retrieve(data,country,chosen['ideal_intervention'],data_dir=DATA,
                                     limit=4,domain=chosen['domain'])
                if related:
                    st.caption('Related institutional context follows, but it does NOT establish implementation of the selected intervention.')
                    _display_retrieved(related)
        st.caption('Exported documents contain the complete list of 72 interventions, supporting links, limitations, questionnaire responses and proposed next actions.')
        st.download_button('Download complete checklist (Excel)',reports.excel_export({
            'Checklist':reports.checklist_export_rows(items),
            'Responses':[{'ID':rid,**rec} for rid,rec in saved['answers'].items()],
            'Update check':[{'Status':update_info.get('status','Not requested'),
                             'Checked UTC':update_info.get('utc',''),
                             'Candidate notes':update_info.get('text',''),
                             'Candidate source URLs':' | '.join(update_info.get('sources',[]))}]}),
            file_name=key+'_prefilled_checklist_DRAFT.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        st.download_button('Download complete checklist (CSV)',reports.as_csv(reports.checklist_export_rows(items)),
                           file_name=key+'_prefilled_checklist_DRAFT.csv',mime='text/csv')
        if st.button('Prepare full Word checklist and action plan'):
            st.session_state['rs_word_'+key]=reports.word_assessment(data,country,items,saved['answers'], update_info)
        if st.session_state.get('rs_word_'+key):
            st.download_button('Download full checklist and recommendations (Word)',st.session_state['rs_word_'+key],
                               file_name=key+'_checklist_action_plan_DRAFT.docx',
                               mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        st.download_button('Backup answers and findings (JSON)',json.dumps(saved,ensure_ascii=False,indent=2),
                           file_name=key+'_checklist_DRAFT.json',mime='application/json')
        st.caption('You should download your files before closing your browser. This version does not include authenticated persistent storage or institutional approval.')
    st.divider()
    st.subheader('Step 3 • Optional detailed self-assessment and action tracking')
    st.write('The original planner is preserved for a full 17-domain assessment, managing actions, and its existing Word/Excel exports. It requires explicit human review.')
    if st.toggle('Open the original detailed action planner',key='rs_open_legacy'):
        import planner
        planner.render()
    _update_check(country,ev.country_context(data,country),'recent changes affecting the prefilled checklist','checklist_'+country)


def render():
    with st.container(key='road_safety_toolkit'):
        try:data=ev.load_data(str(DATA))
        except (FileNotFoundError,ValueError) as err:
            _light_notice('The Toolkit could not load its research data: '+str(err), 'error');return
        st.markdown('''<div class="rs-planner-band"><div class="rs-planner-kicker">GLOBAL ROAD SAFETY • GOVERNANCE TOOLS</div>
        <h1>Road Safety Institutional Toolkit</h1>
        <p>Explore country findings, compare international practices, and develop an evidence-grounded institutional improvement plan.</p></div>''',unsafe_allow_html=True)
        country=st.selectbox('Select your country',data['countries'],
                             index=data['countries'].index('Estonia') if 'Estonia' in data['countries'] else 0,
                             key='rs_toolkit_country',
                             on_change=_context_changed,args=('country',))
        if 'rs_context_country' not in st.session_state:
            st.session_state['rs_context_country']=country
        mode=st.radio('What would you like to do?',(
            'Explore country findings','Benchmark internationally','Compare with another country','Generate my institutional checklist'),
            key='rs_toolkit_mode',horizontal=True,
            on_change=_context_changed,args=('mode',))
        # Unlike a static iframe, Streamlit reruns when country/mode changes.
        # Displaying the active country makes the selected data context explicit.
        st.markdown(
            '<div class="rs-light-notice" role="status" aria-live="polite" '
            'style="background:#edf7fb;color:#17324a;border:1px solid #bdd7e1;'
            'border-left:4px solid #078da0;border-radius:8px;'
            'padding:12px 16px;margin:10px 0 12px;">'
            '<strong>Currently viewing:</strong> '+escape(country)+' &nbsp; | &nbsp; '+escape(mode)+'</div>',
            unsafe_allow_html=True,
        )
        st.divider()
        if mode=='Explore country findings':_country_findings(data,country)
        elif mode=='Benchmark internationally':_benchmark(data,country)
        elif mode=='Compare with another country':_pairwise(data,country)
        else:_checklist(data,country)
