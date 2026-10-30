# Statistical analysis: Intel (Linux, RAPL)

Source: `results-intel/` (read-only). 12 trials, 14 operation types, 504 valid ORM x operation x trial observations; 0 excluded.

Significance level alpha = 0.05. All p-values are Holm-adjusted and significance is decided on the adjusted value: each assumption check and Kruskal-Wallis across the 42 tests of this machine, Dunn across the three ORM pairs of one test, Spearman across the 112 correlations of this machine.

## Metrics and units (original units, no conversion)

| Metric | Unit | Source |
|---|---|---|
| Execution time | ms | `timing.workloadElapsedMs` (controller monotonic clock, GO to DONE) |
| CPU energy consumption | J | RAPL `intel-rapl:0` (package-0): whole CPU package, includes the core and uncore sub-domains. Field `energyJ`. |
| Memory energy consumption | J | RAPL `intel-rapl:0:2` (dram). Field `energyJ`. |

## Parametric assumption checks

Shapiro-Wilk on the residuals (normality) and Brown-Forsythe across the ORMs (equal variances); Holm-adjusted p-values, `*` marks a rejected assumption (adjusted p < 0.05).

| Metric | Normality rejected | Equal variances rejected |
|---|---|---|
| Execution time | 5 / 14 | 0 / 14 |
| CPU energy consumption | 10 / 14 | 0 / 14 |
| Memory energy consumption | 5 / 14 | 0 / 14 |

| Operation | Execution time Shapiro p_holm / B-F p_holm | CPU energy consumption Shapiro p_holm / B-F p_holm | Memory energy consumption Shapiro p_holm / B-F p_holm |
|---|---|---|---|
| create-owner-populated | 1.0000 / 1.0000 | 2.982e-04 * / 1.0000 | 1.0000 / 1.0000 |
| create-pet-populated | 0.7735 / 1.0000 | 0.7339 / 1.0000 | 1.0000 / 1.0000 |
| delete-owner-visits-no-pets | 0.0063 * / 1.0000 | 4.908e-07 * / 1.0000 | 2.209e-06 * / 1.0000 |
| delete-owner-visits-no-visits | 1.520e-04 * / 1.0000 | 8.202e-09 * / 1.0000 | 2.157e-08 * / 1.0000 |
| delete-owner-visits-populated | 1.0000 / 1.0000 | 1.0000 / 1.0000 | 1.0000 / 1.0000 |
| delete-visit-populated | 0.1024 / 1.0000 | 1.203e-09 * / 1.0000 | 1.0000 / 1.0000 |
| read-owner-no-pets | 1.0000 / 1.0000 | 1.705e-08 * / 1.0000 | 2.695e-07 * / 1.0000 |
| read-owner-no-visits | 1.0000 / 1.0000 | 1.0000 / 1.0000 | 1.0000 / 1.0000 |
| read-owner-populated | 9.417e-04 * / 1.0000 | 4.267e-08 * / 1.0000 | 2.430e-07 * / 1.0000 |
| read-pet-populated | 0.3755 / 0.0540 | 1.315e-08 * / 1.0000 | 2.525e-07 * / 1.0000 |
| update-owner-no-pets | 2.209e-06 * / 1.0000 | 1.073e-09 * / 1.0000 | 1.0000 / 1.0000 |
| update-owner-no-visits | 1.0000 / 1.0000 | 0.6608 / 1.0000 | 1.0000 / 1.0000 |
| update-owner-populated | 1.0000 / 1.0000 | 5.520e-04 * / 1.0000 | 1.0000 / 1.0000 |
| update-pet-populated | 2.281e-06 * / 1.0000 | 1.899e-09 * / 1.0000 | 1.0000 / 1.0000 |

## Kruskal-Wallis overview

H statistic and Holm-adjusted p-value per operation; `*` marks adjusted p < 0.05.

| Operation | Execution time H (p_holm) | CPU energy consumption H (p_holm) | Memory energy consumption H (p_holm) |
|---|---|---|---|
| create-owner-populated | 19.88 (4.832e-04) * | 25.10 (9.923e-05) * | 20.23 (4.485e-04) * |
| create-pet-populated | 27.00 (4.521e-05) * | 19.38 (5.563e-04) * | 25.35 (9.691e-05) * |
| delete-owner-visits-no-pets | 27.99 (3.014e-05) * | 23.30 (1.701e-04) * | 27.53 (3.581e-05) * |
| delete-owner-visits-no-visits | 23.65 (1.687e-04) * | 23.93 (1.591e-04) * | 23.35 (1.701e-04) * |
| delete-owner-visits-populated | 5.07 (0.0791) | 9.87 (0.0216) * | 10.60 (0.0200) * |
| delete-visit-populated | 7.43 (0.0487) * | 13.39 (0.0062) * | 16.60 (0.0017) * |
| read-owner-no-pets | 23.42 (1.701e-04) * | 23.41 (1.701e-04) * | 25.09 (9.923e-05) * |
| read-owner-no-visits | 31.14 (7.284e-06) * | 31.14 (7.284e-06) * | 23.65 (1.687e-04) * |
| read-owner-populated | 28.76 (2.221e-05) * | 28.94 (2.080e-05) * | 24.01 (1.587e-04) * |
| read-pet-populated | 28.06 (2.986e-05) * | 25.30 (9.691e-05) * | 28.76 (2.221e-05) * |
| update-owner-no-pets | 15.76 (0.0023) * | 25.25 (9.691e-05) * | 21.50 (2.788e-04) * |
| update-owner-no-visits | 23.42 (1.701e-04) * | 23.19 (1.701e-04) * | 23.45 (1.701e-04) * |
| update-owner-populated | 22.37 (1.947e-04) * | 17.06 (0.0016) * | 23.84 (1.599e-04) * |
| update-pet-populated | 20.39 (4.485e-04) * | 27.73 (3.331e-05) * | 25.98 (7.315e-05) * |

## create-owner-populated

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 20326.7163 | 648.9342 | 20277.6300 | 19967.8448 | 20690.8428 | 19240.7485 | 21560.0178 |
| prisma | 12 | 21943.0228 | 776.7903 | 22027.3385 | 21222.6809 | 22551.1462 | 20850.7908 | 23194.7297 |
| sequelize | 12 | 20091.6602 | 883.5619 | 20135.4421 | 19689.0802 | 20556.2847 | 18569.4153 | 21913.9750 |

Kruskal-Wallis: H(2) = 19.875, epsilon² = 0.568, p = 4.832e-05, Holm-adjusted p = 4.832e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 14.0833 | 29.5000 | 20277.6300 | 22027.3385 | 3.380e-04 | 6.760e-04 | yes |
| drizzle - sequelize | 14.0833 | 11.9167 | 20277.6300 | 20135.4421 | 0.6144 | 0.6144 | no |
| prisma - sequelize | 29.5000 | 11.9167 | 22027.3385 | 20135.4421 | 4.350e-05 | 1.305e-04 | yes |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 44.4500 | 1.3850 | 44.9102 | 43.0286 | 45.3236 | 42.8093 | 46.7723 |
| prisma | 12 | 51.7675 | 3.3713 | 51.0818 | 50.4249 | 51.6623 | 48.7881 | 61.8930 |
| sequelize | 12 | 46.2190 | 1.9083 | 46.5286 | 45.0051 | 47.2242 | 43.0607 | 50.1348 |

