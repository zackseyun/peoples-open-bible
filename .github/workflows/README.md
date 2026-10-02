# Operational GitHub Actions intentionally disabled

This repository now uses AWS CodeBuild for the automated POB operational jobs that used to live in GitHub Actions:

- `cartha-open-bible-publish-pob`
- `cartha-open-bible-regen-status`
- `cartha-open-bible-regen-summary-cache`
- `cartha-open-bible-regen-embeddings`

The old operational workflows are preserved under `.github/workflows/disabled/*.disabled` for audit/rollback, but GitHub will not execute them. The read-only `corpus-integrity.yml` workflow is deliberately enabled for pull requests and branch pushes; it has no AWS credentials or publishing permissions. To land a change on protected `main`, first push the commit to a branch and let the corpus-integrity check pass, then fast-forward or merge it. The CodeBuild status-snapshot deploy key is exempted from only this status-check rule so its automated `status.json` updates remain possible; it is still covered by the separate no-force-push/no-deletion rule.

See `docs/CODEBUILD_OPERATIONS.md` and `scripts/setup_codebuild_deploys.sh`.
