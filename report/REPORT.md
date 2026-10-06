# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Tú Tài | 2A202602455 | Cá nhân: thực hiện toàn bộ bài lab |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: gateway tương thích OpenAI `https://vibi.top/v1`, deployment `gpt-5.6-terra`; `LAB_TEMPERATURE=0`; `recursion_limit=60`.
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: Deep Agents 0.7.21; Windows; chạy trực tiếp trong `.venv` Python 3.11.9.
- Số lần chạy tác vụ đã dùng / ngân sách: 21 lần, gồm 9 lần trước freeze (3 baseline học, 3 subagents học, 3 skills-auto dev học) và 12 lần chính thức sau đó (3 baseline đánh giá, 3 subagents đánh giá, 6 skills-auto); một lần gọi curator và các lần kiểm tra kết nối không tính là tác vụ.
- Commit của tag `freeze`: `36e48fd53e49a5e340b402adbf30e7a448a9e9a1`.

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): dự đoán `subagents` không vượt `baseline` trên điểm trung bình tác vụ đánh giá và tốn nhiều token hơn. Căn cứ là trên tập học, điểm trung bình giảm từ khoảng 0,63 xuống 0,55 trong khi token trung bình tăng từ 55.143 lên 105.887; các tác vụ nhỏ không đủ lợi ích để bù chi phí cô lập và truyền lại ngữ cảnh.
- H2 (skills-auto so với baseline): dự đoán `skills-auto` đạt điểm đánh giá cao nhất nhưng mức tăng nhỏ, chủ yếu ở các check quy ước có thể tổng quát hóa. Lần dev trên tập học tăng từ khoảng 0,63 lên 0,66 và chỉ thêm 1/9 check quy ước. SkillsBench báo skill do người viết có thể cải thiện trung bình, nhưng kết quả skill tự sinh không ổn định nên không kỳ vọng cải thiện lớn.
- H3 (tác vụ học so với tác vụ đánh giá): dự đoán lợi ích của `skills-auto` trên tác vụ đánh giá thấp hơn trên tác vụ học vì evaluation có quy ước mới chưa xuất hiện trong feedback. Đây là nguy cơ quá khớp được nêu trong SkillEvolBench; baseline và subagents dự kiến ít chênh lệch theo vai trò hơn vì không học feedback.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có các công cụ tệp `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`; công cụ shell `execute`; và công cụ subagent `task`. Công cụ cho phép chạy lệnh là `execute`.
2. Công cụ `task` mô tả subagent `general-purpose` là tác tử đa dụng để nghiên cứu câu hỏi phức tạp, tìm tệp/nội dung và thực hiện tác vụ nhiều bước; nó có toàn bộ công cụ giống tác tử chính. Mỗi lần gọi mặc định là độc lập và subagent chỉ nhìn thấy prompt được gửi trong lần gọi đó, không tự nhận toàn bộ hội thoại/ngữ cảnh của tác tử chính.
3. Trích từ `task`: "Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report." Trích từ `execute`: "You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

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

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 6/10 | 6/10 | 7/10 |
| data-learn | 5/8 | 3/8 | 0/8 |
| logs-learn | 6/9 | 6/9 | 6/9 |
| code-eval | 6/11 | 6/11 | 7/11 |
| data-eval | 5/9 | 4/9 | 5/9 |
| logs-eval | 6/10 | 6/10 | 6/10 |
| **Mean score - learning tasks** | 0.63 | 0.55 | 0.46 |
| **Mean score - evaluation tasks** | 0.57 | 0.53 | 0.60 |
| **Mean tokens per run** | 50,463 | 108,206 | 86,318 |
| **Runs that read a skill** | 0/6 | 0/6 | 6/6 |

