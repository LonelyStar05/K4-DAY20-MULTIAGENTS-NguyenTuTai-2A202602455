# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Tú Tài | 2A202602455 | Cá nhân: thực hiện toàn bộ bài lab |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: gateway tương thích OpenAI `https://vibi.top/v1`, deployment `gpt-5.6-terra`; `LAB_TEMPERATURE=0`; `recursion_limit=60`.
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: Deep Agents 0.7.21; Windows; chạy trực tiếp trong `.venv` Python 3.11.
- Số lần chạy tác vụ đã dùng / ngân sách: 9 lần chạy tác vụ trước freeze (3 baseline học, 3 subagents học, 3 skills-auto dev học); một lần gọi curator và các lần kiểm tra kết nối không tính là tác vụ.
- Commit của tag `freeze`:

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline): dự đoán `subagents` không vượt `baseline` trên điểm trung bình tác vụ đánh giá và tốn nhiều token hơn. Căn cứ là trên tập học, điểm trung bình giảm từ khoảng 0,63 xuống 0,55 trong khi token trung bình tăng từ 55.143 lên 105.887; các tác vụ nhỏ không đủ lợi ích để bù chi phí cô lập và truyền lại ngữ cảnh.
- H2 (skills-auto so với baseline): dự đoán `skills-auto` đạt điểm đánh giá cao nhất nhưng mức tăng nhỏ, chủ yếu ở các check quy ước có thể tổng quát hóa. Lần dev trên tập học tăng từ khoảng 0,63 lên 0,66 và chỉ thêm 1/9 check quy ước. SkillsBench báo skill do người viết có thể cải thiện trung bình, nhưng kết quả skill tự sinh không ổn định nên không kỳ vọng cải thiện lớn.
- H3 (tác vụ học so với tác vụ đánh giá): dự đoán lợi ích của `skills-auto` trên tác vụ đánh giá thấp hơn trên tác vụ học vì evaluation có quy ước mới chưa xuất hiện trong feedback. Đây là nguy cơ quá khớp được nêu trong SkillEvolBench; baseline và subagents dự kiến ít chênh lệch theo vai trò hơn vì không học feedback.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có các công cụ tệp `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`; công cụ shell `execute`; và công cụ subagent `task`. Công cụ cho phép chạy lệnh là `execute`.
2. Công cụ `task` mô tả subagent `general-purpose` là tác tử đa dụng để nghiên cứu câu hỏi phức tạp, tìm tệp/nội dung và thực hiện tác vụ nhiều bước; nó có toàn bộ công cụ giống tác tử chính. Mỗi lần gọi mặc định là độc lập và subagent chỉ nhìn thấy prompt được gửi trong lần gọi đó, không tự nhận toàn bộ hội thoại/ngữ cảnh của tác tử chính.
3. Trích từ `task`: "Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report." Trích từ `execute`: "You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

> Chỉ dùng tác vụ học. Mỗi dòng là một check thất bại.

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| code-learn | `tests_not_modified` | A | `the original files in tests/ must not be modified` — tác tử vi phạm yêu cầu đã nêu rõ trong đề. |
| code-learn | `rule_type_hints` | E | `RULE: every public function ... has type annotations` — quy ước Acme không có trong đề. |
| code-learn | `rule_regression_tests` | E | `RULE: add tests/test_regressions.py ... at least 3` — yêu cầu tổ chức chỉ xuất hiện trong feedback. |
| code-learn | `rule_changelog` | E | `RULE: record each fix in CHANGELOG.md ...` — định dạng changelog không có trong đề. |
| data-learn | `rule_money_in_cents` | E | `RULE: money values in answer.json are integer cents`. |
| data-learn | `rule_meta_block` | E | `RULE: answer.json has an object meta = {source, rows_in, rows_used}`. |
| data-learn | `rule_clean_csv` | E | `RULE: write workspace/clean.csv with the header ...`. |
| logs-learn | `rule_service_names` | E | `RULE: service names ... lower-case with '-' replaced by '_'`. |
| logs-learn | `rule_sorted_errors` | E | `RULE: errors is sorted by service, then by timestamp_utc`. |
| logs-learn | `rule_schema_header` | E | `RULE: ... schema_version: 2 and generated_by: log-triage`. |

