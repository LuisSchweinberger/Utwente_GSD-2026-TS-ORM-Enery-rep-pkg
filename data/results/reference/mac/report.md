# Statistical analysis: Apple Silicon Mac (macOS, powermetrics + Zeus)

Source: `results-mac/` (read-only). 12 trials, 14 operation types, 504 valid ORM x operation x trial observations; 0 excluded.

Significance level alpha = 0.05. All p-values are Holm-adjusted and significance is decided on the adjusted value: each assumption check and Kruskal-Wallis across the 42 tests of this machine, Dunn across the three ORM pairs of one test, Spearman across the 112 correlations of this machine.

## Metrics and units (original units, no conversion)

| Metric | Unit | Source |
|---|---|---|
| Execution time | ms | `timing.workloadElapsedMs` (controller monotonic clock, GO to DONE) |
| CPU energy consumption | J | powermetrics `cpu` domain (cpu_power sampler). Field `energyJ`. |
| Memory energy consumption | J | IOReport unified-memory Energy Model estimate via zeus-apple-silicon `dram_mj`; stored as J. Field `energyJ`. |

## Parametric assumption checks

Shapiro-Wilk on the residuals (normality) and Brown-Forsythe across the ORMs (equal variances); Holm-adjusted p-values, `*` marks a rejected assumption (adjusted p < 0.05).

| Metric | Normality rejected | Equal variances rejected |
|---|---|---|
| Execution time | 1 / 14 | 0 / 14 |
| CPU energy consumption | 0 / 14 | 0 / 14 |
| Memory energy consumption | 0 / 14 | 0 / 14 |

| Operation | Execution time Shapiro p_holm / B-F p_holm | CPU energy consumption Shapiro p_holm / B-F p_holm | Memory energy consumption Shapiro p_holm / B-F p_holm |
|---|---|---|---|
| create-owner-populated | 0.1965 / 1.0000 | 1.0000 / 1.0000 | 1.0000 / 1.0000 |
| create-pet-populated | 1.0000 / 1.0000 | 1.0000 / 1.0000 | 1.0000 / 1.0000 |
| delete-owner-visits-no-pets | 2.028e-04 * / 1.0000 | 1.0000 / 1.0000 | 1.0000 / 1.0000 |
| delete-owner-visits-no-visits | 1.0000 / 1.0000 | 1.0000 / 1.0000 | 1.0000 / 1.0000 |
| delete-owner-visits-populated | 1.0000 / 1.0000 | 1.0000 / 1.0000 | 1.0000 / 1.0000 |
| delete-visit-populated | 0.4105 / 1.0000 | 1.0000 / 1.0000 | 1.0000 / 1.0000 |
| read-owner-no-pets | 0.5552 / 1.0000 | 1.0000 / 1.0000 | 0.9697 / 1.0000 |
| read-owner-no-visits | 1.0000 / 1.0000 | 1.0000 / 1.0000 | 1.0000 / 1.0000 |
| read-owner-populated | 1.0000 / 1.0000 | 1.0000 / 1.0000 | 1.0000 / 1.0000 |
| read-pet-populated | 1.0000 / 1.0000 | 1.0000 / 1.0000 | 1.0000 / 1.0000 |
| update-owner-no-pets | 1.0000 / 1.0000 | 1.0000 / 1.0000 | 1.0000 / 1.0000 |
| update-owner-no-visits | 1.0000 / 1.0000 | 0.7732 / 1.0000 | 1.0000 / 1.0000 |
| update-owner-populated | 1.0000 / 1.0000 | 1.0000 / 1.0000 | 1.0000 / 1.0000 |
| update-pet-populated | 1.0000 / 0.1014 | 1.0000 / 1.0000 | 1.0000 / 1.0000 |

## Kruskal-Wallis overview

H statistic and Holm-adjusted p-value per operation; `*` marks adjusted p < 0.05.

| Operation | Execution time H (p_holm) | CPU energy consumption H (p_holm) | Memory energy consumption H (p_holm) |
|---|---|---|---|
| create-owner-populated | 27.11 (4.813e-05) * | 25.19 (1.152e-04) * | 25.81 (8.680e-05) * |
| create-pet-populated | 14.01 (0.0127) * | 11.90 (0.0278) * | 14.43 (0.0110) * |
| delete-owner-visits-no-pets | 13.75 (0.0134) * | 1.88 (0.3915) | 9.69 (0.0576) |
| delete-owner-visits-no-visits | 28.40 (2.652e-05) * | 23.65 (1.981e-04) * | 19.32 (0.0015) * |
| delete-owner-visits-populated | 23.44 (2.117e-04) * | 24.22 (1.654e-04) * | 19.55 (0.0014) * |
| delete-visit-populated | 6.01 (0.1981) | 5.95 (0.1981) | 6.55 (0.1895) |
| read-owner-no-pets | 27.03 (4.855e-05) * | 15.54 (0.0080) * | 7.04 (0.1772) |
| read-owner-no-visits | 31.14 (7.284e-06) * | 30.50 (9.529e-06) * | 17.23 (0.0038) * |
| read-owner-populated | 30.92 (7.916e-06) * | 27.59 (3.887e-05) * | 18.52 (0.0021) * |
| read-pet-populated | 24.89 (1.300e-04) * | 14.58 (0.0109) * | 15.40 (0.0082) * |
| update-owner-no-pets | 22.17 (3.842e-04) * | 24.60 (1.457e-04) * | 11.96 (0.0278) * |
| update-owner-no-visits | 9.87 (0.0576) | 13.44 (0.0145) * | 4.26 (0.2381) |
| update-owner-populated | 16.85 (0.0044) * | 15.26 (0.0083) * | 10.22 (0.0544) |
| update-pet-populated | 23.95 (1.762e-04) * | 24.29 (1.648e-04) * | 24.18 (1.654e-04) * |

## create-owner-populated

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 1288.7066 | 78.3166 | 1248.7605 | 1232.6821 | 1324.2792 | 1212.7987 | 1443.8366 |
| prisma | 12 | 1793.3738 | 45.3377 | 1787.9592 | 1762.4288 | 1800.1471 | 1739.4500 | 1908.6478 |
| sequelize | 12 | 1389.0617 | 54.1251 | 1383.6509 | 1343.5871 | 1416.8686 | 1320.4929 | 1503.8045 |

Kruskal-Wallis: H(2) = 27.105, epsilon² = 0.774, p = 1.301e-06, Holm-adjusted p = 4.813e-05 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 8.3333 | 30.5000 | 1248.7605 | 1787.9592 | 2.555e-07 | 7.664e-07 | yes |
| drizzle - sequelize | 8.3333 | 16.6667 | 1248.7605 | 1383.6509 | 0.0527 | 0.0527 | no |
| prisma - sequelize | 30.5000 | 16.6667 | 1787.9592 | 1383.6509 | 0.0013 | 0.0026 | yes |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 7.1931 | 0.4717 | 7.1300 | 6.8236 | 7.5054 | 6.5287 | 8.0317 |
| prisma | 12 | 10.0607 | 0.3352 | 10.0380 | 9.8525 | 10.0979 | 9.7238 | 11.0018 |
| sequelize | 12 | 7.6311 | 0.4733 | 7.5696 | 7.2342 | 7.9280 | 7.0792 | 8.4503 |