Kruskal-Wallis: H(2) = 25.101, epsilon² = 0.717, p = 3.544e-06, Holm-adjusted p = 9.923e-05 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 9.0833 | 30.2500 | 44.9102 | 51.0818 | 8.604e-07 | 2.581e-06 | yes |
| drizzle - sequelize | 9.0833 | 16.1667 | 44.9102 | 46.5286 | 0.0996 | 0.0996 | no |
| prisma - sequelize | 30.2500 | 16.1667 | 51.0818 | 46.5286 | 0.0011 | 0.0021 | yes |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 18.0332 | 0.5001 | 18.0631 | 17.5911 | 18.3191 | 17.4051 | 19.0217 |
| prisma | 12 | 19.6987 | 0.5889 | 19.7895 | 19.3049 | 20.0901 | 18.8016 | 20.7161 |
| sequelize | 12 | 18.3663 | 0.7483 | 18.3594 | 18.0390 | 18.8064 | 16.9925 | 19.8234 |

Kruskal-Wallis: H(2) = 20.227, epsilon² = 0.578, p = 4.053e-05, Holm-adjusted p = 4.485e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 11.0000 | 29.4167 | 18.0631 | 19.7895 | 1.854e-05 | 5.562e-05 | yes |
| drizzle - sequelize | 11.0000 | 15.0833 | 18.0631 | 18.3594 | 0.3424 | 0.3424 | no |
| prisma - sequelize | 29.4167 | 15.0833 | 19.7895 | 18.3594 | 8.609e-04 | 0.0017 | yes |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.7766 | 2.590e-08 | 2.279e-06 | yes |
| execution_time vs cpu_energy | drizzle | 12 | 0.4545 | 0.1377 | 1.0000 | no |
| execution_time vs cpu_energy | prisma | 12 | 0.3077 | 0.3306 | 1.0000 | no |
| execution_time vs cpu_energy | sequelize | 12 | 0.7552 | 0.0045 | 0.1262 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.9490 | 1.273e-18 | 1.273e-16 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.9790 | 3.090e-08 | 2.688e-06 | yes |
| execution_time vs memory_energy | prisma | 12 | 0.9231 | 1.862e-05 | 0.0011 | yes |
| execution_time vs memory_energy | sequelize | 12 | 0.9650 | 3.881e-07 | 3.027e-05 | yes |

## create-pet-populated

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 16697.3059 | 285.8893 | 16622.0041 | 16583.1850 | 16741.8888 | 16366.2531 | 17509.7698 |
| prisma | 12 | 17245.4345 | 228.2213 | 17207.5588 | 17108.9729 | 17447.7917 | 16870.7051 | 17542.5704 |
| sequelize | 12 | 17879.2082 | 354.9817 | 17889.1139 | 17589.5343 | 18051.5246 | 17461.5302 | 18589.6086 |

Kruskal-Wallis: H(2) = 27.002, epsilon² = 0.771, p = 1.370e-06, Holm-adjusted p = 4.521e-05 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 7.5833 | 18.0000 | 16622.0041 | 17207.5588 | 0.0154 | 0.0154 | yes |
| drizzle - sequelize | 7.5833 | 29.9167 | 16622.0041 | 17889.1139 | 2.076e-07 | 6.228e-07 | yes |
| prisma - sequelize | 18.0000 | 29.9167 | 17207.5588 | 17889.1139 | 0.0056 | 0.0112 | yes |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 35.0594 | 1.2733 | 34.8937 | 34.1154 | 35.5312 | 33.7176 | 38.1359 |
| prisma | 12 | 37.1204 | 1.1472 | 36.7497 | 36.4381 | 38.1862 | 35.4726 | 39.1497 |
| sequelize | 12 | 38.1026 | 1.1816 | 38.0057 | 37.3281 | 38.3906 | 36.4339 | 40.3353 |

Kruskal-Wallis: H(2) = 19.383, epsilon² = 0.554, p = 6.181e-05, Holm-adjusted p = 5.563e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 8.0833 | 20.8333 | 34.8937 | 36.7497 | 0.0030 | 0.0061 | yes |
| drizzle - sequelize | 8.0833 | 26.5833 | 34.8937 | 38.0057 | 1.699e-05 | 5.097e-05 | yes |
| prisma - sequelize | 20.8333 | 26.5833 | 36.7497 | 38.0057 | 0.1813 | 0.1813 | no |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 14.6908 | 0.2731 | 14.6214 | 14.5616 | 14.7590 | 14.4315 | 15.4647 |
| prisma | 12 | 15.4777 | 0.2420 | 15.4260 | 15.3044 | 15.6931 | 15.1172 | 15.8045 |
| sequelize | 12 | 15.9026 | 0.3134 | 15.9561 | 15.6382 | 16.1064 | 15.4903 | 16.4174 |

Kruskal-Wallis: H(2) = 25.351, epsilon² = 0.724, p = 3.126e-06, Holm-adjusted p = 9.691e-05 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 7.0000 | 20.0000 | 14.6214 | 15.4260 | 0.0025 | 0.0050 | yes |
| drizzle - sequelize | 7.0000 | 28.5000 | 14.6214 | 15.9561 | 5.773e-07 | 1.732e-06 | yes |
| prisma - sequelize | 20.0000 | 28.5000 | 15.4260 | 15.9561 | 0.0481 | 0.0481 | yes |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.8842 | 8.814e-13 | 8.285e-11 | yes |
| execution_time vs cpu_energy | drizzle | 12 | 0.7622 | 0.0040 | 0.1146 | no |
| execution_time vs cpu_energy | prisma | 12 | 0.7972 | 0.0019 | 0.0589 | no |
| execution_time vs cpu_energy | sequelize | 12 | 0.8042 | 0.0016 | 0.0517 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.9498 | 9.883e-19 | 1.008e-16 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.8741 | 2.007e-04 | 0.0090 | yes |
| execution_time vs memory_energy | prisma | 12 | 0.8741 | 2.007e-04 | 0.0090 | yes |
| execution_time vs memory_energy | sequelize | 12 | 0.9301 | 1.170e-05 | 7.723e-04 | yes |

## delete-owner-visits-no-pets

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 2145.4101 | 93.9832 | 2113.7570 | 2097.2411 | 2159.8984 | 2040.4681 | 2307.0253 |
| prisma | 12 | 2349.3130 | 87.9217 | 2321.1193 | 2298.9669 | 2360.7126 | 2268.3456 | 2572.2995 |
| sequelize | 12 | 1932.1412 | 87.4821 | 1921.9423 | 1861.7919 | 1959.2468 | 1831.9473 | 2096.1620 |

Kruskal-Wallis: H(2) = 27.986, epsilon² = 0.800, p = 8.372e-07, Holm-adjusted p = 3.014e-05 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 18.7500 | 29.7500 | 2113.7570 | 2321.1193 | 0.0105 | 0.0126 | yes |
| drizzle - sequelize | 18.7500 | 7.0000 | 2113.7570 | 1921.9423 | 0.0063 | 0.0126 | yes |
| prisma - sequelize | 29.7500 | 7.0000 | 2321.1193 | 1921.9423 | 1.228e-07 | 3.684e-07 | yes |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 15.8996 | 0.8122 | 15.6305 | 15.2964 | 16.1908 | 15.1076 | 17.3657 |
| prisma | 12 | 17.7123 | 2.3678 | 17.0197 | 16.7270 | 17.4057 | 16.3369 | 25.0314 |
| sequelize | 12 | 14.5191 | 0.7299 | 14.5128 | 14.0056 | 14.5967 | 13.6307 | 16.0369 |