Nhận xét: nhóm E chiếm 9/10 check thất bại. Bằng chứng phủ định cho A-D là baseline đạt 17/18 check kỹ thuật nhưng 0/9 check quy ước. Skill có thể phòng ngừa một phần nhóm E nếu feedback được chuyển thành checklist tổng quát; tuy nhiên quy ước mới ở evaluation có thể vẫn bị bỏ sót.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế): `explorer` đọc tài liệu, mã và dữ liệu nhưng không sửa; `implementer` thực hiện thay đổi và kiểm chứng; `reviewer` rà soát độc lập theo đặc tả và trường hợp biên nhưng không sửa. Ba vai trò tách bước khám phá, thực thi và kiểm tra để giảm bỏ sót đặc tả, đồng thời mô tả của từng agent nêu rõ thời điểm nên giao việc.
- `subagent_calls` ở từng tác vụ và nhận xét (kể cả trường hợp bằng 0): `code-learn=2` (`explorer`, `implementer`), `data-learn=2` (`general-purpose`, `reviewer`), `logs-learn=1` (`explorer`). Tác tử chính thực sự dùng cơ chế giao việc ở cả ba tác vụ.
- Thông tin thiếu hoặc thừa khi giao việc (nếu có giao việc): lời giao việc code và logs truyền đủ đường dẫn tương đối, tiêu chí docstring, file được phép sửa và yêu cầu kiểm chứng. Với data, hai subagent đều kết luận không tìm thấy quy ước Acme trong workspace; thông tin bị lặp nhưng không bổ sung feedback ẩn. Tác tử chính kiểm tra lại code bằng test, nhưng ở data các lệnh kiểm chứng tự viết bị lỗi cú pháp và kết quả cuối vẫn dùng số liệu subagent, dẫn đến sai hai check kỹ thuật.
- Ảnh hưởng đến token và thời gian: token trung bình tăng từ 55.143 (`baseline`) lên 105.887 (`subagents`, +92%), trong khi điểm học trung bình giảm từ khoảng 0,63 xuống 0,55. Thời gian lần lượt là code 186,1 giây, data 323,5 giây, logs 167,7 giây; đa tác tử không đáng chi phí trên tập học này.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: chạy curator 1 lần, sinh 3 skill hợp lệ; không xóa skill vì cả ba đều tổng quát, đúng với feedback và ngắn hơn 20 dòng.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `repository-change-compliance` | Tổng quát cho việc sửa repository có quy định về test, typing và tài liệu; không chứa id/tên file dữ liệu riêng. | Đúng với feedback code: bảo vệ file, thêm type annotation, regression test và changelog. | 16 dòng; description nêu rõ tình huống sửa repository; được đọc ở `code-learn` và `logs-learn`. |
| `structured-output-contract-validation` | Tổng quát cho CSV/JSON từ dữ liệu bẩn. | Đúng; các bước cents, meta, canonical record, sorting và re-read output khớp feedback. Cụm “when required” tránh áp dụng cents vô điều kiện. | 19 dòng; description kích hoạt rộng cho artifact có cấu trúc; được đọc ở `data-learn` và `logs-learn`. |
| `output-first-verification` | Tổng quát cho tác vụ có hidden checks và trạng thái repository. | Đúng; nhấn mạnh checklist, kiểm tra file thật và trạng thái cuối. | 15 dòng; description phù hợp mọi tác vụ bị chấm bằng file; được đọc ở cả 3 tác vụ học. |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự): `py -3.11 -m venv .venv`; `.venv\\Scripts\\python.exe -m pip install -e .`; `.venv\\Scripts\\python.exe -m pytest tests\\test_01_provided.py`; `.venv\\Scripts\\python.exe scripts\\tour.py`; `.venv\\Scripts\\python.exe -m pytest tests\\test_02_agent.py`; `.venv\\Scripts\\python.exe -m pytest tests\\test_03_runner.py`; `.venv\\Scripts\\python.exe -m pytest tests\\test_04_curator.py`; `.venv\\Scripts\\python.exe -m pytest`; `.venv\\Scripts\\python.exe -m compileall -q src`.
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
