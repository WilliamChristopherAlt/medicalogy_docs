# Trang Đánh Giá Đầu Vào (Onboarding)

**Route:** `/onboarding`

**Tài nguyên:**
- [doc.md](https://williamchristopheralt.github.io/medicalogy_docs/screens/5-initial-assesment/doc.md) (tài liệu này)
- [demo.html](https://williamchristopheralt.github.io/medicalogy_docs/screens/5-initial-assesment/demo.html) (demo tương tác)
- [initial_assessment.json](https://williamchristopheralt.github.io/medicalogy_docs/screens/5-initial-assesment/initial_assessment.json) (nội dung bài đánh giá)
- [md_to_html.py](https://williamchristopheralt.github.io/medicalogy_docs/screens/5-initial-assesment/md_to_html.py) (script chuyển đổi JSON sang HTML)
- [INITIAL_ASSESSMENT_STRUCTURE.md](https://williamchristopheralt.github.io/medicalogy_docs/screens/5-initial-assesment/INITIAL_ASSESSMENT_STRUCTURE.md) (đặc tả cấu trúc JSON)

---

## 1. Mục đích

Thu thập nhóm tuổi và kiến thức y tế cơ bản của người dùng mới để cá nhân hóa lộ trình học tập. Hiển thị một lần duy nhất sau khi tạo tài khoản, trước khi người dùng truy cập bất kỳ nội dung học nào. Dữ liệu từ màn hình này chi phối toàn bộ hệ thống — trình độ kiến thức giả định theo từng section.

> **Dữ liệu ghi bởi màn hình này:** Ký hiệu `bảng.cột` → cột trong database (schema v5).
>
> | Bảng DB | Ý nghĩa | Cột được ghi |
> |---------|---------|--------------|
> | `user` | Tài khoản người dùng | `user_demographic_id` |
> | `user_initial_assessment` | Ghi nhận đã làm bài đánh giá | `user_id`, `initial_assessment_id`, `completed_at` |
> | `initial_user_section_proficiency` | Trình độ kiến thức theo từng section | `user_id`, `initial_assessment_id`, `section_id`, `questions_seen`, `questions_correct`, `knowledge_level` |

> **Onboarding gate:** `user.user_demographic_id IS NULL` nghĩa là onboarding chưa hoàn thành. Mọi màn hình yêu cầu onboarding sẽ redirect về `/onboarding` nếu giá trị này là NULL.

---

## 2. Luồng màn hình

Onboarding là một trang dạng step-by-step. Tiến độ hiển thị dưới dạng thanh progress bar. Người dùng có thể điều hướng Quay lại / Tiếp tục giữa các bước. Nút "Tiếp tục" bị disabled cho đến khi hành động bắt buộc của bước hiện tại được thực hiện.

| Bước | ID | Mô tả | Điều kiện mở khóa "Tiếp tục" |
|------|----|-------|-------------------------------|
| 1 | `step-age` | Chọn nhóm tuổi | Đã chọn một nhóm tuổi |
| 2 | `step-explainer` | Giải thích cách chấm điểm & phân loại | Luôn mở (chỉ đọc) |
| 3 | `q-{id}` | Bài kiểm tra kiến thức — mỗi câu hỏi là một màn hình riêng | Đã trả lời câu hỏi hiện tại |
| 4 | `step-scoring` | Kết quả theo từng section | Luôn mở (tự động điền) |
| 5 | `step-path` | Gợi ý lộ trình học ban đầu + nút Bắt đầu | Không có — nút "Bắt đầu học" thay thế "Tiếp tục" |

---

## 3. Chi tiết từng bước

### Bước 1 — Chọn nhóm tuổi

Người dùng chọn nhóm tuổi từ 5 lựa chọn. Bắt buộc phải chọn trước khi tiếp tục.

| ID nhóm tuổi | Nhãn | Mô tả |
|---|---|---|
| `teen` | 13 – 17 | Học sinh |
| `youngAdult` | 18 – 25 | Sinh viên / Người mới đi làm |
| `adult` | 26 – 45 | Người đi làm |
| `middleAged` | 46 – 60 | Trung niên |
| `senior` | 61+ | Cao tuổi |

Khi hoàn thành, nhóm tuổi được dùng để tra cứu record `user_demographic` phù hợp (theo khoảng tuổi) và ghi vào `user.user_demographic_id`.

### Bước 2 — Giải thích cách chấm điểm & phân loại

Bước chỉ đọc. Giải thích cho người dùng:

**Cấu trúc nội dung học:**

| Cấp độ | Mô tả |
|--------|-------|
| Theme | Lĩnh vực y tế rộng — ví dụ: Cấp cứu, Dinh dưỡng, Sức khỏe tâm thần |
| Section | Chủ đề cụ thể trong một theme — ví dụ: "CPR Cơ Bản" trong Cấp cứu. Mỗi section kết thúc bằng một bài test |
| Course | Bài học ngắn gồm các màn hình infographic và quiz — khoảng 7 phút. Hoàn thành course ghi nhận tiến độ và cập nhật streak |
| Section Test | Bài kiểm tra cuối section. Cần đạt ≥70% để mở khóa section tiếp theo |

**Ý nghĩa của kết quả quiz theo từng section:**

| Ngưỡng | Ảnh hưởng đến section trên roadmap |
|--------|-------------------------------------|
| ≥ 80% đúng | Section hiển thị với nhãn "You already know this section" — không cần học. Không ghi dữ liệu gì vào database |
| < 80% đúng | Luồng bình thường — course mở khóa lần lượt theo thứ tự |

### Bước 3 — Bài kiểm tra kiến thức

Mỗi bước là một câu hỏi từ file `initial_assessment.content` JSON. Loại câu hỏi: `multiple_choice`, `true_false`. Mỗi câu hỏi được gắn `sectionSlug` ánh xạ đến `section` trong Learning Service.

Phản hồi đúng/sai hiển thị ngay sau khi trả lời. Nút "Tiếp tục" được kích hoạt ngay sau khi chọn đáp án — không thể thay đổi đáp án đã chọn.

Điểm được tích lũy theo section trên trình duyệt trong khi người dùng làm bài. Không gửi kết quả lên server cho đến khi toàn bộ bài kiểm tra hoàn thành.

### Bước 4 — Kết quả của bạn

Hiển thị bảng điểm theo từng section, tự động điền từ kết quả quiz:

| Thành phần | Mô tả |
|-----------|-------|
| Tên section | Nhãn hiển thị của section |
| Phân số điểm | `questions_correct / questions_seen` cho section đó |
| Badge trình độ | `Mới bắt đầu`, `Trung cấp`, hoặc `Nâng cao` — phân loại theo bảng ngưỡng ở trên |

### Bước 5 — Gợi ý lộ trình học ban đầu

Hiển thị gợi ý các section người dùng nên bắt đầu dựa trên kết quả. Đây chỉ là thông tin tham khảo — không có đăng ký nào được thực hiện ở bước này.

Nút "Bắt đầu học" kích hoạt ghi dữ liệu cuối cùng và redirect đến `/themes`.

---

## 4. Use Cases

### UC-ONBOARD-01: Hoàn thành onboarding

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-ONBOARD-01 |
| **Tên** | Hoàn thành bài đánh giá đầu vào |
| **Mô tả** | Người dùng mới đi qua toàn bộ các bước onboarding. Khi hoàn thành, hệ thống ghi nhân khẩu học, kết quả đánh giá, và trình độ theo từng section trong một transaction duy nhất |
| **Điều kiện tiên quyết** | Tài khoản đã tồn tại; `user.user_demographic_id IS NULL` |
| **Luồng chính** | 1. Chọn nhóm tuổi → 2. Đọc giải thích phân loại → 3. Trả lời toàn bộ câu hỏi quiz → 4. Xem kết quả theo section → 5. Xem gợi ý lộ trình → 6. Bấm "Bắt đầu học" → 7. Hệ thống commit transaction → 8. Redirect đến `/themes` |
| **Hậu điều kiện** | `user.user_demographic_id` được ghi. Record `user_initial_assessment` được tạo. Một record `initial_user_section_proficiency` cho mỗi section được kiểm tra |
| **Luồng thay thế** | Người dùng thoát trước khi hoàn thành → không ghi dữ liệu, `user_demographic_id` vẫn NULL, onboarding gate redirect lại khi truy cập lần sau |

### UC-ONBOARD-02: Bỏ qua onboarding đã hoàn thành

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-ONBOARD-02 |
| **Tên** | Bỏ qua onboarding cho người dùng đã hoàn thành |
| **Mô tả** | Người dùng đã hoàn thành onboarding cố tình truy cập lại `/onboarding` |
| **Điều kiện tiên quyết** | `user.user_demographic_id IS NOT NULL` |
| **Luồng chính** | 1. Truy cập `/onboarding` → 2. Hệ thống phát hiện onboarding đã hoàn thành → 3. Redirect đến `/themes` |
| **Hậu điều kiện** | Không có dữ liệu thay đổi. Người dùng được chuyển đến trang themes |

---

## 5. Ghi dữ liệu — Transaction

Toàn bộ dữ liệu được commit khi bấm "Bắt đầu học", thực hiện bởi Auth Service:

```sql
BEGIN TRANSACTION

    -- 1. Ghi nhân khẩu học
    UPDATE [user]
    SET user_demographic_id = @demographic_id, updated_at = GETDATE()
    WHERE id = @user_id

    -- 2. Ghi nhận đã làm bài
    INSERT INTO user_initial_assessment (user_id, initial_assessment_id, completed_at)
    VALUES (@user_id, @assessment_id, GETDATE())

    -- 3. Ghi trình độ theo từng section (một row cho mỗi section xuất hiện trong bài)
    INSERT INTO initial_user_section_proficiency
        (user_id, initial_assessment_id, section_id, questions_seen, questions_correct, knowledge_level)
    VALUES ...

COMMIT
```

---

## 6. API

| # | API | Method | Sử dụng tại |
|---|-----|--------|-------------|
| 1 | `/api/onboarding/assessment` | GET | Lấy nội dung `initial_assessment` đang active (câu hỏi, nhóm tuổi) |
| 2 | `/api/onboarding/complete` | POST | Gửi kết quả và kích hoạt transaction (body: `{ ageGroupId, assessmentId, sectionScores[] }`) |
| 3 | `/api/demographics` | GET | Lấy danh sách `user_demographic` để tra cứu nhóm tuổi |