Kruskal-Wallis: H(2) = 23.302, epsilon² = 0.666, p = 8.711e-06, Holm-adjusted p = 1.701e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 18.9167 | 28.6667 | 15.6305 | 17.0197 | 0.0234 | 0.0234 | yes |
| drizzle - sequelize | 18.9167 | 7.9167 | 15.6305 | 14.5128 | 0.0105 | 0.0211 | yes |
| prisma - sequelize | 28.6667 | 7.9167 | 17.0197 | 14.5128 | 1.405e-06 | 4.215e-06 | yes |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 3.0438 | 0.1462 | 2.9945 | 2.9545 | 3.0778 | 2.8973 | 3.2968 |
| prisma | 12 | 3.4673 | 0.3346 | 3.3556 | 3.3224 | 3.4351 | 3.2629 | 4.4967 |
| sequelize | 12 | 2.7765 | 0.1317 | 2.7663 | 2.6756 | 2.8041 | 2.6302 | 3.0384 |

Kruskal-Wallis: H(2) = 27.527, epsilon² = 0.786, p = 1.053e-06, Holm-adjusted p = 3.581e-05 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 17.5000 | 30.2500 | 2.9945 | 3.3556 | 0.0030 | 0.0061 | yes |
| drizzle - sequelize | 17.5000 | 7.7500 | 2.9945 | 2.7663 | 0.0234 | 0.0234 | yes |
| prisma - sequelize | 30.2500 | 7.7500 | 3.3556 | 2.7663 | 1.685e-07 | 5.054e-07 | yes |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.9660 | 1.473e-21 | 1.547e-19 | yes |
| execution_time vs cpu_energy | drizzle | 12 | 0.9161 | 2.843e-05 | 0.0016 | yes |
| execution_time vs cpu_energy | prisma | 12 | 0.9301 | 1.170e-05 | 7.723e-04 | yes |
| execution_time vs cpu_energy | sequelize | 12 | 0.8671 | 2.598e-04 | 0.0112 | yes |
| execution_time vs memory_energy | all ORMs | 36 | 0.9810 | 8.811e-26 | 9.692e-24 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.8881 | 1.141e-04 | 0.0056 | yes |
| execution_time vs memory_energy | prisma | 12 | 0.9510 | 2.038e-06 | 1.468e-04 | yes |
| execution_time vs memory_energy | sequelize | 12 | 0.9720 | 1.287e-07 | 1.068e-05 | yes |

## delete-owner-visits-no-visits

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 2562.1368 | 51.0829 | 2549.2881 | 2528.6911 | 2583.0870 | 2490.8710 | 2673.4108 |
| prisma | 12 | 2814.9252 | 115.2337 | 2781.7064 | 2764.8117 | 2806.2654 | 2701.7467 | 3157.2935 |
| sequelize | 12 | 2812.8416 | 53.3411 | 2810.7775 | 2770.6698 | 2850.8830 | 2737.2744 | 2895.4633 |

Kruskal-Wallis: H(2) = 23.646, epsilon² = 0.676, p = 7.335e-06, Holm-adjusted p = 1.687e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 6.5000 | 23.3333 | 2549.2881 | 2781.7064 | 9.090e-05 | 1.818e-04 | yes |
| drizzle - sequelize | 6.5000 | 25.6667 | 2549.2881 | 2810.7775 | 8.344e-06 | 2.503e-05 | yes |
| prisma - sequelize | 23.3333 | 25.6667 | 2781.7064 | 2810.7775 | 0.5875 | 0.5875 | no |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 19.0759 | 0.4259 | 19.0222 | 18.7412 | 19.3020 | 18.5028 | 19.8952 |
| prisma | 12 | 21.4034 | 3.3748 | 20.3122 | 20.1425 | 20.8533 | 19.8569 | 32.0169 |
| sequelize | 12 | 20.8287 | 0.4993 | 20.7715 | 20.4278 | 21.2546 | 20.1280 | 21.5754 |

Kruskal-Wallis: H(2) = 23.929, epsilon² = 0.684, p = 6.365e-06, Holm-adjusted p = 1.591e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 6.5833 | 22.4167 | 19.0222 | 20.3122 | 2.322e-04 | 4.643e-04 | yes |
| drizzle - sequelize | 6.5833 | 26.5000 | 19.0222 | 20.7715 | 3.647e-06 | 1.094e-05 | yes |
| prisma - sequelize | 22.4167 | 26.5000 | 20.3122 | 20.7715 | 0.3424 | 0.3424 | no |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 3.3633 | 0.0764 | 3.3317 | 3.3169 | 3.4113 | 3.2645 | 3.5342 |
| prisma | 12 | 3.8750 | 0.4349 | 3.7326 | 3.7154 | 3.7849 | 3.6890 | 5.2409 |
| sequelize | 12 | 3.7622 | 0.0903 | 3.7757 | 3.6936 | 3.8208 | 3.6207 | 3.8920 |

Kruskal-Wallis: H(2) = 23.351, epsilon² = 0.667, p = 8.498e-06, Holm-adjusted p = 1.701e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 6.5000 | 24.5000 | 3.3317 | 3.7326 | 2.853e-05 | 8.558e-05 | yes |
| drizzle - sequelize | 6.5000 | 24.5000 | 3.3317 | 3.7757 | 2.853e-05 | 8.558e-05 | yes |
| prisma - sequelize | 24.5000 | 24.5000 | 3.7326 | 3.7757 | 1.0000 | 1.0000 | no |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.9737 | 1.952e-23 | 2.088e-21 | yes |
| execution_time vs cpu_energy | drizzle | 12 | 0.8811 | 1.527e-04 | 0.0073 | yes |
| execution_time vs cpu_energy | prisma | 12 | 0.9580 | 9.544e-07 | 7.253e-05 | yes |
| execution_time vs cpu_energy | sequelize | 12 | 0.9161 | 2.843e-05 | 0.0016 | yes |
| execution_time vs memory_energy | all ORMs | 36 | 0.9858 | 5.894e-28 | 6.602e-26 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.9580 | 9.544e-07 | 7.253e-05 | yes |
| execution_time vs memory_energy | prisma | 12 | 0.9580 | 9.544e-07 | 7.253e-05 | yes |
| execution_time vs memory_energy | sequelize | 12 | 0.9720 | 1.287e-07 | 1.068e-05 | yes |

## delete-owner-visits-populated

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 18586.3680 | 564.8536 | 18549.2185 | 18427.7954 | 18828.2239 | 17640.8606 | 19580.9907 |
| prisma | 12 | 18745.9891 | 387.8233 | 18783.1489 | 18501.9570 | 19001.7992 | 17980.7869 | 19328.8339 |
| sequelize | 12 | 19030.5400 | 583.4457 | 19155.2303 | 18848.7286 | 19355.4257 | 17867.8509 | 19999.5214 |

Kruskal-Wallis: H(2) = 5.074, epsilon² = 0.145, p = 0.0791, Holm-adjusted p = 0.0791 -> no significant difference.

Dunn's test not run (Kruskal-Wallis not significant after adjustment).

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 39.4818 | 0.8718 | 39.4972 | 38.8078 | 39.6381 | 38.3919 | 41.4050 |
| prisma | 12 | 40.1922 | 0.7250 | 40.2542 | 39.9019 | 40.8002 | 38.8200 | 41.1770 |
| sequelize | 12 | 40.6263 | 0.7523 | 40.6550 | 40.1874 | 41.1603 | 39.5643 | 41.9526 |

