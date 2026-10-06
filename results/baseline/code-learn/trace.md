### Human
The test suite of the `inventory` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: ls
{"path": "/"}

### Tool result
['/workspace/']

### Tool call: ls
{"path": "/workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/inventory/', '/workspace/tests/']

### Tool call: ls
{"path": "/workspace/inventory"}

### Tool call: ls
{"path": "/workspace/tests"}

### Tool call: read_file
{"file_path": "/workspace/README.md"}

### Tool call: read_file
{"file_path": "/workspace/CHANGELOG.md"}

### Tool result
['/workspace/inventory/__init__.py', '/workspace/inventory/__pycache__/', '/workspace/inventory/export.py', '/workspace/inventory/pricing.py', '/workspace/inventory/report.py']

### Tool result
['/workspace/tests/__pycache__/', '/workspace/tests/test_report.py']

### Tool result
@@ lines 1-5 of 5 @@
# inventory

Small package. Run the tests from the `workspace/` folder:

    cd workspace && python -m pytest tests -q

### Tool result
@@ lines 1-6 of 6 @@
# Changelog

## Unreleased

## 0.3.1
- initial import

### Tool call: read_file
{"file_path": "/workspace/inventory/export.py", "limit": 400}

### Tool call: read_file
{"file_path": "/workspace/inventory/pricing.py", "limit": 400}

### Tool call: read_file
{"file_path": "/workspace/inventory/report.py", "limit": 400}

### Tool call: read_file
{"file_path": "/workspace/inventory/__init__.py", "limit": 400}

### Tool call: read_file
{"file_path": "/workspace/tests/test_report.py", "limit": 400}

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
@@ lines 1-1 @@
System reminder: File exists but has empty contents

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

### Tool call: edit_file
{"file_path": "/workspace/inventory/pricing.py", "old_string": "\"\"\"Price utilities for the inventory package.\"\"\"\nfrom decimal import Decimal\n\n\ndef parse_price(text):\n    \"\"\"Convert a price string to a Decimal.\n\n    Supported formats:\n      \"$1,299.50\" -> Decimal(\"1299.50\")\n      \"  12 \"     -> Decimal(\"12\")\n      \"1299.5\"    -> Decimal(\"1299.5\")\n      \"(12.00)\"   -> Decimal(\"-12.00\")   # accounting style: parentheses mean negative\n    \"\"\"\n    cleaned = text.strip().replace(\"$\", \"\")\n    return Decimal(cleaned)\n\n\ndef apply_discount(price, percent):\n    \"\"\"Return `price` after a percentage discount.\n\n    The result is a Decimal rounded to 2 decimal places using the\n    commercial rule \"round half up\" (0.005 -> 0.01).\n    \"\"\"\n    discounted = price * (100 - percent) / 100\n    return discounted.quantize(Decimal(\"0.01\"))\n", "new_string": "\"\"\"Price utilities for the inventory package.\"\"\"\nfrom decimal import Decimal, ROUND_HALF_UP\n\n\ndef parse_price(text):\n    \"\"\"Convert a price string to a Decimal.\n\n    Supported formats:\n      \"$1,299.50\" -> Decimal(\"1299.50\")\n      \"  12 \"     -> Decimal(\"12\")\n      \"1299.5\"    -> Decimal(\"1299.5\")\n      \"(12.00)\"   -> Decimal(\"-12.00\")   # accounting style: parentheses mean negative\n    \"\"\"\n    cleaned = text.strip().replace(\"$\", \"\").replace(\",\", \"\")\n    if cleaned.startswith(\"(\") and cleaned.endswith(\")\"):\n        cleaned = f\

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/pricing.py'

### Tool call: edit_file
{"file_path": "/workspace/inventory/export.py", "old_string": "    price = parse_price(item[\"price\"])\n    return f'{item[\"name\"]},{price:.2f},{item[\"qty\"]}'", "new_string": "    name = item[\"name\"]\n    if \",\" in name or '\"' in name:\n        name = f'\"{name.replace(chr(34), chr(34) * 2)}\"'\n\n    price = parse_price(item[\"price\"])\n    return f\"{name},{price:.2f},{item['qty']}\""}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/export.py'

### Tool call: edit_file
{"file_path": "/workspace/inventory/report.py", "old_string": "    return [item[\"name\"] for item in items if item[\"qty\"] <= threshold]", "new_string": "    names = (item[\"name\"] for item in items if item[\"qty\"] < threshold)\n    return sorted(names, key=str.casefold)"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/report.py'

### Tool call: execute
{"command": "python -m pytest workspace/tests -q", "timeout": 120}

### Tool result
[stderr] Traceback (most recent call last):
[stderr]   File "~\Documents\Codex\2026-10-06\https-github-com-lonelystar05-k4-day20\work\repo\.venv\Lib\site-packages\anyio\_core\_eventloop.py", line 204, in get_async_backend
[stderr]     return loaded_backends[asynclib_name]
[stderr]            ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
[stderr] KeyError: 'asyncio'
[stderr] 
[stderr] During handling of the above exception, another exception occurred:
[stderr] 
[stderr] Traceback (most recent call last):
[stderr]   File "<frozen runpy>", line 198, in _run_module_as_main
[stderr]   File "<frozen runpy>", line 88, in _run_code
[stderr]   File "~\Documents\Codex\2026-10-06\https-github-com-lonelystar05-k4-day20\work\repo\.venv\Lib\site-packages\pytest\__main__.py", line 9, in <module>
[stderr]     raise SystemExit(_console_main())
[stderr]                      ^^^^^^^^^^^^^^^
[stderr]   File "~\Documents\Codex\2026-10-06\https-github-com-lonelystar05-k4-day20\work\repo\.venv\Lib\site-packages\_pytest\config\__init__.py", line 253, in _console_main
[stderr]     code = _main(prog=_get_prog_name(sys.argv))
[stderr]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[stderr]   File "~\Documents\Codex\2026-10-06\https-github-com-lonelystar05-k4-day20\work\repo\.venv\Lib\site-packages\_pytest\config\__init__.py", line 223, in _main
[stderr]     config = _prepareconfig(new_args, plugins, prog=prog)
[stderr]              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[stderr]   File "~\Documents\Codex\2026-

### Tool call: execute
{"command": "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest workspace/tests -q", "timeout": 120}

### Tool result
[stderr] 'PYTEST_DISABLE_PLUGIN_AUTOLOAD' is not recognized as an internal or external command,
[stderr] operable program or batch file.

Exit code: 1
[Command failed with exit code 1]

### Tool call: execute
{"command": "set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 && python -m pytest workspace/tests -q", "timeout": 120}

### Tool result

=================================== ERRORS ====================================
_______________ ERROR collecting workspace/tests/test_report.py _______________
ImportError while importing test module '~\AppData\Local\Temp\lab-agent-mfjqs_ie\workspace\tests\test_report.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
..\..\Programs\Python\Python311\Lib\importlib\__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..\..\..\..\Documents\Codex\2026-10-06\https-github-com-lonelystar05-k4-day20\work\repo\tasks\code-learn\workspace\tests\test_report.py:3: in <module>
    from inventory.export import to_csv_row
E   ModuleNotFoundError: No module named 'inventory'
=========================== short test summary info ===========================
ERROR workspace/tests/test_report.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.22s

Exit code: 2
[Command failed with exit code 2]

### Tool call: execute
{"command": "cd workspace && set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 && python -m pytest tests -q", "timeout": 120}

### Tool result
......                                                                   [100%]
6 passed in 0.05s

[Command succeeded with exit code 0]

### Tool call: read_file
{"file_path": "/workspace/inventory/export.py"}

### Tool result
@@ lines 1-16 of 16 @@
"""Export helpers."""
from .pricing import parse_price


def to_csv_row(item):
    """Format one item as a CSV row: name,price,qty (price with 2 decimals).

    A name that contains a comma or a double quote is wrapped in double quotes,
    and every double quote inside it is doubled (RFC 4180).
    """
    name = item["name"]
    if "," in name or '"' in name:
        name = f'"{name.replace(chr(34), chr(34) * 2)}"'

    price = parse_price(item["price"])
    return f"{name},{price:.2f},{item['qty']}"

### Assistant
Fixed the inventory implementation:

- `inventory/pricing.py`: supports commas and accounting-style negative prices, and applies discounts using explicit `ROUND_HALF_UP` decimal rounding.
- `inventory/report.py`: makes low-stock comparison strictly below the threshold and sorts names case-insensitively.
- `inventory/export.py`: correctly RFC 4180-quotes names containing commas or double quotes.

Verified from `workspace/`: all tests pass (`6 passed`).