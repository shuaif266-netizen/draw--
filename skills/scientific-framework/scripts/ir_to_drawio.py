"""Scientific QA runs before editable XML. No raster image is embedded."""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from contracts import digest, read, safe_xml, write
from diagram_scene import build_scene, ROLE_LABELS, STATE_LABELS

def xml_tree(scene):
    file=ET.Element('mxfile',host='scientific-framework',artifact_status=scene['artifact_status'],
                    ir_sha256=scene['ir_sha256'],scene_sha256=digest(scene))
    page=ET.SubElement(file,'diagram',id='scientific-framework',name='研究框架')
    model=ET.SubElement(page,'mxGraphModel',page='1',pageWidth=str(scene['width']),pageHeight=str(scene['height']))
    root=ET.SubElement(model,'root')
    ET.SubElement(root,'mxCell',id='0'); ET.SubElement(root,'mxCell',id='1',parent='0')
    geometries={c['id']:c for c in scene['containers']}
    def geometry(cell,n):
        parent=geometries.get(n.get('parent'))
        ET.SubElement(cell,'mxGeometry',x=str(n['x']-(parent['x'] if parent else 0)),
                      y=str(n['y']-(parent['y'] if parent else 0)),width=str(n['width']),height=str(n['height']),attrib={'as':'geometry'})
    for c in scene['containers']:
        cell=ET.SubElement(root,'mxCell',id=c['id'],value=c['label'],vertex='1',parent=c['parent'] or '1',
                           style='rounded=1;fillColor=none;strokeColor=#94A3B8;verticalAlign=top;align=left;html=0;container=1;')
        geometry(cell,c)
    for n in scene['nodes']:
        label='\n'.join(n['lines'])+'\n['+ROLE_LABELS[n['role']]+' · '+STATE_LABELS[n['statement_status']]+']'
        cell=ET.SubElement(root,'mxCell',id=n['id'],value=safe_xml(label),vertex='1',parent=n['parent'] or '1',
                           semantic_node_ids=json.dumps(n['semantic_node_ids']),
                           source_refs=json.dumps([{'source_id':l['source_id'],'segment_id':l['segment_id']} for l in n['source_refs']]),
                           artifact_status=scene['artifact_status'],statement_status=n['statement_status'],
                           style=f'rounded=1;whiteSpace=wrap;html=0;fontFamily=Microsoft YaHei;fontSize={scene["font_size"]};fillColor={n["fill"]};strokeColor=#526477;spacing=12;')
        geometry(cell,n)
    by_id={n['id']:n for n in scene['nodes']}
    for e in scene['edges']:
        a,b=by_id[e['source']],by_id[e['target']]
        first,last=e['points'][0],e['points'][-1]
        style=(f'edgeStyle=none;html=0;rounded=0;fontSize=12;strokeColor=#64748B;'
               f'endArrow={"block" if e["directed"] else "none"};dashed={int(e["needs_review"])};'
               f'exitX={(first[0]-a["x"])/a["width"]};exitY={(first[1]-a["y"])/a["height"]};'
               f'entryX={(last[0]-b["x"])/b["width"]};entryY={(last[1]-b["y"])/b["height"]};exitPerimeter=0;entryPerimeter=0;')
        cell=ET.SubElement(root,'mxCell',id=e['id'],value=e['label'],edge='1',parent='1',source=e['source'],target=e['target'],
                           semantic_relation_ids=json.dumps(e['semantic_relation_ids']),
                           source_refs=json.dumps([{'source_id':l['source_id'],'segment_id':l['segment_id']} for l in e['source_refs']]),
                           artifact_status=scene['artifact_status'],statement_status=e['statement_status'],style=style)
        geom=ET.SubElement(cell,'mxGeometry',relative='1',attrib={'as':'geometry'})
        pts=ET.SubElement(geom,'Array',attrib={'as':'points'})
        for x,y in e['points'][1:-1]: ET.SubElement(pts,'mxPoint',x=str(x),y=str(y))
    for i,a in enumerate(scene['annotations']):
        cell=ET.SubElement(root,'mxCell',id=f'annotation-{i}',value=safe_xml(a['text']),vertex='1',parent='1',
                           decorative='1',style='text;html=0;align=left;verticalAlign=middle;fontFamily=Microsoft YaHei;fontSize=17;')
        ET.SubElement(cell,'mxGeometry',x=str(a['x']),y=str(a['y']-22),width='1450',height='44',attrib={'as':'geometry'})
    return ET.ElementTree(file)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('ir'); p.add_argument('--sources',required=True); p.add_argument('--layout',required=True)
    p.add_argument('--output',required=True); p.add_argument('--scene',required=True)
    a=p.parse_args(); scene=build_scene(read(a.ir),read(a.layout),read(a.sources))
    write(a.scene,scene); out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(ET.tostring(xml_tree(scene).getroot(),encoding='utf-8',xml_declaration=True))
    print('Editable XML generated after Scientific QA; status='+scene['artifact_status'])

if __name__=='__main__': main()
