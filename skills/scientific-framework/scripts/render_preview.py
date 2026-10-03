"""Same-scene SVG fallback; optional verified draw.io CLI SVG/PNG export."""
import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET
from PIL import Image
from contracts import digest, read, write
from validate_drawio import validate_drawio

def svg_tree(scene):
    svg=ET.Element('svg',xmlns='http://www.w3.org/2000/svg',width=str(scene['width']),height=str(scene['height']),
                   viewBox=f'0 0 {scene["width"]} {scene["height"]}',
                   attrib={'data-backend':'scene_svg_fallback','data-status':scene['artifact_status']})
    ET.SubElement(svg,'metadata').text='scene_sha256='+digest(scene)+'; scientific status='+scene['artifact_status']
    ET.SubElement(svg,'rect',width='100%',height='100%',fill='white')
    defs=ET.SubElement(svg,'defs'); marker=ET.SubElement(defs,'marker',id='arrow',markerWidth='8',markerHeight='8',refX='7',refY='4',orient='auto')
    ET.SubElement(marker,'path',d='M0 0 L8 4 L0 8 Z',fill='#64748B')
    def text(x,y,lines,size,weight=None):
        attrs=dict(x=str(x),y=str(y),fill='#203246')
        attrs.update({'font-family':'Microsoft YaHei,SimHei,sans-serif','font-size':str(size)})
        if weight: attrs['font-weight']=weight
        el=ET.SubElement(svg,'text',attrs)
        for i,line in enumerate(lines): ET.SubElement(el,'tspan',x=str(x),dy='0' if not i else str(size+7)).text=line
    for c in sorted(scene['containers'],key=lambda c:-c['width']*c['height']):
        ET.SubElement(svg,'rect',x=str(c['x']),y=str(c['y']),width=str(c['width']),height=str(c['height']),rx='10',fill='none',stroke='#94A3B8')
        text(c['x']+10,c['y']+23,[c['label']],14)
    for e in scene['edges']:
        attrs=dict(points=' '.join(f'{x},{y}' for x,y in e['points']),fill='none',stroke='#64748B')
        attrs['stroke-width']='1.5'
        if e['directed']: attrs['marker-end']='url(#arrow)'
        if e['needs_review']: attrs['stroke-dasharray']='6 5'
        ET.SubElement(svg,'polyline',attrs)
        p=e['points'][1]; text(p[0]+3,p[1]-6,[e['label']],11)
    for n in scene['nodes']:
        el=ET.SubElement(svg,'g',attrib={'data-semantic-node-ids':','.join(n['semantic_node_ids'])})
        ET.SubElement(el,'rect',x=str(n['x']),y=str(n['y']),width=str(n['width']),height=str(n['height']),rx='10',fill=n['fill'],stroke='#526477')
        text(n['x']+16,n['y']+scene['font_size']+15,n['lines'],scene['font_size'])
        text(n['x']+16,n['y']+n['height']-14,[n['role']+' · '+n['statement_status']],12)
    for a in scene['annotations']: text(a['x'],a['y'],[a['text']],17,'600')
    return ET.ElementTree(svg)

def discover_cli():
    for name in ('drawio','draw.io'):
        path=shutil.which(name)
        if path: return str(Path(path).resolve())
    for path in ('C:/Program Files/draw.io/draw.io.exe',str(Path.home()/'AppData/Local/Programs/draw.io/draw.io.exe')):
        if Path(path).is_file(): return str(Path(path).resolve())
    return None

def render(scene,drawio,output_dir,cli=None,force_fallback=False):
    qa=validate_drawio(drawio,scene)
    if not qa['valid']: raise ValueError('; '.join(qa['errors']))
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    svg=out/'preview.svg'; png=out/'preview.png'
    manifest=dict(artifact_status=scene['artifact_status'],scene_sha256=digest(scene),
                  ir_sha256=scene['ir_sha256'],layout_sha256=scene['layout_sha256'],
                  scientific_qa=scene['scientific_qa'],backend='scene_svg_fallback',
                  rendered_from='layout_spec',native_drawio_render='skipped',png_status='skipped',commands=[])
    # Never leave a stale native PNG that looks like this generation succeeded.
    if png.exists(): png.unlink()
    exe=None if force_fallback else (str(Path(cli).resolve()) if cli else discover_cli())
    if exe:
        ok=True
        for fmt,target in (('svg',svg),('png',png)):
            if target.exists(): target.unlink()
            command=[exe,'--export','--format',fmt,'--output',str(target.resolve()),str(Path(drawio).resolve())]
            record=dict(command=command)
            try:
                run=subprocess.run(command,capture_output=True,text=True,timeout=40)
                record['exit_code']=run.returncode
                if run.returncode!=0 or not target.is_file(): raise ValueError('CLI failed or missing artifact')
                if fmt=='svg':
                    if ET.parse(target).getroot().tag.split('}')[-1]!='svg': raise ValueError('Invalid SVG root')
                else:
                    with Image.open(target) as image:
                        if image.format!='PNG': raise ValueError('Not a PNG')
                        image.verify()
                record['status']='passed'
            except (OSError,ValueError,ET.ParseError,subprocess.TimeoutExpired) as e:
                record['status']='failed'; record['error']=str(e); ok=False
                if target.exists(): target.unlink()
            manifest['commands'].append(record)
        manifest['native_drawio_render']='passed' if ok else 'failed'
        if ok:
            manifest['backend']='drawio_cli'; manifest['rendered_from']='drawio'
            manifest['png_status']='passed'
        else:
            if png.exists(): png.unlink()
            manifest['png_status']='failed'
    if manifest['backend']=='scene_svg_fallback': svg_tree(scene).write(svg,encoding='utf-8',xml_declaration=True)
    manifest['artifacts']={svg.name:hashlib.sha256(svg.read_bytes()).hexdigest()}
    if png.exists(): manifest['artifacts'][png.name]=hashlib.sha256(png.read_bytes()).hexdigest()
    manifest['visual_qa_status']=qa['visual_qa']['status']
    write(out/'render_manifest.json',manifest)
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--scene',required=True); p.add_argument('--drawio',required=True)
    p.add_argument('--output-dir',required=True); p.add_argument('--cli'); p.add_argument('--force-fallback',action='store_true')
    a=p.parse_args(); m=render(read(a.scene),a.drawio,a.output_dir,a.cli,a.force_fallback)
    print(m['backend'],'native_drawio_render='+m['native_drawio_render'])

if __name__=='__main__': main()
