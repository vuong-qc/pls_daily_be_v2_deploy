# pls_daily_be_v2_deploy

Production deploy repo for `pls_daily_be_v2`.

This repository is synced from the source repo and is intended to hold:

- the production GitHub Actions workflow
- production Docker Compose files
- production Nginx templates
- the backend source that is built into the production image

Expected flow:

1. Work and test in the source repo.
2. Run `./scripts/sync_to_deploy_repo.sh /path/to/pls_daily_be_v2_deploy`.
3. Review the deploy repo diff.
4. Commit and push the deploy repo to `main`.
5. GitHub Actions in the deploy repo builds and deploys production.
