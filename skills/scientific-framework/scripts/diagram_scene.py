"""Three deterministic scientific layouts. Geometry never invents semantic edges."""
import argparse
import math
from pathlib import Path
from PIL import ImageFont
from contracts import digest, read, require_schema, safe_xml, write
from validate_ir import validate

LAYOUTS=('overall_research_approach_vertical','question_content_method_three_column','content_evidence_dual_layer')
SECONDARY={'method','research_task','material','data','evidence','research_object','progress','condition','comparison'}
UNDIRECTED={'contains','parallel_with','compares_with','contrasts_with'}
COLORS={'research_content':'#DCEAF7','research_task':'#FFF0D9','method':'#E6F1EA','progress':'#F0F0F0',
        'output':'#ECE5F5','evidence':'#E6F1EA','scientific_question':'#DCEAF7'}

def init_layout(ir, kind):
    if kind not in LAYOUTS: raise ValueError('Unsupported M1 layout')
    return dict(schema_version='scientific-framework/layout/v1',artifact_status=ir['artifact_status'],
                ir_sha256=digest(ir),diagram_type=kind,
                title=ir['project']['title'] or ir['project']['working_title'],
                display_node_ids=[n['id'] for n in ir['nodes']],omitted_nodes=[],font_size=18,
                containers=[],style_id='scientific-neutral',notes=['Display order is not causality.'])

def wrapped(text, width, size):
    safe_xml(text)
    font=None
    for filename in ('C:/Windows/Fonts/msyh.ttc','C:/Windows/Fonts/simhei.ttf'):
        if Path(filename).is_file():
            font=ImageFont.truetype(filename,size); break
    def length(s):
        return font.getlength(s) if font else sum(size if ord(c)>255 else size*0.6 for c in s)
    lines=[]
    for paragraph in text.split('\n'):
        line=''
        for c in paragraph:
            if line and length(line+c)>width:
                lines.append(line); line=''
            line+=c
        lines.append(line)
    return lines, 'measured_msyh_or_simhei' if font else 'estimated_cjk_width'

