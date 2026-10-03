"""Read-only source extraction. No classification, inference, OCR or arrows."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile
import xml.etree.ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def extract(path):
    path = Path(path)
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    sid = 's-' + digest[:16]
    fmt = path.suffix.lower().lstrip('.')
    segments, warnings = [], []
    headings = []

    def add(text, location):
        if not text.strip():
            return
        segments.append(dict(source_id=sid, segment_id=f'p{len(segments)+1}',
                             heading_path=list(headings), location=location,
                             text=text, sha256=hashlib.sha256(text.encode('utf-8')).hexdigest()))

    if fmt in ('txt', 'md'):
        for i, line in enumerate(raw.decode('utf-8-sig').splitlines(), 1):
            match = re.match(r'^(#{1,6})\s+(.+)$', line) if fmt == 'md' else None
            if match:
                level = len(match[1])
                headings[:] = headings[:level-1] + [match[2]]
            add(line, dict(line_start=i, line_end=i))
    elif fmt == 'docx':
        with zipfile.ZipFile(path) as archive:
            if archive.getinfo('word/document.xml').file_size > 20_000_000:
                raise ValueError('DOCX XML too large for simple extraction')
            doc = ET.fromstring(archive.read('word/document.xml'))
        for tag in ('ins', 'del', 'moveFrom', 'moveTo', 'txbxContent', 'altChunk'):
            if doc.find('.//' + W + tag) is not None:
                raise ValueError(f'Unsupported/ambiguous DOCX content: {tag}; resolve revisions/textboxes first')

        def text_of(p):
            parts = []
            for el in p.iter():
                if el.tag == W+'t': parts.append(el.text or '')
                elif el.tag == W+'tab': parts.append('\t')
                elif el.tag in (W+'br', W+'cr'): parts.append('\n')
            return ''.join(parts)

        body = doc.find(W+'body')
        pi = ti = 0
        for child in body:
            if child.tag == W+'p':
                pi += 1
                style = child.find('./'+W+'pPr/'+W+'pStyle')
                if style is not None:
                    match = re.match(r'Heading([1-6])$', style.get(W+'val', ''), re.I)
                    if match:
                        headings[:] = headings[:int(match[1])-1] + [text_of(child)]
                add(text_of(child), dict(body_paragraph_index=pi))
            elif child.tag == W+'tbl':
                ti += 1
                if child.find('.//'+W+'tbl') is not None:
                    raise ValueError('Nested DOCX tables require a richer extractor')
                for ri, row in enumerate(child.findall(W+'tr'), 1):
                    for ci, cell in enumerate(row.findall(W+'tc'), 1):
                        paragraphs = cell.findall(W+'p')
                        add('\n'.join(text_of(p) for p in paragraphs),
                            dict(table_index=ti, row_index=ri, cell_index=ci))
        warnings.append('No page numbers; headers, footers, drawings and embedded objects are not extracted. Agent must check source completeness.')
    else:
        raise ValueError('M1 supports UTF-8 TXT/MD and simple DOCX only')
    if not segments:
        raise ValueError('No readable source segments')
    return dict(schema_version='scientific-framework/source/v1',
                source=dict(source_id=sid, format=fmt, file_alias=path.name, sha256=digest),
                segments=segments, warnings=warnings)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input'); p.add_argument('--output', required=True)
    a = p.parse_args()
    snapshot = extract(a.input)
    out = Path(a.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'Extracted {len(snapshot["segments"])} segments; no scientific inference performed')


if __name__ == '__main__':
    main()
