"""Behavioral regression tests for the scientific contracts and generated artifacts."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/scientific-framework/scripts'))
from contracts import SKILL,digest,semantic_digest,read,require_schema,schema_errors
from extract_sources import extract
from compile_scientific_ir import compile_ir
from validate_ir import validate
from diagram_scene import LAYOUTS,init_layout,build_scene
from ir_to_drawio import xml_tree
from validate_drawio import validate_drawio,structural_check
from render_preview import render
from learn_reference import profile,aggregate
from PIL import Image

class M1Tests(unittest.TestCase):
    def setUp(self):
        self.snapshot=extract(ROOT/'eval_cases/case_001/proposal/proposal.txt')
        self.ir=read(ROOT/'eval_cases/case_001/agent_understanding.json')
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup); self.out=Path(self.temp.name)

    def scene(self,kind=LAYOUTS[0],layout=None):
        # Tests that intentionally modify semantic fixtures simulate a fresh Agent review.
        self.ir['agent_review']['semantic_model_sha256']=semantic_digest(self.ir)
        return build_scene(self.ir,layout or init_layout(self.ir,kind),self.snapshot)

    def xml(self,scene):
        path=self.out/'test.drawio'; xml_tree(scene).write(path,encoding='utf-8',xml_declaration=True); return path

    def observation(self,path,group='composition-1'):
        schema=read(SKILL/'schemas/reference-observation.schema.json')
        unknown=lambda:dict(status='unknown',value=None,note='Not reliably visible')
        data=dict(schema_version='scientific-framework/observation/v1',image_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  composition_group=group,composition_group_status='verified',observer='synthetic-test observer',
                  reusable_principles=['separate-evidence-layer'],do_not_copy_features=['unique module arrangement'],confidence=.7)
        for field in ('visual_style','layout_grammar'):
            data[field]={k:unknown() for k in schema['properties'][field]['properties']}
        for field in ('diagram_type','probable_purpose','reading_path','arrow_semantics','annotation_style','what_makes_it_clear','weaknesses'):
            data[field]=unknown()
        return data

    def image(self,name,color):
        path=self.out/name; Image.new('RGB',(20,20),color).save(path); return path

    def test_all_schemas_are_valid(self):
        from jsonschema import Draft202012Validator
        for path in (SKILL/'schemas').glob('*.json'): Draft202012Validator.check_schema(read(path))

    def test_core_relation_without_source_blocks_approval(self):
        self.ir['relations'][0]['evidence']=[]; self.ir['relations'][0]['source_location']=[]
        q=validate(self.ir,self.snapshot)
        self.assertFalse(q['approval_eligible']); self.assertIn('lacks evidence',' '.join(q['blockers']))
        self.ir['artifact_status']='approved'
        self.assertFalse(validate(self.ir,self.snapshot)['valid'])

    def test_unsupported_cause_blocked_even_noncore(self):
        r=self.ir['relations'][0]; r.update(relation='causes',evidence=[],source_location=[],core=False,needs_review=False)
        q=validate(self.ir,self.snapshot); self.assertIn('causal',' '.join(q['blockers']))

    def test_comparison_kept_nondirectional(self):
        scene=self.scene(); edge=next(e for e in scene['edges'] if e['relation']=='compares_with')
        self.assertFalse(edge['directed']); self.assertFalse(any(e['relation']=='causes' for e in scene['edges']))

    def test_roles_and_no_count_matching(self):
        counts=Counter(n['type'] for n in self.ir['nodes'])
        expected=read(ROOT/'eval_cases/case_001/expected_ir.json')
        for typ,count in expected['node_type_counts'].items(): self.assertEqual(counts[typ],count)
        pairs={(r['source'],r['target']) for r in self.ir['relations']}
        for a,b in expected['forbidden_relation_pairs']: self.assertNotIn((a,b),pairs)
        scene=self.scene()
        self.assertEqual(len(scene['edges']),len(self.ir['relations']))
        self.assertEqual(sum(n['role']=='method' for n in scene['nodes']),5)

    def test_parallel_semantic_edges_not_overwritten(self):
        r=copy.deepcopy(self.ir['relations'][0]); r.update(id='different-same-endpoints',relation='supports')
        self.ir['relations'].append(r)
        scene=self.scene(); edges=[e for e in scene['edges'] if e['source']=='n-c1' and e['target']=='n-m1']
        self.assertEqual(len(edges),2); self.assertEqual({e['relation'] for e in edges},{'uses','supports'})

    def test_expected_and_planned_preserved(self):
        scene=self.scene(); expected=next(n for n in scene['nodes'] if n['id']=='n-output')
        self.assertEqual(expected['statement_status'],'expected')
        tree=xml_tree(scene); self.assertEqual(tree.find('.//mxCell[@id="n-output"]').get('statement_status'),'expected')

    def test_long_chinese_not_truncated(self):
        n=next(n for n in self.scene()['nodes'] if n['id']=='n-c1')
        self.assertGreater(len(n['lines']),1); self.assertEqual(''.join(n['lines']),n['label'])

    def test_xml_special_chars_roundtrip(self):
        scene=self.scene(); path=self.xml(scene); tree=ET.parse(path)
        text=tree.find('.//mxCell[@id="n-c2"]').get('value')
        self.assertIn('<',text); self.assertIn('&',text)
        self.assertTrue(validate_drawio(path,scene)['valid'])

    def test_nested_container_relative_coordinates(self):
        layout=init_layout(self.ir,LAYOUTS[0])
        layout['containers']=[dict(id='outer',label='外层',parent=None,node_ids=['c1']),dict(id='inner',label='内层',parent='outer',node_ids=['c2'])]
        scene=self.scene(layout=layout); path=self.xml(scene); tree=ET.parse(path)
        self.assertEqual(tree.find('.//mxCell[@id="inner"]').get('parent'),'outer')
        self.assertEqual(tree.find('.//mxCell[@id="n-c2"]').get('parent'),'inner')
        self.assertTrue(validate_drawio(path,scene)['valid'])
        self.assertGreaterEqual(float(tree.find('.//mxCell[@id="n-c2"]/mxGeometry').get('x')),0)

    def test_no_cli_fallback_honest(self):
        scene=self.scene(); path=self.xml(scene); m=render(scene,path,self.out,force_fallback=True)
        self.assertEqual(m['backend'],'scene_svg_fallback'); self.assertEqual(m['native_drawio_render'],'skipped')
        self.assertFalse((self.out/'preview.png').exists())
        svg=ET.parse(self.out/'preview.svg'); self.assertEqual(svg.getroot().get('data-backend'),'scene_svg_fallback')

    def test_unknown_observation_not_filled(self):
        path=self.image('one.png','white'); p=profile(path,self.observation(path))
        self.assertIsNone(p['visual_style']['font']['value']); self.assertEqual(p['visual_style']['font']['status'],'unknown')
        bad=self.observation(path); bad['visual_style']['font']['value']='Arial'
        self.assertTrue(schema_errors(bad,'reference-observation'))

    def test_one_image_no_default_promotion(self):
        path=self.image('one.png','white'); style=aggregate([profile(path,self.observation(path))])
        self.assertFalse(style['default_changed']); self.assertEqual(style['patterns'][0]['promotion_status'],'candidate')

    def test_duplicates_variants_do_not_inflate(self):
        a=self.image('a.png','white'); b=self.image('b.png','white'); c=self.image('c.png','blue')
        profiles=[profile(a,self.observation(a,'one')),profile(b,self.observation(b,'two')),profile(c,self.observation(c,'one'))]
        self.assertEqual(aggregate(profiles)['patterns'][0]['independent_composition_count'],1)
        d=self.image('d.png','red'); profiles.append(profile(d,self.observation(d,'three')))
        style=aggregate(profiles); self.assertEqual(style['patterns'][0]['promotion_status'],'promotion_candidate')
        self.assertFalse(style['default_changed'])

    def test_unknown_composition_not_independent(self):
        a=self.image('a.png','white'); o=self.observation(a); o['composition_group_status']='unknown'
        self.assertEqual(aggregate([profile(a,o)])['patterns'][0]['independent_composition_count'],0)

    def test_duplicate_ids_and_dangling_refs(self):
        self.ir['nodes'][1]['id']=self.ir['nodes'][0]['id']
        self.assertFalse(validate(self.ir,self.snapshot)['valid'])

    def test_source_quote_and_location_mismatch(self):
        self.ir['nodes'][0]['source_text']=['Not in original']
        self.ir['nodes'][1]['source_location'][0]['line_start']=100
        q=validate(self.ir,self.snapshot); self.assertFalse(q['valid'])
        self.assertIn('quote mismatch',' '.join(q['errors'])); self.assertIn('inaccurate location',' '.join(q['errors']))

    def test_review_draft_allowed_approved_blocked(self):
        self.assertTrue(validate(self.ir,self.snapshot)['valid'])
        self.assertFalse(validate(self.ir,self.snapshot)['approval_eligible'])
        self.ir['artifact_status']='approved'; self.assertFalse(validate(self.ir,self.snapshot)['valid'])

    def test_layout_cannot_override_semantics_or_status(self):
        l=init_layout(self.ir,LAYOUTS[0]); l['artifact_status']='approved'
        with self.assertRaises(ValueError): self.scene(layout=l)
        l=init_layout(self.ir,LAYOUTS[0]); l['nodes']=[{'label':'invented'}]
        with self.assertRaises(ValueError): self.scene(layout=l)

    def test_progress_not_mechanism(self):
        r=self.ir['relations'][0]; r['source']='progress'; r['relation']='influences'
        self.assertIn('progress used',' '.join(validate(self.ir,self.snapshot)['blockers']))

    def test_no_geometry_in_ir(self):
        self.ir['nodes'][0]['x']=100
        self.assertFalse(validate(self.ir,self.snapshot)['valid'])

    def test_xml_control_character_rejected(self):
        self.ir['nodes'][0]['label']+='\x01'
        with self.assertRaises(ValueError): self.scene()

    def test_all_three_layouts_executable(self):
        for kind in LAYOUTS:
            scene=self.scene(kind); self.assertEqual(len(scene['nodes']),len(self.ir['nodes']))
            self.assertTrue(validate_drawio(self.xml(scene),scene)['valid'])

    def test_simple_docx_body_and_table(self):
        path=self.out/'simple.docx'
        xml='<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>正文中文</w:t></w:r></w:p><w:tbl><w:tr><w:tc><w:p><w:r><w:t>表格中文</w:t></w:r></w:p></w:tc></w:tr></w:tbl></w:body></w:document>'
        with zipfile.ZipFile(path,'w') as z: z.writestr('word/document.xml',xml)
        s=extract(path); self.assertEqual([p['text'] for p in s['segments']],['正文中文','表格中文'])
        self.assertEqual(s['segments'][1]['location'],dict(table_index=1,row_index=1,cell_index=1))
        self.assertTrue(s['warnings'])

    def test_docx_revisions_refused(self):
        path=self.out/'revision.docx'
        xml='<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:ins/></w:p></w:body></w:document>'
        with zipfile.ZipFile(path,'w') as z: z.writestr('word/document.xml',xml)
        with self.assertRaises(ValueError): extract(path)

    def test_markdown_line_and_heading_positions(self):
        path=self.out/'p.md'; path.write_text('# 标题\n\n研究文本\n',encoding='utf-8')
        s=extract(path); self.assertEqual(s['segments'][1]['location']['line_start'],3)
        self.assertEqual(s['segments'][1]['heading_path'],['标题'])

    def test_xml_edit_requires_scene_review(self):
        scene=self.scene(); path=self.xml(scene); tree=ET.parse(path)
        tree.find('.//mxCell[@id="n-c1"]').set('value','Altered science'); tree.write(path,encoding='utf-8')
        self.assertFalse(validate_drawio(path,scene)['valid'])

    def test_container_cycle_and_missing_parent_rejected(self):
        l=init_layout(self.ir,LAYOUTS[0]); l['containers']=[dict(id='loop',label='loop',parent='loop',node_ids=['c1'])]
        with self.assertRaises(ValueError): self.scene(layout=l)

    def test_contains_cycle_rejected(self):
        a=copy.deepcopy(self.ir['relations'][0]); a.update(id='contains-1',source='c1',target='c2',relation='contains')
        b=copy.deepcopy(a); b.update(id='contains-2',source='c2',target='c1')
        self.ir['relations'] += [a,b]
        self.assertIn('contains hierarchy cycle',validate(self.ir,self.snapshot)['errors'])

    def test_stale_ir_snapshot_refused(self):
        l=init_layout(self.ir,LAYOUTS[0]); self.ir['nodes'][0]['short_label']='changed'
        with self.assertRaises(ValueError): self.scene(layout=l)

    def test_missing_core_node_source_fails(self):
        self.ir['nodes'][0]['source_location']=[]
        self.assertFalse(validate(self.ir,self.snapshot)['valid'])

    def test_negative_xml_geometry(self):
        path=self.xml(self.scene()); tree=ET.parse(path)
        tree.find('.//mxCell[@id="n-c1"]/mxGeometry').set('width','-10'); tree.write(path,encoding='utf-8')
        self.assertIn('invalid geometry',' '.join(structural_check(path)))

    def test_semantic_change_invalidates_agent_review(self):
        self.ir['nodes'][1]['type']='method'
        self.assertIn('Semantic model changed',' '.join(validate(self.ir,self.snapshot)['errors']))

    def test_output_status_change_invalidates_review(self):
        next(n for n in self.ir['nodes'] if n['id']=='output')['statement_status']='reported'
        self.assertFalse(validate(self.ir,self.snapshot)['valid'])

    def test_reserved_container_ids_rejected(self):
        l=init_layout(self.ir,LAYOUTS[0]); l['containers']=[dict(id='0',label='bad',parent=None,node_ids=['c1'])]
        with self.assertRaises(ValueError): self.scene(layout=l)

if __name__=='__main__': unittest.main()