Kruskal-Wallis: H(2) = 9.866, epsilon² = 0.282, p = 0.0072, Holm-adjusted p = 0.0216 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 11.3333 | 19.4167 | 39.4972 | 40.2542 | 0.0602 | 0.1204 | no |
| drizzle - sequelize | 11.3333 | 24.7500 | 39.4972 | 40.6550 | 0.0018 | 0.0054 | yes |
| prisma - sequelize | 19.4167 | 24.7500 | 40.2542 | 40.6550 | 0.2150 | 0.2150 | no |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 16.0569 | 0.4101 | 16.0481 | 15.8841 | 16.2160 | 15.4431 | 16.9135 |
| prisma | 12 | 16.3944 | 0.2937 | 16.3893 | 16.2368 | 16.5852 | 15.9111 | 16.8248 |
| sequelize | 12 | 16.6720 | 0.4731 | 16.8220 | 16.5621 | 16.8946 | 15.6273 | 17.4315 |

Kruskal-Wallis: H(2) = 10.599, epsilon² = 0.303, p = 0.0050, Holm-adjusted p = 0.0200 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 11.5833 | 18.3333 | 16.0481 | 16.3893 | 0.1166 | 0.1837 | no |
| drizzle - sequelize | 11.5833 | 25.5833 | 16.0481 | 16.8220 | 0.0011 | 0.0034 | yes |
| prisma - sequelize | 18.3333 | 25.5833 | 16.3893 | 16.8220 | 0.0919 | 0.1837 | no |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.4216 | 0.0104 | 0.2664 | no |
| execution_time vs cpu_energy | drizzle | 12 | 0.2867 | 0.3663 | 1.0000 | no |
| execution_time vs cpu_energy | prisma | 12 | 0.4406 | 0.1517 | 1.0000 | no |
| execution_time vs cpu_energy | sequelize | 12 | 0.2587 | 0.4168 | 1.0000 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.9495 | 1.076e-18 | 1.087e-16 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.9860 | 4.117e-09 | 3.788e-07 | yes |
| execution_time vs memory_energy | prisma | 12 | 0.9720 | 1.287e-07 | 1.068e-05 | yes |
| execution_time vs memory_energy | sequelize | 12 | 0.9021 | 5.998e-05 | 0.0032 | yes |

## delete-visit-populated

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 15745.8619 | 404.3516 | 15591.8338 | 15405.7596 | 16017.3630 | 15372.1327 | 16480.8293 |
| prisma | 12 | 15963.3875 | 659.7759 | 15994.3498 | 15868.2381 | 16346.0667 | 14116.5056 | 16748.8251 |
| sequelize | 12 | 15507.1358 | 422.9521 | 15570.1766 | 15325.8021 | 15762.0139 | 14781.4477 | 16068.3876 |

Kruskal-Wallis: H(2) = 7.429, epsilon² = 0.212, p = 0.0244, Holm-adjusted p = 0.0487 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 17.8333 | 24.6667 | 15591.8338 | 15994.3498 | 0.1121 | 0.2242 | no |
| drizzle - sequelize | 17.8333 | 13.0000 | 15591.8338 | 15570.1766 | 0.2611 | 0.2611 | no |
| prisma - sequelize | 24.6667 | 13.0000 | 15994.3498 | 15570.1766 | 0.0067 | 0.0200 | yes |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 32.3424 | 0.9695 | 32.2493 | 31.8037 | 33.0994 | 30.1310 | 33.7818 |
| prisma | 12 | 37.2979 | 13.3897 | 33.5304 | 33.0802 | 33.9818 | 32.6203 | 79.7784 |
| sequelize | 12 | 32.2269 | 0.9288 | 32.3549 | 32.0351 | 32.7537 | 29.7519 | 33.1772 |

Kruskal-Wallis: H(2) = 13.389, epsilon² = 0.383, p = 0.0012, Holm-adjusted p = 0.0062 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 15.0833 | 27.5000 | 32.2493 | 33.5304 | 0.0039 | 0.0078 | yes |
| drizzle - sequelize | 15.0833 | 12.9167 | 32.2493 | 32.3549 | 0.6144 | 0.6144 | no |
| prisma - sequelize | 27.5000 | 12.9167 | 33.5304 | 32.3549 | 6.975e-04 | 0.0021 | yes |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 13.7140 | 0.3130 | 13.5918 | 13.4783 | 13.9922 | 13.3093 | 14.1847 |
| prisma | 12 | 14.3248 | 0.3602 | 14.2205 | 14.0493 | 14.4451 | 13.9490 | 15.1781 |
| sequelize | 12 | 13.5988 | 0.3459 | 13.6383 | 13.3647 | 13.7941 | 13.0619 | 14.1458 |

Kruskal-Wallis: H(2) = 16.601, epsilon² = 0.474, p = 2.484e-04, Holm-adjusted p = 0.0017 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 14.8333 | 28.5000 | 13.5918 | 14.2205 | 0.0015 | 0.0030 | yes |
| drizzle - sequelize | 14.8333 | 12.1667 | 13.5918 | 13.6383 | 0.5353 | 0.5353 | no |
| prisma - sequelize | 28.5000 | 12.1667 | 14.2205 | 13.6383 | 1.462e-04 | 4.386e-04 | yes |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.5297 | 8.921e-04 | 0.0303 | yes |
| execution_time vs cpu_energy | drizzle | 12 | 0.3776 | 0.2262 | 1.0000 | no |
| execution_time vs cpu_energy | prisma | 12 | 0.0839 | 0.7954 | 1.0000 | no |
| execution_time vs cpu_energy | sequelize | 12 | 0.7063 | 0.0102 | 0.2664 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.7949 | 7.072e-09 | 6.294e-07 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.8951 | 8.367e-05 | 0.0042 | yes |
| execution_time vs memory_energy | prisma | 12 | 0.4476 | 0.1446 | 1.0000 | no |
| execution_time vs memory_energy | sequelize | 12 | 0.9860 | 4.117e-09 | 3.788e-07 | yes |

## read-owner-no-pets

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 2611.5218 | 61.9640 | 2600.5262 | 2563.5642 | 2662.5226 | 2528.6778 | 2712.2726 |
| prisma | 12 | 2933.2881 | 78.1828 | 2907.1325 | 2885.3811 | 2956.1360 | 2867.6843 | 3154.4727 |
| sequelize | 12 | 2613.5452 | 72.3128 | 2609.4551 | 2587.7737 | 2671.0949 | 2480.7465 | 2699.5778 |

Kruskal-Wallis: H(2) = 23.425, epsilon² = 0.669, p = 8.191e-06, Holm-adjusted p = 1.701e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 11.9167 | 30.5000 | 2600.5262 | 2907.1325 | 1.556e-05 | 4.669e-05 | yes |
| drizzle - sequelize | 11.9167 | 13.0833 | 2600.5262 | 2609.4551 | 0.7862 | 0.7862 | no |
| prisma - sequelize | 30.5000 | 13.0833 | 2907.1325 | 2609.4551 | 5.137e-05 | 1.027e-04 | yes |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 19.2943 | 0.5311 | 19.3755 | 18.8089 | 19.6612 | 18.5753 | 20.1188 |
| prisma | 12 | 22.0762 | 3.0269 | 21.2840 | 20.8560 | 21.6541 | 20.6301 | 31.5909 |
| sequelize | 12 | 19.1661 | 0.5340 | 19.0597 | 19.0195 | 19.6306 | 18.2171 | 19.8903 |

