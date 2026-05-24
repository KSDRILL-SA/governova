// Generate TypeScript types from the compiled constitutional JSON Schema.
// Invoked by `governova-codegen` (Python orchestrator) or `npm run generate`.
// Do not edit the output (src/index.ts) by hand.

import { compileFromFile } from "json-schema-to-typescript";
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const schemaPath = resolve(here, "../../../../compiled/constitution.schema.json");
const outPath = resolve(here, "../src/index.ts");

const banner = [
  "/**",
  " * Governova — compiled constitutional index types.",
  " *",
  " * DO NOT EDIT. Generated from compiled/constitution.schema.json by",
  " * `governova-codegen`. The source of truth is",
  " * scripts/governova_compile/schema.py.",
  " */",
  "",
].join("\n");

const ts = await compileFromFile(schemaPath, {
  bannerComment: banner,
  additionalProperties: false,
  style: { singleQuote: false, semi: true },
});

await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, ts, "utf-8");
console.log(`Wrote ${outPath}`);
