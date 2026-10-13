import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.historical_archive_review import (digest, group_bilara, parse_muller, source_job, validate_review)

class HistoricalSourceReviewTests(unittest.TestCase):
    def test_cached_source_tampering_or_lost_receipts_fail_closed(self):
        from tools.historical_archive_review import fetch
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'source.json';path.write_bytes(b'original')
            with self.assertRaises(ValueError):fetch('https://example.org/source',path)
            record=path.with_name(path.name+'.receipt.json')
            record.write_text(json.dumps({'url':'https://example.org/source','sha256':digest(b'original'),'bytes':8}))
            self.assertEqual(fetch('https://example.org/source',path),b'original')
            path.write_bytes(b'changed')
            with self.assertRaises(ValueError):fetch('https://example.org/source',path)
    def test_source_headers_never_enter_verse_text(self):
        data={'dhp1:0.1':'Heading','dhp1:1':'Pali one','dhp1:2':'Pali two','dhp2:1':'Next verse'}
        result=group_bilara(data,1,2)
        self.assertEqual([text for _,text in result[1]],['Pali one','Pali two'])
        self.assertEqual(list(result),[1,2])
    def test_missing_and_empty_source_verses_fail_closed(self):
        with self.assertRaises(ValueError):group_bilara({'dhp1:1':'One'},1,2)
        with self.assertRaises(ValueError):group_bilara({'dhp1:1':''},1,1)
        with self.assertRaises(ValueError):group_bilara({'dhp2:1':'Out of range'},1,1)
        self.assertEqual(group_bilara({'dhp1:1':''},1,1,allow_empty=True),{1:[('dhp1:1','')]})
    def test_archived_english_requires_all_423_verses(self):
        source='\n'.join(f'{n}. Verse {n}' for n in range(1,424))+'\n*** END OF THE PROJECT GUTENBERG EBOOK TITLE ***'
        rows=parse_muller(source.encode())
        self.assertEqual(len(rows),423)
        self.assertEqual(rows[423]['text'],'Verse 423')
        with self.assertRaises(ValueError):parse_muller(source.replace('22. Verse 22\n','').encode())
        with self.assertRaises(ValueError):parse_muller(source.replace('*** END','*** BAD END').encode())
    def test_combined_english_verses_are_not_falsely_individualized(self):
        text='\n'.join(f'{n}. Verse {n}' for n in range(1,424))+'\n*** END OF THE PROJECT GUTENBERG EBOOK TITLE ***'
        text=text.replace('2. Verse 2\n3. Verse 3','2, 3. Combined passage')
        rows=parse_muller(text.encode())
        self.assertEqual(rows[2]['verse_span'],[2,3])
        self.assertEqual(rows[3]['alignment'],'combined_span_not_individually_aligned')
    def test_source_preparation_does_not_claim_verification(self):
        job=source_job('Work','1','pli','Pali',[])
        self.assertFalse(job['publication_allowed'])
        self.assertEqual(job['review_status'],'not_started')
        self.assertFalse(job['claims']['whole_work_verified'])
        self.assertEqual(job['source']['sha256'],digest(b'Pali'))
    def fixture(self):
        job=source_job('Work','1','pli','Pali',[])
        draft={'generator_model':'model-a','units':[{'reference':'1','english':'English'}]}
        review={'reviewer_model':'model-b','source_sha256':job['source']['sha256'],
          'draft_sha256':digest(json.dumps(draft,ensure_ascii=False,sort_keys=True).encode()),
          'units':[{'reference':'1','verdict':'acceptable','unresolved_issues':[]}],
          'rights_accepted':True,'whole_work_verified':False}
        return job,draft,review
    def test_hash_bound_separate_review(self):
        job,draft,review=self.fixture()
        self.assertEqual(validate_review(job,draft,review),[])
        for key in ['source_sha256','draft_sha256']:
            changed={**review,key:'changed'}
            self.assertTrue(validate_review(job,draft,changed))
        self.assertTrue(validate_review(job,draft,{**review,'reviewer_model':'model-a'}))
    def test_coverage_and_unresolved_questions_block(self):
        job,draft,review=self.fixture()
        self.assertTrue(validate_review(job,draft,{**review,'units':[]}))
        self.assertTrue(validate_review(job,draft,{**review,'units':[{'reference':'1','verdict':'needs_correction','unresolved_issues':['gap']}]}))
        self.assertTrue(validate_review(job,draft,{**review,'rights_accepted':False}))
        self.assertTrue(validate_review(job,draft,{**review,'whole_work_verified':True}))
    def test_scan_review_cannot_be_replaced_by_text_consensus(self):
        job,draft,review=self.fixture();job['mode']='english_edition_scan_review'
        self.assertIn('direct scan check required',validate_review(job,draft,review))
        review['scan_checked']=True
        self.assertEqual(validate_review(job,draft,review),[])
    def test_page_locator_is_not_transcribed_as_original_words(self):
        from tools.historical_archive_review import parse_jsp_page
        page={'clearText':'<div class="wasptag">Printed words. [p. [iii]]</div>', 'editorialPageNumber':'[iii]'}
        raw=('<script id="__NEXT_DATA__" type="application/json">'+json.dumps({'props':{'pageProps':{'summary':page}}})+'</script>').encode()
        text,_=parse_jsp_page(raw)
        self.assertEqual(text,'Printed words.')
    def test_jsp_editorial_material_stays_out_of_original_text(self):
        from tools.historical_archive_review import parse_jsp_page
        page={'clearText':'<div class="anonymous-block-p">Modern heading</div><div class="wasptag">Original <span class="footnote-ref">12</span>words.</div>', 'editorialTitle':'Work'}
        html='<script id="__NEXT_DATA__" type="application/json">'+json.dumps({'props':{'pageProps':{'summary':page}}})+'</script>'
        text,_=parse_jsp_page(html.encode())
        self.assertEqual(text,'Original words.')
        with self.assertRaises(ValueError):parse_jsp_page(b'<html>error page</html>')

    def test_blank_pages_are_retained_only_with_explicit_inventory_mode(self):
        from tools.historical_archive_review import parse_jsp_page
        raw=('<script id="__NEXT_DATA__" type="application/json">'+json.dumps({'props':{'pageProps':{'summary':{'clearText':'<div class="anonymous-block-p">Blank page</div>'}}}})+'</script>').encode()
        with self.assertRaises(ValueError):parse_jsp_page(raw)
        self.assertEqual(parse_jsp_page(raw,allow_empty=True)[0],'')

    def test_live_style_popup_keeps_printed_name_not_modern_biography(self):
        from tools.historical_archive_review import parse_jsp_page
        page={'clearText':'<div class="wasptag">Printed by <aside class="popup-wrapper"><a class="reference staticPopup">F. G. WILLIAMS &amp; CO.</a><div class="popup-content"><div class="note-data"><p>Modern biography.</p><a>View Glossary</a></div></div></aside> [p. [iii]]</div>', 'editorialPageNumber':'iii'}
        raw=('<script id="__NEXT_DATA__" type="application/json">'+json.dumps({'props':{'pageProps':{'summary':page}}})+'</script>').encode()
        self.assertEqual(parse_jsp_page(raw)[0],'Printed by F. G. WILLIAMS & CO.')

    def test_a_page_locator_alone_is_not_nonempty_source_text(self):
        from tools.historical_archive_review import parse_jsp_page
        page={'clearText':'<div class="wasptag">[p. [0]]</div>', 'editorialPageNumber':'0'}
        raw=('<script id="__NEXT_DATA__" type="application/json">'+json.dumps({'props':{'pageProps':{'summary':page}}})+'</script>').encode()
        with self.assertRaises(ValueError):parse_jsp_page(raw)
        self.assertEqual(parse_jsp_page(raw,allow_empty=True)[0],'')

