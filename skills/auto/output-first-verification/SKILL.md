---
name: output-first-verification
description: Use when a task is evaluated by hidden checks against files, schemas, or repository state.
---
1. Treat stated rules as acceptance tests, not as optional guidance.
2. Before implementation, list required paths, filenames, schemas, exact literals, and ordering constraints.
3. Prefer a small reproducible script over ad hoc shell one-liners for nontrivial transformations.
4. Account for the active shell and operating system when setting environment variables or chaining commands.
5. After generation, inspect the actual output file rather than relying only on script output.
6. Validate from the evaluator’s likely working directory and with the project’s expected import paths.
7. Check that helper scripts or temporary validation files are not forbidden deliverables.
8. Compare final repository status against protected-file and required-new-file rules.
9. Use programmatic assertions for the rules most likely to be missed: field types, required metadata, sorting, and filenames.
10. Fix failures at their source, regenerate outputs, and rerun validation.
11. Keep the final response limited to work actually completed and verified.
