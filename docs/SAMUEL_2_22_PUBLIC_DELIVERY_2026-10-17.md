# First Samuel 2 22 public delivery

## Verified source record and CDN

The [reviewed Samuel application](SAMUEL_2_22_APPLICATION_2026-10-17.md)
has reached the upstream CDN and public provenance page. At the October 17,
21:33–21:37 UTC check, the [provenance page](https://peoplesbible.com/verse/?ref=1SA.2.22)
displayed the composed Hebrew, shorter English, contrary apparatus and both
exact candidate notes. Clicking note b reached its readable full text,
including the longer Masoretic allegation and the uncertainty about earliest
wording. The current cross-check label was **Review needed**; the old
agreement score was not used to approve the changed wording.

> Eli was very old, and he heard what his sons were doing to the people of Israel.

The successful [publisher job](https://github.com/zackseyun/peoples-open-bible/actions/runs/39070983966)
is distinct from a completed website deployment. The CDN manifest identified
`070328980e86e8771fb8d1e1c3d4a8b2983bf896`, a verified descendant of the
application merge, updated at 21:33:30 UTC. All 811 Samuel verse texts across
31 chapters matched canonical English after removing bracketed note markers.
The target CDN object contained the shorter English but no notes.

## Chapter delivery remains pending

The actual [chapter view](https://peoplesbible.com/read?view=read&book=1+Samuel&chapter=2&verse=22)
still displayed the older longer text. Its selected-verse provenance action
did open the correct updated source record with both notes. Thus on-demand
disclosure works, but the chapter and source page were not yet synchronized.
The newly dispatched [website rebuild](https://github.com/zackseyun/cartha.website/actions/runs/39071463873)
was initially pending. Its status, the changed CDN and source-page success
must not stand in for observing the actual updated chapter.

At the later 22:34–22:35 UTC observation, the requested deployment
`39071463873` and its companion quiet-time run `39071467896` were terminally
cancelled, last updated at 22:06:50 and 22:06:53 respectively. They are not
still-running handles. A newer [quiet-time run](https://github.com/zackseyun/cartha.website/actions/runs/39075344945),
created by a website push at 22:30:24, was observed queued; its existence does
not establish the contents or completion of a replacement deployment. A fresh
actual Samuel chapter still displayed the older full allegation. Synchronized
chapter delivery therefore remains unverified. No duplicate dispatch or
manual restart was performed, and no cancellation cause is inferred from
status alone.

Read-only inspection of that newer run's workflow at website revision
`246f395d9e171b8e8feaf7308812d5901b8b5078` shows cancellable commit builds
after five quiet minutes and a separate serialized, non-cancelling publication
job. This describes the inspected configuration, not the cause of earlier
cancellations, a claim that publication ran, or permission to change the
website repository. No workflow or reader implementation was edited here.

The [dated observation record](../sources/textual_restoration/applications/samuel2_22_public_delivery.2026-10-17.v1.json)
keeps the payload hashes, ancestry check, exact target text and separate
delivery stages. It supplements rather than rewrites the frozen local
application receipt. The default reading view remains free of extra inline
commentary; no external publisher or reader code was changed. Mobile/offline
delivery and the entire website are not certified by this check.

This is progress toward an evidence-linked source corpus and an actual POB
contribution, not a new manuscript discovery, proof of the autograph or a
canon decision. The wider comparison and measured-image recovery program
remains active.
