"""Independent reviewed source inputs, never a canonical-to-source echo.

Chapter registrations point to immutable application evidence. Loading does
not consult installed verse YAMLs or English translations as source text.
Old raw OCR remains available separately for diagnostics and reproducibility.
"""
import json
from pathlib import Path

from tools.enoch import bounded_application as transaction

REGISTRY = transaction.ROOT / 'sources/enoch/ethiopic/reviewed_source_registry.json'


def load_chapter(chapter: int) -> list[dict] | None:
    if not REGISTRY.exists():
        return None
    registry = json.loads(REGISTRY.read_text())
    if registry.get('kind') != 'enoch-selected-edition-sources-v1' or \
            registry.get('primary_pdf_sha256') != transaction.PRIMARY_SHA:
        raise ValueError('Reviewed source registry kind/primary differs')
    name = registry['chapters'].get(str(chapter))
    if name is None:
        return None
    package = transaction.artifact(transaction.APPLICATIONS, name)
    if package.parent != transaction.APPLICATIONS.resolve():
        raise ValueError('Source package must be a direct application directory')
    manifest = transaction.load_manifest(package)
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
    output = []
    for verse in units:
        ref = f'1 Enoch {chapter}:{verse}'
        rows = transaction.reviewed_rows(package, manifest['review_bindings'][ref], ref, manifest['files'])
        sources = [row['source'] for row in rows]
        # Exact input source objects, not a new rendition inferred from English.
        if any(source != sources[0] for source in sources[1:]):
            raise ValueError(f'Accepted source inputs differ: {ref}')
        source = sources[0]
        candidate_name = f'{chapter:03d}-{verse:03d}.candidate.yaml'
        import yaml
        candidate = yaml.load(transaction.artifact(package, candidate_name).read_bytes(),
                              Loader=transaction.LOADER)
        if any(candidate['source'].get(k) != source.get(k)
               for k in ('edition','language','text','pages')) or \
                source.get('edition') != 'charles-1906-enoch' or source.get('language') != 'Geez' or \
                not source.get('text') or not source.get('pages'):
            raise ValueError(f'Reviewed source identity/payload differs: {ref}')
        output.append({'reference': ref, 'verse':verse, 'source': source,
                       'evidence': str(package.relative_to(transaction.ROOT)) + '/' +
                                   manifest['review_bindings'][ref][0]['input']})
    return output
