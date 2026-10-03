"""Validate vision-Agent observations; create profiles and candidates, never defaults."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image
from contracts import read, require_schema, write

def profile(image_path,observation):
    require_schema(observation,'reference-observation')
    path=Path(image_path); sha=hashlib.sha256(path.read_bytes()).hexdigest()
    if observation['image_sha256']!=sha: raise ValueError('Observation refers to a different image snapshot')
    with Image.open(path) as image:
        if image.format not in ('PNG','JPEG'): raise ValueError('M1 references must be PNG/JPG')
        pixels=image.convert('RGBA')
        pixel_hash=hashlib.sha256(str(pixels.size).encode()+pixels.tobytes()).hexdigest()
        metadata=dict(filename=path.name,sha256=sha,pixel_sha256=pixel_hash,width=image.width,height=image.height,format=image.format)
    result=dict(schema_version='scientific-framework/profile/v1',metadata=metadata,observation=observation,
                visual_style=observation['visual_style'],layout_grammar=observation['layout_grammar'],promotion_status='candidate')
    require_schema(result,'reference-profile')
    return result

def markdown(p):
    obs=p['observation']; lines=['# 参考图视觉分析：'+p['metadata']['filename'],'','候选观察；不改变默认风格，不推测科学命题。','']
    for key,value in p.items():
        lines += ['## '+key,'','```json',json.dumps(value,ensure_ascii=False,indent=2),'```','']
    return '\n'.join(lines)

def aggregate(profiles):
    if not profiles: raise ValueError('No profiles')
    for p in profiles: require_schema(p,'reference-profile')
    # Union identical pixels and Agent-verified composition variants before counting.
    parent=list(range(len(profiles)))
    def find(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]]; i=parent[i]
        return i
    for i,a in enumerate(profiles):
        for j,b in enumerate(profiles[:i]):
            same_pixels=a['metadata']['pixel_sha256']==b['metadata']['pixel_sha256']
            oa,ob=a['observation'],b['observation']
            same_group=(oa['composition_group_status']==ob['composition_group_status']=='verified' and
                        oa['composition_group']==ob['composition_group'])
            if same_pixels or same_group: parent[find(i)]=find(j)
    principles={}
    for i,p in enumerate(profiles):
        for principle in set(p['observation']['reusable_principles']): principles.setdefault(principle,[]).append(i)
    patterns=[]
    for principle,indices in sorted(principles.items()):
        independent={find(i) for i in indices if profiles[i]['observation']['composition_group_status']=='verified'}
        patterns.append(dict(pattern_name=principle,sources=[profiles[i]['metadata']['sha256'] for i in indices],
                             occurrence_count=len(indices),independent_composition_count=len(independent),
                             applicable_diagram_types=[],applicable_density='Needs Agent applicability review',description=principle,
                             confidence=min(profiles[i]['observation']['confidence'] for i in indices),
                             promotion_status='promotion_candidate' if len(independent)>=2 else 'candidate'))
    result=dict(schema_version='scientific-framework/style/v1',patterns=patterns,default_changed=False)
    for section in ('visual_style','layout_grammar'):
        result[section]={}
        for key in profiles[0][section]:
            values=[p[section][key] for p in profiles]
            result[section][key]=(values[0] if all(v==values[0] for v in values) else
                                 dict(status='unknown',value=None,note='Observations differ; no unified attribute asserted'))
    require_schema(result,'style-profile')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__); subs=p.add_subparsers(dest='command',required=True)
    one=subs.add_parser('profile'); one.add_argument('image'); one.add_argument('--observation',required=True); one.add_argument('--output',required=True)
    many=subs.add_parser('aggregate'); many.add_argument('profiles',nargs='+'); many.add_argument('--output',required=True)
    a=p.parse_args()
    if a.command=='profile':
        data=profile(a.image,read(a.observation)); write(a.output,data)
        Path(a.output).with_suffix('.md').write_text(markdown(data),encoding='utf-8')
    else: write(a.output,aggregate([read(p) for p in a.profiles]))
    print('Candidate saved; personal default unchanged')

if __name__=='__main__': main()