Kruskal-Wallis: H(2) = 25.191, epsilon² = 0.720, p = 3.388e-06, Holm-adjusted p = 1.152e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 9.5833 | 30.5000 | 7.1300 | 10.0380 | 1.156e-06 | 3.468e-06 | yes |
| drizzle - sequelize | 9.5833 | 15.4167 | 7.1300 | 7.5696 | 0.1750 | 0.1750 | no |
| prisma - sequelize | 30.5000 | 15.4167 | 10.0380 | 7.5696 | 4.535e-04 | 9.070e-04 | yes |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 0.3826 | 0.0247 | 0.3875 | 0.3750 | 0.4020 | 0.3380 | 0.4140 |
| prisma | 12 | 0.4911 | 0.0280 | 0.4900 | 0.4665 | 0.5152 | 0.4470 | 0.5290 |
| sequelize | 12 | 0.4109 | 0.0282 | 0.4175 | 0.3945 | 0.4295 | 0.3600 | 0.4500 |

Kruskal-Wallis: H(2) = 25.814, epsilon² = 0.738, p = 2.480e-06, Holm-adjusted p = 8.680e-05 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 8.9583 | 30.4167 | 0.3875 | 0.4900 | 6.040e-07 | 1.812e-06 | yes |
| drizzle - sequelize | 8.9583 | 16.1250 | 0.3875 | 0.4175 | 0.0956 | 0.0956 | no |
| prisma - sequelize | 30.4167 | 16.1250 | 0.4900 | 0.4175 | 8.893e-04 | 0.0018 | yes |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.9568 | 8.276e-20 | 9.187e-18 | yes |
| execution_time vs cpu_energy | drizzle | 12 | 0.7972 | 0.0019 | 0.1539 | no |
| execution_time vs cpu_energy | prisma | 12 | 0.8252 | 9.514e-04 | 0.0799 | no |
| execution_time vs cpu_energy | sequelize | 12 | 0.8392 | 6.428e-04 | 0.0546 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.7751 | 2.870e-08 | 2.985e-06 | yes |
| execution_time vs memory_energy | drizzle | 12 | -0.1298 | 0.6876 | 1.0000 | no |
| execution_time vs memory_energy | prisma | 12 | -0.1329 | 0.6806 | 1.0000 | no |
| execution_time vs memory_energy | sequelize | 12 | 0.2028 | 0.5273 | 1.0000 | no |

## create-pet-populated

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 600.7095 | 34.1432 | 598.5842 | 577.9435 | 616.1643 | 556.1697 | 673.6804 |
| prisma | 12 | 659.6595 | 35.6093 | 668.5098 | 655.3736 | 671.0518 | 587.2182 | 704.5113 |
| sequelize | 12 | 664.0264 | 28.6180 | 666.0962 | 642.1402 | 680.1524 | 609.2443 | 705.6595 |

Kruskal-Wallis: H(2) = 14.011, epsilon² = 0.400, p = 9.071e-04, Holm-adjusted p = 0.0127 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 9.2500 | 22.3333 | 598.5842 | 668.5098 | 0.0024 | 0.0047 | yes |
| drizzle - sequelize | 9.2500 | 23.9167 | 598.5842 | 666.0962 | 6.498e-04 | 0.0019 | yes |
| prisma - sequelize | 22.3333 | 23.9167 | 668.5098 | 666.0962 | 0.7128 | 0.7128 | no |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 2.7569 | 0.2009 | 2.7350 | 2.6398 | 2.8309 | 2.4569 | 3.1159 |
| prisma | 12 | 3.0812 | 0.1824 | 3.1611 | 2.9146 | 3.2026 | 2.7336 | 3.2962 |
| sequelize | 12 | 3.0154 | 0.2711 | 3.0189 | 2.7931 | 3.1131 | 2.6881 | 3.6400 |

Kruskal-Wallis: H(2) = 11.902, epsilon² = 0.340, p = 0.0026, Holm-adjusted p = 0.0278 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 10.4167 | 25.0000 | 2.7350 | 3.1611 | 6.975e-04 | 0.0021 | yes |
| drizzle - sequelize | 10.4167 | 20.0833 | 2.7350 | 3.0189 | 0.0246 | 0.0492 | yes |
| prisma - sequelize | 25.0000 | 20.0833 | 3.1611 | 3.0189 | 0.2530 | 0.2530 | no |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 0.1887 | 0.0148 | 0.1875 | 0.1800 | 0.1958 | 0.1650 | 0.2200 |
| prisma | 12 | 0.2074 | 0.0102 | 0.2110 | 0.2010 | 0.2152 | 0.1860 | 0.2170 |
| sequelize | 12 | 0.2167 | 0.0179 | 0.2180 | 0.2037 | 0.2295 | 0.1820 | 0.2420 |

Kruskal-Wallis: H(2) = 14.430, epsilon² = 0.412, p = 7.355e-04, Holm-adjusted p = 0.0110 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 9.4583 | 20.7083 | 0.1875 | 0.2110 | 0.0089 | 0.0177 | yes |
| drizzle - sequelize | 9.4583 | 25.3333 | 0.1875 | 0.2180 | 2.216e-04 | 6.649e-04 | yes |
| prisma - sequelize | 20.7083 | 25.3333 | 0.2110 | 0.2180 | 0.2820 | 0.2820 | no |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.2837 | 0.0936 | 1.0000 | no |
| execution_time vs cpu_energy | drizzle | 12 | -0.2727 | 0.3911 | 1.0000 | no |
| execution_time vs cpu_energy | prisma | 12 | -0.2657 | 0.4038 | 1.0000 | no |
| execution_time vs cpu_energy | sequelize | 12 | 0.1049 | 0.7456 | 1.0000 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.7256 | 5.514e-07 | 5.625e-05 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.7461 | 0.0053 | 0.4104 | no |
| execution_time vs memory_energy | prisma | 12 | 0.1090 | 0.7360 | 1.0000 | no |
| execution_time vs memory_energy | sequelize | 12 | 0.5534 | 0.0620 | 1.0000 | no |

## delete-owner-visits-no-pets

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 636.5648 | 31.0068 | 623.5555 | 621.0688 | 640.0291 | 603.5146 | 697.1977 |
| prisma | 12 | 670.5107 | 14.6593 | 669.7903 | 662.5078 | 675.0057 | 646.9649 | 706.0745 |
| sequelize | 12 | 594.6123 | 48.5071 | 577.4326 | 570.4486 | 585.6635 | 555.6847 | 698.8232 |

