"""End-to-end export and framing checks against the actual research data."""
from io import BytesIO
from pathlib import Path
import csv
import zipfile

from docx import Document

from institutional_toolkit import evidence, reports

ROOT = Path(__file__).resolve().parents[1]


def test_country_specific_word_reports_and_missing_country():
    data=evidence.load_data(str(ROOT/'data'))
    for country in ['Estonia','Sweden','Afghanistan','Canada']:
        content=reports.word_country(data,country)
        assert zipfile.is_zipfile(BytesIO(content))
        doc=Document(BytesIO(content))
        text='\n'.join(p.text for p in doc.paragraphs)
        assert country in text
        assert 'Road Safety Institutional Toolkit' in text
        assert 'DRAFT' in text
        if country=='Afghanistan':
            assert 'not proof of institutional absence' in text.lower()


def test_country_pairwise_word_reports_are_country_specific():
    data=evidence.load_data(str(ROOT/'data'))
    for a,b in [('Estonia','Sweden'),('Sweden','Estonia'),('Estonia','Afghanistan')]:
        content=reports.word_comparison(data,a,b)
        doc=Document(BytesIO(content))
        title='\n'.join(p.text for p in doc.paragraphs[:5])
        assert a in title and b in title
        paragraphs='\n'.join(p.text for p in doc.paragraphs)
        assert 'Detailed institutional dimension comparison' in paragraphs
        assert 'Intervention-level evidence differences' in paragraphs


def test_excel_workbooks_are_valid_and_have_country_rows():
    data=evidence.load_data(str(ROOT/'data'))
    rows=evidence.all_coverage(data)
    payload=reports.excel_export({'Country coverage':rows})
    assert zipfile.is_zipfile(BytesIO(payload))
    with zipfile.ZipFile(BytesIO(payload)) as z:
        assert 'xl/workbook.xml' in z.namelist()
        assert 'xl/worksheets/sheet1.xml' in z.namelist()
        # The workbook is well-formed and contains a populated sheet.
        xml=z.read('xl/worksheets/sheet1.xml').decode('utf-8')
        assert '<sheetData>' in xml
        assert xml.count('<row ') >= 196  # header + 195 country rows


def test_checklist_prefill_remains_country_specific():
    data=evidence.load_data(str(ROOT/'data'))
    for country in ('Estonia','Sweden','Canada','Afghanistan'):
        items=evidence.checklist_prefill(data,country)
        assert len(items)==72
        assert all(x['assessment_status']=='Draft, not government validated' for x in items)
        assert sum(bool(x['source_urls']) for x in items)==evidence.coverage(data,country)['Source-linked checklist items']
