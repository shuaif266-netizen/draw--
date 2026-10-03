"""Re-run the public synthetic case; Agent semantic fixture is input, not inferred by script."""
import argparse
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/scientific-framework/scripts'))
from contracts import digest, read, write
from extract_sources import extract
from compile_scientific_ir import compile_ir
from validate_ir import validate, logic_report
from diagram_scene import LAYOUTS, init_layout, build_scene
from ir_to_drawio import xml_tree
from validate_drawio import validate_drawio
from render_preview import render
from learn_reference import profile,markdown,aggregate

def run(output=None):
    case=ROOT/'eval_cases/case_001'
    out=Path(output) if output else case/'generated'
    out.mkdir(parents=True,exist_ok=True)
    snapshot=extract(case/'proposal/proposal.txt'); write(out/'source_segments.json',snapshot)
    agent=read(case/'agent_understanding.json')
    ir,qa=compile_ir(agent,snapshot); write(out/'scientific_ir.json',ir)
    write(out/'scientific_qa.json',qa)
    (out/'logic_review.md').write_text(logic_report(ir,qa),encoding='utf-8')
    directions='''# 三种结构方向（Agent根据合成IR制定）

A. 纵向研究主轴：问题与四项内容、综合分析、预期工具为主层；方法、任务、资料、进度为侧层。优点是认识推进明确；风险是内容上下排列易误读为时序，应只保留真实边。

B. 问题—内容—方法三栏：中栏内容与综合阶段，左问题，右五种共享方法。优点是方法支撑可辨；任务/资料放中栏会增加密度，不按行复制共享方法。

C. 内容＋任务/证据双层：上层问题/内容/综合分析/工具，下层四任务、五方法、资料和进度。优点是防止内容和任务数量配对；跨层边较多，需更大版面或后续明确显示投影。

三方案科研语义一致，不创建任务到内容的待定分配关系；检验边r-validation保留虚线和待审。M1案例默认输出A草稿，B/C用于布局回归。完整IR的A4字号与复杂交叉须在Visual QA列出，不宣称final。
'''
    (out/'diagram_directions.md').write_text(directions,encoding='utf-8')
    for i,kind in enumerate(LAYOUTS):
        dest=out if i==0 else out/('layout-'+str(i+1)); dest.mkdir(parents=True,exist_ok=True)
        layout=init_layout(ir,kind); scene=build_scene(ir,layout,snapshot)
        write(dest/'layout_spec.json',layout); write(dest/'diagram_scene.json',scene)
        path=dest/'research-framework.drawio'
        path.write_bytes(ET.tostring(xml_tree(scene).getroot(),encoding='utf-8',xml_declaration=True))
        checks=validate_drawio(path,scene); write(dest/'drawio_qa.json',checks)
        visual=checks['visual_qa']
        review_path=case/'agent_visual_reviews.json'
        if review_path.is_file():
            review=read(review_path)[kind]
            visual_hash=digest({k:scene[k] for k in ('nodes','edges','containers','annotations','width','height','font_size')})
            if visual_hash==review['visual_scene_sha256']:
                visual['agent_visual_review']=review
            else:
                visual['agent_visual_review']=dict(status='stale_review_not_applied')
        write(dest/'visual_qa.json',visual)
        render(scene,path,dest)
    image_path=case/'reference_images/synthetic-framework.png'
    observation_path=case/'reference_observation.json'
    if image_path.is_file() and observation_path.is_file():
        ref=profile(image_path,read(observation_path)); write(out/'reference_profile.json',ref)
        (out/'reference_profile.md').write_text(markdown(ref),encoding='utf-8')
        write(out/'style_candidates.json',aggregate([ref]))
    print('Synthetic case completed: '+str(out))
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output'); a=p.parse_args(); run(a.output)
