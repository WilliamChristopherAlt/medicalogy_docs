# Trang Roadmap Chủ đề

**Route:** `/:theme-slug`

**Tài nguyên:**
- [doc.md](https://williamchristopheralt.github.io/medicalogy_docs/screens/3-roadmap/doc.md) (tài liệu này)
- [demo.html](https://williamchristopheralt.github.io/medicalogy_docs/screens/3-roadmap/demo.html) (demo tương tác)

---

## 1. Mục đích

Hiển thị lộ trình học tập của một chủ đề, bao gồm các section và course theo thứ tự. Người dùng xem tiến độ và tiếp tục học course tiếp theo.

> **Nguồn dữ liệu:** Ký hiệu dạng `bảng.cột` trong tài liệu tham chiếu đến cột trong database (schema v5).
>
> | Bảng DB | Ý nghĩa | Cột chính sử dụng trong trang này |
> |---------|---------|-----------------------------------|
> | `theme` | Chủ đề học tập | `name`, `description`, `color_code`, `slug` |
> | `section` | Phân mục trong theme | `name`, `order_index` |
> | `course` | Khóa học trong section | `name`, `order_index`, `is_active`, `content_file_name` (file JSON) |
> | `section_test` | Bài test cuối section | `content_file_name` (file JSON), `passing_score_percentage` |
> | `user_course` | Tiến độ khóa học của user | `quizzes_correct`, `completed_at` |
> | `user_section_test` | Kết quả test section của user | `score`, `completed_at` |
> | `user_daily_streak` | Streak học tập hàng ngày | `current_streak` |
> | `initial_user_section_proficiency` | Điểm đánh giá đầu vào theo section | `section_id`, `questions_seen`, `questions_correct` |

---

## 2. Cấu trúc trang

### 2.1. Header (cố định)

| Vùng | Thành phần | Chức năng |
|------|-----------|-----------|
| Trên | Tên chủ đề + mô tả | Lấy từ `theme.name`, `theme.description` |
| Giữa | Thanh tiến độ | % course đã hoàn thành = (số record `user_course` / tổng course active) × 100%. Hiển thị "X/Y courses". Màu từ `theme.color_code` |
| Dưới | Streak card *(đóng được)* | Số ngày streak hiện tại (`user_daily_streak.current_streak`). Thông điệp động theo số ngày. Nút đóng (X), trạng thái lưu localStorage |

### 2.2. Body — Danh sách section & course

Các section sắp xếp theo `section.order_index` ASC. Mỗi section gồm:

| Thành phần | Mô tả |
|-----------|-------|
| Tiêu đề section | `section.name`, font lớn, in đậm |
| Danh sách course | Layout đường đi dọc (vertical path), sắp xếp theo `course.order_index`. Có đường nối (connector line) giữa các course |
| Course button | Hiển thị: icon số thứ tự, tên course, điểm quiz "X/Y questions correct" |
| Section test button | Cuối mỗi section. Icon "T", text "Section Test: [tên section]", số câu hỏi, màu tím. Chỉ mở khóa khi tất cả course trong section đã hoàn thành |

**Trạng thái course:**

| Trạng thái | Mô tả | Có thể click |
|-----------|-------|:---:|
| **Completed** (xanh lá, checkmark) | Có record trong `user_course` | ✅ |
| **Unlocked** (xanh dương, arrow) | Course tiếp theo cần học, có hiệu ứng pulse | ✅ |
| **Locked** (xám nhạt, lock) | Chưa mở khóa — course trước chưa đạt ≥80% quiz | ❌ |
| **Stale** (xám trung bình, checkmark mờ) | Đã hoàn thành nhưng quá X ngày chưa ôn lại. Ribbon hiển thị "3 weeks ago". Hover → phục hồi màu xanh Completed | ✅ |
| **Skippable** (xanh lá nhạt, badge "Already known · Onboarding") | Section có `questions_correct / questions_seen >= 0.80` trong `initial_user_section_proficiency`. Tất cả course trong section đều có thể click theo bất kỳ thứ tự nào — không phụ thuộc vào nhau. Section tiếp theo không bị khóa bởi section này. Không có ghi dữ liệu nào vào database | ✅ |

### 2.3. Bottom Sheet "Continue Learning" (cố định dưới)

| Trường hợp | Nội dung hiển thị |
|-----------|------------------|
| Course thông thường | Label "Continue", breadcrumb "[Section] - Course [X]", tên course, nút "Start Course" |
| Section test | Label "Test", breadcrumb "Section Test", tên test, mô tả "X questions - Need ≥Y% to pass", nút "Start Test" |

- Chỉ hiển thị khi có course/test ở trạng thái Unlocked.
- Ẩn khi đã hoàn thành tất cả nội dung.
- Click → navigate đến `/:theme-slug/:section-slug/:course-order-index` hoặc `/:theme-slug/:section-slug/test`.

### 2.4. Thông báo hoàn thành

Khi tất cả course + section test trong theme đã hoàn thành: hiển thị icon trophy, text chúc mừng, background vàng/gold ở cuối danh sách.

---

## 3. Use Cases

### UC-ROADMAP-01: Hiển thị danh sách course theo roadmap

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-ROADMAP-01 |
| **Tên** | Hiển thị danh sách course theo roadmap |
| **Mô tả** | Hệ thống hiển thị các section và course của một theme theo thứ tự, bao gồm trạng thái hoàn thành / khóa / mở khóa / stale và tiến độ của người dùng |
| **Điều kiện tiên quyết** | Đã đăng nhập; theme slug hợp lệ; theme có ít nhất 1 section và 1 course active |
| **Luồng chính** | 1. Truy cập `/:theme-slug` → 2. Hệ thống load thông tin theme, sections (theo `order_index`), courses (theo `order_index`), section tests → 3. Với mỗi course, xác định trạng thái (Completed / Unlocked / Locked / Stale) dựa trên `user_course` → 4. Hiển thị thanh tiến độ, danh sách section + course, bottom sheet |
| **Hậu điều kiện** | Roadmap hiển thị đầy đủ với trạng thái chính xác |
| **Luồng thay thế** | Theme không tồn tại → 404. Chưa đăng nhập → redirect login |

### UC-ROADMAP-02: Tiếp tục học từ Bottom Sheet

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-ROADMAP-02 |
| **Tên** | Tiếp tục học từ Bottom Sheet |
| **Mô tả** | Người dùng bấm "Start Course" hoặc "Start Test" trên bottom sheet để tiếp tục học course/test tiếp theo |
| **Điều kiện tiên quyết** | Có ít nhất 1 course hoặc section test ở trạng thái Unlocked |
| **Luồng chính** | 1. Bottom sheet hiển thị course/test Unlocked đầu tiên (theo thứ tự section + course) → 2. Người dùng kéo lên để xem chi tiết → 3. Bấm "Start Course" / "Start Test" → 4. Navigate đến trang học |
| **Hậu điều kiện** | Người dùng được chuyển đến trang course hoặc test |
| **Luồng thay thế** | Đã hoàn thành tất cả → bottom sheet ẩn |

### UC-ROADMAP-03: Xem lại course đã hoàn thành

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-ROADMAP-03 |
| **Tên** | Xem lại course đã hoàn thành |
| **Mô tả** | Người dùng click vào course Completed hoặc Stale để xem lại nội dung |
| **Điều kiện tiên quyết** | Course ở trạng thái Completed hoặc Stale |
| **Luồng chính** | 1. Click course Completed/Stale → 2. Navigate đến trang course → 3. Xem lại nội dung |
| **Hậu điều kiện** | Người dùng xem lại nội dung course. Nếu Stale, cập nhật thời gian truy cập |
| **Luồng thay thế** | Course Locked → không thể click, không có phản hồi |

---

## 4. API

| # | API | Method | Sử dụng tại |
|---|-----|--------|-------------|
| 1 | `/api/themes/:slug` | GET | Header → tên, mô tả, color_code |
| 2 | `/api/themes/:themeId/sections` | GET | Body → danh sách section + course + section test (sắp xếp theo order_index) |
| 3 | `/api/users/me/themes/:themeId/progress` | GET | Header → thanh tiến độ + trạng thái từng course (user_course, user_section_test, initial_user_section_proficiency) |
| 4 | `/api/users/me/streak` | GET | Header → streak card |