def build_scene(ir, layout, snapshot):
    require_schema(layout,'layout-spec')
    qa=validate(ir,snapshot)
    if not qa['valid']: raise ValueError('Scientific QA invalid: '+'; '.join(qa['errors']))
    if layout['ir_sha256']!=digest(ir): raise ValueError('Layout semantic snapshot mismatch')
    rank={'draft':0,'reviewed':1,'approved':2}
    if rank[layout['artifact_status']]>rank[ir['artifact_status']]: raise ValueError('Layout status exceeds IR status')
    if layout['artifact_status']=='approved' and not qa['approval_eligible']:
        raise ValueError('Scientific blockers prevent approved scene')
    ids=layout['display_node_ids']; nodes={n['id']:n for n in ir['nodes']}
    if len(ids)!=len(set(ids)) or any(i not in nodes for i in ids): raise ValueError('Invalid display node IDs')
    omitted={n['id'] for n in layout['omitted_nodes']}
    if len(omitted)!=len(layout['omitted_nodes']) or omitted != set(nodes)-set(ids):
        raise ValueError('Every omitted node needs one explicit reason')
    if any(nodes[i]['core'] for i in omitted): raise ValueError('Cannot omit core nodes')
    display=sorted((nodes[i] for i in ids),key=lambda n:(n['level'],ids.index(n['id'])))
    kind=layout['diagram_type']; size=layout['font_size']
    columns=[[],[],[]]
    if kind==LAYOUTS[0]:
        columns[1]=[n for n in display if n['type'] not in SECONDARY]
        columns[0]=[n for n in display if n['type'] in {'method','research_object','condition','progress','comparison'}]
        columns[2]=[n for n in display if n['type'] in SECONDARY and n not in columns[0]]
        headings=['方法 / 条件 / 进度','研究主轴（顺序须有来源）','任务 / 资料 / 证据']
    elif kind==LAYOUTS[1]:
        columns[0]=[n for n in display if n['type'] in {'background','research_gap','research_problem','scientific_question','overall_objective','sub_objective'}]
        columns[2]=[n for n in display if n['type']=='method']
        columns[1]=[n for n in display if n not in columns[0]+columns[2]]
        headings=['问题 / 目标','研究内容与相关阶段','共享研究方法']
    else:
        # Two horizontal bands; distributed columns do not imply pairing.
        headings=['研究内容 / 问题主层','任务 / 方法 / 资料辅助层']
        main=[n for n in display if n['type'] not in SECONDARY]
        aux=[n for n in display if n['type'] in SECONDARY]
        for idx,n in enumerate(main+aux): columns[idx%3].append(n)
    rendered=[]; metrics=[]
    xs=[160,650,1140]; widths=[330,370,330]
    ytop=160
    if kind!=LAYOUTS[2]:
        for col, ns in enumerate(columns):
            y=ytop
            for n in ns:
                lines,metric=wrapped(n['label'],widths[col]-32,size)
                h=max(80,len(lines)*(size+7)+48)
                rendered.append(dict(id='n-'+n['id'],semantic_node_ids=[n['id']],label=n['label'],lines=lines,
                                     role=n['type'],statement_status=n['statement_status'],needs_review=n['needs_review'],
                                     x=xs[col],y=y,width=widths[col],height=h,parent=None,
                                     fill=COLORS.get(n['type'],'#F5F7FA'),source_refs=n['source_location']))
                metrics.append(metric); y+=h+42
    else:
        y=ytop
        for band,ns in enumerate((main,aux)):
            if band: y+=70
            for start in range(0,len(ns),3):
                row=[]
                for col,n in enumerate(ns[start:start+3]):
                    lines,metric=wrapped(n['label'],widths[col]-32,size)
                    h=max(80,len(lines)*(size+7)+48)
                    row.append(dict(id='n-'+n['id'],semantic_node_ids=[n['id']],label=n['label'],lines=lines,
                                    role=n['type'],statement_status=n['statement_status'],needs_review=n['needs_review'],
                                    x=xs[col],y=y,width=widths[col],height=h,parent=None,
                                    fill=COLORS.get(n['type'],'#F5F7FA'),source_refs=n['source_location']))
                    metrics.append(metric)
                rendered.extend(row); y+=max(n['height'] for n in row)+42
            if not band: divider=y+25
    by_id={n['semantic_node_ids'][0]:n for n in rendered}
    containers=[]; specifications={c['id']:c for c in layout['containers']}
    if len(specifications)!=len(layout['containers']) or set(specifications)&{n['id'] for n in rendered}:
        raise ValueError('Duplicate/reserved container ID')
    assigned=set()
    def container(cid,trail):
        if cid in trail: raise ValueError('Container cycle')
        c=specifications[cid]
        if c['parent'] is not None and c['parent'] not in specifications: raise ValueError('Missing container parent')
        members=[]
        for i in c['node_ids']:
            if i not in by_id or i in assigned: raise ValueError('Invalid/multiple container membership')
            assigned.add(i); by_id[i]['parent']=cid; members.append(by_id[i])
        for child in specifications.values():
            if child['parent']==cid: members.append(container(child['id'],trail|{cid}))
        x=min(n['x'] for n in members)-22; y=min(n['y'] for n in members)-44
        right=max(n['x']+n['width'] for n in members)+22
        bottom=max(n['y']+n['height'] for n in members)+22
        result=dict(id=cid,label=safe_xml(c['label']),parent=c['parent'],x=x,y=y,width=right-x,height=bottom-y)
        containers.append(result); return result
    for cid,c in specifications.items():
        if c['parent'] is None: container(cid,set())
    if len(containers)!=len(specifications): raise ValueError('Container hierarchy cycle')
    edges=[]; unshown=[]
    for idx,r in enumerate(ir['relations']):
        if r['source'] not in by_id or r['target'] not in by_id:
            unshown.append(r['id']); continue
        a,b=by_id[r['source']],by_id[r['target']]
        # Explicit simple channels. Complex obstacle routing is deliberately not claimed.
        if a['x']!=b['x']:
            forward=a['x']<b['x']
            p1=[a['x']+a['width'] if forward else a['x'],a['y']+a['height']/2]
            p2=[b['x'] if forward else b['x']+b['width'],b['y']+b['height']/2]
            mx=(p1[0]+p2[0])/2 + (idx%5-2)*9
            points=[p1,[mx,p1[1]],[mx,p2[1]],p2]
        else:
            p1=[a['x'],a['y']+a['height']/2]; p2=[b['x'],b['y']+b['height']/2]
            lane=a['x']-34-(idx%7)*12
            points=[p1,[lane,p1[1]],[lane,p2[1]],p2]
        edges.append(dict(id='e-'+r['id'],semantic_relation_ids=[r['id']],source=a['id'],target=b['id'],
                          relation=r['relation'],label=r['id']+' · '+r['relation'],points=points,
                          directed=r['relation'] not in UNDIRECTED,needs_review=r['needs_review'],
                          statement_status=r['statement_status'],source_refs=r['source_location']))
    if unshown and layout['artifact_status']=='approved': raise ValueError('Unshown scientific relations prevent approved display')
    height=max(n['y']+n['height'] for n in rendered)+160
    annotations=[dict(x=160,y=55,text=layout['title']+' · '+layout['artifact_status'])]
    if kind==LAYOUTS[2]:
        annotations.extend([dict(x=160,y=120,text=headings[0]),dict(x=160,y=divider,text=headings[1])])
    else:
        annotations.extend(dict(x=xs[i],y=120,text=s) for i,s in enumerate(headings))
    annotations.append(dict(x=160,y=height-80,text='类型色仅区分角色；实线=来源关系，虚线=待审；无箭头=比较/归属/并列；planned/expected不等于已验证。'))
    return dict(schema_version='scientific-framework/scene/v1',artifact_status=layout['artifact_status'],
                ir_sha256=digest(ir),layout_sha256=digest(layout),width=1640,height=height,font_size=size,
                nodes=rendered,edges=edges,containers=containers,annotations=annotations,
                unshown_relation_ids=unshown,text_metrics=list(set(metrics)),scientific_qa=qa)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('ir'); p.add_argument('--sources',required=True); p.add_argument('--layout',required=True)
    p.add_argument('--scene',required=True); p.add_argument('--init-layout',choices=LAYOUTS)
    a=p.parse_args(); ir=read(a.ir)
    layout=init_layout(ir,a.init_layout) if a.init_layout else read(a.layout)
    scene=build_scene(ir,layout,read(a.sources))
    write(a.layout,layout); write(a.scene,scene)
    print('Scene contains',len(scene['nodes']),'nodes and',len(scene['edges']),'source relations')

if __name__=='__main__': main()
