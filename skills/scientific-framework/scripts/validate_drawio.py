"""Original XML/scene consistency and simple geometry checks; no upstream code copied."""
import argparse
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
from contracts import digest, read, write
from ir_to_drawio import xml_tree

def structural_check(path):
    errors=[]
    tree=ET.parse(path); root=tree.find('.//mxGraphModel/root')
    if root is None: return ['Missing mxGraphModel/root']
    cells=root.findall('mxCell'); ids=[c.get('id') for c in cells]; by_id={c.get('id'):c for c in cells}
    if len(ids)!=len(set(ids)): errors.append('Duplicate mxCell IDs')
    if '0' not in by_id or '1' not in by_id or by_id['1'].get('parent')!='0': errors.append('Invalid root cells 0/1')
    for c in cells:
        cid=c.get('id'); parent=c.get('parent')
        if cid!='0' and parent not in by_id: errors.append(f'{cid}: dangling parent')
        seen={cid}; ancestor=parent
        while ancestor in by_id:
            if ancestor in seen: errors.append(f'{cid}: parent cycle'); break
            seen.add(ancestor); ancestor=by_id[ancestor].get('parent')
        if c.get('vertex')=='1':
            geom=c.find('mxGeometry')
            if geom is None: errors.append(f'{cid}: missing vertex geometry'); continue
            try:
                vals=[float(geom.get(k,'nan')) for k in ('x','y','width','height')]
                if not all(math.isfinite(v) for v in vals) or vals[2]<=0 or vals[3]<=0: errors.append(f'{cid}: invalid geometry')
            except ValueError: errors.append(f'{cid}: nonnumeric geometry')
        if c.get('edge')=='1':
            if any(c.get(k) not in by_id or by_id[c.get(k)].get('vertex')!='1' for k in ('source','target')):
                errors.append(f'{cid}: dangling edge')
            geom=c.find('mxGeometry')
            if geom is None or geom.get('relative')!='1': errors.append(f'{cid}: missing relative edge geometry')
            if not c.get('semantic_relation_ids'): errors.append(f'{cid}: missing semantic relation IDs')
    return errors

def geometry_qa(scene):
    issues=[]; nodes=scene['nodes']
    for i,a in enumerate(nodes):
        for b in nodes[i+1:]:
            if max(a['x'],b['x'])<min(a['x']+a['width'],b['x']+b['width']) and max(a['y'],b['y'])<min(a['y']+a['height'],b['y']+b['height']):
                issues.append('Node overlap: '+a['id']+'/'+b['id'])
    def hits(p,q,n):
        left,top,right,bottom=n['x'],n['y'],n['x']+n['width'],n['y']+n['height']
        if p[0]==q[0]: return left<p[0]<right and max(min(p[1],q[1]),top)<min(max(p[1],q[1]),bottom)
        if p[1]==q[1]: return top<p[1]<bottom and max(min(p[0],q[0]),left)<min(max(p[0],q[0]),right)
        return False
    segs=[]
    for e in scene['edges']:
        for p,q in zip(e['points'],e['points'][1:]):
            segs.append((e['id'],p,q))
            for n in nodes:
                if n['id'] not in (e['source'],e['target']) and hits(p,q,n):
                    issues.append('Edge crosses unrelated node: '+e['id']+'/'+n['id'])
    crossings=0
    for i,(eid,p,q) in enumerate(segs):
        for fid,r,s in segs[i+1:]:
            if eid==fid: continue
            if p[0]==q[0] and r[1]==s[1]:
                if min(r[0],s[0])<p[0]<max(r[0],s[0]) and min(p[1],q[1])<r[1]<max(p[1],q[1]): crossings+=1
            elif p[1]==q[1] and r[0]==s[0]:
                if min(p[0],q[0])<r[0]<max(p[0],q[0]) and min(r[1],s[1])<p[1]<max(r[1],s[1]): crossings+=1
    if crossings: issues.append(f'Orthogonal edge crossings: {crossings}')
    a4_scale=min(793.7/scene['width'],1122.5/scene['height'])
    points=scene['font_size']*a4_scale*72/96
    if points<9: issues.append(f'A4 fit-to-page node label is only {points:.1f} pt; use a larger page or simplify projection')
    return dict(status='issues_found' if issues else 'automatic_checks_passed',issues=list(dict.fromkeys(issues)),
                a4_fit_font_pt=round(points,2),edge_crossing_count=crossings,
                human_visual_review='not_run',reading_3_to_5_seconds='not_run',grayscale_print='not_run',
                native_drawio_render='not_run',text_metrics=scene['text_metrics'])

def validate_drawio(path,scene):
    errors=structural_check(path)
    actual=ET.canonicalize(Path(path).read_text(encoding='utf-8'))
    expected=ET.canonicalize(ET.tostring(xml_tree(scene).getroot(),encoding='unicode'))
    if actual!=expected: errors.append('XML differs from bound scene; update layout/scene or review edits before export')
    return dict(valid=not errors,errors=errors,scene_sha256=digest(scene),artifact_status=scene['artifact_status'],
                structure_qa='passed' if not errors else 'failed',visual_qa=geometry_qa(scene))

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('drawio'); p.add_argument('--scene',required=True)
    p.add_argument('--output',required=True); p.add_argument('--visual-output')
    a=p.parse_args(); qa=validate_drawio(a.drawio,read(a.scene)); write(a.output,qa)
    if a.visual_output: write(a.visual_output,qa['visual_qa'])
    print('structure=',qa['structure_qa'],'visual=',qa['visual_qa']['status'])
    raise SystemExit(0 if qa['valid'] else 1)

if __name__=='__main__': main()
