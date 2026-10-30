# Execution-time comparison: Drizzle and Sequelize

**How to read the percentages.** All percentages compare **mean execution time** (n = 12 per ORM and operation) and are relative to the
ORM being compared against:

- "**X% faster** than B" means the ORM needs X% less time than B: (B − ORM) / B.
- "**X% slower** than B" means the ORM needs X% more time than B: (ORM − B) / B.

Each figure is marked with the result of Dunn's test (Holm-adjusted, after a significant Holm-adjusted Kruskal–Wallis test; see [analysis methods](../src/analysis/README.md)):

- **sig.**: the difference is statistically significant.
- n.s.: not significant. Treat these as no difference.
- n.s. (KW): the Kruskal–Wallis test found no difference between any ORMs for this operation.

Only significant differences count as strengths or weaknesses. The machines are analysed separately. Absolute times differ between them and must not be compared.

Source: `../data/results/reference/intel/` and `../data/results/reference/mac/` (`descriptive_statistics.csv`, `kruskal_wallis.csv`, `dunn.csv`).

---

## 1. Drizzle

### Strengths

| Operation | Intel vs Prisma | Intel vs Sequelize | Mac vs Prisma | Mac vs Sequelize |
|---|---|---|---|---|
| read-owner-no-visits | **20.3% faster** (sig.) | **14.9% faster** (sig.) | **19.3% faster** (sig.) | **13.1% faster** (sig.) |
| read-owner-populated | **20.7% faster** (sig.) | **15.6% faster** (sig.) | **20.1% faster** (sig.) | **13.9% faster** (sig.) |
| read-pet-populated | **21.3% faster** (sig.) | **5.9% faster** (sig.) | **11.8% faster** (sig.) | 1.5% faster (n.s.) |
| create-pet-populated | **3.2% faster** (sig.) | **6.6% faster** (sig.) | **8.9% faster** (sig.) | **9.5% faster** (sig.) |
| delete-owner-visits-no-visits | **9.0% faster** (sig.) | **8.9% faster** (sig.) | **4.7% faster** (sig.) | **19.5% faster** (sig.) |
| create-owner-populated | **7.4% faster** (sig.) | 1.2% slower (n.s.) | **28.1% faster** (sig.) | 7.2% faster (n.s.) |
| update-pet-populated | **6.9% faster** (sig.) | **4.7% faster** (sig.) | **37.4% faster** (sig.) | 1.7% faster (n.s.) |

- **Reads of an owner with relations are Drizzle's clearest advantage.** It is about 20% faster than Prisma and 13–16% faster than Sequelize, significantly, on both machines.
- **`create-pet-populated` and `delete-owner-visits-no-visits`:** Drizzle is significantly faster than both other ORMs on both machines.
- **The largest single gaps are against Prisma on the Mac:** 37.4% faster for `update-pet-populated` and 28.1% faster for `create-owner-populated`.

### Weaknesses

| Operation | Intel vs Prisma | Intel vs Sequelize | Mac vs Prisma | Mac vs Sequelize |
|---|---|---|---|---|
| delete-owner-visits-no-pets | **8.7% faster** (sig.) | **11.0% slower** (sig.) | 5.1% faster (n.s.) | 7.1% slower (n.s.) |
| read-owner-no-pets | **11.0% faster** (sig.) | 0.1% faster (n.s.) | **2.7% faster** (sig.) | **6.0% slower** (sig.) |
| update-owner-no-pets | **5.2% faster** (sig.) | 2.7% slower (n.s.) | **9.9% faster** (sig.) | 3.0% faster (n.s.) |
| update-owner-no-visits | **7.9% faster** (sig.) | 2.0% slower (n.s.) | 5.8% faster (n.s. (KW)) | 2.6% faster (n.s. (KW)) |

- **Drizzle is never significantly slower than Prisma**, in any of the 14 operations on either machine.
- **Its only significant weaknesses are against Sequelize, in operations on owners without pets:**
  - `delete-owner-visits-no-pets` on Intel: 11.0% slower.
  - `read-owner-no-pets` on the Mac: 6.0% slower.
- **Owner updates on Intel:** Drizzle's mean time is 0.8–2.7% above Sequelize's, but none of these differences is significant.

### Overall (geometric mean of the per-operation ratios over all 14 operations)

| | Intel | Mac |
|---|---|---|
| vs Prisma | 9.6% faster; significantly faster in 12 / 14, slower in 0 | 12.8% faster; significantly faster in 10 / 14, slower in 0 |
| vs Sequelize | 3.1% faster; significantly faster in 6 / 14, slower in 1 | 5.8% faster; significantly faster in 6 / 14, slower in 1 |

---

## 2. Sequelize

