### Human
The test suite of the `inventory` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: task
{"subagent_type": "explorer", "description": "Inspect the failing Python package and tests under workspace/ only. Do not edit files. Follow these task rules: do not modify tests; source must satisfy every docstring, including behavior not visibly tested; use shell commands from sandbox root with relative workspace/ paths. Identify project structure, test failures (run whole suite if feasible), relevant source/docstrings, and recommend precise changes. Return a concise verified report with file paths and commands/results."}

### Tool result
## Verified inspection report

No files were modified.

### Project structure
- `workspace/README.md` — package test instruction: `cd workspace && python -m pytest tests -q`
- `workspace/inventory/`
  - `__init__.py` — empty
  - `pricing.py` — price parsing and discount calculation
  - `report.py` — total-value and low-stock reporting
  - `export.py` — CSV-row formatting
- `workspace/tests/test_report.py` — 6 visible tests

### Test execution

From the sandbox root, the normal command:

```bat
python -m pytest workspace/tests -q
```

could not begin collection because an externally installed `anyio` pytest plugin failed while importing Windows `asyncio` (`OSError: [WinError 10106]`). This is an environment/plugin issue, not a failure in `workspace/` package code.

Re-ran with third-party pytest plugin autoload disabled and the package directory on `PYTHONPATH`:

```bat
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 && set PYTHONPATH=workspace && python -m pytest workspace/tests -q
```

Result: **2 failed, 4 passed**.

Failures:
1. `workspace/tests/test_report.py::test_total_value_thousands_separator`
   - `workspace/inventory/pricing.py:15`
   - `parse_price("$1,299.50")` passes `"1,299.50"` to `Decimal`, causing `decimal.InvalidOperation`.