Kruskal-Wallis: H(2) = 13.749, epsilon² = 0.393, p = 0.0010, Holm-adjusted p = 0.0134 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 19.0833 | 26.1667 | 623.5555 | 669.7903 | 0.0996 | 0.0996 | no |
| drizzle - sequelize | 19.0833 | 10.2500 | 623.5555 | 577.4326 | 0.0400 | 0.0800 | no |
| prisma - sequelize | 26.1667 | 10.2500 | 669.7903 | 577.4326 | 2.151e-04 | 6.454e-04 | yes |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 3.1798 | 0.2817 | 3.1164 | 3.0169 | 3.4124 | 2.7196 | 3.7055 |
| prisma | 12 | 3.0606 | 0.2666 | 3.0266 | 2.8738 | 3.1209 | 2.7740 | 3.7784 |
| sequelize | 12 | 3.0690 | 0.2938 | 3.0539 | 2.9037 | 3.2167 | 2.6586 | 3.6490 |

Kruskal-Wallis: H(2) = 1.875, epsilon² = 0.054, p = 0.3915, Holm-adjusted p = 0.3915 -> no significant difference.

Dunn's test not run (Kruskal-Wallis not significant after adjustment).

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 0.1927 | 0.0179 | 0.1900 | 0.1842 | 0.1990 | 0.1720 | 0.2400 |
| prisma | 12 | 0.2007 | 0.0141 | 0.2000 | 0.1895 | 0.2122 | 0.1750 | 0.2200 |
| sequelize | 12 | 0.1800 | 0.0150 | 0.1760 | 0.1693 | 0.1862 | 0.1620 | 0.2100 |

Kruskal-Wallis: H(2) = 9.693, epsilon² = 0.277, p = 0.0079, Holm-adjusted p = 0.0576 -> no significant difference.

Dunn's test not run (Kruskal-Wallis not significant after adjustment).

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.2888 | 0.0876 | 1.0000 | no |
| execution_time vs cpu_energy | drizzle | 12 | 0.2657 | 0.4038 | 1.0000 | no |
| execution_time vs cpu_energy | prisma | 12 | 0.1049 | 0.7456 | 1.0000 | no |
| execution_time vs cpu_energy | sequelize | 12 | 0.3776 | 0.2262 | 1.0000 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.8160 | 1.320e-09 | 1.399e-07 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.8476 | 4.978e-04 | 0.0433 | yes |
| execution_time vs memory_energy | prisma | 12 | 0.3853 | 0.2161 | 1.0000 | no |
| execution_time vs memory_energy | sequelize | 12 | 0.3818 | 0.2207 | 1.0000 | no |

## delete-owner-visits-no-visits

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 779.4005 | 21.3660 | 780.2665 | 765.4816 | 795.9240 | 745.4800 | 813.4380 |
| prisma | 12 | 817.4823 | 23.2687 | 814.8403 | 802.5261 | 829.4724 | 785.9831 | 870.3048 |
| sequelize | 12 | 968.2031 | 21.3766 | 970.6381 | 948.3536 | 978.7240 | 939.1752 | 1004.4792 |

Kruskal-Wallis: H(2) = 28.402, epsilon² = 0.811, p = 6.800e-07, Holm-adjusted p = 2.652e-05 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 7.6667 | 17.3333 | 780.2665 | 814.8403 | 0.0246 | 0.0246 | yes |
| drizzle - sequelize | 7.6667 | 30.5000 | 780.2665 | 970.6381 | 1.104e-07 | 3.313e-07 | yes |
| prisma - sequelize | 17.3333 | 30.5000 | 814.8403 | 970.6381 | 0.0022 | 0.0044 | yes |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 4.2487 | 0.1772 | 4.2269 | 4.1100 | 4.3293 | 4.0479 | 4.6371 |
| prisma | 12 | 4.1598 | 0.3023 | 4.1780 | 3.9751 | 4.2643 | 3.6692 | 4.7282 |
| sequelize | 12 | 5.3489 | 0.1975 | 5.2966 | 5.2412 | 5.4511 | 5.0486 | 5.7465 |

Kruskal-Wallis: H(2) = 23.646, epsilon² = 0.676, p = 7.335e-06, Holm-adjusted p = 1.981e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 13.6667 | 11.3333 | 4.2269 | 4.1780 | 0.5875 | 0.5875 | no |
| drizzle - sequelize | 13.6667 | 30.5000 | 4.2269 | 5.2966 | 9.090e-05 | 1.818e-04 | yes |
| prisma - sequelize | 11.3333 | 30.5000 | 4.1780 | 5.2966 | 8.344e-06 | 2.503e-05 | yes |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 0.2278 | 0.0174 | 0.2270 | 0.2155 | 0.2412 | 0.2040 | 0.2620 |
| prisma | 12 | 0.2380 | 0.0212 | 0.2310 | 0.2228 | 0.2605 | 0.2120 | 0.2690 |
| sequelize | 12 | 0.2799 | 0.0185 | 0.2795 | 0.2652 | 0.2947 | 0.2550 | 0.3060 |

Kruskal-Wallis: H(2) = 19.315, epsilon² = 0.552, p = 6.394e-05, Holm-adjusted p = 0.0015 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 11.3333 | 14.9583 | 0.2270 | 0.2310 | 0.3992 | 0.3992 | no |
| drizzle - sequelize | 11.3333 | 29.2083 | 0.2270 | 0.2795 | 3.226e-05 | 9.677e-05 | yes |
| prisma - sequelize | 14.9583 | 29.2083 | 0.2310 | 0.2795 | 9.200e-04 | 0.0018 | yes |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.6605 | 1.167e-05 | 0.0011 | yes |
| execution_time vs cpu_energy | drizzle | 12 | 0.2168 | 0.4986 | 1.0000 | no |
| execution_time vs cpu_energy | prisma | 12 | -0.0280 | 0.9312 | 1.0000 | no |
| execution_time vs cpu_energy | sequelize | 12 | -0.0909 | 0.7787 | 1.0000 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.7515 | 1.275e-07 | 1.313e-05 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.4685 | 0.1245 | 1.0000 | no |
| execution_time vs memory_energy | prisma | 12 | 0.6993 | 0.0114 | 0.8644 | no |
| execution_time vs memory_energy | sequelize | 12 | -0.2732 | 0.3902 | 1.0000 | no |

## delete-owner-visits-populated

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 791.1200 | 20.5320 | 781.2491 | 777.9819 | 811.2554 | 760.2725 | 823.6714 |
| prisma | 12 | 802.8491 | 38.5865 | 817.1143 | 758.4292 | 828.7390 | 748.3637 | 858.6498 |
| sequelize | 12 | 917.5835 | 37.2615 | 927.5215 | 885.9688 | 939.2506 | 858.0505 | 973.7059 |