Kruskal-Wallis: H(2) = 23.405, epsilon² = 0.669, p = 8.271e-06, Holm-adjusted p = 1.701e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 13.0000 | 30.5000 | 19.3755 | 21.2840 | 4.728e-05 | 9.457e-05 | yes |
| drizzle - sequelize | 13.0000 | 12.0000 | 19.3755 | 19.0597 | 0.8162 | 0.8162 | no |
| prisma - sequelize | 30.5000 | 12.0000 | 21.2840 | 19.0597 | 1.699e-05 | 5.097e-05 | yes |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 3.6093 | 0.1016 | 3.6017 | 3.5150 | 3.6753 | 3.4786 | 3.7677 |
| prisma | 12 | 4.2427 | 0.3801 | 4.1193 | 4.0837 | 4.2190 | 4.0550 | 5.4311 |
| sequelize | 12 | 3.7001 | 0.1157 | 3.6877 | 3.6726 | 3.7983 | 3.4846 | 3.8410 |

Kruskal-Wallis: H(2) = 25.087, epsilon² = 0.717, p = 3.568e-06, Holm-adjusted p = 9.923e-05 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 9.6667 | 30.5000 | 3.6017 | 4.1193 | 1.275e-06 | 3.824e-06 | yes |
| drizzle - sequelize | 9.6667 | 15.3333 | 3.6017 | 3.6877 | 0.1877 | 0.1877 | no |
| prisma - sequelize | 30.5000 | 15.3333 | 4.1193 | 3.6877 | 4.216e-04 | 8.432e-04 | yes |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.9745 | 1.182e-23 | 1.276e-21 | yes |
| execution_time vs cpu_energy | drizzle | 12 | 0.9790 | 3.090e-08 | 2.688e-06 | yes |
| execution_time vs cpu_energy | prisma | 12 | 0.9021 | 5.998e-05 | 0.0032 | yes |
| execution_time vs cpu_energy | sequelize | 12 | 0.8531 | 4.181e-04 | 0.0163 | yes |
| execution_time vs memory_energy | all ORMs | 36 | 0.9614 | 1.249e-20 | 1.287e-18 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.9720 | 1.287e-07 | 1.068e-05 | yes |
| execution_time vs memory_energy | prisma | 12 | 0.9021 | 5.998e-05 | 0.0032 | yes |
| execution_time vs memory_energy | sequelize | 12 | 0.8601 | 3.317e-04 | 0.0139 | yes |

## read-owner-no-visits

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 3444.7735 | 95.3171 | 3403.3688 | 3389.5198 | 3491.5129 | 3330.3102 | 3667.8797 |
| prisma | 12 | 4320.4308 | 53.1169 | 4317.0358 | 4285.9538 | 4342.6859 | 4237.9364 | 4436.3466 |
| sequelize | 12 | 4046.3008 | 102.7714 | 4058.1249 | 3956.6625 | 4123.0485 | 3886.4593 | 4207.6957 |

Kruskal-Wallis: H(2) = 31.135, epsilon² = 0.890, p = 1.734e-07, Holm-adjusted p = 7.284e-06 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 6.5000 | 30.5000 | 3403.3688 | 4317.0358 | 2.407e-08 | 7.220e-08 | yes |
| drizzle - sequelize | 6.5000 | 18.5000 | 3403.3688 | 4058.1249 | 0.0053 | 0.0105 | yes |
| prisma - sequelize | 30.5000 | 18.5000 | 4317.0358 | 4058.1249 | 0.0053 | 0.0105 | yes |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 26.6299 | 0.8346 | 26.3568 | 26.0863 | 26.9669 | 25.8795 | 28.5840 |
| prisma | 12 | 33.1946 | 0.5102 | 33.2217 | 32.8067 | 33.4589 | 32.5096 | 34.0358 |
| sequelize | 12 | 30.7146 | 0.9886 | 30.6940 | 29.7967 | 31.4012 | 29.4587 | 32.4384 |

Kruskal-Wallis: H(2) = 31.135, epsilon² = 0.890, p = 1.734e-07, Holm-adjusted p = 7.284e-06 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 6.5000 | 30.5000 | 26.3568 | 33.2217 | 2.407e-08 | 7.220e-08 | yes |
| drizzle - sequelize | 6.5000 | 18.5000 | 26.3568 | 30.6940 | 0.0053 | 0.0105 | yes |
| prisma - sequelize | 30.5000 | 18.5000 | 33.2217 | 30.6940 | 0.0053 | 0.0105 | yes |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 4.5106 | 0.1509 | 4.4542 | 4.4115 | 4.5678 | 4.3641 | 4.8804 |
| prisma | 12 | 5.3922 | 0.0760 | 5.4066 | 5.3391 | 5.4308 | 5.2656 | 5.5378 |
| sequelize | 12 | 5.3266 | 0.1670 | 5.3114 | 5.1608 | 5.4477 | 5.1029 | 5.6341 |

Kruskal-Wallis: H(2) = 23.646, epsilon² = 0.676, p = 7.335e-06, Holm-adjusted p = 1.687e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 6.5000 | 25.6667 | 4.4542 | 5.4066 | 8.344e-06 | 2.503e-05 | yes |
| drizzle - sequelize | 6.5000 | 23.3333 | 4.4542 | 5.3114 | 9.090e-05 | 1.818e-04 | yes |
| prisma - sequelize | 25.6667 | 23.3333 | 5.4066 | 5.3114 | 0.5875 | 0.5875 | no |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.9848 | 1.929e-27 | 2.141e-25 | yes |
| execution_time vs cpu_energy | drizzle | 12 | 0.8601 | 3.317e-04 | 0.0139 | yes |
| execution_time vs cpu_energy | prisma | 12 | 0.9161 | 2.843e-05 | 0.0016 | yes |
| execution_time vs cpu_energy | sequelize | 12 | 0.8112 | 0.0014 | 0.0450 | yes |
| execution_time vs memory_energy | all ORMs | 36 | 0.8759 | 2.653e-12 | 2.468e-10 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.9371 | 6.993e-06 | 4.685e-04 | yes |
| execution_time vs memory_energy | prisma | 12 | 0.9301 | 1.170e-05 | 7.723e-04 | yes |
| execution_time vs memory_energy | sequelize | 12 | 0.9580 | 9.544e-07 | 7.253e-05 | yes |

## read-owner-populated

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 3512.1987 | 128.0975 | 3439.4023 | 3419.3255 | 3582.2027 | 3408.1367 | 3808.8475 |
| prisma | 12 | 4430.9157 | 131.7533 | 4415.9209 | 4352.3065 | 4454.0947 | 4305.9355 | 4805.0643 |
| sequelize | 12 | 4159.5237 | 184.8152 | 4122.6029 | 4069.6154 | 4167.9611 | 3962.2465 | 4662.1558 |

Kruskal-Wallis: H(2) = 28.757, epsilon² = 0.822, p = 5.696e-07, Holm-adjusted p = 2.221e-05 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 6.5000 | 29.5000 | 3439.4023 | 4415.9209 | 8.923e-08 | 2.677e-07 | yes |
| drizzle - sequelize | 6.5000 | 19.5000 | 3439.4023 | 4122.6029 | 0.0025 | 0.0050 | yes |
| prisma - sequelize | 29.5000 | 19.5000 | 4415.9209 | 4122.6029 | 0.0201 | 0.0201 | yes |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 26.9328 | 0.9559 | 26.4125 | 26.3665 | 27.1438 | 26.1545 | 28.8412 |
| prisma | 12 | 35.1972 | 4.6809 | 33.9130 | 33.3425 | 34.5900 | 32.7459 | 49.8725 |
| sequelize | 12 | 31.4268 | 2.0034 | 30.6745 | 30.5243 | 31.7069 | 30.0220 | 37.4891 |