### Strengths

| Operation | Intel vs Prisma | Intel vs Drizzle | Mac vs Prisma | Mac vs Drizzle |
|---|---|---|---|---|
| delete-owner-visits-no-pets | **17.8% faster** (sig.) | **9.9% faster** (sig.) | **11.3% faster** (sig.) | 6.6% faster (n.s.) |
| read-owner-no-pets | **10.9% faster** (sig.) | 0.1% slower (n.s.) | **8.2% faster** (sig.) | **5.6% faster** (sig.) |
| read-pet-populated | **16.4% faster** (sig.) | **6.3% slower** (sig.) | **10.5% faster** (sig.) | 1.5% slower (n.s.) |
| create-owner-populated | **8.4% faster** (sig.) | 1.2% faster (n.s.) | **22.5% faster** (sig.) | 7.8% slower (n.s.) |
| update-owner-no-pets | **7.7% faster** (sig.) | 2.6% faster (n.s.) | **7.1% faster** (sig.) | 3.1% slower (n.s.) |
| update-pet-populated | 2.3% faster (n.s.) | **4.9% slower** (sig.) | **36.3% faster** (sig.) | 1.8% slower (n.s.) |

- **Sequelize is faster than Prisma when deleting the visits of an owner without pets, reading a pet or an owner without pets, creating an owner, and updating an owner without pets.**
  These differences are significant on both machines: about 7–18% on Intel and 7–23% on the Mac. On Intel, Sequelize is also significantly faster than Prisma for the other two owner
  updates (7.5–9.7%). On the Mac, it is 36.3% faster than Prisma for `update-pet-populated`.
- **Owners without pets are where Sequelize beats Drizzle:**
  - `delete-owner-visits-no-pets` on Intel: 9.9% faster.
  - `read-owner-no-pets` on the Mac: 5.6% faster.

  These are its only significant wins over Drizzle.

### Weaknesses

| Operation | Intel vs Prisma | Intel vs Drizzle | Mac vs Prisma | Mac vs Drizzle |
|---|---|---|---|---|
| read-owner-no-visits | **6.3% faster** (sig.) | **17.5% slower** (sig.) | **7.1% faster** (sig.) | **15.1% slower** (sig.) |
| read-owner-populated | **6.1% faster** (sig.) | **18.4% slower** (sig.) | **7.2% faster** (sig.) | **16.2% slower** (sig.) |
| delete-owner-visits-no-visits | 0.1% faster (n.s.) | **9.8% slower** (sig.) | **18.4% slower** (sig.) | **24.2% slower** (sig.) |
| delete-owner-visits-populated | 1.5% slower (n.s. (KW)) | 2.4% slower (n.s. (KW)) | **14.3% slower** (sig.) | **16.0% slower** (sig.) |
| create-pet-populated | **3.7% slower** (sig.) | **7.1% slower** (sig.) | 0.7% slower (n.s.) | **10.5% slower** (sig.) |

- **Reads of an owner with relations are Sequelize's clearest weakness against Drizzle:** 15–18% slower, significantly, on both machines. It is still significantly faster than Prisma
  in these operations.
- **Deleting an owner's visits:** on the Mac, Sequelize is significantly the slowest ORM in both `delete-owner-visits-no-visits` (18.4% slower than Prisma, 24.2% slower than Drizzle)
  and `delete-owner-visits-populated` (14.3% and 16.0%). On Intel, it is significantly slower than Drizzle only in `delete-owner-visits-no-visits`.
- **Pet creation:** on Intel, Sequelize is significantly the slowest ORM in `create-pet-populated`. Over both machines, Prisma is significantly faster than Sequelize in only three operations: this one on Intel and the two owner-visit deletes on the Mac.

### Overall (geometric mean of the per-operation ratios over all 14 operations)

| | Intel | Mac |
|---|---|---|
| vs Prisma | 6.7% faster; significantly faster in 10 / 14, slower in 1 | 7.4% faster; significantly faster in 8 / 14, slower in 2 |
| vs Drizzle | 3.2% slower; significantly faster in 1 / 14, slower in 6 | 6.2% slower; significantly faster in 1 / 14, slower in 6 |

---

## 3. Summary

- **Drizzle** is the fastest ORM overall: about 10–13% faster than Prisma and 3–6% faster than Sequelize, as a geometric mean over operations. It is never significantly slower than Prisma.
  Its strengths are largest in reads with relations. Its only significant weaknesses are against Sequelize, in operations on owners without pets.
- **Sequelize** is about 7% faster than Prisma overall and is usually faster than Prisma in simple operations. It is significantly slower than Drizzle for reads with relations,
  and it is the slowest ORM for deleting an owner's visits on the Mac.
