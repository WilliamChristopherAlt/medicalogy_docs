# Trang Tìm kiếm / Bách khoa (Search / Encyclopedia)

**Route:** `/encyclopedia` (hero) → `/encyclopedia?q={keyword}` (kết quả)

**Tài nguyên:**
- [doc.md](https://williamchristopheralt.github.io/medicalogy_docs/screens/10-search/doc.md) (tài liệu này)
- [demo.html](https://williamchristopheralt.github.io/medicalogy_docs/screens/10-search/demo.html) (demo tương tác)

---

## 1. Mục đích

Trang tìm kiếm trung tâm cho toàn bộ nội dung: bài viết, course, theme, section. Có 2 trạng thái: hero search (mặc định) và trang kết quả đầy đủ.

---

## 2. Cấu trúc trang

### 2.1. Trạng thái 1 — Hero Search (mặc định)

| Thành phần | Mô tả |
|-----------|-------|
| Eyebrow text | "Medical Encyclopedia" |
| Tiêu đề lớn | "What do you want to learn?" |
| Phụ đề | "Search across articles, courses, themes and sections" |
| Ô tìm kiếm lớn | Căn giữa, full-width. Có nút clear |
| Trending tags | Các tag phổ biến (Heart Attack, CPR, Diabetes, Stroke, Anxiety, Nutrition). Click → điền vào ô search |
| Typeahead dropdown | Xuất hiện khi gõ. Hiển thị tối đa 7 gợi ý bài viết với highlight từ khóa. Hỗ trợ keyboard (Arrow Up/Down, Enter, Escape) |
| Gợi ý | "Press Enter to see full results" khi đang gõ |

### 2.2. Trạng thái 2 — Trang kết quả (sau khi Enter)

| Thành phần | Mô tả |
|-----------|-------|
| Nút Back | Quay về hero search |
| Ô tìm kiếm phụ | Cho phép sửa từ khóa |
| Sort dropdown | Most relevant, Most viewed, Newest first, A→Z |
| Per-page selector | 3 / 5 / 10 |
| Filter theme buttons | All, Emergency, Mental Health, Cardiovascular, Nutrition |
| Dòng meta | Số kết quả tìm thấy |
| Danh sách kết quả | Mỗi kết quả: type label ("Article"), breadcrumb theme, tiêu đề (highlight), excerpt (highlight), view count, ngày publish, read time, tags (tối đa 3) |
| Phân trang | Prev/Next + số trang |
| Empty state | Không tìm thấy → thông báo + gợi ý |

### 2.3. Redirect toast

Khi click vào gợi ý typeahead hoặc kết quả → toast hiển thị URL đích và simulate navigation.

---

## 3. Use Cases

### UC-SEARCH-01: Tìm kiếm nhanh (typeahead)

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-SEARCH-01 |
| **Tên** | Tìm kiếm nhanh với gợi ý typeahead |
| **Mô tả** | Người dùng gõ từ khóa, hệ thống hiển thị dropdown gợi ý bài viết real-time |
| **Điều kiện tiên quyết** | Không bắt buộc đăng nhập |
| **Luồng chính** | 1. Gõ từ khóa vào ô search → 2. Hệ thống gọi API tìm kiếm → 3. Hiển thị dropdown tối đa 7 gợi ý (bài viết, highlight từ khóa) → 4. Click gợi ý → navigate đến bài viết |
| **Hậu điều kiện** | Người dùng được điều hướng đến bài viết được chọn |
| **Luồng thay thế** | Không tìm thấy → dropdown trống. Bấm Enter thay vì click → chuyển sang trang kết quả đầy đủ |

### UC-SEARCH-02: Tìm kiếm đầy đủ

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-SEARCH-02 |
| **Tên** | Tìm kiếm đầy đủ với filter và phân trang |
| **Mô tả** | Người dùng bấm Enter để xem trang kết quả đầy đủ, có thể lọc theo theme, sắp xếp, phân trang |
| **Điều kiện tiên quyết** | Đã nhập từ khóa tìm kiếm |
| **Luồng chính** | 1. Bấm Enter từ ô search → 2. Chuyển sang trạng thái kết quả → 3. Hệ thống gọi API tìm kiếm đầy đủ → 4. Hiển thị danh sách kết quả (article/course/theme/section) → 5. Người dùng có thể lọc theme, sắp xếp, thay đổi per-page, phân trang |
| **Hậu điều kiện** | Kết quả hiển thị chính xác theo bộ lọc |
| **Luồng thay thế** | Không tìm thấy → empty state. Bấm Back → quay về hero search |

### UC-SEARCH-03: Tìm kiếm theo trending tag

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-SEARCH-03 |
| **Tên** | Tìm kiếm theo trending tag |
| **Mô tả** | Người dùng click vào trending tag để tìm kiếm nhanh theo chủ đề phổ biến |
| **Điều kiện tiên quyết** | Đang ở trạng thái hero search |
| **Luồng chính** | 1. Click trending tag (VD: "CPR") → 2. Từ khóa được điền vào ô search → 3. Typeahead dropdown hiển thị gợi ý |
| **Hậu điều kiện** | Ô search có từ khóa, dropdown gợi ý hiển thị |
| **Luồng thay thế** | Không có kết quả cho tag → dropdown trống |

---

## 4. API

| # | API | Method | Sử dụng tại |
|---|-----|--------|-------------|
| 1 | `/api/search?q={keyword}&type=article&limit=7` | GET | Typeahead → gợi ý nhanh (chỉ article) |
| 2 | `/api/search?q={keyword}&theme={id}&sort={field}&page={p}&limit={n}` | GET | Trang kết quả → tìm kiếm đầy đủ (article, course, theme, section) |
| 3 | `/api/tags/trending` | GET | Hero → trending tags |