Kruskal-Wallis: H(2) = 28.938, epsilon² = 0.827, p = 5.201e-07, Holm-adjusted p = 2.080e-05 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 6.5000 | 29.5833 | 26.4125 | 33.9130 | 8.016e-08 | 2.405e-07 | yes |
| drizzle - sequelize | 6.5000 | 19.4167 | 26.4125 | 30.6745 | 0.0027 | 0.0053 | yes |
| prisma - sequelize | 29.5833 | 19.4167 | 33.9130 | 30.6745 | 0.0181 | 0.0181 | yes |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 4.6126 | 0.2037 | 4.5402 | 4.4450 | 4.7538 | 4.4153 | 5.0589 |
| prisma | 12 | 5.6340 | 0.5487 | 5.4999 | 5.4062 | 5.5715 | 5.3282 | 7.3501 |
| sequelize | 12 | 5.5379 | 0.4393 | 5.4091 | 5.3306 | 5.5201 | 5.2495 | 6.8724 |

Kruskal-Wallis: H(2) = 24.014, epsilon² = 0.686, p = 6.103e-06, Holm-adjusted p = 1.587e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 6.5000 | 26.2500 | 4.5402 | 5.4999 | 4.395e-06 | 1.318e-05 | yes |
| drizzle - sequelize | 6.5000 | 22.7500 | 4.5402 | 5.4091 | 1.581e-04 | 3.161e-04 | yes |
| prisma - sequelize | 26.2500 | 22.7500 | 5.4999 | 5.4091 | 0.4158 | 0.4158 | no |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.9704 | 1.462e-22 | 1.550e-20 | yes |
| execution_time vs cpu_energy | drizzle | 12 | 0.7413 | 0.0058 | 0.1566 | no |
| execution_time vs cpu_energy | prisma | 12 | 0.8811 | 1.527e-04 | 0.0073 | yes |
| execution_time vs cpu_energy | sequelize | 12 | 0.5804 | 0.0479 | 1.0000 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.9295 | 2.738e-16 | 2.656e-14 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.8601 | 3.317e-04 | 0.0139 | yes |
| execution_time vs memory_energy | prisma | 12 | 0.9720 | 1.287e-07 | 1.068e-05 | yes |
| execution_time vs memory_energy | sequelize | 12 | 0.9301 | 1.170e-05 | 7.723e-04 | yes |

## read-pet-populated

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 1647.5547 | 75.3544 | 1641.7355 | 1577.6356 | 1703.8588 | 1565.5313 | 1780.7716 |
| prisma | 12 | 2094.6525 | 51.3012 | 2080.1057 | 2073.9380 | 2090.8503 | 2059.7828 | 2253.6642 |
| sequelize | 12 | 1751.3730 | 23.4763 | 1759.8417 | 1744.1170 | 1764.0129 | 1701.2374 | 1782.8553 |

Kruskal-Wallis: H(2) = 28.060, epsilon² = 0.802, p = 8.069e-07, Holm-adjusted p = 2.986e-05 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 7.8333 | 30.5000 | 1641.7355 | 2080.1057 | 1.365e-07 | 4.095e-07 | yes |
| drizzle - sequelize | 7.8333 | 17.1667 | 1641.7355 | 1759.8417 | 0.0300 | 0.0300 | yes |
| prisma - sequelize | 30.5000 | 17.1667 | 2080.1057 | 1759.8417 | 0.0019 | 0.0039 | yes |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 12.1390 | 0.5277 | 11.9942 | 11.7953 | 12.4981 | 11.4294 | 13.1045 |
| prisma | 12 | 15.5695 | 2.0670 | 14.9428 | 14.8543 | 15.1743 | 14.7649 | 22.1114 |
| sequelize | 12 | 12.5296 | 0.2332 | 12.5448 | 12.4393 | 12.6477 | 12.0547 | 12.9532 |

Kruskal-Wallis: H(2) = 25.297, epsilon² = 0.723, p = 3.212e-06, Holm-adjusted p = 9.691e-05 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 9.5000 | 30.5000 | 11.9942 | 14.9428 | 1.048e-06 | 3.144e-06 | yes |
| drizzle - sequelize | 9.5000 | 15.5000 | 11.9942 | 12.5448 | 0.1630 | 0.1630 | no |
| prisma - sequelize | 30.5000 | 15.5000 | 14.9428 | 12.5448 | 4.877e-04 | 9.754e-04 | yes |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 2.5246 | 0.1197 | 2.5079 | 2.4206 | 2.6180 | 2.3749 | 2.7374 |
| prisma | 12 | 3.3482 | 0.2638 | 3.2678 | 3.2611 | 3.2921 | 3.2423 | 4.1838 |
| sequelize | 12 | 2.7085 | 0.0401 | 2.7265 | 2.6944 | 2.7331 | 2.6336 | 2.7459 |

Kruskal-Wallis: H(2) = 28.757, epsilon² = 0.822, p = 5.696e-07, Holm-adjusted p = 2.221e-05 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 7.5000 | 30.5000 | 2.5079 | 3.2678 | 8.923e-08 | 2.677e-07 | yes |
| drizzle - sequelize | 7.5000 | 17.5000 | 2.5079 | 2.7265 | 0.0201 | 0.0201 | yes |
| prisma - sequelize | 30.5000 | 17.5000 | 3.2678 | 2.7265 | 0.0025 | 0.0050 | yes |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.9313 | 1.789e-16 | 1.753e-14 | yes |
| execution_time vs cpu_energy | drizzle | 12 | 0.9091 | 4.191e-05 | 0.0023 | yes |
| execution_time vs cpu_energy | prisma | 12 | 0.4965 | 0.1006 | 1.0000 | no |
| execution_time vs cpu_energy | sequelize | 12 | 0.4476 | 0.1446 | 1.0000 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.9753 | 7.046e-24 | 7.680e-22 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.9301 | 1.170e-05 | 7.723e-04 | yes |
| execution_time vs memory_energy | prisma | 12 | 0.6434 | 0.0240 | 0.5521 | no |
| execution_time vs memory_energy | sequelize | 12 | 0.8392 | 6.428e-04 | 0.0238 | yes |

## update-owner-no-pets

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 20397.3461 | 615.2635 | 20512.4142 | 19860.5494 | 20934.3144 | 19489.8401 | 21223.2554 |
| prisma | 12 | 21523.5516 | 2203.6466 | 22113.2304 | 21446.3150 | 22591.2047 | 14902.9198 | 23124.0891 |
| sequelize | 12 | 19867.8126 | 653.6529 | 19884.6627 | 19364.7854 | 20150.4763 | 19059.7258 | 21344.4416 |

Kruskal-Wallis: H(2) = 15.761, epsilon² = 0.450, p = 3.780e-04, Holm-adjusted p = 0.0023 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 16.5833 | 27.8333 | 20512.4142 | 22113.2304 | 0.0089 | 0.0178 | yes |
| drizzle - sequelize | 16.5833 | 11.0833 | 20512.4142 | 19884.6627 | 0.2010 | 0.2010 | no |
| prisma - sequelize | 27.8333 | 11.0833 | 22113.2304 | 19884.6627 | 9.848e-05 | 2.955e-04 | yes |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 44.9095 | 1.1185 | 44.7383 | 44.3753 | 45.5168 | 43.0879 | 46.7559 |
| prisma | 12 | 55.6607 | 21.5985 | 49.4978 | 49.0463 | 50.1239 | 47.8917 | 124.1815 |
| sequelize | 12 | 46.0700 | 1.2366 | 45.6774 | 45.4036 | 47.1811 | 43.8633 | 48.2465 |

