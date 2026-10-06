---
name: repository-change-compliance
description: Use when modifying an existing code repository with explicit implementation, testing, typing, and documentation requirements.
---
1. Read the task rules before editing and turn each rule into a checklist item.
2. Inspect repository layout, public APIs, existing tests, and project tooling.
3. Never modify protected files; use version-control status/diff to confirm this before finishing.
4. Add complete type annotations to every changed public function and audit other public functions if required.
5. Make behavior changes narrowly and preserve established interfaces unless the task requires otherwise.
6. Add a dedicated regression test for every distinct bug fixed; make each test independently meaningful.
7. Update required release notes in the exact requested heading and bullet format.
8. Run tests from the project root or documented working directory so imports resolve correctly.
9. If the test runner fails because of environment or plugin issues, diagnose that separately from code failures.
10. Run the mandated tests plus targeted new tests.
11. Inspect the final diff for accidental edits, missing files, and uncommitted generated artifacts.
12. Report verification only after all required checks have actually passed.