Kruskal-Wallis: H(2) = 23.437, epsilon² = 0.670, p = 8.142e-06, Holm-adjusted p = 2.117e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 11.1667 | 13.9167 | 781.2491 | 817.1143 | 0.5226 | 0.5226 | no |
| drizzle - sequelize | 11.1667 | 30.4167 | 781.2491 | 927.5215 | 7.622e-06 | 2.287e-05 | yes |
| prisma - sequelize | 13.9167 | 30.4167 | 817.1143 | 927.5215 | 1.250e-04 | 2.499e-04 | yes |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 4.1107 | 0.2249 | 4.1375 | 3.9956 | 4.2576 | 3.6984 | 4.4299 |
| prisma | 12 | 3.9993 | 0.1741 | 4.0389 | 3.8494 | 4.1339 | 3.6797 | 4.2302 |
| sequelize | 12 | 4.9929 | 0.3376 | 4.9964 | 4.7325 | 5.1299 | 4.5103 | 5.7164 |

Kruskal-Wallis: H(2) = 24.216, epsilon² = 0.692, p = 5.515e-06, Holm-adjusted p = 1.654e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 14.5000 | 10.5000 | 4.1375 | 4.0389 | 0.3524 | 0.3524 | no |
| drizzle - sequelize | 14.5000 | 30.5000 | 4.1375 | 4.9964 | 1.993e-04 | 3.986e-04 | yes |
| prisma - sequelize | 10.5000 | 30.5000 | 4.0389 | 4.9964 | 3.321e-06 | 9.963e-06 | yes |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 0.2336 | 0.0142 | 0.2290 | 0.2235 | 0.2430 | 0.2160 | 0.2580 |
| prisma | 12 | 0.2342 | 0.0167 | 0.2355 | 0.2230 | 0.2472 | 0.2030 | 0.2560 |
| sequelize | 12 | 0.2707 | 0.0173 | 0.2705 | 0.2622 | 0.2815 | 0.2330 | 0.3000 |

Kruskal-Wallis: H(2) = 19.548, epsilon² = 0.559, p = 5.691e-05, Holm-adjusted p = 0.0014 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 12.5417 | 13.5000 | 0.2290 | 0.2355 | 0.8236 | 0.8236 | no |
| drizzle - sequelize | 12.5417 | 29.4583 | 0.2290 | 0.2705 | 8.300e-05 | 2.490e-04 | yes |
| prisma - sequelize | 13.5000 | 29.4583 | 0.2355 | 0.2705 | 2.051e-04 | 4.102e-04 | yes |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.7161 | 9.089e-07 | 9.180e-05 | yes |
| execution_time vs cpu_energy | drizzle | 12 | 0.2797 | 0.3786 | 1.0000 | no |
| execution_time vs cpu_energy | prisma | 12 | 0.0909 | 0.7787 | 1.0000 | no |
| execution_time vs cpu_energy | sequelize | 12 | 0.4825 | 0.1121 | 1.0000 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.6972 | 2.302e-06 | 2.279e-04 | yes |
| execution_time vs memory_energy | drizzle | 12 | -0.1263 | 0.6957 | 1.0000 | no |
| execution_time vs memory_energy | prisma | 12 | 0.3217 | 0.3079 | 1.0000 | no |
| execution_time vs memory_energy | sequelize | 12 | 0.2028 | 0.5273 | 1.0000 | no |

## delete-visit-populated

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 516.4569 | 36.2535 | 525.2930 | 481.3385 | 541.5735 | 465.3316 | 570.7484 |
| prisma | 12 | 555.9559 | 42.0178 | 573.2270 | 509.4308 | 582.5623 | 487.6510 | 605.2565 |
| sequelize | 12 | 520.2016 | 27.9316 | 529.2401 | 515.7666 | 536.3243 | 462.2093 | 548.8082 |

Kruskal-Wallis: H(2) = 6.011, epsilon² = 0.172, p = 0.0495, Holm-adjusted p = 0.1981 -> no significant difference.

Dunn's test not run (Kruskal-Wallis not significant after adjustment).

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 2.5094 | 0.1514 | 2.4998 | 2.3834 | 2.5763 | 2.3349 | 2.8819 |
| prisma | 12 | 2.6633 | 0.2037 | 2.6454 | 2.5069 | 2.8010 | 2.3903 | 2.9865 |
| sequelize | 12 | 2.4814 | 0.1858 | 2.4655 | 2.3575 | 2.5405 | 2.2293 | 2.9415 |

Kruskal-Wallis: H(2) = 5.950, epsilon² = 0.170, p = 0.0510, Holm-adjusted p = 0.1981 -> no significant difference.

Dunn's test not run (Kruskal-Wallis not significant after adjustment).

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 0.1607 | 0.0127 | 0.1570 | 0.1535 | 0.1678 | 0.1430 | 0.1860 |
| prisma | 12 | 0.1735 | 0.0095 | 0.1745 | 0.1693 | 0.1800 | 0.1540 | 0.1850 |
| sequelize | 12 | 0.1677 | 0.0116 | 0.1670 | 0.1595 | 0.1755 | 0.1490 | 0.1890 |

Kruskal-Wallis: H(2) = 6.545, epsilon² = 0.187, p = 0.0379, Holm-adjusted p = 0.1895 -> no significant difference.

Dunn's test not run (Kruskal-Wallis not significant after adjustment).

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.1992 | 0.2441 | 1.0000 | no |
| execution_time vs cpu_energy | drizzle | 12 | -0.0280 | 0.9312 | 1.0000 | no |
| execution_time vs cpu_energy | prisma | 12 | 0.1608 | 0.6175 | 1.0000 | no |
| execution_time vs cpu_energy | sequelize | 12 | -0.2657 | 0.4038 | 1.0000 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.6196 | 5.583e-05 | 0.0051 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.6084 | 0.0358 | 1.0000 | no |
| execution_time vs memory_energy | prisma | 12 | 0.7622 | 0.0040 | 0.3121 | no |
| execution_time vs memory_energy | sequelize | 12 | 0.1119 | 0.7292 | 1.0000 | no |

## read-owner-no-pets

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 948.9012 | 16.6614 | 949.6351 | 935.8889 | 957.2985 | 926.5493 | 985.8862 |
| prisma | 12 | 975.6397 | 15.4811 | 979.3340 | 959.7006 | 989.1444 | 958.2461 | 995.7051 |
| sequelize | 12 | 895.4114 | 22.7093 | 887.9521 | 878.7922 | 909.3770 | 869.8781 | 941.7330 |

Kruskal-Wallis: H(2) = 27.033, epsilon² = 0.772, p = 1.349e-06, Holm-adjusted p = 4.855e-05 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 19.1667 | 29.3333 | 949.6351 | 979.3340 | 0.0181 | 0.0181 | yes |
| drizzle - sequelize | 19.1667 | 7.0000 | 949.6351 | 887.9521 | 0.0047 | 0.0093 | yes |
| prisma - sequelize | 29.3333 | 7.0000 | 979.3340 | 887.9521 | 2.076e-07 | 6.228e-07 | yes |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 5.1537 | 0.2766 | 5.1026 | 4.9608 | 5.2334 | 4.8484 | 5.8437 |
| prisma | 12 | 4.8578 | 0.2364 | 4.8380 | 4.7369 | 5.0317 | 4.4327 | 5.3072 |
| sequelize | 12 | 4.6607 | 0.2335 | 4.6056 | 4.4856 | 4.8125 | 4.4012 | 5.0970 |