Kruskal-Wallis: H(2) = 25.254, epsilon² = 0.722, p = 3.283e-06, Holm-adjusted p = 9.691e-05 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 9.3333 | 30.4167 | 44.7383 | 49.4978 | 9.497e-07 | 2.849e-06 | yes |
| drizzle - sequelize | 9.3333 | 15.7500 | 44.7383 | 45.6774 | 0.1357 | 0.1357 | no |
| prisma - sequelize | 30.4167 | 15.7500 | 49.4978 | 45.6774 | 6.498e-04 | 0.0013 | yes |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 17.9391 | 0.4640 | 18.0349 | 17.5290 | 18.2815 | 17.2623 | 18.6765 |
| prisma | 12 | 19.9212 | 0.7288 | 20.1184 | 19.5269 | 20.3818 | 18.3599 | 20.9066 |
| sequelize | 12 | 18.0357 | 0.5272 | 18.0434 | 17.6008 | 18.2171 | 17.3747 | 19.2509 |

Kruskal-Wallis: H(2) = 21.500, epsilon² = 0.614, p = 2.145e-05, Holm-adjusted p = 2.788e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 12.2500 | 30.0000 | 18.0349 | 20.1184 | 3.679e-05 | 1.104e-04 | yes |
| drizzle - sequelize | 12.2500 | 13.2500 | 18.0349 | 18.0434 | 0.8162 | 0.8162 | no |
| prisma - sequelize | 30.0000 | 13.2500 | 20.1184 | 18.0434 | 9.848e-05 | 1.970e-04 | yes |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.5503 | 5.063e-04 | 0.0192 | yes |
| execution_time vs cpu_energy | drizzle | 12 | 0.2308 | 0.4705 | 1.0000 | no |
| execution_time vs cpu_energy | prisma | 12 | 0.2378 | 0.4568 | 1.0000 | no |
| execution_time vs cpu_energy | sequelize | 12 | 0.3846 | 0.2170 | 1.0000 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.8891 | 4.401e-13 | 4.181e-11 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.9441 | 3.927e-06 | 2.788e-04 | yes |
| execution_time vs memory_energy | prisma | 12 | 0.9860 | 4.117e-09 | 3.788e-07 | yes |
| execution_time vs memory_energy | sequelize | 12 | 0.9301 | 1.170e-05 | 7.723e-04 | yes |

## update-owner-no-visits

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 20337.7022 | 855.2963 | 20435.6341 | 19941.1449 | 20737.9959 | 18761.3661 | 21706.4866 |
| prisma | 12 | 22079.5419 | 535.1391 | 22138.4177 | 21884.9827 | 22339.6396 | 20960.7732 | 22797.6522 |
| sequelize | 12 | 19945.4087 | 358.3777 | 19984.4679 | 19812.3906 | 20136.4592 | 19119.4095 | 20557.0017 |

Kruskal-Wallis: H(2) = 23.423, epsilon² = 0.669, p = 8.197e-06, Holm-adjusted p = 1.701e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 15.1667 | 30.1667 | 20435.6341 | 22138.4177 | 4.877e-04 | 9.754e-04 | yes |
| drizzle - sequelize | 15.1667 | 10.1667 | 20435.6341 | 19984.4679 | 0.2450 | 0.2450 | no |
| prisma - sequelize | 30.1667 | 10.1667 | 22138.4177 | 19984.4679 | 3.321e-06 | 9.963e-06 | yes |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 45.0073 | 1.4582 | 44.6817 | 44.0420 | 46.3720 | 42.2655 | 46.8627 |
| prisma | 12 | 49.7606 | 1.8742 | 49.4286 | 49.0867 | 49.9292 | 47.3489 | 54.9794 |
| sequelize | 12 | 45.6023 | 1.2924 | 45.7134 | 44.5787 | 46.4135 | 43.5049 | 47.6848 |

Kruskal-Wallis: H(2) = 23.194, epsilon² = 0.663, p = 9.195e-06, Holm-adjusted p = 1.701e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 11.0833 | 30.3333 | 44.6817 | 49.4286 | 7.622e-06 | 2.287e-05 | yes |
| drizzle - sequelize | 11.0833 | 14.0833 | 44.6817 | 45.7134 | 0.4855 | 0.4855 | no |
| prisma - sequelize | 30.3333 | 14.0833 | 49.4286 | 45.7134 | 1.581e-04 | 3.161e-04 | yes |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 17.9895 | 0.6627 | 17.9355 | 17.6479 | 18.4063 | 16.9083 | 19.0131 |
| prisma | 12 | 20.1075 | 0.3678 | 20.1163 | 19.9425 | 20.2853 | 19.5092 | 20.6597 |
| sequelize | 12 | 18.0824 | 0.3132 | 18.0645 | 17.9706 | 18.3139 | 17.4263 | 18.5256 |

Kruskal-Wallis: H(2) = 23.447, epsilon² = 0.670, p = 8.099e-06, Holm-adjusted p = 1.701e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 11.8333 | 30.5000 | 17.9355 | 20.1163 | 1.425e-05 | 4.276e-05 | yes |
| drizzle - sequelize | 11.8333 | 13.1667 | 17.9355 | 18.0645 | 0.7566 | 0.7566 | no |
| prisma - sequelize | 30.5000 | 13.1667 | 20.1163 | 18.0645 | 5.580e-05 | 1.116e-04 | yes |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.7725 | 3.413e-08 | 2.867e-06 | yes |
| execution_time vs cpu_energy | drizzle | 12 | 0.6154 | 0.0332 | 0.7297 | no |
| execution_time vs cpu_energy | prisma | 12 | 0.3846 | 0.2170 | 1.0000 | no |
| execution_time vs cpu_energy | sequelize | 12 | 0.4406 | 0.1517 | 1.0000 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.9393 | 2.335e-17 | 2.312e-15 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.9790 | 3.090e-08 | 2.688e-06 | yes |
| execution_time vs memory_energy | prisma | 12 | 0.9441 | 3.927e-06 | 2.788e-04 | yes |
| execution_time vs memory_energy | sequelize | 12 | 0.8392 | 6.428e-04 | 0.0238 | yes |

## update-owner-populated

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 20286.2377 | 411.5333 | 20361.4986 | 19976.2539 | 20562.8277 | 19550.2092 | 20974.0949 |
| prisma | 12 | 21763.6913 | 637.9392 | 21696.2709 | 21237.4419 | 22060.5910 | 21091.1695 | 23153.6479 |
| sequelize | 12 | 20123.2321 | 549.9681 | 20129.2118 | 19713.0481 | 20474.8781 | 19204.4649 | 21241.1906 |

