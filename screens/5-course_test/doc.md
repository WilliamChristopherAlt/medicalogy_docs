# Trang Course (Khóa học)

**Route:** `/:theme-slug/:section-slug/:course-order-index`

**Tài nguyên:**
- [doc.md](https://williamchristopheralt.github.io/medicalogy_docs/screens/5-course_test/doc.md) (tài liệu này)
- [demo.html](https://williamchristopheralt.github.io/medicalogy_docs/screens/5-course_test/demo.html) (demo tương tác)
- [JSON_SPEC.md](https://williamchristopheralt.github.io/medicalogy_docs/screens/5-course_test/JSON_SPEC.md) (cấu trúc JSON nội dung course)
- [json_demo.json](https://williamchristopheralt.github.io/medicalogy_docs/screens/5-course_test/json_demo.json) (ví dụ JSON course)
- [json_to_html.py](https://williamchristopheralt.github.io/medicalogy_docs/screens/5-course_test/json_to_html.py) (script chuyển đổi JSON sang HTML)

---

## 1. Mục đích

Hiển thị nội dung học tập của một course, bao gồm các màn hình infographic (nội dung giáo dục) và quiz (câu hỏi đánh giá). Người dùng học từng màn hình theo thứ tự, trả lời quiz, và hoàn thành course để mở khóa course tiếp theo (cần ≥80% quiz đúng).

> **Nguồn dữ liệu:**
> - Ký hiệu `bảng.cột` → cột trong database (schema v4)
> - Ký hiệu `content.field` hoặc `type: "value"` → trường trong JSON lưu ở cột `course.content` hoặc `section_test.content` (chi tiết xem file `JSON_SPEC.md`)
>
> | Bảng DB | Ý nghĩa | Cột chính |
> |---------|---------|----------|
> | `course` | Khóa học | `content` (JSON chứa danh sách screens), `is_active`, `order_index` |
> | `section_test` | Bài test section | `content` (JSON chứa danh sách questions), `passing_score_percentage` |
> | `user_course` | Kết quả học của user | `quizzes_correct` |
> | `user_section_test` | Kết quả test section | `score` |
>
> | Trường JSON (trong `course.content`) | Ý nghĩa |
> |--------------------------------------|----------|
> | `screens[].type` | Loại màn hình: `"infographic"` hoặc `"quiz"` |
> | `screens[].orderIndex` | Thứ tự hiển thị |
> | `screens[].content.imageFileName` | Tên file hình ảnh (infographic) |
> | `screens[].content.summaryText` | Nội dung giáo dục (infographic) |
> | `screens[].content.questionText` | Câu hỏi (quiz multiple choice / true-false) |
> | `screens[].content.options[]` | Danh sách đáp án (multiple choice) |
> | `screens[].content.correctAnswer` | Đáp án đúng (true/false) |
> | `screens[].content.sentence` | Câu có chỗ trống `<1>`, `<2>`... (matching) |
> | `screens[].content.correctAnswers[]` | Đáp án đúng cho từng chỗ trống (matching) |
> | `screens[].content.wrongAnswers[]` | Đáp án nhiễu (matching) |
> | `screens[].content.explanation` | Giải thích sau khi trả lời (quiz) |

---

## 2. Cấu trúc trang

### 2.1. Header (cố định)

| Thành phần | Chức năng |
|-----------|-----------|
| Breadcrumb | "[Tên theme] > [Tên section] > Course [X]". Theme và section có thể click để quay lại |
| Thanh tiến độ | X/Y màn hình đã xem. Màu từ `theme.color_code` |
| Nút thoát | "← Quay lại" hoặc icon X. Nếu chưa hoàn thành → hiện modal xác nhận |

### 2.2. Body — Nội dung màn hình

Hiển thị từng màn hình một theo `orderIndex`. Có 2 loại:

**A. Infographic** (`type: "infographic"`)

| Thành phần | Mô tả |
|-----------|-------|
| Hình ảnh | Lấy từ `content.imageFileName`. Full-width hoặc căn giữa |
| Nội dung giáo dục | Lấy từ `content.summaryText`. Hiển thị dưới hình ảnh |
| Nút "Tiếp tục" | Chuyển sang màn hình tiếp theo. Màn hình cuối → text đổi thành "Hoàn thành" |

**B. Quiz** (`type: "quiz"`) — 3 loại:

| Loại quiz | Cách hoạt động |
|----------|---------------|
| **Multiple Choice** (`multiple_choice`) | Hiển thị `questionText` + danh sách `options[]`. Chọn 1 đáp án → bấm "Kiểm tra" → hiển thị đúng/sai + `explanation` → bấm "Tiếp tục" |
| **True/False** (`true_false`) | Hiển thị câu khẳng định + 2 nút "Đúng" / "Sai". Chọn → bấm "Kiểm tra" → so sánh với `correctAnswer` → hiển thị kết quả + `explanation` |
| **Matching** (`matching`) | Hiển thị `sentence` với placeholder `<1>`, `<2>`... Danh sách đáp án xáo trộn (`correctAnswers` + `wrongAnswers`). Kéo/click đáp án vào chỗ trống → bấm "Kiểm tra" → hiển thị đúng/sai từng ô |

Trạng thái chung cho tất cả quiz:
- Chưa trả lời → nút "Kiểm tra" disabled
- Đã chọn → nút "Kiểm tra" enabled
- Sau submit → đáp án đúng xanh lá ✓, sai đỏ ✗, hiển thị explanation, không thể thay đổi, nút đổi thành "Tiếp tục"

### 2.3. Footer (cố định dưới)

| Nút | Điều kiện |
|-----|----------|
| "Quay lại" | Xem lại màn hình trước (ẩn ở màn hình đầu tiên) |
| "Kiểm tra" | Quiz chưa submit (disabled nếu chưa chọn đáp án) |
| "Tiếp tục" | Infographic hoặc quiz đã submit |
| "Hoàn thành" | Màn hình cuối cùng |

### 2.4. Modal hoàn thành course

| Trường hợp | Nội dung |
|-----------|---------|
| **Đạt** (≥80% quiz đúng) | Icon celebration, "Chúc mừng!", "Điểm số: X/Y câu đúng (Z%)". Nút: "Tiếp tục" (về roadmap, mở khóa course tiếp) hoặc "Xem lại" (ở lại) |
| **Chưa đạt** (<80%) | Icon cảnh báo, "Chưa đạt yêu cầu", "Cần ≥80% để mở khóa course tiếp theo". Nút: "Học lại" (reset, bắt đầu lại) hoặc "Quay lại" (về roadmap, course tiếp vẫn khóa) |

Modal không đóng được bằng click ngoài — phải bấm nút.

---

## 3. Use Cases

### UC-COURSE-01: Tiến hành học một course

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-COURSE-01 |
| **Tên** | Tiến hành học một course |
| **Mô tả** | Người dùng học qua từng màn hình của course theo thứ tự (infographic + quiz), sau đó hoàn thành course |
| **Điều kiện tiên quyết** | Đã đăng nhập; course tồn tại với `is_active = 1`; course ở trạng thái Unlocked hoặc Completed |
| **Luồng chính** | 1. Truy cập `/:theme-slug/:section-slug/:course-order-index` → 2. Hệ thống load course content (JSON) → 3. Hiển thị màn hình đầu tiên → 4. Nếu infographic: đọc nội dung → bấm "Tiếp tục" → 5. Nếu quiz: chọn đáp án → bấm "Kiểm tra" → xem kết quả + giải thích → bấm "Tiếp tục" → 6. Lặp lại đến màn hình cuối → 7. Bấm "Hoàn thành" → 8. Modal hiển thị kết quả → 9. Đạt ≥80%: bấm "Tiếp tục" về roadmap |
| **Hậu điều kiện** | Record `user_course` được tạo/cập nhật với `quizzes_correct`. Nếu đạt ≥80%, course tiếp theo mở khóa |
| **Luồng thay thế** | Thoát giữa chừng → modal xác nhận, tiến độ không lưu. Course không tồn tại → 404. Course bị khóa → thông báo + redirect roadmap. Chưa đạt → "Học lại" hoặc "Quay lại" |

### UC-COURSE-02: Làm section test

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-COURSE-02 |
| **Tên** | Làm section test |
| **Mô tả** | Người dùng làm bài test tổng hợp cuối section để mở khóa section tiếp theo |
| **Điều kiện tiên quyết** | Tất cả course trong section đã hoàn thành (Completed) |
| **Luồng chính** | 1. Truy cập `/:theme-slug/:section-slug/test` → 2. Hệ thống load `section_test.content` (JSON) → 3. Hiển thị từng câu hỏi (cùng 3 loại quiz) → 4. Trả lời tất cả → 5. Bấm "Hoàn thành" → 6. Hiển thị kết quả với ngưỡng đạt (`section_test.passing_score_percentage`) |
| **Hậu điều kiện** | Record `user_section_test` được tạo. Nếu đạt, section tiếp theo mở khóa |
| **Luồng thay thế** | Chưa hoàn thành tất cả course → test bị khóa. Chưa đạt ngưỡng → làm lại |

---

## 4. API

| # | API | Method | Sử dụng tại |
|---|-----|--------|-------------|
| 1 | `/api/courses/:courseId/content` | GET | Body → nội dung course (JSON screens) |
| 2 | `/api/section-tests/:sectionTestId/content` | GET | Body → nội dung section test (JSON questions) |
| 3 | `/api/users/me/courses/:courseId/complete` | POST | Modal hoàn thành → gửi kết quả (quizzes_correct) |
| 4 | `/api/users/me/section-tests/:sectionTestId/complete` | POST | Modal hoàn thành → gửi kết quả section test |
| 5 | `/api/themes/:slug` | GET | Breadcrumb → tên theme |
| 6 | `/api/sections/:sectionId` | GET | Breadcrumb → tên section |