Kruskal-Wallis: H(2) = 15.538, epsilon² = 0.444, p = 4.227e-04, Holm-adjusted p = 0.0080 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 27.5000 | 17.3333 | 5.1026 | 4.8380 | 0.0181 | 0.0362 | yes |
| drizzle - sequelize | 27.5000 | 10.6667 | 5.1026 | 4.6056 | 9.090e-05 | 2.727e-04 | yes |
| prisma - sequelize | 17.3333 | 10.6667 | 4.8380 | 4.6056 | 0.1211 | 0.1211 | no |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 0.2787 | 0.0161 | 0.2780 | 0.2668 | 0.2937 | 0.2550 | 0.3020 |
| prisma | 12 | 0.2777 | 0.0156 | 0.2790 | 0.2620 | 0.2885 | 0.2540 | 0.2990 |
| sequelize | 12 | 0.2605 | 0.0157 | 0.2640 | 0.2475 | 0.2732 | 0.2350 | 0.2790 |

Kruskal-Wallis: H(2) = 7.044, epsilon² = 0.201, p = 0.0295, Holm-adjusted p = 0.1772 -> no significant difference.

Dunn's test not run (Kruskal-Wallis not significant after adjustment).

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.3606 | 0.0307 | 1.0000 | no |
| execution_time vs cpu_energy | drizzle | 12 | 0.6713 | 0.0168 | 1.0000 | no |
| execution_time vs cpu_energy | prisma | 12 | -0.0629 | 0.8459 | 1.0000 | no |
| execution_time vs cpu_energy | sequelize | 12 | 0.3986 | 0.1993 | 1.0000 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.4591 | 0.0049 | 0.3783 | no |
| execution_time vs memory_energy | drizzle | 12 | 0.5919 | 0.0426 | 1.0000 | no |
| execution_time vs memory_energy | prisma | 12 | -0.2487 | 0.4357 | 1.0000 | no |
| execution_time vs memory_energy | sequelize | 12 | 0.5044 | 0.0945 | 1.0000 | no |

## read-owner-no-visits

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 1371.0352 | 26.4789 | 1362.0273 | 1351.3589 | 1384.5472 | 1345.9010 | 1422.9676 |
| prisma | 12 | 1698.3404 | 25.8079 | 1698.5382 | 1689.0746 | 1712.8358 | 1648.4989 | 1741.3704 |
| sequelize | 12 | 1577.4278 | 25.0825 | 1579.1585 | 1557.6652 | 1588.4460 | 1545.7569 | 1634.3236 |

Kruskal-Wallis: H(2) = 31.135, epsilon² = 0.890, p = 1.734e-07, Holm-adjusted p = 7.284e-06 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 6.5000 | 30.5000 | 1362.0273 | 1698.5382 | 2.407e-08 | 7.220e-08 | yes |
| drizzle - sequelize | 6.5000 | 18.5000 | 1362.0273 | 1579.1585 | 0.0053 | 0.0105 | yes |
| prisma - sequelize | 30.5000 | 18.5000 | 1698.5382 | 1579.1585 | 0.0053 | 0.0105 | yes |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 7.7519 | 0.3146 | 7.6418 | 7.5509 | 7.9492 | 7.3576 | 8.3999 |
| prisma | 12 | 9.5575 | 0.2628 | 9.5908 | 9.4135 | 9.7109 | 9.0855 | 9.9337 |
| sequelize | 12 | 8.8937 | 0.2361 | 8.9670 | 8.6900 | 9.0875 | 8.5149 | 9.1910 |

Kruskal-Wallis: H(2) = 30.500, epsilon² = 0.871, p = 2.382e-07, Holm-adjusted p = 9.529e-06 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 6.5000 | 30.2500 | 7.6418 | 9.5908 | 3.356e-08 | 1.007e-07 | yes |
| drizzle - sequelize | 6.5000 | 18.7500 | 7.6418 | 8.9670 | 0.0044 | 0.0088 | yes |
| prisma - sequelize | 30.2500 | 18.7500 | 9.5908 | 8.9670 | 0.0075 | 0.0088 | yes |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 0.3833 | 0.0327 | 0.3765 | 0.3575 | 0.3962 | 0.3470 | 0.4440 |
| prisma | 12 | 0.4612 | 0.0371 | 0.4555 | 0.4317 | 0.4835 | 0.4170 | 0.5340 |
| sequelize | 12 | 0.4513 | 0.0349 | 0.4590 | 0.4170 | 0.4855 | 0.4040 | 0.4980 |

Kruskal-Wallis: H(2) = 17.230, epsilon² = 0.492, p = 1.814e-04, Holm-adjusted p = 0.0038 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 8.2917 | 24.8333 | 0.3765 | 0.4555 | 1.199e-04 | 3.597e-04 | yes |
| drizzle - sequelize | 8.2917 | 22.3750 | 0.3765 | 0.4590 | 0.0011 | 0.0021 | yes |
| prisma - sequelize | 24.8333 | 22.3750 | 0.4555 | 0.4590 | 0.5676 | 0.5676 | no |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.9601 | 2.160e-20 | 2.419e-18 | yes |
| execution_time vs cpu_energy | drizzle | 12 | 0.9161 | 2.843e-05 | 0.0027 | yes |
| execution_time vs cpu_energy | prisma | 12 | 0.5664 | 0.0548 | 1.0000 | no |
| execution_time vs cpu_energy | sequelize | 12 | 0.5245 | 0.0800 | 1.0000 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.5953 | 1.282e-04 | 0.0117 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.2098 | 0.5128 | 1.0000 | no |
| execution_time vs memory_energy | prisma | 12 | -0.2098 | 0.5128 | 1.0000 | no |
| execution_time vs memory_energy | sequelize | 12 | -0.1646 | 0.6092 | 1.0000 | no |

## read-owner-populated

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 1369.5011 | 27.1940 | 1360.4512 | 1356.5481 | 1375.2335 | 1343.0758 | 1438.0620 |
| prisma | 12 | 1714.1893 | 24.7980 | 1715.2948 | 1701.5313 | 1728.7217 | 1670.1322 | 1759.3639 |
| sequelize | 12 | 1591.3384 | 40.7733 | 1580.5122 | 1558.5721 | 1618.0625 | 1538.4090 | 1679.6300 |

