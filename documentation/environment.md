# Recorded environment and reproducibility limits

The authoritative records are each experiment's `manifest.json`, trial manifests,
and measurement reports. The table below summarizes their recorded values;
these are not independently verified hardware/software claims.

| Property | Intel experiment | Mac experiment |
|---|---|---|
| CPU | Intel Core i7-6500U, 4 logical CPUs | Apple M4 Pro, 12 logical CPUs |
| Memory | 8,168,050,688 bytes | 25,769,803,776 bytes |
| OS | CachyOS Linux, release 7.2.9-1-cachyos | macOS 26.6.2, Darwin 25.6.0 |
| Architecture | x86_64 | arm64 |
| Node.js | v26.10.0 | v24.9.0 |
| Python | 3.14.7 | 3.14.5 |
| PostgreSQL | 17.11, Alpine, x86_64 | 17.11, Alpine, aarch64 |
| Backend | RAPL | powermetrics + Zeus/IOReport |
| CPU governor / power | powersave | AC power, battery charged |

Both manifests record Prisma client 6.19.3, Sequelize 6.37.8, Drizzle ORM 0.45.3,
pg 8.23.0, Express 5.2.1 and tsx 4.23.15. The copied `package-lock.json` SHA-256
matches both experiment manifests:
`9248e49eb755e05faf74324b8dce6e9c4d83dc487eb8eea329f21d881242b4d9`.

Both runs used seed 42, 12 complete trials, SIZE=QUERY_COUNT=1000, 100 ms energy
sampling, 30 s trial cooldown, 10 s ORM cooldown and 30 s idle measurement.

## Limits

- Both archived experiments record `gitDirty: true` and different source
  revisions. The copied working tree is not proven byte-identical to either
  execution's source; matching dependency locks do not establish that.
- `documentation/source-provenance.json` records the source revision/dirty state
  at packaging time and original imported file hashes.
- `postgres:17-alpine` is a mutable image tag; original image digests were not
  recorded. A new run can resolve to a newer PostgreSQL build. No historical
  digest has been invented.
- Original Python analysis dependency versions were not recorded. Minimum
  requirements are preserved; a validation lock is not a historical lock.
- Machine-specific manifests contain hostnames and logs can contain local paths.
  Review these before public release; originals have not been silently redacted.
- Whole-host energy includes background activity and collector overhead. Intel
  package/DRAM and Apple's CPU/unified-memory estimates are not interchangeable.
- No full measurement rerun is implied by assembling or verifying this package.
