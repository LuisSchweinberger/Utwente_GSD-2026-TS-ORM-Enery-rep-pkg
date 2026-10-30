# Experiment setup

The original run settings and software versions are recorded in
`data/raw/{intel,mac}/experiment-42/manifest.json`.

| Property | Intel | Mac |
|---|---|---|
| CPU | Intel Core i7-6500U, 4 logical CPUs | Apple M4 Pro, 12 logical CPUs |
| Memory | Approximately 8 GB | 24 GiB |
| OS | CachyOS Linux, 7.2.9-1-cachyos | macOS 26.6.2 |
| Architecture | x86_64 | arm64 |
| Node.js | v26.10.0 | v24.9.0 |
| Python | 3.14.7 | 3.14.5 |
| PostgreSQL | 17.11, Alpine | 17.11, Alpine |
| Energy backend | RAPL | powermetrics + Zeus/IOReport |
| Power configuration | powersave governor | AC power |

Both runs used Prisma client 6.19.3, Sequelize 6.37.8 and Drizzle ORM 0.45.3.
The benchmark's `package-lock.json` records Node dependency versions;
`docker-compose.yml` uses the `postgres:17-alpine` image tag.

## Run settings

- Seed: 42; each trial increments the dataset seed by one.
- Trials: 12 per machine, each containing 14 tasks for each of the three ORMs.
- `SIZE=1000` owners per profile; `QUERY_COUNT=1000` requests per task.
- Energy sampling interval: 100 ms.
- Trial cooldown: 30 s; ORM cooldown: 10 s; idle measurement: 30 s.
- ORM order rotates; task order is shuffled per trial and shared across ORMs.

See [benchmark instructions](../src/benchmark/README.md) to configure a new run.