Kruskal-Wallis: H(2) = 30.920, epsilon² = 0.883, p = 1.931e-07, Holm-adjusted p = 7.916e-06 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 6.5000 | 30.4167 | 1360.4512 | 1715.2948 | 2.690e-08 | 8.070e-08 | yes |
| drizzle - sequelize | 6.5000 | 18.5833 | 1360.4512 | 1580.5122 | 0.0050 | 0.0099 | yes |
| prisma - sequelize | 30.4167 | 18.5833 | 1715.2948 | 1580.5122 | 0.0059 | 0.0099 | yes |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 7.6941 | 0.3203 | 7.6567 | 7.4555 | 7.8850 | 7.2715 | 8.3354 |
| prisma | 12 | 9.4909 | 0.3281 | 9.3826 | 9.2759 | 9.6737 | 9.0213 | 10.0242 |
| sequelize | 12 | 8.8872 | 0.4005 | 8.9822 | 8.5950 | 9.1650 | 8.2435 | 9.4688 |

Kruskal-Wallis: H(2) = 27.586, epsilon² = 0.788, p = 1.023e-06, Holm-adjusted p = 3.887e-05 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 6.6667 | 29.1667 | 7.6567 | 9.3826 | 1.685e-07 | 5.054e-07 | yes |
| drizzle - sequelize | 6.6667 | 19.6667 | 7.6567 | 8.9822 | 0.0025 | 0.0050 | yes |
| prisma - sequelize | 29.1667 | 19.6667 | 9.3826 | 8.9822 | 0.0272 | 0.0272 | yes |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 0.3892 | 0.0295 | 0.3825 | 0.3700 | 0.4037 | 0.3500 | 0.4430 |
| prisma | 12 | 0.4585 | 0.0237 | 0.4630 | 0.4353 | 0.4808 | 0.4260 | 0.4880 |
| sequelize | 12 | 0.4482 | 0.0310 | 0.4465 | 0.4217 | 0.4700 | 0.4060 | 0.5070 |

Kruskal-Wallis: H(2) = 18.521, epsilon² = 0.529, p = 9.509e-05, Holm-adjusted p = 0.0021 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 8.0000 | 25.4583 | 0.3825 | 0.4630 | 4.901e-05 | 1.470e-04 | yes |
| drizzle - sequelize | 8.0000 | 22.0417 | 0.3825 | 0.4465 | 0.0011 | 0.0022 | yes |
| prisma - sequelize | 25.4583 | 22.0417 | 0.4630 | 0.4465 | 0.4268 | 0.4268 | no |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.9158 | 4.973e-15 | 5.421e-13 | yes |
| execution_time vs cpu_energy | drizzle | 12 | 0.4755 | 0.1182 | 1.0000 | no |
| execution_time vs cpu_energy | prisma | 12 | 0.8252 | 9.514e-04 | 0.0799 | no |
| execution_time vs cpu_energy | sequelize | 12 | 0.4056 | 0.1908 | 1.0000 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.5765 | 2.332e-04 | 0.0208 | yes |
| execution_time vs memory_energy | drizzle | 12 | -0.0070 | 0.9828 | 1.0000 | no |
| execution_time vs memory_energy | prisma | 12 | -0.4343 | 0.1583 | 1.0000 | no |
| execution_time vs memory_energy | sequelize | 12 | -0.3636 | 0.2453 | 1.0000 | no |

## read-pet-populated

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 486.6816 | 11.2462 | 485.0285 | 479.9036 | 491.0070 | 472.3323 | 516.1741 |
| prisma | 12 | 551.8502 | 11.0664 | 554.2057 | 548.1024 | 557.8466 | 525.6806 | 568.3995 |
| sequelize | 12 | 493.9474 | 10.4323 | 493.9132 | 486.3371 | 499.4892 | 476.5176 | 512.4707 |

Kruskal-Wallis: H(2) = 24.889, epsilon² = 0.711, p = 3.940e-06, Holm-adjusted p = 1.300e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 9.8333 | 30.5000 | 485.0285 | 554.2057 | 1.548e-06 | 4.645e-06 | yes |
| drizzle - sequelize | 9.8333 | 15.1667 | 485.0285 | 493.9132 | 0.2150 | 0.2150 | no |
| prisma - sequelize | 30.5000 | 15.1667 | 554.2057 | 493.9132 | 3.640e-04 | 7.279e-04 | yes |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 2.2780 | 0.2047 | 2.3261 | 2.1158 | 2.4646 | 1.9331 | 2.5084 |
| prisma | 12 | 2.6917 | 0.2829 | 2.6750 | 2.4655 | 2.8498 | 2.2783 | 3.2243 |
| sequelize | 12 | 2.2250 | 0.2059 | 2.2057 | 2.0337 | 2.3804 | 1.9579 | 2.5207 |

Kruskal-Wallis: H(2) = 14.578, epsilon² = 0.417, p = 6.830e-04, Holm-adjusted p = 0.0109 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 14.7500 | 27.9167 | 2.3261 | 2.6750 | 0.0022 | 0.0044 | yes |
| drizzle - sequelize | 14.7500 | 12.8333 | 2.3261 | 2.2057 | 0.6559 | 0.6559 | no |
| prisma - sequelize | 27.9167 | 12.8333 | 2.6750 | 2.2057 | 4.535e-04 | 0.0014 | yes |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 0.1529 | 0.0082 | 0.1490 | 0.1470 | 0.1575 | 0.1430 | 0.1690 |
| prisma | 12 | 0.1726 | 0.0118 | 0.1720 | 0.1620 | 0.1775 | 0.1590 | 0.2000 |
| sequelize | 12 | 0.1586 | 0.0106 | 0.1545 | 0.1517 | 0.1653 | 0.1430 | 0.1800 |

Kruskal-Wallis: H(2) = 15.400, epsilon² = 0.440, p = 4.528e-04, Holm-adjusted p = 0.0082 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 11.0000 | 27.6250 | 0.1490 | 0.1720 | 1.092e-04 | 3.276e-04 | yes |
| drizzle - sequelize | 11.0000 | 16.8750 | 0.1490 | 0.1545 | 0.1715 | 0.1715 | no |
| prisma - sequelize | 27.6250 | 16.8750 | 0.1720 | 0.1545 | 0.0124 | 0.0247 | yes |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.3951 | 0.0171 | 1.0000 | no |
| execution_time vs cpu_energy | drizzle | 12 | -0.2168 | 0.4986 | 1.0000 | no |
| execution_time vs cpu_energy | prisma | 12 | 0.4755 | 0.1182 | 1.0000 | no |
| execution_time vs cpu_energy | sequelize | 12 | -0.5594 | 0.0586 | 1.0000 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.6701 | 7.816e-06 | 7.581e-04 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.1587 | 0.6222 | 1.0000 | no |
| execution_time vs memory_energy | prisma | 12 | -0.3853 | 0.2161 | 1.0000 | no |
| execution_time vs memory_energy | sequelize | 12 | 0.5835 | 0.0464 | 1.0000 | no |

## update-owner-no-pets

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 1277.0835 | 35.9864 | 1274.0385 | 1243.8188 | 1309.8982 | 1225.1088 | 1327.7715 |
| prisma | 12 | 1416.9429 | 72.9963 | 1382.4658 | 1361.2703 | 1478.5036 | 1340.8815 | 1532.2728 |
| sequelize | 12 | 1316.2049 | 37.9794 | 1312.9851 | 1286.2061 | 1342.6878 | 1265.1777 | 1379.7002 |

