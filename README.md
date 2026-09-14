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
6. ...

## MongoDB replica set

Production uses the single-node replica set `rs0`. Update
`deploy/docker-compose.production.yml`, which replaces the server's
`docker-compose.yml` on every deployment.

Provision a non-empty `mongo-keyfile` in the server deploy directory before the
first deployment, with mode `400` and ownership matching the MongoDB container
user (verify the UID/GID in the deployed image). Keep the existing keyfile on
subsequent deployments; never commit it. The workflow preserves it during cleanup
and excludes it from the source archive. A missing keyfile stops deployment
before cleanup; restore/provision it on the server before retrying.

Back up database data before converting an existing standalone deployment.
MongoDB restarts during conversion. Keep the Compose project name and `mongo_data`
volume unchanged. The healthcheck initializes an unconfigured replica set and
waits for a writable primary. Verify `db.hello()` reports `setName: "rs0"` and
`isWritablePrimary: true`, then exercise an application transaction.
