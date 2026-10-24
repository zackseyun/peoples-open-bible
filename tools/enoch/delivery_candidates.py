"""Order installed candidate evidence for live comparison, never approve wording."""
import json
import re
from tools.enoch import bounded_application as t


def ordered_packages():
    """Keep the actual metadata26 transaction before its language successors.

    Appending metadata26 last would silently hide new26:5/6 explanations from
    latest-candidate verification. Only installed, receipt-bound batches belong
    in this comparison; a retained unapplied proposal must not replace one.
    """
    metadata=t.APPLICATIONS/'enoch_26_metadata_v3_20261023'
    batches=[]
    for p in t.APPLICATIONS.glob('enoch_full_repair_batch*'):
        receipt=p/'application.json'
        if not receipt.exists():continue
        r=json.loads(receipt.read_text())
        if r.get('status')!='applied_verified' or r.get('manifest_sha256')!=t.sha((p/'manifest.json').read_bytes()):
            raise ValueError('Delivery batch lacks an exact applied receipt: '+p.name)
        batches.append((int(re.search(r'batch(\d+)',p.name)[1]),p))
    batches.sort()
    fifteen=[p for n,p in batches if n==15]
    if len(fifteen)!=1 or not(metadata/'application.json').exists():
        raise ValueError('Delivery metadata26 chronology lacks its applied boundary')
    m=json.loads((fifteen[0]/'manifest.json').read_text())
    for v in(5,6):
        if m['canonical_baseline_sha256'][f'026/{v:03d}.yaml']!=t.sha((metadata/f'026-{v:03d}.candidate.yaml').read_bytes()):
            raise ValueError('Delivery metadata26 does not precede batch15 preimage')
    return ([t.APPLICATIONS/'enoch_source_repairs_20261020']+
            [p for n,p in batches if n<15]+[metadata]+[p for n,p in batches if n>=15])