Kruskal-Wallis: H(2) = 22.167, epsilon² = 0.633, p = 1.537e-05, Holm-adjusted p = 3.842e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 9.4167 | 29.4167 | 1274.0385 | 1382.4658 | 3.321e-06 | 9.963e-06 | yes |
| drizzle - sequelize | 9.4167 | 16.6667 | 1274.0385 | 1312.9851 | 0.0919 | 0.0919 | no |
| prisma - sequelize | 29.4167 | 16.6667 | 1382.4658 | 1312.9851 | 0.0030 | 0.0061 | yes |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 6.9805 | 0.2343 | 6.9830 | 6.8692 | 7.1166 | 6.5572 | 7.3836 |
| prisma | 12 | 8.0330 | 0.4359 | 7.9552 | 7.6825 | 8.2962 | 7.5649 | 9.0401 |
| sequelize | 12 | 7.2594 | 0.2505 | 7.1622 | 7.0851 | 7.3437 | 7.0686 | 7.9012 |

Kruskal-Wallis: H(2) = 24.599, epsilon² = 0.703, p = 4.554e-06, Holm-adjusted p = 1.457e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 9.0833 | 30.0833 | 6.9830 | 7.9552 | 1.048e-06 | 3.144e-06 | yes |
| drizzle - sequelize | 9.0833 | 16.3333 | 6.9830 | 7.1622 | 0.0919 | 0.0919 | no |
| prisma - sequelize | 30.0833 | 16.3333 | 7.9552 | 7.1622 | 0.0014 | 0.0028 | yes |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 0.3625 | 0.0239 | 0.3595 | 0.3488 | 0.3765 | 0.3260 | 0.4030 |
| prisma | 12 | 0.4073 | 0.0255 | 0.4130 | 0.3910 | 0.4197 | 0.3590 | 0.4430 |
| sequelize | 12 | 0.3812 | 0.0337 | 0.3855 | 0.3572 | 0.3972 | 0.3350 | 0.4530 |

Kruskal-Wallis: H(2) = 11.958, epsilon² = 0.342, p = 0.0025, Holm-adjusted p = 0.0278 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 11.6667 | 26.4167 | 0.3595 | 0.4130 | 6.027e-04 | 0.0018 | yes |
| drizzle - sequelize | 11.6667 | 17.4167 | 0.3595 | 0.3855 | 0.1811 | 0.1811 | no |
| prisma - sequelize | 26.4167 | 17.4167 | 0.4130 | 0.3855 | 0.0363 | 0.0727 | no |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.9153 | 5.494e-15 | 5.934e-13 | yes |
| execution_time vs cpu_energy | drizzle | 12 | 0.7972 | 0.0019 | 0.1539 | no |
| execution_time vs cpu_energy | prisma | 12 | 0.9161 | 2.843e-05 | 0.0027 | yes |
| execution_time vs cpu_energy | sequelize | 12 | 0.5734 | 0.0513 | 1.0000 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.6684 | 8.378e-06 | 8.043e-04 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.3636 | 0.2453 | 1.0000 | no |
| execution_time vs memory_energy | prisma | 12 | -0.1086 | 0.7369 | 1.0000 | no |
| execution_time vs memory_energy | sequelize | 12 | 0.5944 | 0.0415 | 1.0000 | no |

## update-owner-no-visits

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 1322.5147 | 51.0006 | 1325.4346 | 1284.6527 | 1367.8644 | 1242.9366 | 1398.1268 |
| prisma | 12 | 1404.4226 | 62.7591 | 1392.7603 | 1365.8904 | 1421.2907 | 1332.0352 | 1548.3280 |
| sequelize | 12 | 1357.3211 | 50.1344 | 1347.3881 | 1320.7235 | 1370.6239 | 1289.9929 | 1455.8654 |

Kruskal-Wallis: H(2) = 9.866, epsilon² = 0.282, p = 0.0072, Holm-adjusted p = 0.0576 -> no significant difference.

Dunn's test not run (Kruskal-Wallis not significant after adjustment).

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 7.3179 | 0.3086 | 7.2812 | 7.0216 | 7.5778 | 6.9094 | 7.8609 |
| prisma | 12 | 7.9303 | 0.3867 | 7.8228 | 7.7374 | 7.9917 | 7.4683 | 8.9363 |
| sequelize | 12 | 7.5249 | 0.4088 | 7.4539 | 7.1680 | 7.7418 | 7.0593 | 8.1596 |

Kruskal-Wallis: H(2) = 13.437, epsilon² = 0.384, p = 0.0012, Holm-adjusted p = 0.0145 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 11.5833 | 27.0833 | 7.2812 | 7.8228 | 3.137e-04 | 9.412e-04 | yes |
| drizzle - sequelize | 11.5833 | 16.8333 | 7.2812 | 7.4539 | 0.2222 | 0.2222 | no |
| prisma - sequelize | 27.0833 | 16.8333 | 7.8228 | 7.4539 | 0.0172 | 0.0343 | yes |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 0.3806 | 0.0221 | 0.3770 | 0.3598 | 0.3975 | 0.3540 | 0.4140 |
| prisma | 12 | 0.4045 | 0.0306 | 0.4025 | 0.3752 | 0.4210 | 0.3680 | 0.4680 |
| sequelize | 12 | 0.3960 | 0.0171 | 0.3915 | 0.3878 | 0.4022 | 0.3750 | 0.4370 |

Kruskal-Wallis: H(2) = 4.256, epsilon² = 0.122, p = 0.1191, Holm-adjusted p = 0.2381 -> no significant difference.

Dunn's test not run (Kruskal-Wallis not significant after adjustment).

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.9264 | 5.539e-16 | 6.093e-14 | yes |
| execution_time vs cpu_energy | drizzle | 12 | 0.8741 | 2.007e-04 | 0.0181 | yes |
| execution_time vs cpu_energy | prisma | 12 | 0.9441 | 3.927e-06 | 3.849e-04 | yes |
| execution_time vs cpu_energy | sequelize | 12 | 0.8601 | 3.317e-04 | 0.0292 | yes |
| execution_time vs memory_energy | all ORMs | 36 | 0.3833 | 0.0210 | 1.0000 | no |
| execution_time vs memory_energy | drizzle | 12 | 0.4764 | 0.1174 | 1.0000 | no |
| execution_time vs memory_energy | prisma | 12 | 0.3047 | 0.3355 | 1.0000 | no |
| execution_time vs memory_energy | sequelize | 12 | 0.1156 | 0.7206 | 1.0000 | no |

## update-owner-populated

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 1304.7677 | 40.7639 | 1300.1749 | 1284.1701 | 1344.1501 | 1242.2037 | 1371.7213 |
| prisma | 12 | 1415.5467 | 65.0560 | 1391.4835 | 1372.2052 | 1442.2279 | 1327.4111 | 1544.3179 |
| sequelize | 12 | 1362.2867 | 56.9042 | 1344.8744 | 1321.0504 | 1394.1250 | 1298.0980 | 1479.5390 |