Kết quả `python scripts/check_breakdown.py`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     17/18         0/12          45,783      0/3
baseline      learn    17/18         0/9           55,143      0/3
subagents     eval     16/18         0/12         110,525      0/3
subagents     learn    15/18         0/9          105,887      0/3
skills-auto   eval     17/18         1/12          92,318      3/3
skills-auto   learn    12/18         1/9           80,317      3/3
```

Cả 18 lần chạy trong bảng có `error = null`; không lần nào có `skills_modified = true`. `python scripts/verify_freeze.py` báo `checked 6 runs of skill conditions: OK`. Thư mục `results/skills-auto-dev/` là bản sao ba lượt học ở Phần 3.4 và được `lab.compare` chủ động bỏ qua.

## 8. Phân tích

1. Trên kết quả học chính thức, không điều kiện nào vượt baseline `0,63`: subagents đạt `0,55` (-0,08) và skills-auto đạt `0,46` (-0,17). Tuy nhiên, ở lần dev Phần 3.4, cùng bộ skill đạt trung bình `0,66`, cao hơn baseline khoảng `0,03`. Trên tác vụ đánh giá, subagents giảm từ `0,57` xuống `0,53`, còn skills-auto tăng lên `0,60` (+0,03) và đứng đầu. Vì skills-auto cũng tăng trên lần học dev nên không có điều kiện nào trong thí nghiệm này cải thiện học mà không cải thiện đánh giá; thay vào đó, chênh lệch lớn giữa hai lần học skills-auto cho thấy kết quả một lần chạy rất nhạy với nhiễu.
2. Baseline đạt `17/18` check kỹ thuật nhưng `0/9` quy ước trên học, và `17/18` kỹ thuật nhưng `0/12` quy ước trên đánh giá. Lần dev của skills-auto vẫn đạt `17/18` kỹ thuật và tăng quy ước lên `1/9`; lần chính thức đạt `12/18` và `1/9` do `data-learn` thất bại toàn bộ. Trên đánh giá, skills-auto giữ `17/18` kỹ thuật và tăng quy ước lên `1/12`, nên bằng chứng chỉ hỗ trợ lợi ích nhỏ cho nhóm quy ước, cụ thể là `rule_type_hints`. Ba quy ước mới (`rule_version_bump`, `rule_sorted_keys_format`, `rule_source_line`) đều thất bại: skill được sinh trước freeze không chứa các literal/định dạng mới, còn hướng dẫn tổng quát về metadata và sorting không đủ để suy ra hợp đồng ẩn chính xác.
3. Ở `code-eval`, vết cho thấy tác tử đọc `repository-change-compliance` và `output-first-verification`; nó làm theo mục “Add complete type annotations”, thêm annotation cho các hàm công khai như `calendar_export.slot_end`, và đạt `rule_type_hints` trong khi baseline không đạt. Ngược lại, ở `data-eval`, tác tử đã đọc hai skill dữ liệu nhưng lệnh xác thực lại ép `answer.json` có đúng năm khóa được nêu công khai, không tạo `meta`, không đổi tiền sang cents và không tạo `clean.csv`; vì vậy cả bốn check quy ước đều thất bại. Tương tự, `code-eval` đọc skill nhưng vẫn giữ `__version__ = "1.4.2"`, do skill không có quy tắc bump phiên bản mới, nên `rule_version_bump` thất bại.
4. Token trung bình trên cả sáu tác vụ là `50.463` cho baseline, `108.206` cho subagents và `86.318` cho skills-auto. Nếu lấy điểm trung bình chia token trung bình rồi chuẩn hóa trên 100.000 token, hiệu quả lần lượt khoảng `1,19`, `0,50` và `0,61`; riêng tập đánh giá là `1,24`, `0,48` và `0,65`. Baseline vì thế hiệu quả nhất; subagents dùng hơn gấp đôi token nhưng điểm toàn bộ giảm từ khoảng `0,60` xuống `0,54`, nên đa tác tử không đáng chi phí trong ba tác vụ nhỏ này.
5. Không có bằng chứng rò rỉ tác vụ đánh giá: ba skill không chứa tên tác vụ, id dữ liệu hay quy ước mới chỉ xuất hiện ở evaluation; chúng được sinh và commit trước tag `freeze`, sau đó băm skill khớp ở cả sáu lượt và `skills_modified = false`. Tuy vậy, skill phản ánh các mẫu feedback học như type hints, cents, metadata và sorting, nên có nguy cơ quá khớp vào quy ước học; việc chỉ tổng quát hóa thành công `rule_type_hints` còn các quy ước mới đều trượt phù hợp với nguy cơ này. Nhóm phòng tránh bằng cách giữ nguyên đầu ra curator, sao lưu kết quả dev, commit giả thuyết trước freeze và dùng `verify_freeze.py` để ngăn sửa hậu nghiệm.
6. Với cùng bộ skill, lần dev và lần chính thức lần lượt là: code `7/10 -> 7/10`, data `5/8 -> 0/8`, logs `6/9 -> 6/9`. Điểm học trung bình giảm từ `0,663889` xuống `0,455556`, tức `-0,208333`; nguyên nhân trực tiếp là lượt `data-learn` chính thức đọc hai skill nhưng tính sai cả năm chỉ số kỹ thuật và bỏ cả ba artifact/quy ước. Dao động khoảng 0,21 lớn hơn nhiều mức tăng evaluation `+0,03`, vì vậy thứ hạng sát nhau trong bảng chỉ là bằng chứng thăm dò, không phải kết luận ổn định về hiệu quả nhân quả.

## 9. Hạn chế và tính hợp lệ

1. Mỗi vai trò chỉ có ba tác vụ, nên một thất bại như `data-learn=0/8` làm dịch chuyển mạnh giá trị trung bình và hạn chế khả năng khái quát sang repository thực tế.
2. Mỗi cấu hình/tác vụ chỉ được chạy chính thức một lần; chênh lệch `-0,208333` giữa hai lượt học cùng skill cho thấy phương sai mô hình đủ lớn để che lấp hiệu ứng `+0,03` trên evaluation.
3. Thí nghiệm chỉ dùng một deployment (`gpt-5.6-terra`), nhiệt độ 0 và một gateway; kết luận có thể thay đổi với mô hình, bộ giải mã, giới hạn đệ quy hoặc nhà cung cấp khác.
4. Quy ước ẩn do giảng viên thiết kế và lặp lại theo ba họ tác vụ code/data/logs; cấu trúc này thuận lợi cho skill học mẫu hơn môi trường mở, nhưng các literal ẩn lại khiến việc đánh giá khả năng suy luận quy ước khó tách khỏi khả năng đoán.
5. Token chỉ là đại diện cho chi phí, chưa tính giá tiền thực, độ trễ, giới hạn tốc độ hay lợi ích từ chạy song song; vì vậy nhận định “không đáng chi phí” chỉ áp dụng cho số token và điểm của thí nghiệm này.

## 10. Kết luận

Trên ba tác vụ đánh giá, skills-auto đạt điểm trung bình cao nhất `0,60`, nhỉnh hơn baseline `0,57`, nhưng chỉ cải thiện một check quy ước và dùng gần gấp đôi token. Subagents giảm điểm xuống `0,53` trong khi token tăng lên `110.525` mỗi lượt đánh giá, nên không có lợi trong quy mô bài lab này. Dao động của cùng bộ skill từ `0,66` xuống `0,46` trên tác vụ học cho thấy chênh lệch nhỏ chưa đủ đáng tin nếu chỉ chạy một lần. Bước tiếp theo nên lặp mỗi cấu hình nhiều lần với seed/tập tác vụ rộng hơn và cải thiện skill theo hướng biến hướng dẫn quy ước thành bước kiểm chứng có thể thực thi mà không chứa đáp án ẩn.

## Phụ lục

- Lệnh đã chạy (theo thứ tự chính): `py -3.11 -m venv .venv`; `.venv\\Scripts\\python.exe -m pip install -e .`; `.venv\\Scripts\\python.exe -m pytest tests\\test_01_provided.py`; `.venv\\Scripts\\python.exe scripts\\tour.py`; `.venv\\Scripts\\python.exe -m pytest tests\\test_02_agent.py`; `.venv\\Scripts\\python.exe -m pytest tests\\test_03_runner.py`; `.venv\\Scripts\\python.exe -m pytest tests\\test_04_curator.py`; `.venv\\Scripts\\python.exe -m pytest`; `.venv\\Scripts\\python.exe -m compileall -q src`; `.venv\\Scripts\\python.exe -m lab.runner --condition baseline --tasks learn`; `.venv\\Scripts\\python.exe -m lab.runner --condition subagents --tasks learn`; `.venv\\Scripts\\python.exe -m lab.curator`; `.venv\\Scripts\\python.exe -m lab.runner --condition skills-auto --tasks learn`; `git commit -m "hypotheses"`; `git commit --allow-empty -m "freeze skills"`; `git tag freeze`; `.venv\\Scripts\\python.exe -m lab.runner --condition baseline --tasks eval`; `.venv\\Scripts\\python.exe -m lab.runner --condition subagents --tasks eval`; `.venv\\Scripts\\python.exe -m lab.runner --condition skills-auto --tasks all`; `.venv\\Scripts\\python.exe -m lab.compare > report\\table.md`; `.venv\\Scripts\\python.exe scripts\\check_breakdown.py`; `.venv\\Scripts\\python.exe scripts\\verify_freeze.py`.
- Thử thách mở rộng (nếu có): không thực hiện; kết quả trên là toàn bộ phần bắt buộc.
- Ghi chú khác: `.env` được Git bỏ qua; báo cáo, vết và mã nguồn không chứa khóa API.
