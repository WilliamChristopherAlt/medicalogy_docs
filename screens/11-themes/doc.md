# Trang Danh sách Chủ đề (Themes)

**Route:** `/themes`

**Tài nguyên:**
- [doc.md](https://williamchristopheralt.github.io/medicalogy_docs/screens/11-themes/doc.md) (tài liệu này)
- [demo.html](https://williamchristopheralt.github.io/medicalogy_docs/screens/11-themes/demo.html) (demo tương tác)

---

## 1. Mục đích

Hiển thị tất cả chủ đề học tập. Chia thành 2 phần: chủ đề đã đăng ký (Enrolled) với tiến độ, và chủ đề chưa đăng ký (Explore More) để enroll mới.

> **Nguồn dữ liệu:** Ký hiệu `bảng.cột` → cột trong database (schema v4).
>
> | Bảng DB | Ý nghĩa | Cột chính |
> |---------|---------|----------|
> | `theme` | Chủ đề học tập | `name`, `description`, `color_code`, `slug` |
> | `user_theme_enrollment` | Đăng ký chủ đề | `user_id`, `theme_id`, `enrolled_at` |
> | `user_course` | Tiến độ khóa học | `quizzes_correct`, `completed_at` |

---

## 2. Cấu trúc trang

### 2.1. Header trang

| Thành phần | Mô tả |
|-----------|-------|
| Tiêu đề | "Knowledge Themes" |
| Phụ đề | "Pick a domain to start learning. Complete all sections to earn a badge." |

### 2.2. Enrolled Themes (chủ đề đã đăng ký)

Hiển thị dạng row card full-width. Mỗi card:

| Thành phần | Dữ liệu |
|-----------|---------|
| Icon theme | SVG icon có màu theo `theme.color_code` |
| Tên theme | `theme.name` |
| Meta chips | Số course đã hoàn thành / tổng, số section, ngày đăng ký |
| Mô tả | `theme.description` |
| Progress bar | % hoàn thành (số `user_course` / tổng course) |

Click card → navigate đến `/:theme-slug` (roadmap).

### 2.3. Explore More (chủ đề chưa đăng ký)

Hiển thị dạng grid 3 cột. Mỗi card:

| Thành phần | Dữ liệu |
|-----------|---------|
| Icon theme | SVG icon với colored top border |
| Tên theme | `theme.name` |
| Subtitle | "X sections · Y courses" |
| Badge "NEW" | Hiển thị cho theme mới (optional) |
| Mô tả | `theme.description` (cắt 2 dòng) |
| Thời gian ước tính | ~X phút (sections × 7 phút) |
| Nút "Enroll" | Click → đăng ký theme |

### 2.4. Toast notification

Khi click Enroll → toast "Enrolled in [tên theme]". Card chuyển từ Explore sang Enrolled (progress 0%).

---

## 3. Use Cases

### UC-THEMES-01: Xem danh sách chủ đề

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-THEMES-01 |
| **Tên** | Xem danh sách chủ đề |
| **Mô tả** | Hệ thống hiển thị tất cả theme, chia thành Enrolled (có tiến độ) và Explore (chưa đăng ký) |
| **Điều kiện tiên quyết** | Đã đăng nhập |
| **Luồng chính** | 1. Truy cập `/themes` → 2. Hệ thống load tất cả theme + danh sách `user_theme_enrollment` → 3. Phân thành 2 nhóm: enrolled (có record enrollment) và explore (không có) → 4. Với enrolled: tính tiến độ từ `user_course` → 5. Hiển thị 2 phần |
| **Hậu điều kiện** | Danh sách theme hiển thị chính xác với tiến độ |
| **Luồng thay thế** | Chưa enroll theme nào → phần Enrolled trống |

### UC-THEMES-02: Đăng ký chủ đề mới

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-THEMES-02 |
| **Tên** | Đăng ký chủ đề mới (Enroll) |
| **Mô tả** | Người dùng đăng ký một chủ đề để bắt đầu học |
| **Điều kiện tiên quyết** | Đã đăng nhập; chưa đăng ký theme này |
| **Luồng chính** | 1. Bấm "Enroll" trên card theme → 2. Hệ thống tạo record `user_theme_enrollment` → 3. Card chuyển từ Explore sang Enrolled (progress 0%) → 4. Toast "Enrolled in [tên theme]" |
| **Hậu điều kiện** | Record `user_theme_enrollment` được tạo. Theme xuất hiện trong phần Enrolled và sidebar submenu |
| **Luồng thay thế** | Đã đăng ký rồi → nút Enroll không hiển thị |

### UC-THEMES-03: Truy cập roadmap chủ đề

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-THEMES-03 |
| **Tên** | Truy cập roadmap chủ đề đã đăng ký |
| **Mô tả** | Người dùng click vào enrolled theme để xem roadmap học tập |
| **Điều kiện tiên quyết** | Theme đã đăng ký (có record `user_theme_enrollment`) |
| **Luồng chính** | 1. Click card enrolled theme → 2. Navigate đến `/:theme-slug` (trang roadmap) |
| **Hậu điều kiện** | Người dùng được chuyển đến trang roadmap |
| **Luồng thay thế** | — |

---

## 4. API

| # | API | Method | Sử dụng tại |
|---|-----|--------|-------------|
| 1 | `/api/themes` | GET | Danh sách tất cả theme (tên, mô tả, color_code, số section, số course) |
| 2 | `/api/users/me/enrolled-themes` | GET | Danh sách theme đã đăng ký + tiến độ (% hoàn thành, courses completed/total) |
| 3 | `/api/users/me/enroll` | POST | Đăng ký theme mới (body: `{themeId}`) |
