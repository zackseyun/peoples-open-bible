"""Explicit source identity and immutable input checks precede model review."""
import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
from tools.hermas import review_repair_draft as review

ROOT=Path(__file__).resolve().parents[1]

def paths(n):
    return [ROOT/folder/'extra_canonical/shepherd_of_hermas'/f'{n:03d}.yaml' for folder in ['translation','translation_simplified']]


class RepairReviewTests(unittest.TestCase):
    def test_legacy_reader_does_not_select_source_by_current_sequence(self):
        docs,manifest=review.load_pair(*paths(35))
        self.assertEqual(docs[0]['source']['unit_id'],'M.8')
        self.assertEqual(docs[0]['source']['sequence'],38)
        self.assertEqual(manifest[0]['path'],'translation/extra_canonical/shepherd_of_hermas/035.yaml')
        body,_=review.prepare(*paths(35))
        self.assertEqual(body['model'],review.DEPLOYMENT)
        self.assertEqual(json.loads(body['messages'][1]['content'])['source']['unit_id'],'M.8')

    def test_compound_review_covers_both_historical_sections(self):
        docs,_=review.load_pair(*paths(31))
        self.assertEqual([s['unit_id'] for s in docs[0]['source']['source_unit_spans']],['M.4.iii','M.4.iv'])
        self.assertIn('Ἠρώτησα',docs[0]['source']['text'])
        with self.assertRaisesRegex(ValueError,'source scopes'):
            review.load_pair(paths(31)[0],paths(35)[1])

    def test_changed_base_or_source_cannot_be_submitted(self):
        original=Path.read_bytes
        for field in ['source','base_translation']:
            def changed(path):
                raw=original(path)
                if path==paths(35)[1]:
                    import yaml
                    doc=yaml.safe_load(raw);doc[field]['text']+=' changed'
                    return yaml.safe_dump(doc,allow_unicode=True).encode()
                return raw
            with patch.object(Path,'read_bytes',changed):
                with self.assertRaises(ValueError):review.load_pair(*paths(35))

    def test_acceptance_requires_complete_checks_and_exact_findings(self):
        docs,_=review.load_pair(*paths(35))
        good=dict(summary='Separate model review.',editions=[dict(edition=e,verdict='accept',checks={c:True for c in review.CHECKS},findings=[]) for e in ['standard','simplified']])
        review.validate_result(good,docs)
        bad=copy.deepcopy(good);bad['editions'][0]['checks']['complete_coverage']=False
        with self.assertRaisesRegex(ValueError,'contradicts'):review.validate_result(bad,docs)
        bad=copy.deepcopy(good);bad['editions'][0].update(verdict='revise',findings=[dict(source_quote='invented Greek',english_quote='',issue='omission',suggested_revision='change',severity='major')])
        with self.assertRaisesRegex(ValueError,'source quote'):review.validate_result(bad,docs)
        bad=copy.deepcopy(good);bad['editions'][0].update(verdict='revise',findings=[dict(source_quote='ῥήματα δικαιοσύνης',english_quote='invented metadata',issue='bad note',suggested_revision='change',severity='minor')])
        with self.assertRaisesRegex(ValueError,'text or metadata'):review.validate_result(bad,docs)
        bad['editions'][0]['findings'][0]['english_quote']=docs[0]['lexical_decisions'][0]['rationale']
        review.validate_result(bad,docs)


if __name__=='__main__':unittest.main()
