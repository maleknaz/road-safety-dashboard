"""Self-contained, source-aware Word and Excel working reports.

Each export is explicitly labelled a draft, and observations are about evidence
coverage rather than assessed national safety performance.
"""
from __future__ import annotations
import csv, io, json, re
from datetime import datetime, timezone
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from .evidence import coverage, country_context, compare, checklist_prefill, sources_for


def _header(doc, title, subtitle):
    sec = doc.sections[0]
    sec.top_margin = sec.bottom_margin = Inches(.7)
    sec.left_margin = sec.right_margin = Inches(.8)
    doc.styles['Normal'].font.name = 'Aptos'
    doc.styles['Normal'].font.size = Pt(9)
    doc.add_heading(title, 0)
    doc.add_paragraph(subtitle, style='Subtitle')
    p=doc.add_paragraph('DRAFT • Research evidence only • Not government approved • Generated '+datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'))
    p.style='Caption'
    doc.add_paragraph('Documented plans and source-linked records do not establish implementation, effectiveness, or the absence of undocumented arrangements.')


def word_country(data: dict, country: str) -> bytes:
    ctx=country_context(data,country); c=coverage(data,country)
    doc=Document();_header(doc, 'Road Safety Institutional Toolkit', f'{country} | Country evidence brief')
    doc.add_heading('Executive evidence summary',1)
    doc.add_paragraph(f"{len(ctx['mechanisms'])} coordinating mechanism(s) are represented in the reviewed research subset for {country}. "
                      f"This subset has source-linked records for {c['Institutional domains with sources']} of {c['Total domains']} institutional domains "
                      f"and {c['Source-linked checklist items']} of {c['Total eligible interventions']} defined interventions. "
                      "These are documentation coverage counts, not an effectiveness rating.")
    doc.add_heading('Reviewed mechanisms',1)
    if not ctx['mechanisms']:doc.add_paragraph('No mechanism in the detailed review subset. This is not proof of institutional absence.')
    for p in ctx['mechanisms']:
        doc.add_paragraph(f"{p['coordinating_body']} | jurisdiction: {p['jurisdiction']}",style='List Bullet')
    doc.add_heading('Institutional source findings',1)
    linked=[r for r in ctx['institutional'] if r.get('source_url')]
    if not linked:doc.add_paragraph('No institutional sources linked in the current research subset.')
    for r in linked:
        doc.add_heading(r['domain'],2)
        doc.add_paragraph('Institution: '+(r.get('responsible_institution') or 'Not stated'))
        doc.add_paragraph('Role: '+(r.get('functional_responsibility') or 'Not verified'))
        doc.add_paragraph('Limitations: '+(r.get('classification_rationale') or 'Not specified'))
        doc.add_paragraph('Evidence: '+r['source_url'])
    doc.add_heading('Linked intervention evidence',1)
    linked_items=[r for r in checklist_prefill(data,country) if r['source_urls']]
    if not linked_items:doc.add_paragraph('No intervention-specific official evidence was linked in the reviewed subset.')
    for item in linked_items:
        doc.add_heading(item['matrix_id']+' | '+item['ideal_intervention'],2)
        doc.add_paragraph('Research classification: '+item['research_status'])
        doc.add_paragraph('Documented action: '+(item['documented_action'] or 'Not stated'))
        doc.add_paragraph('Verification limits: '+(item['evidence_note'] or 'Not specified'))
        for source in item['source_urls']:doc.add_paragraph('Source: '+source)
    b=io.BytesIO();doc.save(b);return b.getvalue()



def word_benchmark(data: dict, country: str, table: list[dict]) -> bytes:
    """Export a short factual benchmark summary and its coverage table."""
    doc=Document();_header(doc,'Road Safety Institutional Toolkit',f'{country} | International evidence coverage briefing')
    c=coverage(data,country)
    doc.add_heading('Executive evidence summary',1)
    doc.add_paragraph(f"In the reviewed country-specific dataset, {country} has {c['Reviewed mechanisms']} recorded coordinating mechanisms, "
                      f"{c['Institutional domains with sources']} of {c['Total domains']} institutional domains with source links, "
                      f"and {c['Source-linked checklist items']} of {c['Total eligible interventions']} interventions with linked source-specific records.")
    doc.add_paragraph('The following table represents research documentation coverage, not national road safety performance or comparative institutional effectiveness. Countries with no reviewed mechanisms have not been established as lacking institutions.')
    doc.add_heading('Evidence coverage by country',1)
    t=doc.add_table(rows=1,cols=4); t.style='Light Shading Accent 1'
    for cell,value in zip(t.rows[0].cells,['Country','Reviewed mechanisms','Linked domains','Linked items']):cell.text=value
    for row in table:
        cells=t.add_row().cells
        for cell,value in zip(cells,[row['Country'],str(row['Reviewed mechanisms']),str(row['Institutional domains with sources']),str(row['Source-linked checklist items'])]):cell.text=value
    doc.add_heading('Interpretation and further evidence needs',1)
    doc.add_paragraph('A valid international performance assessment requires harmonized data on mandates, implementation arrangements and outcome indicators. This research inventory should be used to select comparison cases, identify source coverage gaps and prepare questions for official verification.')
    result=io.BytesIO();doc.save(result);return result.getvalue()

def word_comparison(data: dict, a: str, b: str) -> bytes:
    doc=Document();_header(doc,'Road Safety Institutional Toolkit',f'Detailed country comparison | {a} and {b}')
    x=coverage(data,a);y=coverage(data,b)
    doc.add_heading('Executive comparison',1)
    doc.add_paragraph(f"The current research subset includes {x['Reviewed mechanisms']} reviewed coordinating mechanisms for {a} "
                      f"and {y['Reviewed mechanisms']} for {b}. Linked institutional domains: "
                      f"{x['Institutional domains with sources']}/{x['Total domains']} and "
                      f"{y['Institutional domains with sources']}/{y['Total domains']}, respectively. "
                      f"Source-linked interventions: {x['Source-linked checklist items']} and {y['Source-linked checklist items']}. "
                      "Differences in evidence availability do not demonstrate differences in performance.")
    doc.add_heading('Institutions',1)
    for country in (a,b):
        doc.add_heading(country,2)
        ms=country_context(data,country)['mechanisms']
        for r in ms:doc.add_paragraph(f"{r['coordinating_body']} | {r['jurisdiction']}",style='List Bullet')
        if not ms:doc.add_paragraph('No mechanism in the detailed research subset.')
    doc.add_heading('Detailed institutional dimension comparison',1)
    for row in compare(data,a,b):
        doc.add_heading(row['domain'],2)
        for country in (a,b):
            v=row[country]
            doc.add_paragraph(f"{country} | {v['evidence']}")
            doc.add_paragraph('Institution: '+(v['responsible_institution'] or 'Not verified'))
            doc.add_paragraph('Function: '+(v['functional_responsibility'] or 'Not verified'))
            doc.add_paragraph('Source: '+(v['source_url'] or 'No source linked'))
            if v['rationale']:doc.add_paragraph('Qualification: '+v['rationale'])
    doc.add_heading('Intervention-level evidence differences',1)
    ra=checklist_prefill(data,a);rb=checklist_prefill(data,b)
    for left,right in zip(ra,rb):
        if not left['source_urls'] and not right['source_urls']:continue
        doc.add_heading(left['matrix_id']+' | '+left['ideal_intervention'],2)
        for country,r in ((a,left),(b,right)):
            doc.add_paragraph(f"{country}: {r['research_status']}")
            doc.add_paragraph('Action: '+(r['documented_action'] or 'Not verified in source-linked research'))
            doc.add_paragraph('Limits: '+(r['evidence_note'] or 'Not specified'))
            for src in r['source_urls']:doc.add_paragraph('Source: '+src)
    doc.add_heading('Interpretation',1)
    doc.add_paragraph('For dimensions with incomplete or incomparable source coverage, conduct a targeted source check or request official documents. Adaptation of an approach requires legal, administrative, institutional and resource review. This document does not assert a governance model is transferable without review.')
    buff=io.BytesIO();doc.save(buff);return buff.getvalue()


def word_assessment(data: dict,country: str, rows: list[dict], responses: dict, updates: dict | None = None) -> bytes:
    doc=Document();_header(doc,'Road Safety Institutional Toolkit',f'{country} | Prefilled institutional checklist and actions')
    doc.add_heading('Executive summary',1)
    sourced=sum(bool(r['source_urls']) for r in rows)
    doc.add_paragraph(f"{len(rows)} eligible interventions; {sourced} have linked source-specific research records. "
                      f"The respondent provided information on {len(responses)} interventions. "
                      "All items are provisional. A reported absence is not a confirmed gap, and a planned intervention is not an implemented outcome.")
    doc.add_heading('Interventions, source links and recommended next steps',1)
    for r in rows:
        doc.add_heading(r['matrix_id']+' | '+r['ideal_intervention'],2)
        doc.add_paragraph(f"Domain: {r['domain']} | pillar: {r['pillar']}")
        doc.add_paragraph('Research finding: '+r['research_status'])
        doc.add_paragraph('Documented action: '+(r['documented_action'] or 'Not verified'))
        doc.add_paragraph('Respondent answer (not verified): '+r['respondent_answer'])
        if r['respondent_note']:doc.add_paragraph('Respondent note: '+r['respondent_note'])
        if r['respondent_source']:doc.add_paragraph('Respondent source (unverified): '+r['respondent_source'])
        doc.add_paragraph('Recommended next step: '+r['recommended_next_step'])
        if r['evidence_note']:doc.add_paragraph('Evidence limitation: '+r['evidence_note'])
        for s in r['source_urls']:doc.add_paragraph('Research source: '+s)
    if updates and updates.get('status') not in ('Not requested',None):
        doc.add_heading('Limited recent update check (unverified leads)',1)
        doc.add_paragraph('Status: '+updates.get('status',''))
        doc.add_paragraph(updates.get('text') or 'No search result')
        for link in updates.get('sources',[]):doc.add_paragraph('Candidate source: '+link)
        doc.add_paragraph('These leads are not automatically incorporated into verified intervention classifications. A reviewer must reconcile them with existing records.')
    buff=io.BytesIO();doc.save(buff);return buff.getvalue()


def _safe_excel(v):
    text = str(v if v is not None else '')
    return "'" + text if text.lstrip().startswith(('=','+','-','@')) else text


def excel_export(tables: dict[str,list[dict]]) -> bytes:
    wb=Workbook();wb.remove(wb.active)
    for title, rows in tables.items():
        ws=wb.create_sheet(title[:31]); ws.freeze_panes='A2'
        if not rows:
            ws.append(['No records']);continue
        heads=list(rows[0]);ws.append(heads)
        for row in rows:
            ws.append([_safe_excel(row.get(h,'')) for h in heads])
        ws.auto_filter.ref=ws.dimensions
        for cell in ws[1]:
            cell.fill=PatternFill('solid', fgColor='103B54')
            cell.font=Font(color='FFFFFF',bold=True,size=10)
            cell.alignment=Alignment(wrap_text=True,vertical='center')
        ws.row_dimensions[1].height=30
        for i,h in enumerate(heads,1):ws.column_dimensions[get_column_letter(i)].width=min(max(len(h)+4,16),45)
        for row in ws.iter_rows(min_row=2):
            for cell in row:cell.alignment=Alignment(wrap_text=True,vertical='top')
    b=io.BytesIO();wb.save(b);return b.getvalue()


def checklist_export_rows(items: list[dict]) -> list[dict]:
    return [{k: (' | '.join(v) if isinstance(v,list) else v) for k,v in item.items()} for item in items]


def as_csv(rows: list[dict]) -> bytes:
    if not rows:return b''
    b=io.StringIO(); cols=list(rows[0]); w=csv.DictWriter(b,fieldnames=cols,extrasaction='ignore');w.writeheader()
    for row in rows:w.writerow({c:_safe_excel(row.get(c,'')) for c in cols})
    return b.getvalue().encode('utf-8-sig')


def word_rag(title: str, question: str, hits: list[dict], result: dict) -> bytes:
    """Reference-backed AI working draft; include retrieved source IDs and URLs."""
    doc = Document()
    _header(doc, 'Road Safety Institutional Toolkit', title + ' | Controlled RAG evidence analysis')
    doc.add_heading('Research question', 1)
    doc.add_paragraph(question or 'Research question not specified')
    doc.add_heading('Interpretation status', 1)
    doc.add_paragraph(result.get('status', 'Not generated'))
    doc.add_paragraph('The cited passages are previously prepared research excerpts, not necessarily quotations from the linked source documents. Any AI-assisted interpretation requires review of the actual official sources before publication.')
    doc.add_heading('Evidence-grounded findings', 1)
    if not result.get('claims'):
        doc.add_paragraph('No source-grounded AI conclusion was available. Consult the retrieved evidence below.')
    for claim in result.get('claims', []):
        doc.add_paragraph(claim['text'], style='List Bullet')
        for ref in claim.get('references', []):
            doc.add_paragraph('Reference: ' + ref['evidence_id'] + ' | ' + ref['url'])
    doc.add_heading('Evidence limitations', 1)
    for text in result.get('limitations', []):
        doc.add_paragraph(text, style='List Bullet')
    doc.add_heading('Outstanding verification questions', 1)
    for text in result.get('questions_for_verification', []):
        doc.add_paragraph(text, style='List Bullet')
    doc.add_heading('Retrieval record and source bibliography', 1)
    if not hits:
        doc.add_paragraph('No relevant source-linked research records were retrieved.')
    for hit in hits:
        doc.add_heading(hit['evidence_id']+' | '+hit['country']+' | '+(hit.get('domain') or hit['record_type']), 2)
        doc.add_paragraph('Jurisdiction: '+(hit.get('jurisdiction') or 'Not recorded'))
        doc.add_paragraph('Source: '+hit['source_url'])
        doc.add_paragraph('Source locator: '+(hit.get('locator') or 'Not supplied')+' | Research check date: '+(hit.get('checked_on') or 'Not supplied'))
        doc.add_paragraph('Reviewed excerpt: '+hit['excerpt'][:650])
        if hit.get('limitations'):
            doc.add_paragraph('Limitations: '+hit['limitations'][:450])
    buff=io.BytesIO()
    doc.save(buff)
    return buff.getvalue()
