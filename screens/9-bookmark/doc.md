# Trang Bookmark

**Route:** `/bookmarks`

**Tài nguyên:**
- [doc.md](https://williamchristopheralt.github.io/medicalogy_docs/screens/9-bookmark/doc.md) (tài liệu này)
- [demo.html](https://williamchristopheralt.github.io/medicalogy_docs/screens/9-bookmark/demo.html) (demo tương tác)

---

## 1. Mục đích

Hiển thị danh sách bài viết mà người dùng đã bookmark. Hỗ trợ tìm kiếm, lọc theo theme, sắp xếp, và phân trang.

> **Nguồn dữ liệu:** Ký hiệu `bảng.cột` → cột trong database (schema v4).
>
> | Bảng DB | Ý nghĩa | Cột chính |
> |---------|---------|----------|
> | `user_bookmark` | Bookmark bài viết | `user_id`, `article_id`, `created_at` |
> | `article` | Bài viết bách khoa | `name`, `slug`, `content_markdown`, `theme_id`, `is_published` |
> | `tag` | Nhãn phân loại | `name` |

---

## 2. Cấu trúc trang

### 2.1. Header trang

| Thành phần | Mô tả |
|-----------|-------|
| Tiêu đề | "My Bookmarks" + badge số lượng |
| Phụ đề | "Articles you've saved for later reading" |

### 2.2. Toolbar (thanh công cụ)

| Thành phần | Chức năng |
|-----------|-----------|
| Ô tìm kiếm | Lọc bookmark theo tiêu đề, nội dung, tag (real-time) |
| Sort dropdown | Newest first, Oldest first, Most viewed, A→Z |
| Per-page selector | 6 / 12 / 24 items mỗi trang |
| Filter theme buttons | All, Emergency, Mental Health, Cardiovascular, Nutrition |

### 2.3. Lưới bookmark cards

Mỗi card hiển thị:

| Thành phần | Dữ liệu |
|-----------|---------|
| Theme badge | Tên theme (có màu) |
| Tiêu đề bài viết | `article.name` |
| Đoạn trích | Excerpt từ nội dung bài viết |
| Tags | Tối đa 3 tag chips |
| Thông tin phụ | Số lượt xem, ngày publish, ngày bookmark |
| Nút xóa bookmark | Icon thùng rác → xóa bookmark (animation fade-out + toast xác nhận) |

Click card → navigate đến `/wiki/:slug`.

### 2.4. Phân trang

Prev/Next + số trang. Thay đổi theo per-page selector.

### 2.5. Empty state

Khi không có bookmark hoặc không tìm thấy kết quả → hiển thị thông báo + nút "Browse Encyclopedia".

---

## 3. Use Cases

### UC-BOOKMARK-01: Xem danh sách bookmark

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-BOOKMARK-01 |
| **Tên** | Xem danh sách bookmark |
| **Mô tả** | Người dùng xem tất cả bài viết đã bookmark, có thể lọc/sắp xếp/phân trang |
| **Điều kiện tiên quyết** | Đã đăng nhập |
| **Luồng chính** | 1. Truy cập `/bookmarks` → 2. Hệ thống load danh sách bookmark (kèm thông tin article: tên, excerpt, theme, tags, view count) → 3. Hiển thị dạng lưới card → 4. Người dùng có thể tìm kiếm, lọc theo theme, sắp xếp, thay đổi per-page |
| **Hậu điều kiện** | Danh sách bookmark hiển thị chính xác |
| **Luồng thay thế** | Không có bookmark → empty state với nút "Browse Encyclopedia" |

### UC-BOOKMARK-02: Xóa bookmark

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-BOOKMARK-02 |
| **Tên** | Xóa bookmark khỏi danh sách |
| **Mô tả** | Người dùng xóa một bài viết khỏi danh sách bookmark |
| **Điều kiện tiên quyết** | Đã đăng nhập; bài viết đang trong danh sách bookmark |
| **Luồng chính** | 1. Bấm icon thùng rác trên card → 2. Hệ thống xóa record `user_bookmark` → 3. Card fade-out → 4. Toast "Bookmark removed" |
| **Hậu điều kiện** | Record `user_bookmark` bị xóa. Badge số lượng cập nhật |
| **Luồng thay thế** | Xóa bookmark cuối cùng → hiển thị empty state |

---

## 4. API

| # | API | Method | Sử dụng tại |
|---|-----|--------|-------------|
| 1 | `/api/bookmarks?page={p}&limit={n}&theme={id}&sort={field}&search={q}` | GET | Danh sách bookmark (có filter, sort, search, pagination) |
| 2 | `/api/bookmarks` | POST | Xóa bookmark (body: `{articleId}` — toggle) |