2. `workspace/tests/test_report.py::test_discount_rounding_half_up`
   - `workspace/inventory/pricing.py:25`
   - `apply_discount(Decimal("10.05"), 10)` returns `Decimal("9.04")`, but the required result is `Decimal("9.05")`.
   - Cause: `Decimal.q

### Tool call: ls
{"path": "/workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/inventory/', '/workspace/tests/']

### Tool call: read_file
{"file_path": "/workspace/inventory/pricing.py", "limit": 400}

### Tool call: read_file
{"file_path": "/workspace/inventory/report.py", "limit": 400}

### Tool call: read_file
{"file_path": "/workspace/inventory/export.py", "limit": 400}

### Tool call: read_file
{"file_path": "/workspace/tests/test_report.py", "limit": 400}

### Tool call: read_file
{"file_path": "/workspace/README.md", "limit": 300}

### Tool result
@@ lines 1-25 of 25 @@
"""Price utilities for the inventory package."""
from decimal import Decimal


def parse_price(text):
    """Convert a price string to a Decimal.

    Supported formats:
      "$1,299.50" -> Decimal("1299.50")
      "  12 "     -> Decimal("12")
      "1299.5"    -> Decimal("1299.5")
      "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
    """
    cleaned = text.strip().replace("$", "")
    return Decimal(cleaned)


def apply_discount(price, percent):
    """Return `price` after a percentage discount.

    The result is a Decimal rounded to 2 decimal places using the
    commercial rule "round half up" (0.005 -> 0.01).
    """
    discounted = price * (100 - percent) / 100
    return discounted.quantize(Decimal("0.01"))

### Tool result
@@ lines 1-25 of 25 @@
"""Inventory reports."""
from decimal import Decimal

from .pricing import apply_discount, parse_price


def total_value(items):
    """Total value of `items` after per-item discounts.

    Each item is a dict: {"name": str, "price": str, "qty": int, "discount": percent (optional)}.
    """
    total = Decimal("0")
    for item in items:
        price = parse_price(item["price"])
        price = apply_discount(price, item.get("discount", 0))
        total += price * item["qty"]
    return total


def low_stock(items, threshold=5):
    """Names of the items whose quantity is strictly below `threshold`.

    The names are sorted alphabetically, ignoring case.
    """
    return [item["name"] for item in items if item["qty"] <= threshold]

### Tool result
@@ lines 1-12 of 12 @@
"""Export helpers."""
from .pricing import parse_price


def to_csv_row(item):
    """Format one item as a CSV row: name,price,qty (price with 2 decimals).

    A name that contains a comma or a double quote is wrapped in double quotes,
    and every double quote inside it is doubled (RFC 4180).
    """
    price = parse_price(item["price"])
    return f'{item["name"]},{price:.2f},{item["qty"]}'

### Tool result
@@ lines 1-32 of 32 @@
from decimal import Decimal

from inventory.export import to_csv_row
from inventory.pricing import apply_discount
from inventory.report import low_stock, total_value


def test_total_value_plain():
    items = [{"name": "pen", "price": "$2.50", "qty": 4}]
    assert total_value(items) == Decimal("10.00")


def test_total_value_thousands_separator():
    items = [{"name": "laptop", "price": "$1,299.50", "qty": 2}]
    assert total_value(items) == Decimal("2599.00")


def test_discount_rounding_half_up():
    assert apply_discount(Decimal("10.05"), 10) == Decimal("9.05")


def test_total_value_with_discount():
    items = [{"name": "desk", "price": "100.00", "qty": 1, "discount": 15}]
    assert total_value(items) == Decimal("85.00")


def test_low_stock_basic():
    assert low_stock([{"name": "pen", "qty": 2}, {"name": "ink", "qty": 9}]) == ["pen"]


def test_csv_row_plain_name():
    assert to_csv_row({"name": "pen", "price": "2.5", "qty": 4}) == "pen,2.50,4"

### Tool result
@@ lines 1-5 of 5 @@
# inventory

Small package. Run the tests from the `workspace/` folder:

    cd workspace && python -m pytest tests -q

### Tool call: task
{"subagent_type": "implementer", "description": "Implement and validate this fix in workspace/ only. Task rules: source code must make entire test suite pass and satisfy all docstrings; do not modify any existing files in workspace/tests/; use only workspace-relative paths in shell commands (shell starts sandbox root). Review code before edits and only edit these source files as needed: workspace/inventory/pricing.py, workspace/inventory/report.py, workspace/inventory/export.py. Required behavior: parse_price supports whitespace, dollar signs, comma thousands separators, and accounting negatives with outer parentheses; apply_discount rounds Decimal values to exactly 2 places using ROUND_HALF_UP; low_stock includes qty strictly below threshold and sorts returned names alphabetically case-insensitively; to_csv_row uses RFC 4180 quote escaping for names containing comma or double quote. Preserve appropriate simple style/type behavior. Run tests with third-party pytest plugin autoload disabled if needed, e.g. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=workspace python -m pytest workspace/tests -q. Report exactly changed files and validation results. Do not edit tests."}

### Tool result
Changed files:
- `workspace/inventory/pricing.py`
  - Added comma separator and accounting-parentheses parsing.
  - Applied explicit `ROUND_HALF_UP` quantization to two decimal places.
- `workspace/inventory/report.py`
  - Corrected low-stock comparison to strictly below threshold.
  - Added case-insensitive alphabetical sorting.
- `workspace/inventory/export.py`
  - Added RFC 4180 escaping for commas and double quotes in names.

Validation:
- Attempted requested POSIX-style command; sandbox uses Windows shell and rejected environment-variable syntax.
- Ran equivalent command:
  - `set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1&& set PYTHONPATH=workspace&& python -m pytest workspace/tests -q`
  - Result: `6 passed in 0.03s`

Remaining risk: none identified.

### Tool call: read_file
{"file_path": "/workspace/inventory/pricing.py", "limit": 200}

### Tool call: read_file
{"file_path": "/workspace/inventory/report.py", "limit": 200}

### Tool call: read_file
{"file_path": "/workspace/inventory/export.py", "limit": 200}

### Tool result
@@ lines 1-27 of 27 @@
"""Price utilities for the inventory package."""
from decimal import ROUND_HALF_UP, Decimal


def parse_price(text):
    """Convert a price string to a Decimal.

    Supported formats:
      "$1,299.50" -> Decimal("1299.50")
      "  12 "     -> Decimal("12")
      "1299.5"    -> Decimal("1299.5")
      "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
    """
    cleaned = text.strip().replace("$", "").replace(",", "")
    if cleaned.startswith("(") and cleaned.endswith(")"):
        cleaned = f"-{cleaned[1:-1]}"
    return Decimal(cleaned)


def apply_discount(price, percent):
    """Return `price` after a percentage discount.

    The result is a Decimal rounded to 2 decimal places using the
    commercial rule "round half up" (0.005 -> 0.01).
    """
    discounted = price * (100 - percent) / 100
    return discounted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

### Tool result
@@ lines 1-28 of 28 @@
"""Inventory reports."""
from decimal import Decimal

from .pricing import apply_discount, parse_price


def total_value(items):
    """Total value of `items` after per-item discounts.

    Each item is a dict: {"name": str, "price": str, "qty": int, "discount": percent (optional)}.
    """
    total = Decimal("0")
    for item in items:
        price = parse_price(item["price"])
        price = apply_discount(price, item.get("discount", 0))
        total += price * item["qty"]
    return total


def low_stock(items, threshold=5):
    """Names of the items whose quantity is strictly below `threshold`.

    The names are sorted alphabetically, ignoring case.
    """
    return sorted(
        (item["name"] for item in items if item["qty"] < threshold),
        key=str.casefold,
    )

### Tool result
@@ lines 1-15 of 15 @@
"""Export helpers."""
from .pricing import parse_price


def to_csv_row(item):
    """Format one item as a CSV row: name,price,qty (price with 2 decimals).

    A name that contains a comma or a double quote is wrapped in double quotes,
    and every double quote inside it is doubled (RFC 4180).
    """
    name = item["name"]
    if "," in name or '"' in name:
        name = '"' + name.replace('"', '""') + '"'
    price = parse_price(item["price"])
    return f"{name},{price:.2f},{item['qty']}"

### Tool call: execute
{"command": "set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1&& set PYTHONPATH=workspace&& python -m pytest workspace/tests -q", "timeout": 120}

### Tool result
......                                                                   [100%]
6 passed in 0.01s

[Command succeeded with exit code 0]

### Assistant
Fixed inventory behavior to match its docstrings:

- `workspace/inventory/pricing.py`: supports comma separators and accounting-style negative prices; discount rounding now uses `ROUND_HALF_UP`.
- `workspace/inventory/report.py`: low-stock results are strictly below the threshold and sorted case-insensitively.
- `workspace/inventory/export.py`: CSV names now escape commas and double quotes per RFC 4180.

Validated with the full visible suite: **6 passed**.