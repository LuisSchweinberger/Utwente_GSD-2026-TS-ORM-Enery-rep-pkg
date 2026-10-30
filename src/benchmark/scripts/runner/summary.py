"""Means/medians per ORM + task; retain counts and incomplete-run status."""
import csv
import json
import math
import statistics
from .artifacts import ORMS, now, write_json


def statistics_for(values):
    values = [value for value in values if isinstance(value, (int, float)) and math.isfinite(value)]
    return {"count": len(values), "mean": statistics.mean(values) if values else None,
            "median": statistics.median(values) if values else None}


def summarize(directory, manifest):
    groups = {(orm, task["scenario"], task["profile"]): [] for orm in ORMS for task in manifest["tasks"]}
    invalid = 0
    paths = [directory / "trials" / f"trial-{index:03d}" / orm / f"{task['scenario']}-{task['profile']}.json"
             for index in range(1, manifest["trialsPlanned"] + 1) for orm in ORMS for task in manifest["tasks"]]
    for path in paths:
        if not path.exists():
            continue
        try:
            record = json.loads(path.read_text())
        except ValueError:
            invalid += 1
            continue
        key = (record.get("orm"), record.get("scenario"), record.get("profile"))
        if key not in groups:
            continue
        if record.get("status") != "valid":
            invalid += 1
            continue
        groups[key].append(record)
    rows, csv_rows = [], []
    for (orm, scenario, profile), records in groups.items():
        metrics = {name: statistics_for([row.get(name) for row in records]) for name in ("workloadElapsedMs", "throughputOpsPerSecond")}
        domain_key = lambda domain: f"{domain['id']}:{domain['name']}" if domain.get("id") else domain["name"]
        domains = sorted({domain_key(domain) for row in records for domain in row.get("measurement", {}).get("domains", [])})
        energy = {}
        for name in domains:
            values = [domain for row in records for domain in row["measurement"]["domains"] if domain_key(domain) == name]
            energy[name] = {metric: statistics_for([domain.get(metric) for domain in values])
                            for metric in ("energyJ", "averagePowerW", "energyPerOperationJ")}
        rows.append({"orm": orm, "scenario": scenario, "profile": profile, "validTaskCount": len(records),
                     "expectedTaskCount": manifest["trialsPlanned"], "metrics": metrics, "energyDomains": energy})
        for metric, stats in metrics.items():
            csv_rows.append([orm, scenario, profile, "", metric, stats["count"], stats["mean"], stats["median"]])
        for domain, domain_metrics in energy.items():
            for metric, stats in domain_metrics.items():
                csv_rows.append([orm, scenario, profile, domain, metric, stats["count"], stats["mean"], stats["median"]])
    result = {"formatVersion": 1, "createdAt": now(), "runStatus": manifest["status"],
              "complete": manifest["status"] == "completed" and all(len(records) == manifest["trialsPlanned"] for records in groups.values()), "trialsPlanned": manifest["trialsPlanned"],
              "trialsCompleted": manifest["trialsCompleted"], "invalidTaskResults": invalid,
              "baselineAdjustment": "none; raw workload energy", "groups": rows}
    write_json(directory / "summary.json", result)
    with (directory / "summary.csv").open("w", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(["orm", "scenario", "profile", "domain", "metric", "count", "mean", "median"])
        writer.writerows(csv_rows)
    return result
