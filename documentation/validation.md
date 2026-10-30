# Package validation

Validated locally on 2026-10-30 with macOS 26.6.2 arm64, Python 3.14.5 and Node.js
v24.9.0. Analysis dependency versions are pinned in
[`requirements-validation.txt`](../src/analysis/requirements-validation.txt).
They describe this validation run, not the original analysis environment.

| Check | Outcome |
|---|---|
| Archive SHA-256 and size verification | 7,484 files passed |
| Archived measurements | 504 valid per machine; no exclusions |
| Descriptive counts/means/medians | 126 rows per machine match observations |
| Statistical analysis rerun | Both machines completed |
| All 10 regenerated statistical CSVs vs references | Match at relative tolerance 1e-9, absolute 1e-12 |
| Box plot generation | 42 figures per machine generated |
| `npm ci --ignore-scripts --no-audit --no-fund` | Passed |
| `npm run prisma:generate` | Passed |
| `npm run typecheck` | Passed |
| `npm run test:dataset` | 2 tests passed |
| `npm run test:runner` | 37 tests passed |

The runner suite initially exposed references to the old analysis location and
an obsolete `output_name` attribute assertion. Only those test paths/assertions
were adapted; no benchmark execution or measurement implementation was changed.

Database integration tests, Docker startup and live energy experiments were
**not run**. PNG generation was checked, not byte-for-byte or visually compared.
No claim is made that this is an independent replication of the measurements.
