"""Explicit unknown-glyph treatment retains low confidence, never promotes it."""
import json
from pathlib import Path
import unittest
import yaml
from test_enoch_bounded_application import fixture
from tools.enoch import bounded_application as t

class CriticalConfidenceTest(unittest.TestCase):
    def critical(self,package,manifest,repin):
        path=package/'001-001.candidate.yaml';candidate=yaml.safe_load(path.read_text())
        candidate['source'].update(text='መ⟦?⟧ትከ',confidence='low',note='POB-added unknown span, not Charles print.',transcription_uncertainties=[{'marker':'⟦?⟧','status':'unresolved'}])
        candidate['translation'].update(text='A provisional fixture.[a]',footnotes=[{'marker':'a','text':'Fixture meaning is provisional; unknown span remains.', 'reason':'textual_variant'}])
        candidate['enoch_witnesses']['available_witnesses'][0]['text']=candidate['source']['text']
        for role in ('author','independent_reviewer'):
            inp=package/f'{role}-input.json';rows=json.loads(inp.read_text());rows[0]['source']=candidate['source'];rows[0]['translation']=candidate['translation'];inp.write_text(json.dumps(rows))
            pv=package/f'{role}-provenance.json';d=json.loads(pv.read_text());d['input_sha256']=t.sha(inp.read_bytes());pv.write_text(json.dumps(d))
        path.write_text(yaml.safe_dump(candidate,allow_unicode=True));repin();return candidate,path

    def test_exact_accepted_low_confidence_treatment_can_pass_without_certifying_glyphs(self):
        with fixture() as (p,_,m,repin):
            self.critical(p,m,repin)
            result=t.verify(p)
            self.assertEqual(result['candidate_files'],1)
            self.assertFalse(result['full_book_verified'])

    def test_low_to_medium_promotion_is_rejected_even_after_outer_repin(self):
        with fixture() as (p,_,m,repin):
            d,path=self.critical(p,m,repin);d['source']['confidence']='medium';path.write_text(yaml.safe_dump(d,allow_unicode=True));repin()
            with self.assertRaisesRegex(ValueError,'differs from accepted'):t.verify(p)

    def test_unknown_source_explanation_cannot_be_erased(self):
        with fixture() as (p,_,m,repin):
            d,path=self.critical(p,m,repin);d['source']['note']='Unqualified reading';path.write_text(yaml.safe_dump(d,allow_unicode=True));repin()
            with self.assertRaisesRegex(ValueError,'uncertainty/explanation controls'):t.verify(p)

    def test_critical_treatment_requires_structured_unknown_span(self):
        with fixture() as (p,_,m,repin):
            d,path=self.critical(p,m,repin);del d['source']['transcription_uncertainties'];path.write_text(yaml.safe_dump(d,allow_unicode=True));repin()
            with self.assertRaisesRegex(ValueError,'uncertainty/explanation controls'):t.verify(p)

    def test_critical_treatment_requires_exact_explanation_definition(self):
        with fixture() as (p,_,m,repin):
            d,path=self.critical(p,m,repin);d['translation']['text']='A provisional fixture.';d['translation']['footnotes']=[];path.write_text(yaml.safe_dump(d,allow_unicode=True));repin()
            with self.assertRaisesRegex(ValueError,'uncertainty/explanation controls'):t.verify(p)

if __name__=='__main__':unittest.main()
