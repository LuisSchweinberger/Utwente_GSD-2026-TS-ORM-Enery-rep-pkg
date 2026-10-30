import { fileURLToPath } from "node:url";
import { benchmarkSize } from "./config.js";
import { restoreSnapshot } from "./snapshot.js";

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const snapshot = await restoreSnapshot(benchmarkSize());
  console.log(`Database restored to snapshot (SIZE=${snapshot.size}, SHA-256 ${snapshot.sha256})`);
}
