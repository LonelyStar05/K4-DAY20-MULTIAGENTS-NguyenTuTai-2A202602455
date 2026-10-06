"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use when a task requires inspecting documentation, source files, data formats, "
                "or logs before deciding what to change. Return verified findings and do not edit files."
            ),
            "system_prompt": (
                "You are a read-only explorer. Inspect the relevant instructions, documentation, "
                "source, and sample data. Report concrete findings, edge cases, and exact file paths. "
                "Do not modify files, and clearly distinguish observations from assumptions."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use when the required change is understood and files must be created or edited, "
                "then validated with the task's tests or scripts."
            ),
            "system_prompt": (
                "You are an implementation specialist. Make only the changes requested in the "
                "delegation, preserve unrelated files, and run the relevant validation commands. "
                "Return a concise report of changed files, commands run, and any remaining risk."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use after an implementation or generated output needs an independent check against "
                "the full specification, edge cases, and available tests. Do not edit files."
            ),
            "system_prompt": (
                "You are an independent reviewer. Re-read the supplied requirements, inspect the "
                "result, and run non-destructive checks. Look for missed edge cases and unsupported "
                "completion claims. Do not modify files; report findings with evidence."
            ),
        },
    ]