class WholeEditionInventoryTests(unittest.TestCase):
    def test_offline_snapshot_audit_never_repairs_or_fetches(self):
        from tools.historical_dc_whole_edition import read_snapshot
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'page.html';path.write_bytes(b'original')
            record=path.with_name(path.name+'.receipt.json')
            with self.assertRaises(FileNotFoundError):read_snapshot(path,'https://example.org/page')
            record.write_text(json.dumps({'url':'https://example.org/page','sha256':digest(b'original'),'bytes':8}))
            self.assertEqual(read_snapshot(path,'https://example.org/page'),b'original')
            with self.assertRaises(ValueError):read_snapshot(path,'https://example.org/other-copy')
            path.write_bytes(b'tampered')
            with self.assertRaises(ValueError):read_snapshot(path,'https://example.org/page')
    def ia_fixture(self):
        scan=b'<book><bookData><bookId>GR_711</bookId><leafCount>2</leafCount></bookData><pageData><page leafNum="0"><pageType>Normal</pageType></page><page leafNum="1"><pageNumber>i</pageNumber></page></pageData></book>'
        djvu=b'<DjVuXML><BODY><OBJECT usemap="GR_711_0000.djvu"></OBJECT><OBJECT usemap="GR_711_0001.djvu"><LINE><WORD coords="1,2,3,4">Printed</WORD><WORD>words</WORD></LINE></OBJECT></BODY></DjVuXML>'
        return scan,djvu
    def jsp_fixture(self):
        data={'props':{'pageProps':{'statusCode':200,'is404':False,
          'summary':{'uri':'doctrine-and-covenants-1835','numberOfPages':2},
          'gallery':[{'page':'1','label':'[0]','href':'/paper-summary/doctrine-and-covenants-1835/1'},
                     {'page':'2','label':'[i]','href':'/paper-summary/doctrine-and-covenants-1835/2'}]}}}
        return data
    def encode_jsp(self,data):
        return ('<script id="__NEXT_DATA__" type="application/json">'+json.dumps(data)+'</script>').encode()
    def test_every_leaf_including_empty_ocr_is_in_scope(self):
        from tools.historical_dc_whole_edition import ia_inventory
        rows=ia_inventory(*self.ia_fixture())
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[0]['ocr']['text'],'')
        self.assertEqual(rows[0]['review_status'],'not_started')
        self.assertFalse(rows[0]['publication_allowed'])
        self.assertEqual(rows[1]['ocr']['text'],'Printed words')
        self.assertEqual(rows[1]['ocr']['lines'][0][0]['coords'],'1,2,3,4')
    def test_archive_missing_reordered_or_different_copy_fails_closed(self):
        from tools.historical_dc_whole_edition import ia_inventory
        scan,djvu=self.ia_fixture()
        for changed in [scan.replace(b'leafNum="1"',b'leafNum="0"'),
                        scan.replace(b'leafCount>2',b'leafCount>3'),
                        scan.replace(b'GR_711',b'other-copy')]:
            with self.assertRaises(ValueError):ia_inventory(changed,djvu)
        with self.assertRaises(ValueError):ia_inventory(scan,djvu.replace(b'GR_711_0001',b'GR_711_0000'))
    def test_jsp_inventory_does_not_assume_shared_binding_offsets(self):
        from tools.historical_dc_whole_edition import jsp_inventory
        rows=jsp_inventory(self.encode_jsp(self.jsp_fixture()))
        self.assertEqual([row['page'] for row in rows],[1,2])
        self.assertNotIn('newberry_leaf',rows[1])
        self.assertFalse(rows[1]['publication_allowed'])
    def test_jsp_errors_wrong_identity_and_incomplete_gallery_fail_closed(self):
        from tools.historical_dc_whole_edition import jsp_inventory
        for field,value in [('is404',True),('statusCode',404)]:
            data=self.jsp_fixture();data['props']['pageProps'][field]=value
            with self.assertRaises(ValueError):jsp_inventory(self.encode_jsp(data))
        data=self.jsp_fixture();data['props']['pageProps']['summary']['uri']='other-work'
        with self.assertRaises(ValueError):jsp_inventory(self.encode_jsp(data))
        data=self.jsp_fixture();data['props']['pageProps']['gallery'].pop()
        with self.assertRaises(ValueError):jsp_inventory(self.encode_jsp(data))
        data=self.jsp_fixture();data['props']['pageProps']['gallery'][1]['href']='/different-copy/2'
        with self.assertRaises(ValueError):jsp_inventory(self.encode_jsp(data))

if __name__=='__main__':unittest.main()
