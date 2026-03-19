# Trang Bách Khoa Y Tế (Encyclopedia Article)

**Route:** `/wiki/:article-slug`

**Tài nguyên:**
- [doc.md](https://williamchristopheralt.github.io/medicalogy_docs/screens/6-infographic/doc.md) (tài liệu này)
- [demo.html](https://williamchristopheralt.github.io/medicalogy_docs/screens/6-infographic/demo.html) (demo tương tác)
- [MARKDOWN_SPEC.md](https://williamchristopheralt.github.io/medicalogy_docs/screens/6-infographic/MARKDOWN_SPEC.md) (cú pháp Markdown tùy chỉnh)
- [markdown.md](https://williamchristopheralt.github.io/medicalogy_docs/screens/6-infographic/markdown.md) (ví dụ Markdown)
- [md_to_html_v2.py](https://williamchristopheralt.github.io/medicalogy_docs/screens/6-infographic/md_to_html_v2.py) (script chuyển đổi Markdown sang HTML)

---

## 1. Mục đích

Hiển thị bài viết bách khoa y tế cho người dùng. Nội dung được viết bằng custom Markdown bởi Staff, tự động parse thành HTML. Người dùng có thể đọc bài, bookmark, comment, reply, vote comment, và xem bài viết liên quan.

> **Nguồn dữ liệu:** Ký hiệu `bảng.cột` → cột trong database (schema v4). Custom Markdown syntax xem file `MARKDOWN_SPEC.md`.
>
> | Bảng DB | Ý nghĩa | Cột chính sử dụng trong trang này |
> |---------|---------|-----------------------------------|
> | `article` | Bài viết bách khoa | `name`, `slug`, `content_markdown`, `is_published`, `published_at`, `theme_id` |
> | `tag` | Nhãn phân loại | `name` |
> | `article_tag` | Liên kết bài viết ↔ tag (N-N) | `article_id`, `tag_id` |
> | `article_related` | Bài viết liên quan (N-N) | `article_id`, `related_article_id` |
> | `user_article_view` | Lượt xem bài viết của user | `view_count`, `last_viewed_at` |
> | `user_bookmark` | Bookmark bài viết | `user_id`, `article_id` |
> | `user_article_comment` | Comment trên bài viết | `comment_text`, `parent_comment_id`, `is_approved` |
> | `user_comment_vote` | Vote comment (like/dislike) | `vote_type` (`'like'` / `'dislike'`) |

---

## 2. Cấu trúc trang

### 2.1. Nội dung bài viết (vùng chính)

| Thành phần | Mô tả |
|-----------|-------|
| Tiêu đề (H1) | `article.name` |
| Metadata | Theme badge, tên tác giả, ngày publish, số lượt xem, tags |
| Nút Bookmark | Toggle bookmark/unbookmark. Thay đổi icon + text khi click |
| Nội dung HTML | Parse từ `article.content_markdown`. Gồm: heading (H2, H3), đoạn văn, bold (`*bold*`), italic (`/italic/`), hình ảnh (left/right/center), wiki links (`[display\|slug]`), external links (`{display\|url}`), danh sách, nguồn tham khảo (## Sources) |

### 2.2. Sidebar phải

| Thành phần | Mô tả |
|-----------|-------|
| Table of Contents (TOC) | Tự động generate từ H2 + H3. Click → smooth scroll đến section. Highlight mục đang active khi scroll |
| Related Articles | Tối đa 5 bài liên quan. Ưu tiên: cùng theme → cùng tag → random. Không hiển thị bài hiện tại |

### 2.3. Discussion Section (dưới bài viết)

| Thành phần | Mô tả |
|-----------|-------|
| Comment box | Textarea để nhập comment (10–5000 ký tự). Nút "Post Comment" |
| Danh sách comment | Hiển thị comment đã duyệt (`is_approved = 1`). Mỗi comment: avatar, tên user, thời gian, nội dung, nút Like/Dislike (số đếm), nút Reply |
| Reply | Nested dưới comment cha. Cùng format, cũng cần duyệt |
| Vote (Like/Dislike) | Click like → thêm vote. Click lại → hủy vote. Click dislike khi đã like → đổi vote. Không vote comment của chính mình |

---

## 3. Use Cases

### UC-WIKI-01: Xem bài viết

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-WIKI-01 |
| **Tên** | Xem bài viết bách khoa |
| **Mô tả** | Người dùng truy cập bài viết, hệ thống hiển thị nội dung đã parse, TOC, related articles, và tự động track view |
| **Điều kiện tiên quyết** | Bài viết tồn tại với `is_published = 1` |
| **Luồng chính** | 1. Truy cập `/wiki/:slug` → 2. Hệ thống load bài viết → 3. Track view: tạo/cập nhật `user_article_view` (1 view/session) → 4. Hiển thị nội dung HTML + TOC + related articles + comments |
| **Hậu điều kiện** | View count được cập nhật. Nội dung hiển thị đầy đủ |
| **Luồng thay thế** | Bài viết không tồn tại hoặc chưa publish → 404 |

### UC-WIKI-02: Bookmark bài viết

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-WIKI-02 |
| **Tên** | Bookmark / Unbookmark bài viết |
| **Mô tả** | Người dùng toggle bookmark bài viết để đọc sau |
| **Điều kiện tiên quyết** | Đã đăng nhập; bài viết `is_published = 1` |
| **Luồng chính** | 1. Bấm nút Bookmark → 2. Nếu chưa bookmark → tạo record `user_bookmark` → icon đổi thành "Bookmarked" → 3. Nếu đã bookmark → xóa record → icon đổi lại |
| **Hậu điều kiện** | Record `user_bookmark` được tạo hoặc xóa. UI cập nhật |
| **Luồng thay thế** | Chưa đăng nhập → yêu cầu đăng nhập |

### UC-WIKI-03: Comment bài viết

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-WIKI-03 |
| **Tên** | Đăng comment trên bài viết |
| **Mô tả** | Người dùng viết comment hoặc reply comment khác |
| **Điều kiện tiên quyết** | Đã đăng nhập |
| **Luồng chính** | 1. Nhập nội dung comment (10–5000 ký tự) → 2. Bấm "Post Comment" → 3. Hệ thống tạo record `user_article_comment` với `is_approved = 0` → 4. Hiển thị "Comment đang chờ duyệt" |
| **Hậu điều kiện** | Comment được tạo, chờ Staff/Admin duyệt. Khi `is_approved = 1` mới hiển thị công khai |
| **Luồng thay thế** | Reply → gửi kèm `parent_comment_id`. Nội dung < 10 hoặc > 5000 ký tự → validation error |

### UC-WIKI-04: Vote comment

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-WIKI-04 |
| **Tên** | Like / Dislike comment |
| **Mô tả** | Người dùng vote comment của người khác |
| **Điều kiện tiên quyết** | Đã đăng nhập; comment đã duyệt; không phải comment của chính mình |
| **Luồng chính** | 1. Bấm Like hoặc Dislike → 2. Chưa vote → tạo record `user_comment_vote` → 3. Đã vote cùng loại → xóa record (hủy vote) → 4. Đã vote khác loại → update `vote_type` |
| **Hậu điều kiện** | Record `user_comment_vote` được tạo/cập nhật/xóa. Số like/dislike cập nhật trên UI |
| **Luồng thay thế** | Vote comment của chính mình → không cho phép |

---

## 4. API

| # | API | Method | Sử dụng tại |
|---|-----|--------|-------------|
| 1 | `/api/articles/:slug` | GET | Nội dung bài viết (HTML đã parse, theme, tags, author, viewCount, bookmarked status) |
| 2 | `/api/articles/:articleId/related` | GET | Sidebar → related articles (tối đa 5) |
| 3 | `/api/articles/:articleId/view` | POST | Tự động gọi khi mở bài → track view |
| 4 | `/api/bookmarks` | POST | Nút Bookmark → toggle add/remove (body: `{articleId}`) |
| 5 | `/api/articles/:articleId/comments` | GET | Discussion → danh sách comment (có replies nested) |
| 6 | `/api/articles/:articleId/comments` | POST | Discussion → đăng comment mới (body: `{commentText, parentCommentId}`) |
| 7 | `/api/comments/:commentId/vote` | POST | Discussion → like/dislike (body: `{voteType}`) |
| 8 | `/api/comments/:commentId` | PUT | Discussion → sửa comment của mình |
| 9 | `/api/comments/:commentId` | DELETE | Discussion → xóa comment của mình |
