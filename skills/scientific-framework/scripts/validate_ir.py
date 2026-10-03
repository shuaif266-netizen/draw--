"""Deterministic Scientific QA; Agent evidence review remains a separate input."""
import argparse
import hashlib
from pathlib import Path
from contracts import digest, read, schema_errors, write


def validate(ir, snapshot):
    errors = schema_errors(ir, 'scientific-ir')
    blockers, warnings = [], []
    if errors:
        return dict(schema_valid=False, valid=False, approval_eligible=False,
                    artifact_status=ir.get('artifact_status'), errors=errors, blockers=[], warnings=[])
    source = snapshot['source']
    segments = {(s['source_id'], s['segment_id']): s for s in snapshot['segments']}
    if len(segments) != len(snapshot['segments']): errors.append('Duplicate source segment IDs')
    for s in snapshot['segments']:
        if s['sha256'] != hashlib.sha256(s['text'].encode('utf-8')).hexdigest():
            errors.append('Source segment checksum mismatch: '+s['segment_id'])
        if s['source_id'] != source['source_id']: errors.append('Segment source_id mismatch')
    if ir['project']['source'] != [source]: errors.append('IR source registry differs from snapshot')
    if (ir['project']['title'] is None) != (ir['project']['title_status']=='missing'):
        errors.append('title/title_status inconsistent')
    ids = [n['id'] for n in ir['nodes']]
    rid = [r['id'] for r in ir['relations']]
    if len(set(ids+rid)) != len(ids+rid): errors.append('Duplicate semantic IDs')
    nodes = {n['id']:n for n in ir['nodes']}

    def location(loc, subject):
        segment = segments.get((loc['source_id'],loc['segment_id']))
        if not segment:
            errors.append(f'{subject}: missing source location'); return None
        for key,value in loc.items():
            if key not in ('source_id','segment_id'):
                actual = segment['heading_path'] if key=='heading_path' else segment['location'].get(key)
                if value != actual: errors.append(f'{subject}: inaccurate location {key}')
        return segment

    for n in ir['nodes']:
        segs = [location(loc,n['id']) for loc in n['source_location']]
        for quote in n['source_text']:
            if not any(s and quote in s['text'] for s in segs):
                errors.append(n['id']+': source quote mismatch')
        if n['core'] and (n['needs_review'] or n['extraction_status'] in ('inferred','missing')):
            blockers.append(n['id']+': core node requires review')
    hierarchy = {}
    for r in ir['relations']:
        if r['source'] not in nodes or r['target'] not in nodes:
            errors.append(r['id']+': dangling relation'); continue
        for loc in r['source_location']: location(loc,r['id'])
        keys = {(l['source_id'],l['segment_id']) for l in r['source_location']}
        for e in r['evidence']:
            segment=segments.get((e['source_id'],e['segment_id']))
            if not segment or e['quote'] not in segment['text']:
                errors.append(r['id']+': evidence quote mismatch')
            if (e['source_id'],e['segment_id']) not in keys:
                errors.append(r['id']+': evidence has no matching location')
        if r['core'] and (not r['evidence'] or not r['source_location']):
            blockers.append(r['id']+': core relation lacks evidence/location')
        if r['core'] and r['needs_review']: blockers.append(r['id']+': unresolved core relation')
        if r['relation']=='causes':
            if not r['evidence'] or r['needs_review']:
                blockers.append(r['id']+': unconfirmed causal proposition')
            warnings.append(r['id']+': causality needs Agent entailment review; evidence presence alone is insufficient')
        if r['relation'] not in ('temporal_before','parallel_with','contains','applies_to'):
            if any(nodes[i]['type']=='progress' for i in (r['source'],r['target'])):
                blockers.append(r['id']+': progress used as scientific mechanism/support')
        if r['relation']=='contains': hierarchy.setdefault(r['source'],[]).append(r['target'])
    def cycle(n, trail):
        if n in trail: return True
        return any(cycle(c,trail|{n}) for c in hierarchy.get(n,[]))
    if any(cycle(n,set()) for n in hierarchy): errors.append('contains hierarchy cycle')
    for issue in ir['review_items']+ir['agent_review']['issues']:
        if any(i not in set(ids+rid) for i in issue['subject_ids']): errors.append('Review item refers to unknown ID')
        if issue['needs_review'] and issue['severity']=='blocker': blockers.append(issue['issue'])
    review=ir['agent_review']
    if review['source_snapshot_sha256'] != digest(snapshot): errors.append('Agent review source snapshot changed')
    if review['status']!='completed': blockers.append('Agent scientific/terminology/status review pending')
    warnings.extend(snapshot.get('warnings',[]))
    eligible = not errors and not blockers
    if ir['artifact_status']=='approved' and not eligible:
        errors.append('approved artifact violates Scientific QA gate')
    return dict(schema_valid=True, valid=not errors, approval_eligible=eligible,
                artifact_status=ir['artifact_status'], errors=errors,
                blockers=list(dict.fromkeys(blockers)), warnings=warnings,
                source_snapshot_sha256=digest(snapshot), ir_sha256=digest(ir),
                semantic_review='agent_record_completed' if review['status']=='completed' else 'pending')


def logic_report(ir, qa):
    groups={}
    for n in ir['nodes']: groups.setdefault(n['type'],[]).append(n['label'])
    lines=['# 科研逻辑审查', '', f'状态：{ir["artifact_status"]}；批准条件满足：{qa["approval_eligible"]}', '',
           'Agent审查：'+ir['agent_review']['summary'], '', '## 角色清单']
    for t,labels in groups.items(): lines.append(f'- {t}：'+ '；'.join(labels))
    lines += ['', '## 有来源关系（状态保留）']
    for r in ir['relations']:
        lines.append(f'- {r["id"]}: {r["source"]} — {r["relation"]} → {r["target"]}；{r["statement_status"]}；待审={r["needs_review"]}。{r["interpretation_note"]}')
    lines += ['', '## 阻止最终批准的问题']
    lines += ['- '+x for x in qa['errors']+qa['blockers']] or ['无程序门槛阻塞；仍应核对Agent审查真实性。']
    lines += ['', '## 压缩与不可合并', '保留完整IR；短标签仅用于显示。内容、任务、方法、进度不可互相合并。同数量不是对应关系证据。',
              '', '## 能力边界', '本报告汇总确定性检查和已提供的Agent审查；脚本不推断主线、不证明因果。具体主线/遗漏/压缩判断由Agent填写在审查摘要与问题中。']
    return '\n'.join(lines)+'\n'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('ir'); p.add_argument('--sources',required=True); p.add_argument('--output',required=True)
    p.add_argument('--logic-review')
    a=p.parse_args(); ir=read(a.ir); qa=validate(ir,read(a.sources)); write(a.output,qa)
    if a.logic_review:
        Path(a.logic_review).write_text(logic_report(ir,qa),encoding='utf-8')
    print('valid=',qa['valid'],'approval_eligible=',qa['approval_eligible'])
    raise SystemExit(0 if qa['valid'] else 1)

if __name__=='__main__': main()