Kruskal-Wallis: H(2) = 22.366, epsilon² = 0.639, p = 1.391e-05, Holm-adjusted p = 1.947e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 13.8333 | 30.1667 | 20361.4986 | 21696.2709 | 1.462e-04 | 2.924e-04 | yes |
| drizzle - sequelize | 13.8333 | 11.5000 | 20361.4986 | 20129.2118 | 0.5875 | 0.5875 | no |
| prisma - sequelize | 30.1667 | 11.5000 | 21696.2709 | 20129.2118 | 1.425e-05 | 4.276e-05 | yes |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 46.4008 | 2.8750 | 45.4532 | 44.9597 | 46.1692 | 44.0675 | 54.4884 |
| prisma | 12 | 49.7724 | 1.1950 | 49.7728 | 49.0787 | 50.4683 | 47.8958 | 52.0246 |
| sequelize | 12 | 46.5131 | 1.4489 | 46.5288 | 45.2753 | 47.3481 | 44.6781 | 49.6043 |

Kruskal-Wallis: H(2) = 17.056, epsilon² = 0.487, p = 1.979e-04, Holm-adjusted p = 0.0016 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 12.2500 | 28.6667 | 45.4532 | 49.7728 | 1.352e-04 | 4.056e-04 | yes |
| drizzle - sequelize | 12.2500 | 14.5833 | 45.4532 | 46.5288 | 0.5875 | 0.5875 | no |
| prisma - sequelize | 28.6667 | 14.5833 | 49.7728 | 46.5288 | 0.0011 | 0.0021 | yes |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 18.0654 | 0.3687 | 18.0616 | 17.8928 | 18.2443 | 17.3695 | 18.7644 |
| prisma | 12 | 19.8876 | 0.5029 | 19.7482 | 19.5221 | 20.0690 | 19.3372 | 21.0392 |
| sequelize | 12 | 18.2573 | 0.4480 | 18.2139 | 17.9791 | 18.4443 | 17.4584 | 19.2014 |

Kruskal-Wallis: H(2) = 23.838, epsilon² = 0.681, p = 6.663e-06, Holm-adjusted p = 1.599e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 11.0000 | 30.5000 | 18.0616 | 19.7482 | 5.797e-06 | 1.739e-05 | yes |
| drizzle - sequelize | 11.0000 | 14.0000 | 18.0616 | 18.2139 | 0.4855 | 0.4855 | no |
| prisma - sequelize | 30.5000 | 14.0000 | 19.7482 | 18.2139 | 1.250e-04 | 2.499e-04 | yes |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.5864 | 1.712e-04 | 0.0079 | yes |
| execution_time vs cpu_energy | drizzle | 12 | -0.0559 | 0.8629 | 1.0000 | no |
| execution_time vs cpu_energy | prisma | 12 | 0.2448 | 0.4433 | 1.0000 | no |
| execution_time vs cpu_energy | sequelize | 12 | 0.3077 | 0.3306 | 1.0000 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.9233 | 1.087e-15 | 1.044e-13 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.7063 | 0.0102 | 0.2664 | no |
| execution_time vs memory_energy | prisma | 12 | 0.9091 | 4.191e-05 | 0.0023 | yes |
| execution_time vs memory_energy | sequelize | 12 | 0.9441 | 3.927e-06 | 2.788e-04 | yes |

## update-pet-populated

### Execution time (ms)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 16743.3244 | 391.8225 | 16817.9162 | 16405.8832 | 16959.1548 | 16014.9088 | 17437.0070 |
| prisma | 12 | 17985.0769 | 1589.5897 | 18277.4456 | 17895.4887 | 18604.1388 | 13355.5207 | 19713.2066 |
| sequelize | 12 | 17570.4433 | 373.4695 | 17527.0886 | 17334.5369 | 17596.2522 | 17111.7124 | 18520.3686 |

Kruskal-Wallis: H(2) = 20.389, epsilon² = 0.583, p = 3.738e-05, Holm-adjusted p = 4.485e-04 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (ms) | Median B (ms) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 7.9167 | 27.0000 | 16817.9162 | 18277.4456 | 9.131e-06 | 2.739e-05 | yes |
| drizzle - sequelize | 7.9167 | 20.5833 | 16817.9162 | 17527.0886 | 0.0032 | 0.0065 | yes |
| prisma - sequelize | 27.0000 | 20.5833 | 18277.4456 | 17527.0886 | 0.1357 | 0.1357 | no |

### CPU energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 34.7524 | 1.2381 | 34.7610 | 33.7160 | 35.5726 | 33.0385 | 36.9577 |
| prisma | 12 | 42.2338 | 11.8190 | 38.8244 | 38.5103 | 39.4383 | 38.0670 | 79.7271 |
| sequelize | 12 | 36.7049 | 0.9117 | 36.7590 | 36.3282 | 37.4699 | 35.0342 | 37.9568 |

Kruskal-Wallis: H(2) = 27.730, epsilon² = 0.792, p = 9.518e-07, Holm-adjusted p = 3.331e-05 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 8.0000 | 30.5000 | 34.7610 | 38.8244 | 1.685e-07 | 5.054e-07 | yes |
| drizzle - sequelize | 8.0000 | 17.0000 | 34.7610 | 36.7590 | 0.0364 | 0.0364 | yes |
| prisma - sequelize | 30.5000 | 17.0000 | 38.8244 | 36.7590 | 0.0017 | 0.0034 | yes |

### Memory energy consumption (J)

| ORM | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| drizzle | 12 | 14.7432 | 0.3370 | 14.8420 | 14.4405 | 14.9729 | 14.1203 | 15.1961 |
| prisma | 12 | 16.2549 | 0.6219 | 16.3297 | 15.8531 | 16.4869 | 14.9795 | 17.4083 |
| sequelize | 12 | 15.5821 | 0.2934 | 15.5744 | 15.4124 | 15.5986 | 15.1546 | 16.3287 |

Kruskal-Wallis: H(2) = 25.977, epsilon² = 0.742, p = 2.286e-06, Holm-adjusted p = 7.315e-05 -> significant difference between ORMs.

Dunn's test (Holm-adjusted over the three pairs):

| Pair (A - B) | Mean rank A | Mean rank B | Median A (J) | Median B (J) | p | p_holm | Significant |
|---|---|---|---|---|---|---|---|
| drizzle - prisma | 6.8333 | 28.5833 | 14.8420 | 16.3297 | 4.264e-07 | 1.279e-06 | yes |
| drizzle - sequelize | 6.8333 | 20.0833 | 14.8420 | 15.5744 | 0.0021 | 0.0041 | yes |
| prisma - sequelize | 28.5833 | 20.0833 | 16.3297 | 15.5744 | 0.0481 | 0.0481 | yes |

### Spearman rank-order correlation

| Pair | Scope | n | rho | p | p_holm | Significant |
|---|---|---|---|---|---|---|
| execution_time vs cpu_energy | all ORMs | 36 | 0.6736 | 6.708e-06 | 4.562e-04 | yes |
| execution_time vs cpu_energy | drizzle | 12 | 0.7692 | 0.0034 | 0.1034 | no |
| execution_time vs cpu_energy | prisma | 12 | 0.1958 | 0.5419 | 1.0000 | no |
| execution_time vs cpu_energy | sequelize | 12 | -0.1329 | 0.6806 | 1.0000 | no |
| execution_time vs memory_energy | all ORMs | 36 | 0.9642 | 3.498e-21 | 3.637e-19 | yes |
| execution_time vs memory_energy | drizzle | 12 | 0.9301 | 1.170e-05 | 7.723e-04 | yes |
| execution_time vs memory_energy | prisma | 12 | 0.9650 | 3.881e-07 | 3.027e-05 | yes |
| execution_time vs memory_energy | sequelize | 12 | 0.8322 | 7.854e-04 | 0.0275 | yes |
