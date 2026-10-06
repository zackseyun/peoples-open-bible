import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

from tools import export_mobile_bible as exporter

ROOT = Path(__file__).resolve().parents[1]


class ReaderFootnoteExportTests(unittest.TestCase):
    def test_deuteronomy_27_4_discloses_versional_gerizim_without_priority_claim(self):
        packet = json.loads((ROOT / 'sources/textual_restoration/applications/deuteronomy27_4_disclosure.2026-10-06.v1.json').read_text())
        raw = (ROOT / packet['target']).read_bytes()
        record = yaml.safe_load(raw)
        candidate = json.loads((ROOT / packet['candidate']).read_bytes())
        self.assertEqual(record, candidate)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), packet['application']['yaml_sha256'])
        self.assertEqual(record['status'], 'draft')
        self.assertEqual(record['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', record)
        history = {item['field']: item for item in record['review_history']}
        self.assertEqual(set(history), {'status', 'revision_pass', 'cross_check',
                                       'translation.footnotes', 'theological_decisions'})
        self.assertTrue(all(not item['certifies_this_candidate'] for item in history.values()))
        self.assertTrue(all(item['archived_from_baseline_sha256'] == packet['baseline_sha256']
                            for item in history.values()))
        self.assertTrue(all(history[field]['historical_review_inputs_verified'] is False
                            for field in ('status', 'revision_pass', 'cross_check')))
        self.assertEqual(record['source'], packet['baseline_source'])
        self.assertEqual(record['ai_draft'], packet['baseline_generation'])
        self.assertEqual(record['translation']['text'], packet['baseline_english'])
        self.assertIn('Mount Ebal[a]', record['translation']['text'])
        self.assertEqual(record['translation']['text'].count('[a]'), 1)
        notes = record['translation']['footnotes']
        self.assertEqual([note['marker'] for note in notes], ['a'])
        self.assertEqual(notes[0]['reason'], 'textual_variant')
        for detail in ('selected Rahlfs', 'Samaritan Pentateuch', 'Giessen Greek',
                       'supplied letter', 'uncertainty in the opening', 'VL100', 'Garzin',
                       'relationships', 'came first remain uncertain', '4Q33',
                       'wholly reconstructed', 'supporting neither reading'):
            self.assertIn(detail, notes[0]['text'])
        out = exporter._export_record_verse(4, record)
        self.assertEqual(out['text'], record['translation']['text'])
        self.assertEqual(out['footnotes'], notes)
        self.assertFalse(packet['decision']['source_changed'])
        self.assertFalse(packet['decision']['main_english_changed'])
        self.assertFalse(packet['decision']['historical_priority_settled'])
        self.assertFalse(packet['decision']['novel_reading_demonstrated'])
        self.assertFalse(packet['decision']['publication_approved'])

    def test_samuel_24_13_discloses_greek_numeral_without_settling_priority(self):
        packet = json.loads((ROOT / 'sources/textual_restoration/applications/samuel24_13_disclosure.2026-10-06.v1.json').read_text())
        raw = (ROOT / packet['target']).read_bytes()
        record = yaml.safe_load(raw)
        candidate = json.loads((ROOT / packet['candidate']).read_bytes())
        self.assertEqual(record, candidate)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), packet['application']['yaml_sha256'])
        self.assertEqual(record['status'], 'draft')
        self.assertEqual(record['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', record)
        history = {item['field']: item for item in record['review_history']}
        self.assertTrue(all(item['certifies_this_candidate'] is False for item in history.values()))
        strip_markers = lambda text: text.replace('[a]', '').replace('[b]', '').replace('[c]', '')
        text = record['translation']['text']
        self.assertEqual(strip_markers(text), strip_markers(history['translation.text']['value']))
        for phrase in ('seven years of famine[a]', 'your adversaries[b]', 'pestilence[c]'):
            self.assertIn(phrase, text)
        for marker in 'abc':
            self.assertEqual(text.count(f'[{marker}]'), 1)
        notes = record['translation']['footnotes']
        self.assertEqual(notes[1:], history['translation.footnotes']['value'][1:])
        for detail in ('seven years', 'Cambridge', 'Rahlfs–Hanhart', 'three years',
                       '1 Chronicles 21:12', 'remains uncertain'):
            self.assertIn(detail, notes[0]['text'])
        out = exporter._export_record_verse(13, record)
        self.assertEqual(out['text'], text)
        self.assertEqual(out['footnotes'], notes)
        self.assertFalse(packet['decision']['historical_priority_settled'])
        self.assertFalse(packet['decision']['source_changed'])
        self.assertFalse(packet['decision']['main_english_words_changed'])
        self.assertFalse(packet['decision']['publication_approved'])

    def test_proverbs_24_5_discloses_only_the_comparative_first_clause(self):
        packet = json.loads((ROOT / 'sources/textual_restoration/applications/proverbs24_5_disclosure.2026-10-05.v1.json').read_text())
        raw = (ROOT / packet['target']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), packet['application']['applied_yaml_sha256'])
        record = yaml.safe_load(raw)
        self.assertEqual(record['translation']['text'],
                         'A wise man is strong[a], and a man of knowledge increases strength[b].')
        notes = record['translation']['footnotes']
        self.assertEqual([n['marker'] for n in notes], ['a', 'b'])
        self.assertEqual(notes[0]['reason'], 'textual_variant')
        self.assertTrue(notes[0]['text'].startswith('The Hebrew is compact, literally,'))
        self.assertIn('In this clause, Greek and Syriac', notes[0]['text'])
        self.assertIn('different Hebrew reading or interpretation', notes[0]['text'])
        self.assertIn('which Hebrew wording came first remains uncertain', notes[0]['text'])
        self.assertEqual(notes[1], {'marker': 'b', 'text': 'Or “makes power strong.”',
                                  'reason': 'lexical_alternative'})
        self.assertEqual(record['source']['edition'], 'WLC')
        self.assertEqual(record['status'], 'draft')
        self.assertEqual(record['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('source_audit', record)
        archives = {h['field']: h for h in record['review_history']}
        self.assertEqual(set(archives), {'status', 'revision_pass', 'cross_check', 'source_audit'})
        self.assertEqual(archives['cross_check']['value']['agreement_score'], 0.95)
        self.assertEqual(record['revisions'][-1]['from'], record['revisions'][-1]['to'])
        book = exporter.export_book('PRO')
        self.assertEqual(len(book['chapters']), 31)
        self.assertEqual(sum(len(c['verses']) for c in book['chapters']), 915)
        verse = next(v for c in book['chapters'] if c['chapter'] == 24
                     for v in c['verses'] if v['verse'] == 5)
        self.assertEqual(verse['text'], record['translation']['text'])
        self.assertEqual(verse['footnotes'], notes)

    def test_ecclesiastes_particle_notes_preserve_main_wording_and_disclose_limits(self):
        expected = {
            (5, 14): (
                '8baaa514de9d861b2853a71eafa4ec956af336494dc541079f4fdc40b037416d',
                'As he came from his mother’s womb, naked he will return, going as he came; and he will carry away nothing from his labor that he can take in his hand.',
                'As[b] he',
                ('editorially supplied', 'earlier wording and function remain uncertain'),
            ),
            (6, 8): (
                '7b460d17c6704354252a91a966a5157f69edcca8cb961adeed2882b5d569777d',
                'For what advantage does the wise man have over the fool? What advantage does the poor man have who knows how to conduct himself before the living?',
                'the fool[b]?',
                ('supplied or unidentified', 'admits an assertion', 'added question word',
                 'Neither construction uniquely recovers Hebrew', 'earlier wording and function remain unresolved'),
            ),
        }
        book = exporter.export_book('ECC')
        self.assertEqual(len(book['chapters']), 12)
        self.assertEqual(sum(len(c['verses']) for c in book['chapters']), 222)
        for (chapter, number), (sha, plain, anchor, limits) in expected.items():
            with self.subTest(chapter=chapter, verse=number):
                raw = (ROOT / f'translation/ot/ecclesiastes/{chapter:03}/{number:03}.yaml').read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), sha)
                record = yaml.safe_load(raw)
                verse = next(v for c in book['chapters'] if c['chapter'] == chapter
                             for v in c['verses'] if v['verse'] == number)
                self.assertEqual(verse['text'], record['translation']['text'])
                self.assertEqual(verse['footnotes'], record['translation']['footnotes'])
                self.assertEqual(verse['text'].replace('[a]', '').replace('[b]', ''), plain)
                self.assertIn(anchor, verse['text'])
                notes = {n['marker']: n for n in verse['footnotes']}
                self.assertEqual(set(notes), {'a', 'b'})
                self.assertEqual(notes['b']['reason'], 'textual_variant')
                for phrase in limits:
                    self.assertIn(phrase, notes['b']['text'])
                for marker in notes:
                    self.assertEqual(verse['text'].count(f'[{marker}]'), 1)
                self.assertEqual(record['status'], 'draft')
                self.assertEqual(record['cross_check'], {'status': 'needs_review'})
                self.assertNotIn('source_audit', record)
                archives = {h['field']: h for h in record['review_history']}
                self.assertEqual(archives['status']['value'], 'revised')
                self.assertEqual(archives['cross_check']['value']['status'], 'high_agreement')
                self.assertFalse(archives['cross_check']['historical_review_inputs_verified'])
                self.assertEqual(len(record['revisions']), 4)
                self.assertEqual(record['revisions'][-1]['category'], 'footnotes')

    def test_ecclesiastes_7_5_preserves_explicit_generic_listener_and_qualified_scroll_note(self):
        raw = (ROOT / 'translation/ot/ecclesiastes/007/005.yaml').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         '04251412b26caea560bfff6576f1f7060764412727b0009fb53c3405ec8252f0')
        record = yaml.safe_load(raw)
        history = record['textual_comparison_history'][0]
        self.assertEqual(record['source'], history['source'])
        self.assertEqual(record['status'], 'draft')
        self.assertEqual(record['cross_check'], {'status': 'needs_review'})
        self.assertEqual(record['revisions'][-2]['from'], record['revisions'][-2]['to'])
        packet = json.loads((ROOT / 'sources/textual_restoration/applications/ecclesiastes7_5_listener.2026-10-05.v1.json').read_text())
        self.assertEqual(record['translation']['text'].replace('[a]', '').replace('[b]', ''),
                         packet['english_comparison']['candidates']['B'])
        self.assertTrue(packet['english_comparison']['candidate_identity_withheld'])
        self.assertFalse(packet['english_comparison']['randomized_order'])
        book = exporter.export_book('ECC')
        self.assertEqual(len(book['chapters']), 12)
        self.assertEqual(sum(len(c['verses']) for c in book['chapters']), 222)
        verse = next(v for c in book['chapters'] if c['chapter'] == 7
                     for v in c['verses'] if v['verse'] == 5)
        self.assertEqual(verse['text'], record['translation']['text'])
        self.assertEqual(verse['footnotes'], record['translation']['footnotes'])
        self.assertIn('rebuke[a]', verse['text'])
        self.assertIn('for a man[b] to hear', verse['text'])
        self.assertIn('comparative prefix', verse['footnotes'][0]['text'])
        self.assertIn('crossed-out characters are unidentified', verse['footnotes'][0]['text'])
        self.assertIn('not necessarily a different person', verse['footnotes'][1]['text'])

    def test_ecclesiastes_scroll_verb_disclosures_preserve_source_and_main_wording(self):
        expected = {
            7: ('3eefe19504ce3082b4c67a91ff52b5cfce85aac6586322c621578d4a35e3cf2c',
                'For oppression makes a wise man foolish, and a bribe destroys the heart.'),
            19: ('2695e9b80ec012307e2d62782fd7abf34f7f8e21e49ff5036f50397a5987f3a8',
                 'Wisdom gives a wise man more strength than ten rulers in the city.'),
        }
        book = exporter.export_book('ECC')
        self.assertEqual(len(book['chapters']), 12)
        self.assertEqual(sum(len(c['verses']) for c in book['chapters']), 222)
        for number, (sha, plain) in expected.items():
            raw = (ROOT / f'translation/ot/ecclesiastes/007/{number:03}.yaml').read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), sha)
            record = yaml.safe_load(raw)
            verse = next(v for c in book['chapters'] if c['chapter'] == 7
                         for v in c['verses'] if v['verse'] == number)
            self.assertEqual(verse['text'], record['translation']['text'])
            self.assertEqual(verse['footnotes'], record['translation']['footnotes'])
            text = verse['text']
            for note in verse['footnotes']:
                self.assertEqual(text.count(f"[{note['marker']}]"), 1)
                text = text.replace(f"[{note['marker']}]", '')
            self.assertEqual(text, plain)
            self.assertEqual(record['cross_check'], {'status': 'needs_review'})
            self.assertEqual(record['status'], 'draft')
        seven = next(v for c in book['chapters'] if c['chapter'] == 7
                     for v in c['verses'] if v['verse'] == 7)
        self.assertIn('destroys[c] the heart[b].', seven['text'])
        self.assertIn('final letter doubtful', seven['footnotes'][2]['text'])
        self.assertIn('not surviving words', seven['footnotes'][2]['text'])
        nineteen = next(v for c in book['chapters'] if c['chapter'] == 7
                        for v in c['verses'] if v['verse'] == 19)
        self.assertIn('strength[a]', nineteen['text'])
        self.assertIn('reported as preserved', nineteen['footnotes'][0]['text'])
        self.assertIn('partly supplied or damaged', nineteen['footnotes'][0]['text'])
        self.assertIn('earliest wording remains unresolved', nineteen['footnotes'][0]['text'])

    def test_malachi_2_16_discloses_conditional_interpretation_and_preserves_hebrew(self):
        candidate = ROOT / 'sources/textual_restoration/applications/mal2_16_candidate.2026-10-05.v1.yaml'
        canonical = ROOT / 'translation/ot/malachi/002/016.yaml'
        raw = candidate.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         '92d227e38138412ac8354a0fd45053780af06f0101de09dc8711cf4cc220df14')
        self.assertEqual(canonical.read_bytes(), raw)
        record = yaml.safe_load(raw)
        history = record['textual_comparison_history'][-1]
        self.assertEqual(record['source'], history['source'])
        self.assertEqual(record['ai_draft']['output_hash'],
                         '62c9ce007a90dd4dde0c0a084e33dd899974ed1ee6dde98d821ec05d40aca277')
        self.assertEqual(record['cross_check'], {'status': 'needs_review'})
        self.assertEqual(record['status'], 'draft')
        self.assertTrue(record['textual_adjudication']['source_interpretation_changed'])
        packet = json.loads((ROOT / 'sources/textual_restoration/applications/mal2_16_english_comparison.2026-10-05.v1.json').read_text())
        text = record['translation']['text']
        for marker in ('a', 'b', 'c', 'd'):
            text = text.replace(f'[{marker}]', '')
        self.assertEqual(text, packet['candidates']['A'])
        book = exporter.export_book('MAL')
        self.assertEqual(len(book['chapters']), 3)
        self.assertEqual(sum(len(c['verses']) for c in book['chapters']), 55)
        verse = next(v for c in book['chapters'] if c['chapter'] == 2
                     for v in c['verses'] if v['verse'] == 16)
        self.assertEqual(verse['text'], record['translation']['text'])
        self.assertEqual(verse['footnotes'], record['translation']['footnotes'])
        notes = {n['marker']: n for n in verse['footnotes']}
        self.assertEqual(notes['b'], history['translation']['footnotes'][1])
        self.assertIn('faithlessly[b]', verse['text'])
        self.assertNotIn('spirit[b]', verse['text'])
        self.assertIn('construction is disputed', notes['a']['text'])
        self.assertIn("'Her' is supplied", notes['a']['text'])
        self.assertIn('ending is doubtful', notes['c']['text'])
        self.assertIn('not newly deciphered letters', notes['c']['text'])
        self.assertIn('another interpretation makes divorce', notes['d']['text'])

    def test_zechariah_12_10_preserves_person_shift_and_disputed_syntax(self):
        candidate = ROOT / 'sources/textual_restoration/applications/zech12_10_candidate.2026-10-04.v1.yaml'
        canonical = ROOT / 'translation/ot/zechariah/012/010.yaml'
        raw = candidate.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         '7a463ed5ad57c1159db46ae1fd94221a4514968eb51e3bf23563f4d4673e7128')
        self.assertEqual(canonical.read_bytes(), raw)
        record = yaml.safe_load(raw)
        historical = record['textual_comparison_history'][-1]
        self.assertEqual(record['source'], historical['source'])
        self.assertEqual(record['status'], 'draft')
        self.assertEqual(record['cross_check'], {'status': 'needs_review'})
        packet = json.loads((ROOT / 'sources/textual_restoration/applications/zech12_10_english_comparison.2026-10-04.v1.json').read_text())
        marker_free = record['translation']['text']
        for marker in ('a', 'b', 'c', 'd', 'e'):
            marker_free = marker_free.replace(f'[{marker}]', '')
        self.assertEqual(marker_free, packet['candidates']['B'])
        self.assertNotIn('the one whom', marker_free)
        book = exporter.export_book('ZEC')
        self.assertEqual([c['chapter'] for c in book['chapters']], list(range(1, 15)))
        self.assertEqual(sum(len(c['verses']) for c in book['chapters']), 211)
        verse = next(v for c in book['chapters'] if c['chapter'] == 12
                     for v in c['verses'] if v['verse'] == 10)
        self.assertEqual(verse['text'], record['translation']['text'])
        self.assertEqual(verse['footnotes'], record['translation']['footnotes'])
        for phrase in ('pleas for mercy[c]', 'look to me[a]',
                       'whom they pierced[d][e]', 'mourn for him[b]'):
            self.assertIn(phrase, verse['text'])
        notes = {n['marker']: n for n in verse['footnotes']}
        for original in historical['translation']['footnotes']:
            self.assertEqual(notes[original['marker']], original)
        self.assertIn('concerning the one they pierced', notes['d']['text'])
        self.assertIn('construction is disputed', notes['d']['text'])
        self.assertIn("only the ending 'רו'", notes['e']['text'])
        self.assertIn('are supplied', notes['e']['text'])
        self.assertIn('not newly deciphered letters', notes['e']['text'])

    def test_deuteronomy_32_43_distinguishes_forms_and_samaritan_closing(self):
        candidate = ROOT / 'sources/textual_restoration/applications/deut32_43_disclosure_candidate.2026-10-04.v1.yaml'
        canonical = ROOT / 'translation/ot/deuteronomy/032/043.yaml'
        raw = candidate.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         '83bb71136c7e5cf16f6624b9d304f216dedf3cd63261ac2ad6b79afb58cb69c4')
        self.assertEqual(canonical.read_bytes(), raw)
        record = yaml.safe_load(raw)
        historical = record['textual_comparison_history'][-1]
        self.assertEqual(record['source'], historical['source'])
        self.assertEqual(record['translation']['text'].replace('[e]', ''),
                         historical['translation']['text'])
        self.assertEqual(record['status'], 'draft')
        self.assertEqual(record['cross_check'], {'status': 'needs_review'})
        book = exporter.export_book('DEU')
        chapter = next(c for c in book['chapters'] if c['chapter'] == 32)
        verse = next(v for v in chapter['verses'] if v['verse'] == 43)
        self.assertEqual(verse['text'], record['translation']['text'])
        self.assertEqual(verse['footnotes'], record['translation']['footnotes'])
        notes = {n['marker']: n for n in verse['footnotes']}
        for phrase in ('six poetic lines', 'eight-line form', 'Psalm 97:7',
                       'Deuteronomy 32:41', 'earliest wording is unresolved',
                       'not newly restored letters'):
            self.assertIn(phrase, notes['c']['text'])
        for phrase in ('“and” is supplied', 'Samaritan Pentateuch',
                       'the land of his people', 'different verbal form',
                       'does not establish priority for the entire verse'):
            self.assertIn(phrase, notes['e']['text'])
        for note in historical['translation']['footnotes']:
            if note['marker'] != 'c':
                self.assertEqual(notes[note['marker']], note)

    def test_tobit_fish_connected_greek_form_and_disclosures_reach_reader(self):
        pins = {
            1: 'e5e4a2116e2d72eac276f7c4fc6387465660198134cf599fea6b73484facf12e',
            2: 'c0ae9a43f43fb515df5b3eb04a13b173a1eb65a3c23ac4358328b558bf78a346',
            3: '4abf3218d792b532ef67809195b4717e49c06a6a32e1156ef4ae52c41d0e5153',
            4: 'f7e58c0168a7c328352bf2a4f8f56e02305fc2fbe0702b6535498b2666ca3b84',
            5: '2b1c8ff4a309e2e11bcc8288ddd47cace0ae498fbcbcf1171d40eac82a022609',
            6: '8f185387df336d12eb49b55d5e39cc28c0ee1689730e5d6e4f40dddf0bd055de',
        }
        book = exporter.export_apocrypha_book('TOB')
        chapter = next(c for c in book['chapters'] if c['chapter'] == 6)
        self.assertEqual([v['verse'] for v in chapter['verses']], list(range(1, 19)))
        reader = {v['verse']: v for v in chapter['verses']}
        records = {}
        for verse, pin in pins.items():
            candidate = ROOT / f'sources/textual_restoration/applications/tobit6_{verse}_candidate.2026-10-04.v1.yaml'
            canonical = ROOT / f'translation/deuterocanon/tobit/006/{verse:03}.yaml'
            raw = candidate.read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), pin)
            self.assertEqual(canonical.read_bytes(), raw)
            record = yaml.safe_load(raw)
            records[verse] = record
            self.assertEqual(reader[verse]['text'], record['translation']['text'])
            self.assertEqual(reader[verse]['footnotes'], record['translation']['footnotes'])
            self.assertEqual(record['status'], 'draft')
            self.assertEqual(record['cross_check'], {'status': 'needs_review'})
            historical = record['textual_comparison_history'][-1]
            if verse < 3:
                self.assertEqual(record['source']['text'], historical['source']['text'])
                self.assertEqual(record['translation']['text'], historical['translation']['text'])
            else:
                self.assertEqual(record['source']['literary_form'], 'Greek II, Swete lower Sinaiticus text')
                self.assertIn('not restored Aramaic', record['source']['note'])
        self.assertIn('wanted to swallow the young man’s foot[a]', reader[3]['text'])
        self.assertIn('young man cried out', reader[3]['text'])
        self.assertIn('swallowing verb is only partly preserved', reader[3]['footnotes'][0]['text'])
        self.assertIn('earliest wording is unresolved', reader[3]['footnotes'][0]['text'])
        self.assertIn('get a firm grip on it[a]', reader[4]['text'])
        self.assertIn('brought it up onto the land', reader[4]['text'])
        self.assertIn('gall[a]', reader[5]['text'])
        self.assertIn('medicine[b]', reader[5]['text'])
        self.assertIn('He roasted some of the fish and ate it[a]', reader[6]['text'])
        self.assertIn('set aside some of it, salted', reader[6]['text'])
        self.assertIn('came near Media[b]', reader[6]['text'])
        self.assertIn('conditionally supporting the singular', reader[6]['footnotes'][0]['text'])
        self.assertIn('not a continuous Sinaiticus edition', reader[2]['footnotes'][0]['text'])

    def test_habakkuk_2_4_discloses_suffix_and_lexical_choices_separately(self):
        path = ROOT / 'translation/ot/habakkuk/002/004.yaml'
        candidate_path = ROOT / 'sources/textual_restoration/applications/habakkuk2_4_disclosure_candidate.2026-10-04.v1.yaml'
        candidate_bytes = candidate_path.read_bytes()
        self.assertEqual(hashlib.sha256(candidate_bytes).hexdigest(),
                         '81940940f5823cc6c6e4aa515bd3d025e32c702d71c445f169c070f2ca8d2776')
        self.assertEqual(path.read_bytes(), candidate_bytes)
        record = yaml.safe_load(path.read_text())
        self.assertEqual(record['source'], {
            'edition': 'WLC',
            'text': 'הִנֵּ֣ה עֻפְּלָ֔ה לֹא יָשְׁרָ֥ה נַפְשׁ֖/וֹ בּ֑/וֹ וְ/צַדִּ֖יק בֶּ/אֱמוּנָת֥/וֹ יִחְיֶֽה־׃',
        })
        text = record['translation']['text']
        self.assertEqual(text.replace('[a]', '').replace('[b]', ''),
                         'Look: his soul is puffed up; it is not upright within him, but the righteous will live by his faithfulness.')
        self.assertIn('his[a] faithfulness[b]', text)
        self.assertEqual(text.count('[a]'), 1)
        self.assertEqual(text.count('[b]'), 1)
        out = exporter._export_record_verse(4, record)
        self.assertEqual(out['text'], text)
        self.assertEqual(out['footnotes'], record['translation']['footnotes'])
        notes = {note['marker']: note for note in out['footnotes']}
        self.assertEqual(notes['a']['reason'], 'textual_variant')
        for detail in ('Masoretic Hebrew', 'my faith/faithfulness', '1QpHab',
                       'Mur 88', '4Q82', 'editorially restored, not preserved',
                       'earliest wording is unresolved'):
            self.assertIn(detail, notes['a']['text'])
        self.assertEqual(notes['b']['reason'], 'lexical_alternative')
        for detail in ('his faith', 'his trust', 'steadfast fidelity'):
            self.assertIn(detail, notes['b']['text'])
        self.assertEqual(record['status'], 'draft')
        self.assertEqual(record['cross_check'], {'status': 'needs_review'})

    def test_psalm145_nun_line_and_repeated_colon_disclosures_reach_reader(self):
        thirteen = yaml.safe_load((ROOT / 'translation/ot/psalms/145/013.yaml').read_text())
        seventeen = yaml.safe_load((ROOT / 'translation/ot/psalms/145/017.yaml').read_text())
        self.assertEqual(thirteen['source']['edition'], 'POB-critical')
        self.assertEqual(seventeen['source']['edition'], 'WLC')
        self.assertIn('God is faithful in his words and loyal[c] in all his deeds[b]', thirteen['translation']['text'])
        self.assertIn('loyal in all his deeds[a]', seventeen['translation']['text'])
        for v, record in [(13, thirteen), (17, seventeen)]:
            out = exporter._export_record_verse(v, record)
            self.assertEqual(out['footnotes'], record['translation']['footnotes'])
        source_note = next(n for n in thirteen['translation']['footnotes'] if n['marker'] == 'b')
        self.assertIn('earliest wording is unresolved', source_note['text'])
        self.assertIn('Masoretic Text lacks it', source_note['text'])
        self.assertIn('does not establish a different Hebrew reading', seventeen['translation']['footnotes'][0]['text'])

    def test_acts_24_disclosure_preserves_connected_shorter_form(self):
        six = yaml.safe_load((ROOT / 'translation/nt/acts/024/006.yaml').read_text())
        eight = yaml.safe_load((ROOT / 'translation/nt/acts/024/008.yaml').read_text())
        self.assertEqual(six['source']['edition'], 'SBLGNT')
        self.assertEqual(eight['source']['edition'], 'SBLGNT')
        self.assertIn('we seized him[a]', six['translation']['text'])
        self.assertIn('From him[a][b]', eight['translation']['text'])
        for v, record in [(6, six), (8, eight)]:
            out = exporter._export_record_verse(v, record)
            self.assertEqual(out['footnotes'], record['translation']['footnotes'])
            self.assertEqual(record['cross_check'], {'status': 'needs_review'})
        self.assertIn('Byzantine main texts retain the shorter unit', six['translation']['footnotes'][0]['text'])
        self.assertIn('Paul remains possible', eight['translation']['footnotes'][1]['text'])
        self.assertIn('beginning of verse 8', eight['translation']['footnotes'][1]['text'])

    def test_lamentations_1_8_discloses_source_and_interpretation_separately(self):
        record = yaml.safe_load((ROOT / 'translation/ot/lamentations/001/008.yaml').read_text())
        self.assertEqual(record['source']['edition'], 'WLC')
        self.assertIn('נִידָ', record['source']['text'])
        text = record['translation']['text']
        self.assertIn('unclean[a][c]', text)
        self.assertNotIn('[b]', text)
        self.assertEqual(text.count('[a]'), 1)
        self.assertEqual(text.count('[c]'), 1)
        out = exporter._export_record_verse(8, record)
        self.assertEqual(out['footnotes'], record['translation']['footnotes'])
        notes = {n['marker']: n for n in out['footnotes']}
        self.assertIn('ritual impurity is not its only possible sense', notes['a']['text'])
        self.assertEqual(notes['c']['reason'], 'textual_variant')
        for detail in ('Published 4Q111', 'לנוד', 'לנידה', 'either Hebrew spelling',
                       'historical priority remains unresolved'):
            self.assertIn(detail, notes['c']['text'])
        self.assertEqual(record['cross_check'], {'status': 'needs_review'})
        self.assertEqual(record['status'], 'draft')

    def test_lamentations_junction_disclosure_and_phrase_anchors_reach_reader(self):
        cases = [
            (10, {'a': 'precious things[a]', 'b': 'nations[b]',
                  'c': 'your assembly[c]', 'd': 'your assembly[c][d]'}),
            (11, {'a': 'their precious things[a]', 'b': 'restore life[b]',
                  'c': 'become despised[c]', 'd': 'restore life[b][d]'}),
        ]
        for verse, anchors in cases:
            with self.subTest(verse=verse):
                record = yaml.safe_load((ROOT / f'translation/ot/lamentations/001/{verse:03}.yaml').read_text())
                text = record['translation']['text']
                for marker, phrase in anchors.items():
                    self.assertIn(phrase, text)
                    self.assertEqual(text.count(f'[{marker}]'), 1)
                out = exporter._export_record_verse(verse, record)
                self.assertEqual(out['text'], text)
                self.assertEqual(out['footnotes'], record['translation']['footnotes'])
                note = next(n for n in out['footnotes'] if n['marker'] == 'd')
                self.assertEqual(note['reason'], 'textual_variant')
                for detail in ('Published 4Q111', 'retains the longer form',
                               'historical priority remains unresolved'):
                    self.assertIn(detail, note['text'])

    def test_lamentations_junction_retains_declared_longer_source_and_english(self):
        ten = yaml.safe_load((ROOT / 'translation/ot/lamentations/001/010.yaml').read_text())
        eleven = yaml.safe_load((ROOT / 'translation/ot/lamentations/001/011.yaml').read_text())
        self.assertEqual(ten['source']['edition'], 'WLC')
        self.assertEqual(eleven['source']['edition'], 'WLC')
        self.assertIn('your assembly', ten['translation']['text'])
        self.assertIn('All her people groan, seeking bread; they have given', eleven['translation']['text'])
        self.assertIn('their precious things', eleven['translation']['text'])
        note = next(n['text'] for n in ten['translation']['footnotes'] if n['marker'] == 'd')
        self.assertIn('eight Masoretic words', note)
        self.assertIn('not merely a physical gap', note)
        note = next(n['text'] for n in eleven['translation']['footnotes'] if n['marker'] == 'd')
        self.assertIn('copying loss is plausible but not proven', note)

    def test_amos_acts_comparison_notes_are_anchored_to_their_actual_phrases(self):
        cases = [
            ('translation/ot/amos/009/012.yaml', {
                'a': 'who are called by my name[a]',
                'b': 'possess the remnant of Edom[b]',
            }),
            ('translation/nt/acts/015/017.yaml', {
                'a': 'all the Gentiles[a]',
                'b': 'on whom my name has been called[b]',
                'c': 'may seek the Lord[c]',
            }),
        ]
        for relative, anchors in cases:
            with self.subTest(record=relative):
                record = yaml.safe_load((ROOT / relative).read_text())
                text = record['translation']['text']
                for marker, phrase in anchors.items():
                    self.assertIn(phrase, text)
                    self.assertEqual(text.count(f'[{marker}]'), 1)
                out = exporter._export_record_verse(int(record['id'].split('.')[-1]), record)
                self.assertEqual(out['text'], text)
                self.assertEqual(out['footnotes'], record['translation']['footnotes'])
                marker = 'b' if record['id'] == 'AMO.9.12' else 'c'
                note = next(n['text'] for n in out['footnotes'] if n['marker'] == marker)
                for detail in ('Swete', 'without an explicit object', 'apparatus',
                               'Codex Alexandrinus', 'Acts'):
                    self.assertIn(detail, note)

    def test_amos_acts_disclosure_preserves_distinct_source_forms_and_limits(self):
        amos = yaml.safe_load((ROOT / 'translation/ot/amos/009/012.yaml').read_text())
        acts = yaml.safe_load((ROOT / 'translation/nt/acts/015/017.yaml').read_text())
        self.assertEqual(amos['source']['edition'], 'WLC')
        self.assertIn('אֱדוֹם', amos['source']['text'])
        self.assertIn('possess the remnant of Edom', amos['translation']['text'])
        self.assertEqual(acts['source']['edition'], 'SBLGNT')
        self.assertIn('τὸν κύριον', acts['source']['text'])
        self.assertIn('remnant of mankind may seek the Lord', acts['translation']['text'])
        note = next(n['text'] for n in amos['translation']['footnotes'] if n['marker'] == 'b')
        self.assertIn('beginning of the verb is restored', note)
        self.assertIn('earlier remains unresolved', note)
        note = next(n['text'] for n in acts['translation']['footnotes'] if n['marker'] == 'c')
        self.assertIn('not another Hebrew manuscript', note)
        self.assertIn('proof of which Greek form influenced the other', note)

    def record(self):
        return {'translation': {'text': 'A disputed reading[a] and a supplied [word].',
                'footnotes': [{'marker': 'a', 'text': 'A contrary witness.', 'reason': 'textual_variant'},
                             {'marker': 'b', 'text': 'An unreferenced archival note.'}]}}

    def test_referenced_note_and_reason_survive_without_mutation(self):
        record = self.record()
        before = copy.deepcopy(record)
        result = exporter._export_record_verse(8, record)
        self.assertEqual(result['text'], record['translation']['text'])
        self.assertEqual(result['footnotes'], [record['translation']['footnotes'][0]])
        self.assertEqual(record, before)
        result['footnotes'][0]['text'] = 'changed output only'
        self.assertEqual(record, before)

    def test_bracketed_marker_normalizes_like_publisher(self):
        record = self.record()
        record['translation']['footnotes'][0]['marker'] = ' [a] '
        self.assertEqual(exporter._export_record_verse(8, record)['footnotes'][0]['marker'], 'a')

    def test_empty_malformed_and_background_notes_are_not_exported(self):
        record = self.record()
        record['translation']['footnotes'] = [None, 3, {}, {'marker': 'a', 'text': None},
                                              {'marker': 'a', 'text': '  '},
                                              {'marker': 'z', 'text': 'old rationale'}]
        result = exporter._export_record_verse(8, record)
        self.assertNotIn('footnotes', result)
        self.assertEqual(result['text'], record['translation']['text'])

    def test_absent_notes_and_manuscript_brackets_do_not_invent_notes(self):
        record = {'translation': {'text': 'Text with [supplied words].'}}
        self.assertEqual(exporter._export_record_verse(1, record),
                         {'verse': 1, 'text': record['translation']['text']})

    def test_canonical_ot_and_nt_book_paths_use_note_export(self):
        for code in ('DEU', 'MAT'):
            with self.subTest(code=code), \
                 patch.object(exporter, 'expected_chapter_map', return_value={1: [1]}), \
                 patch.object(exporter, 'load_translation_record', return_value=self.record()):
                book = exporter.export_book(code)
                self.assertEqual(book['chapters'][0]['verses'][0]['footnotes'][0]['text'], 'A contrary witness.')

    def test_final_payload_normalization_and_json_keep_note_bodies(self):
        with patch.object(exporter, 'CANONICAL_BOOK_ORDER', ['DEU']), \
             patch.object(exporter, 'APOCRYPHA_BOOK_ORDER', []), \
             patch.object(exporter, 'EXTRA_CANONICAL_BOOK_ORDER', []), \
             patch.object(exporter, 'expected_chapter_map', return_value={1: [1]}), \
             patch.object(exporter, 'load_translation_record', return_value=self.record()):
            payload = json.loads(json.dumps(exporter.export_translation()))
        verse = payload['books'][0]['chapters'][0]['verses'][0]
        self.assertEqual(verse['text'], self.record()['translation']['text'])
        self.assertEqual(verse['footnotes'], [self.record()['translation']['footnotes'][0]])

    def test_psalm_superscription_and_body_notes_survive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            chapter = root / 'ot/psalms/001'
            chapter.mkdir(parents=True)
            for number in (0, 1):
                (chapter / f'{number:03}.yaml').write_text(yaml.safe_dump(self.record()))
            with patch.object(exporter, 'TRANSLATION_ROOT', root):
                verses = exporter.export_psalms_book()['chapters'][0]['verses']
            self.assertTrue(verses[0]['is_superscription'])
            self.assertTrue(all(v['footnotes'] for v in verses))

    def write_apocrypha_fixture(self, root, chapter, verse, record):
        directory = root / exporter.APOCRYPHA_BOOK_SLUGS['SIR'] / f'{chapter:03}'
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f'{verse:03}.yaml'
        path.write_text(yaml.safe_dump(record), encoding='utf-8')
        return path

    def test_apocrypha_referenced_notes_normalize_and_background_notes_stay_hidden(self):
        record = self.record()
        record['translation']['text'] = '  A disputed reading[a] and a supplied [word].  '
        record['translation']['footnotes'][0] = {
            'marker': ' [a] ', 'text': '  A contrary witness.  ',
            'reason': ' textual_variant ', 'archival_detail': 'not a reader field',
        }
        record['translation']['footnotes'].extend([
            None, {'marker': 'word', 'text': '  '}, {'marker': 'a', 'text': None},
        ])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_apocrypha_fixture(root, 1, 1, record)
            with patch.object(exporter, 'APOCRYPHA_ROOT', root):
                book = exporter.export_apocrypha_book('SIR')
        self.assertEqual(book, {
            'name': exporter.APOCRYPHA_BOOK_TITLES['SIR'],
            'chapters': [{'chapter': 1, 'verses': [{
                'verse': 1, 'text': record['translation']['text'].strip(),
                'footnotes': [{'marker': 'a', 'text': 'A contrary witness.',
                              'reason': 'textual_variant'}],
            }]}],
        })

    def test_apocrypha_no_note_records_keep_original_shape_without_superscription(self):
        records = [
            {'translation': {'text': ' Text with [supplied words]. '}},
            {'translation': {'text': 'Another text.', 'footnotes': [
                {'marker': 'a', 'text': 'Not referenced.'}]}},
        ]
        records[0]['is_superscription'] = True
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for number, record in enumerate(records, 1):
                self.write_apocrypha_fixture(root, 1, number, record)
            with patch.object(exporter, 'APOCRYPHA_ROOT', root):
                book = exporter.export_apocrypha_book('SIR')
        self.assertEqual(book, {
            'name': exporter.APOCRYPHA_BOOK_TITLES['SIR'],
            'chapters': [{'chapter': 1, 'verses': [
                {'verse': number, 'text': record['translation']['text'].strip()}
                for number, record in enumerate(records, 1)
            ]}],
        })

    def test_apocrypha_incomplete_chapters_do_not_withhold_later_complete_chapter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for number in (1, 3):
                self.write_apocrypha_fixture(root, 1, number, self.record())
            self.write_apocrypha_fixture(root, 2, 1, self.record())
            self.write_apocrypha_fixture(root, 2, 2, {'translation': {'text': '  '}})
            self.write_apocrypha_fixture(root, 2, 3, self.record())
            for number in (1, 2):
                self.write_apocrypha_fixture(root, 3, number, self.record())
            with patch.object(exporter, 'APOCRYPHA_ROOT', root):
                book = exporter.export_apocrypha_book('SIR')
        self.assertEqual([chapter['chapter'] for chapter in book['chapters']], [3])
        verses = book['chapters'][0]['verses']
        self.assertEqual([verse['verse'] for verse in verses], [1, 2])
        self.assertTrue(all(verse['footnotes'] for verse in verses))

    def test_apocrypha_export_does_not_mutate_record_or_fixture(self):
        record = self.record()
        before = copy.deepcopy(record)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_apocrypha_fixture(root, 1, 1, record)
            original_bytes = path.read_bytes()
            with patch.object(exporter, 'APOCRYPHA_ROOT', root), \
                 patch.object(exporter.yaml, 'safe_load', return_value=record):
                book = exporter.export_apocrypha_book('SIR')
            self.assertEqual(record, before)
            book['chapters'][0]['verses'][0]['footnotes'][0]['text'] = 'output-only change'
            self.assertEqual(record, before)
            self.assertEqual(path.read_bytes(), original_bytes)

    def test_thirteen_actual_comparison_baselines_preserve_reader_notes(self):
        comparisons = ROOT / 'sources/textual_restoration/comparisons'
        cases = []
        for name in ('pentateuch_controls.v1.json', 'samuel_controls.v1.json', 'psalms_controls.v1.json'):
            cases.extend(json.loads((comparisons / name).read_text())['cases'])
        self.assertEqual(len(cases), 13)
        for case in cases:
            record = yaml.safe_load((ROOT / case['baseline']['repo_path']).read_text())
            out = exporter._export_record_verse(int(record['id'].split('.')[-1]), record)
            expected = [
                {k: str(n[k]).strip() for k in ('marker', 'text', 'reason') if n.get(k) is not None}
                for n in record['translation']['footnotes']
                if f"[{n['marker']}]" in record['translation']['text']
            ]
            self.assertTrue(expected, case['id'])
            self.assertEqual(out['footnotes'], expected)
            self.assertEqual(out['text'], record['translation']['text'].strip())


if __name__ == '__main__':
    unittest.main()
