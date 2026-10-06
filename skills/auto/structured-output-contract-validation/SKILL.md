---
name: structured-output-contract-validation
description: Use when producing CSV, JSON, or other machine-checked data artifacts from messy source data.
---
1. Extract every required output field, type, format, ordering rule, and metadata rule into a checklist.
2. Read input with an explicit parser and count raw data rows separately from headers.
3. Normalize values before aggregation: whitespace, case, identifiers, timestamps, categories, and sentinels.
4. Define deduplication identity and conflict handling before computing metrics.
5. Preserve required distinctions between raw-row counts, distinct-record counts, and usable-record counts.
6. Represent money internally as `Decimal` or integer minor units; never use binary floats.
7. Convert monetary values to integer minor units before serializing when required.
8. Parse timestamps with timezone awareness and serialize all output timestamps in the specified UTC format.
9. Build cleaned artifacts from the same canonical records used for summary calculations.
10. Write CSV headers in the exact required order and emit only permitted rows.
11. Write all required JSON top-level fields, including schema/version/provenance metadata.
12. Sort arrays and records exactly as specified, using explicit sort keys.
13. Validate JSON syntax and CSV structure after writing.
14. Re-read generated files and assert key invariants: types, counts, headers, order, and canonical values.
15. Do not claim completion until every requested artifact exists at its required path.