Kruskal-Wallis: H(2) = 16.848, epsilon² = 0.481, p = 2.195e-04, Holm-adjusted p = 0.0044 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 9.2500 | 26.8333 | 1300.1749 | 1391.4835 | 4.350e-05 | 1.305e-04 | yes |
| drizzle - sequelize | 9.2500 | 19.4167 | 1300.1749 | 1344.8744 | 0.0181 | 0.0362 | yes |
| prisma - sequelize | 26.8333 | 19.4167 | 1391.4835 | 1344.8744 | 0.0846 | 0.0846 | no |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 7.2253 | 0.3471 | 7.2724 | 7.0023 | 7.4636 | 6.6327 | 7.6741 |
| prisma | 12 | 8.0154 | 0.3640 | 7.9192 | 7.8432 | 8.0879 | 7.5225 | 8.7831 |
| sequelize | 12 | 7.5800 | 0.4789 | 7.4676 | 7.2273 | 7.9528 | 7.0481 | 8.6038 |

Kruskal-Wallis: H(2) = 15.257, epsilon² = 0.436, p = 4.864e-04, Holm-adjusted p = 0.0083 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 10.5000 | 27.2500 | 7.2724 | 7.9192 | 9.848e-05 | 2.955e-04 | yes |
| drizzle - sequelize | 10.5000 | 17.7500 | 7.2724 | 7.4676 | 0.0919 | 0.0919 | no |
| prisma - sequelize | 27.2500 | 17.7500 | 7.9192 | 7.4676 | 0.0272 | 0.0544 | no |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 0.3738 | 0.0200 | 0.3695 | 0.3578 | 0.3832 | 0.3530 | 0.4200 |
| prisma | 12 | 0.4060 | 0.0190 | 0.4080 | 0.4000 | 0.4120 | 0.3750 | 0.4420 |
| sequelize | 12 | 0.3942 | 0.0250 | 0.3980 | 0.3860 | 0.4080 | 0.3490 | 0.4380 |

Kruskal-Wallis: H(2) = 10.217, epsilon² = 0.292, p = 0.0060, Holm-adjusted p = 0.0544 -> no significant difference.

Dunn's test not run (Kruskal-Wallis not significant after adjustment).

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.8847 | 8.205e-13 | 8.779e-11 | yes |
| execution_time vs cpu_energy | drizzle | 12 | 0.8462 | 5.211e-04 | 0.0448 | yes |
| execution_time vs cpu_energy | prisma | 12 | 0.6713 | 0.0168 | 1.0000 | no |
| execution_time vs cpu_energy | sequelize | 12 | 0.8252 | 9.514e-04 | 0.0799 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.4097 | 0.0131 | 0.9817 | no |
| execution_time vs memory_energy | drizzle | 12 | -0.1049 | 0.7456 | 1.0000 | no |
| execution_time vs memory_energy | prisma | 12 | -0.4842 | 0.1107 | 1.0000 | no |
| execution_time vs memory_energy | sequelize | 12 | 0.4238 | 0.1698 | 1.0000 | no |

## update-pet-populated

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 611.4929 | 16.6070 | 604.3778 | 601.0635 | 620.2298 | 593.2416 | 640.6344 |
| prisma | 12 | 976.6179 | 60.5305 | 965.6229 | 931.9592 | 1021.3540 | 885.1130 | 1092.7524 |
| sequelize | 12 | 622.2105 | 32.5770 | 634.0229 | 606.6262 | 638.7479 | 562.9256 | 676.8897 |

Kruskal-Wallis: H(2) = 23.952, epsilon² = 0.684, p = 6.294e-06, Holm-adjusted p = 1.762e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 10.8333 | 30.5000 | 604.3778 | 965.6229 | 4.822e-06 | 1.446e-05 | yes |
| drizzle - sequelize | 10.8333 | 14.1667 | 604.3778 | 634.0229 | 0.4383 | 0.4383 | no |
| prisma - sequelize | 30.5000 | 14.1667 | 965.6229 | 634.0229 | 1.462e-04 | 2.924e-04 | yes |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 2.7513 | 0.2524 | 2.6968 | 2.5630 | 3.0037 | 2.4288 | 3.1149 |
| prisma | 12 | 5.3172 | 0.3205 | 5.3039 | 5.1107 | 5.3862 | 4.8927 | 6.1648 |
| sequelize | 12 | 2.9178 | 0.2660 | 2.9718 | 2.6853 | 3.1126 | 2.5164 | 3.2336 |

Kruskal-Wallis: H(2) = 24.290, epsilon² = 0.694, p = 5.315e-06, Holm-adjusted p = 1.648e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 10.4167 | 30.5000 | 2.6968 | 5.3039 | 3.023e-06 | 9.068e-06 | yes |
| drizzle - sequelize | 10.4167 | 14.5833 | 2.6968 | 2.9718 | 0.3327 | 0.3327 | no |
| prisma - sequelize | 30.5000 | 14.5833 | 5.3039 | 2.9718 | 2.151e-04 | 4.303e-04 | yes |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 0.1935 | 0.0125 | 0.1965 | 0.1860 | 0.2018 | 0.1730 | 0.2110 |
| prisma | 12 | 0.2844 | 0.0187 | 0.2850 | 0.2752 | 0.2945 | 0.2550 | 0.3240 |
| sequelize | 12 | 0.2040 | 0.0166 | 0.2030 | 0.1923 | 0.2070 | 0.1900 | 0.2510 |

Kruskal-Wallis: H(2) = 24.177, epsilon² = 0.691, p = 5.624e-06, Holm-adjusted p = 1.654e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 10.5833 | 30.5000 | 0.1965 | 0.2850 | 3.595e-06 | 1.079e-05 | yes |
| drizzle - sequelize | 10.5833 | 14.4167 | 0.1965 | 0.2030 | 0.3725 | 0.3725 | no |
| prisma - sequelize | 30.5000 | 14.4167 | 0.2850 | 0.2030 | 1.828e-04 | 3.655e-04 | yes |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.7122 | 1.106e-06 | 1.106e-04 | yes |
| execution_time vs cpu_energy | drizzle | 12 | -0.2867 | 0.3663 | 1.0000 | no |
| execution_time vs cpu_energy | prisma | 12 | 0.5734 | 0.0513 | 1.0000 | no |
| execution_time vs cpu_energy | sequelize | 12 | 0.1399 | 0.6646 | 1.0000 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.7772 | 2.482e-08 | 2.606e-06 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.1538 | 0.6331 | 1.0000 | no |
| execution_time vs memory_energy | prisma | 12 | 0.3544 | 0.2584 | 1.0000 | no |
| execution_time vs memory_energy | sequelize | 12 | 0.4841 | 0.1107 | 1.0000 | no |
