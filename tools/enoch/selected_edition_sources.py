"""Independent reviewed source inputs, never a canonical-to-source echo.

Chapter registrations point to immutable application evidence. Loading does
not consult installed verse YAMLs or English translations as source text.
Old raw OCR remains available separately for diagnostics and reproducibility.
"""
import json
from pathlib import Path
import yaml

from tools.enoch import bounded_application as transaction

REGISTRY = transaction.ROOT / 'sources/enoch/ethiopic/reviewed_source_registry.json'


def registry_data() -> dict | None:
    if not REGISTRY.exists():
        return None
    registry = json.loads(REGISTRY.read_text())
    if registry.get('kind') != 'enoch-selected-edition-sources-v1' or \
            registry.get('primary_pdf_sha256') != transaction.PRIMARY_SHA:
        raise ValueError('Reviewed source registry kind/primary differs')
    return registry


def package_evidence(name: str) -> tuple[Path, dict]:
    package = transaction.artifact(transaction.APPLICATIONS, name)
    if package.parent != transaction.APPLICATIONS.resolve():
        raise ValueError('Source package must be a direct application directory')
    return package, transaction.load_manifest(package)


def source_row(package: Path, manifest: dict, chapter: int, verse: int) -> dict:
    ref = f'1 Enoch {chapter}:{verse}'
    if ref not in manifest['review_bindings']:
        raise ValueError(f'Registered source lacks the exact unit: {ref}')
    rows = transaction.reviewed_rows(package, manifest['review_bindings'][ref], ref, manifest['files'])
    sources = [row['source'] for row in rows]
    if any(source != sources[0] for source in sources[1:]):
        raise ValueError(f'Accepted source inputs differ: {ref}')
    source = sources[0]
    candidate_name = f'{chapter:03d}-{verse:03d}.candidate.yaml'
    candidate = yaml.load(transaction.artifact(package, candidate_name).read_bytes(),
                          Loader=transaction.LOADER)
    if any(candidate['source'].get(k) != source.get(k)
           for k in ('edition','language','text','pages','additional_translation_input','transcription_uncertainties')) or \
            source.get('edition') != 'charles-1906-enoch' or source.get('language') != 'Geez' or \
            not source.get('text') or not source.get('pages'):
        raise ValueError(f'Reviewed source identity/payload differs: {ref}')
    if 'confidence' in source and candidate['source'].get('confidence')!=source['confidence']:
        raise ValueError(f'Reviewed source confidence differs: {ref}')
    return {'reference': ref, 'verse':verse, 'source':source,
            'evidence':str(package.relative_to(transaction.ROOT)) + '/' +
                       manifest['review_bindings'][ref][0]['input']}


def load_chapter(chapter: int) -> list[dict] | None:
    registry = registry_data()
    if registry is None:
        return None
    name = registry['chapters'].get(str(chapter))
    if name is None:
        return None
    package, manifest = package_evidence(name)
    certificates = [c for c in manifest.get('chapter_inventories', []) if c['chapter'] == chapter]
    if len(certificates) != 1:
        raise ValueError('Reviewed source chapter lacks one exact count certificate')
    certificate = certificates[0]
    units = certificate['units']
    if not units or units != list(range(1, len(units)+1)) or \
            certificate.get('independent_count_confirmation') is not True or \
            certificate.get('artifact') not in manifest['files']:
        raise ValueError('Reviewed source count is not independently bound')
    inventory = json.loads(transaction.artifact(package, certificate['artifact']).read_text())
    matching = [c for c in inventory['chapters'] if c['chapter'] == chapter]
    if len(matching) != 1 or matching[0]['units'] != units or \
            inventory.get('primary_pdf_sha256') != transaction.PRIMARY_SHA:
        raise ValueError('Count certificate differs from pinned printed inventory')
    return [source_row(package,manifest,chapter,verse) for verse in units]


def load_unit_overrides(chapter: int) -> list[dict]:
    """Exact accepted units inside an already declared printed count.

    A unit registration does not certify other units or an entire chapter.
    It prevents an individually repaired negative/glyph from regressing to OCR.
    """
    registry = registry_data()
    if registry is None:
        return []
    output = []
    for key, name in registry.get('units',{}).items():
        c,v = transaction.parse_ref('1 Enoch ' + key)
        if c != chapter:
            continue
        from tools.enoch.audit_pob_source_coverage import EXPECTED_VERSES
        package,manifest = package_evidence(name)
        count = EXPECTED_VERSES.get(c)
        if count is None:
            # Versioned paired source-only counts are not reader/export release
            # declarations: neighboring held wording must remain unavailable.
            matches = [row for row in manifest.get('source_only_count_inventories', [])
                       if row['chapter'] == c]
            if len(matches) == 1:
                count = len(matches[0]['units'])
        if count is None or v > count:
            raise ValueError('Individual source override requires a declared printed count/address')
        output.append(source_row(package,manifest,c,v))
    return sorted(output,key=lambda row:row['verse'])
