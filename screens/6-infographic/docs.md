# Tài liệu BA - Trang Bách Khoa Y Tế (Encyclopedia/Infographic Page)

## 1. Overview - Tổng quan dự án

### 1.1. Mục đích

Tài liệu BA này mô tả chi tiết yêu cầu nghiệp vụ, chức năng và kỹ thuật cho **Trang Bách Khoa Y Tế** của BioBasics. Hệ thống cho phép Staff viết nội dung bài viết y tế dưới dạng file Markdown (.md), sau đó tự động chuyển đổi thành trang HTML hiển thị cho User xem. Tài liệu phục vụ như nguồn tham chiếu chính thức cho Product Owner, Dev Team, QA Team, UI/UX Designer, và Stakeholders.

### 1.2. Phạm vi

Hệ thống bao gồm:

- **Viết nội dung**: Staff viết nội dung Markdown theo cú pháp quy định (lưu trực tiếp trong database dưới dạng string)
- **Chuyển đổi tự động**: Parser chuyển Markdown string thành HTML styled
- **Hiển thị bài viết**: User xem bài viết với layout đẹp, có TOC, related articles
- **Comment**: User có thể comment, reply, like/dislike
- **Bookmark**: User có thể bookmark bài viết để đọc sau
- **View tracking**: Hệ thống đếm lượt xem bài viết
- **Tag & Search**: Phân loại và tìm kiếm bài viết

---

## 2. Actor & Quyền - Vai trò và Phân quyền

### 2.1. Staff (Người viết nội dung)

**Mô tả**: Nhân viên y tế, biên tập viên, chuyên gia nội dung

**Quyền hạn**:
- Viết nội dung Markdown mới cho bài viết (lưu trong database)
- Chỉnh sửa nội dung Markdown hiện có
- Upload hình ảnh minh họa
- Thêm tags cho bài viết
- Thiết lập related articles
- Preview bài viết trước khi công khai
- Công khai/ẩn bài viết

**Không được phép**:
- Xóa bài viết đã công khai (chỉ ẩn)
- Chỉnh sửa comment của user
- Xem thông tin cá nhân của user

### 2.2. User (Người đọc)

**Mô tả**: Người dùng đã đăng ký tài khoản BioBasics

**Quyền hạn**:
- Xem tất cả bài viết đã công khai
- Bookmark bài viết
- Comment trên bài viết
- Reply comment của người khác
- Like/dislike comment
- Chỉnh sửa/xóa comment của chính mình
- Xem lịch sử bài viết đã đọc

**Không được phép**:
- Tạo hoặc chỉnh sửa bài viết
- Xóa comment của người khác
- Xem bài viết chưa công khai

---

## 3. Business Rules - Quy tắc nghiệp vụ

### 3.1. Quy tắc Viết nội dung (Staff)

#### BR-001: Cú pháp Markdown

| Rule ID | Quy tắc | Bắt buộc |
|---------|---------|----------|
| BR-001-01 | Staff phải viết nội dung theo custom Markdown syntax được quy định | Có |
| BR-001-02 | Nội dung Markdown lưu trực tiếp trong database dưới dạng NVARCHAR(MAX) | Có |
| BR-001-03 | Bắt buộc có H1 title (# Title) | Có |
| BR-001-04 | Bắt buộc có ít nhất 1 H2 section (## Section) | Có |
| BR-001-05 | Bắt buộc có phần Sources ở cuối (## Sources) | Có |
| BR-001-06 | Hình ảnh phải chỉ rõ vị trí: `left`, `right`, hoặc `center` | Có |
| BR-001-07 | Wiki links dùng cú pháp `[[term]]` để link tới bài viết khác | Không |

#### BR-002: Metadata bài viết

| Rule ID | Quy tắc | Bắt buộc |
|---------|---------|----------|
| BR-002-01 | Mỗi bài viết phải thuộc 1 theme duy nhất | Có |
| BR-002-02 | Bài viết có thể có nhiều tags (không giới hạn) | Không |
| BR-002-03 | Slug được tự động generate từ title (lowercase, dấu gạch nối) | Có |
| BR-002-04 | Slug phải unique trong toàn hệ thống | Có |

#### BR-003: Hình ảnh

| Rule ID | Quy tắc | Bắt buộc |
|---------|---------|----------|
| BR-003-01 | Hình ảnh upload qua CDN/file storage riêng | Có |
| BR-003-02 | Chỉ hỗ trợ định dạng: JPG, PNG, WebP | Có |
| BR-003-03 | Kích thước tối đa: 5MB/file | Có |
| BR-003-04 | Tên file theo format: `theme-slug_article-slug_image-name.extension` | Có |

#### BR-004: Công khai/Ẩn bài viết

| Rule ID | Quy tắc | Bắt buộc |
|---------|---------|----------|
| BR-004-01 | Bài viết mới tạo mặc định `is_published = 0` (nháp) | Có |
| BR-004-02 | Chỉ công khai khi đã có đầy đủ: title, content, theme, ít nhất 1 tag | Có |
| BR-004-03 | Công khai: cập nhật `is_published = 1`, `published_at = NOW()` | Có |
| BR-004-04 | Ẩn bài viết: cập nhật `is_published = 0`, giữ nguyên `published_at` | Có |
| BR-004-05 | Bài viết bị ẩn vẫn giữ nguyên comments, bookmarks, views | Có |

### 3.2. Quy tắc Xem bài viết (User)

#### BR-005: Hiển thị bài viết

| Rule ID | Quy tắc | Bắt buộc |
|---------|---------|----------|
| BR-005-01 | Chỉ hiển thị bài viết có `is_published = 1` | Có |
| BR-005-02 | User xem bài viết → tự động tăng view count | Có |
| BR-005-03 | Mỗi user chỉ được tính 1 view/bài viết/session | Có |
| BR-005-04 | View count được track trong bảng `user_article_view` | Có |

#### BR-006: Table of Contents (TOC)

| Rule ID | Quy tắc | Bắt buộc |
|---------|---------|----------|
| BR-006-01 | TOC tự động generate từ H2 và H3 headers | Có |
| BR-006-02 | TOC hiển thị ở sidebar (desktop) | Có |
| BR-006-03 | Click vào TOC item → scroll smooth đến section tương ứng | Có |
| BR-006-04 | Highlight TOC item đang active khi user scroll | Có |

#### BR-007: Related Articles

| Rule ID | Quy tắc | Bắt buộc |
|---------|---------|----------|
| BR-007-01 | Hiển thị tối đa 5 related articles ở sidebar | Có |
| BR-007-02 | Ưu tiên: articles cùng theme > articles cùng tags > random | Có |
| BR-007-03 | Không hiển thị bài viết hiện tại trong related articles | Có |

### 3.3. Quy tắc Comment

#### BR-008: Tạo Comment

| Rule ID | Quy tắc | Bắt buộc |
|---------|---------|----------|
| BR-008-01 | User phải đăng nhập mới được comment | Có |
| BR-008-02 | Comment text tối thiểu 10 ký tự, tối đa 5000 ký tự | Có |
| BR-008-03 | Comment mặc định `is_approved = 0` (chờ duyệt) | Có |
| BR-008-04 | Staff/Admin có thể duyệt/từ chối comment | Có |
| BR-008-05 | Comment được duyệt mới hiển thị công khai | Có |

#### BR-009: Reply Comment

| Rule ID | Quy tắc | Bắt buộc |
|---------|---------|----------|
| BR-009-01 | User có thể reply comment đã được duyệt | Có |
| BR-009-02 | Reply cũng phải qua duyệt mới hiển thị | Có |
| BR-009-03 | Số cấp reply không giới hạn (nested) | Có |
| BR-009-04 | Không thể reply comment của chính mình | Có |

#### BR-010: Vote Comment

| Rule ID | Quy tắc | Bắt buộc |
|---------|---------|----------|
| BR-010-01 | User có thể like hoặc dislike mỗi comment 1 lần | Có |
| BR-010-02 | Click like: `vote_type = 'like'`, tăng like count | Có |
| BR-010-03 | Click dislike: `vote_type = 'dislike'`, tăng dislike count | Có |
| BR-010-04 | Click lại cùng vote → hủy vote, giảm count | Có |
| BR-010-05 | Click vote khác → đổi vote, cập nhật count | Có |
| BR-010-06 | Không thể vote comment của chính mình | Có |

#### BR-011: Chỉnh sửa/Xóa Comment

| Rule ID | Quy tắc | Bắt buộc |
|---------|---------|----------|
| BR-011-01 | User chỉ có thể edit/delete comment của chính mình | Có |
| BR-011-02 | Edit comment: cập nhật `comment_text`, `updated_at` | Có |
| BR-011-03 | Delete comment: xóa vĩnh viễn khỏi database | Có |
| BR-011-04 | Xóa parent comment → tự động xóa tất cả replies | Có |

### 3.4. Quy tắc Bookmark

#### BR-012: Bookmark bài viết

| Rule ID | Quy tắc | Bắt buộc |
|---------|---------|----------|
| BR-012-01 | User phải đăng nhập mới được bookmark | Có |
| BR-012-02 | Mỗi user chỉ bookmark 1 lần/bài viết (unique constraint) | Có |
| BR-012-03 | Click bookmark → thêm record vào `user_bookmark` | Có |
| BR-012-04 | Click unbookmark → xóa record khỏi `user_bookmark` | Có |
| BR-012-05 | Số lượng bookmark không giới hạn | Có |

---

## 4. User Flow - Luồng người dùng

### 4.1. Flow Staff viết bài viết

```
1. Staff đăng nhập vào CMS
2. Click "Tạo bài viết mới"
3. Điền thông tin:
   - Tiêu đề bài viết
   - Chọn Theme
   - Nhập nội dung Markdown vào textarea
4. Upload hình ảnh (nếu có) lên CDN
5. Paste image URLs vào Markdown
6. Chọn Tags (multiple select)
7. Chọn Related Articles (optional)
8. Click "Preview" để xem trước
   - Backend parse Markdown → HTML
   - Hiển thị preview page
9. Nếu OK: Click "Lưu nháp"
   - Backend:
     - Parse Markdown → HTML
     - Generate slug từ title
     - Validate nội dung
     - INSERT vào bảng article:
       - name, slug, content_markdown
       - theme_id, author_admin_id
       - is_published = 0
     - INSERT vào article_tag (nếu có tags)
     - INSERT vào article_related (nếu có)
   - Hiển thị: "Lưu nháp thành công"
10. Staff review bài viết ở chế độ nháp
11. Nếu OK: Click "Công khai"
    - Backend:
      - Validate: phải có title, content, theme, ít nhất 1 tag
      - UPDATE article SET is_published = 1, published_at = NOW()
    - Bài viết xuất hiện công khai
12. Nếu cần sửa:
    - Staff click "Chỉnh sửa"
    - Sửa nội dung Markdown
    - Click "Lưu"
    - Backend re-parse và UPDATE
```

### 4.2. Flow User xem bài viết

```
1. User truy cập trang chủ hoặc search
2. Click vào bài viết muốn đọc
3. Backend:
   - Kiểm tra is_published = 1
   - Load article content từ database
   - Check user_article_view:
     - Nếu chưa có record → tạo mới (view_count = 1)
     - Nếu đã có → cập nhật last_viewed_at, view_count +1
4. Frontend render:
   - Global navbar + sidebar
   - Article content (HTML đã parse)
   - TOC (auto-generate từ H2/H3)
   - Related articles sidebar
   - Discussion section (comments)
5. User đọc bài viết, scroll trang
   - TOC highlight theo scroll position
6. User có thể:
   - Bookmark bài viết
   - Comment
   - Reply comment
   - Vote comment
```

### 4.3. Flow Bookmark bài viết

```
1. User đang xem bài viết
2. Click nút "Bookmark" (icon bookmark hoặc text)
3. Frontend gửi POST /api/bookmarks
   Request body: { articleId: "uuid" }
4. Backend:
   - Kiểm tra user đã đăng nhập
   - Kiểm tra đã bookmark chưa (query user_bookmark)
   - Nếu chưa:
     - INSERT vào user_bookmark (user_id, article_id)
     - Trả về success: true
   - Nếu đã có:
     - DELETE khỏi user_bookmark
     - Trả về success: true, action: "removed"
5. Frontend cập nhật UI:
   - Đổi icon/text: "Bookmarked" / "Bookmark"
   - Đổi màu nút
   - Hiển thị toast notification
```

### 4.4. Flow Comment trên bài viết

```
1. User đang xem bài viết
2. Scroll xuống Discussion section
3. Nhập comment vào textarea
4. Click "Post Comment"
5. Frontend gửi POST /api/articles/:articleId/comments
   Request body:
   {
     commentText: "Nội dung comment",
     parentCommentId: null  // null = top-level, có giá trị = reply
   }
6. Backend:
   - Kiểm tra user đã đăng nhập
   - Validate comment_text (10-5000 ký tự)
   - INSERT vào user_article_comment:
     - user_id
     - article_id
     - parent_comment_id (null hoặc uuid)
     - comment_text
     - is_approved = 0
     - created_at = NOW()
   - Trả về success, message: "Comment đang chờ duyệt"
7. Frontend hiển thị thông báo
   - "Comment của bạn đang chờ duyệt"
   - Không hiển thị comment ngay lập tức
8. Staff/Admin vào CMS:
   - Xem danh sách comments chờ duyệt
   - Approve hoặc Reject
   - Nếu Approve: is_approved = 1
9. Comment được approve xuất hiện công khai
```

### 4.5. Flow Vote Comment

```
1. User xem comment đã được approve
2. Click icon "Like" hoặc "Dislike"
3. Frontend gửi POST /api/comments/:commentId/vote
   Request body: { voteType: "like" }  // hoặc "dislike"
4. Backend:
   - Kiểm tra user đã đăng nhập
   - Query user_comment_vote (user_id, comment_id)
   - Case 1: Chưa vote
     - INSERT vào user_comment_vote (vote_type)
     - Trả về: action: "added", voteType: "like"
   - Case 2: Đã vote cùng loại (like → like again)
     - DELETE khỏi user_comment_vote
     - Trả về: action: "removed"
   - Case 3: Đã vote khác loại (like → dislike)
     - UPDATE user_comment_vote SET vote_type = "dislike"
     - Trả về: action: "changed", voteType: "dislike"
5. Frontend cập nhật UI:
   - Tăng/giảm like count hoặc dislike count
   - Đổi màu icon (active/inactive)
```

---

## 5. Wireframe - Giao diện màn hình

### 5.1. Màn hình Desktop - Xem bài viết

```
┌─────────────────────────────────────────────────────────────────┐
│ [Logo] BioBasics    [Search...]      🔥7  🔔3  [JD]             │ ← Global Navbar
├──────────┬──────────────────────────────────────────┬───────────┤
│          │                                          │           │
│ Sidebar  │        ARTICLE CONTENT AREA              │ TOC +     │
│          │                                          │ Related   │
│ • Home   │  # Myocardial Infarction (Heart Attack) │           │
│ • Themes │                                          │ • Intro   │
│ • Encyclo│  [Bookmark btn]                          │ • Risk    │
│   • CPR  │                                          │ • Symptoms│
│   • Chok.│  A myocardial infarction (MI)...        │ • Treat   │
│          │                                          │           │
│          │  ## Understanding the Condition          │ ─────────│
│          │                                          │ Related:  │
│          │  [img-left] The heart muscle requires...│ • CAD     │
│          │  text wraps around... lorem ipsum dolor │ • CPR     │
│          │                                          │ • Stroke  │
│          │  ## Risk Factors                         │           │
│          │                                          │           │
│          │  | Category | Factors |                  │           │
│          │  | Modif.   | Smoking |                  │           │
│          │                                          │           │
│          │  ## Warning Signs                        │           │
│          │  - Chest discomfort                      │           │
│          │  - Upper body pain                       │           │
│          │                                          │           │
│          │  ────────────────────────────            │           │
│          │                                          │           │
│          │  ## Discussion                           │           │
│          │  [Your avatar] [Write comment...]        │           │
│          │                [Post Comment]            │           │
│          │                                          │           │
│          │  ┌─ Dr. Sarah Chen  2 hours ago         │           │
│          │  │  Great article! The golden hour...   │           │
│          │  │  👍 24  👎 1  💬 Reply                 │           │
│          │  │                                       │           │
│          │  │  ├─ Medical Student Mike 1h ago      │           │
│          │  │  │  That's a great point...          │           │
│          │  │  │  👍 8  👎 0  💬 Reply               │           │
│          │  └────────────────────────────          │           │
│          │                                          │           │
└──────────┴──────────────────────────────────────────┴───────────┘
```

**Các thành phần:**

1. **Global Navbar**: Logo, Search, Streak, Notifications, Account
2. **Left Sidebar**: Navigation menu (Dashboard, Themes, Encyclopedia)
3. **Main Content Area**: Bài viết đã parse từ Markdown
4. **Right Sidebar**: 
   - Table of Contents (scroll-spy)
   - Related Articles (5 items)
5. **Discussion Section**: Comment box + list comments
6. **Bookmark Button**: Góc phải trên, sticky khi scroll

---

## 6. Data Specification - Đặc tả dữ liệu

### 6.1. Bảng `article`

Lưu trữ bài viết bách khoa y tế.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UNIQUEIDENTIFIER | PRIMARY KEY, DEFAULT NEWID() | ID bài viết |
| `theme_id` | UNIQUEIDENTIFIER | NOT NULL, FK → theme(id) | Thuộc theme nào |
| `name` | NVARCHAR(300) | NOT NULL | Tiêu đề bài viết |
| `slug` | NVARCHAR(300) | NOT NULL, UNIQUE | URL-friendly slug |
| `content_markdown` | NVARCHAR(MAX) | NOT NULL | Nội dung gốc (Markdown) |
| `author_admin_id` | UNIQUEIDENTIFIER | FK → user(id) | Staff viết bài |
| `is_published` | BIT | DEFAULT 0 | 0=draft, 1=published |
| `published_at` | DATETIME2 | NULL | Thời điểm publish |
| `created_at` | DATETIME2 | DEFAULT GETDATE() | Thời điểm tạo |
| `updated_at` | DATETIME2 | DEFAULT GETDATE() | Thời điểm cập nhật |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `slug`
- INDEX on `theme_id`
- INDEX on `is_published`

### 6.2. Bảng `tag`

Danh sách tags phân loại bài viết.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UNIQUEIDENTIFIER | PRIMARY KEY | ID tag |
| `name` | NVARCHAR(100) | NOT NULL, UNIQUE | Tên tag |
| `created_at` | DATETIME2 | DEFAULT GETDATE() | Thời điểm tạo |

### 6.3. Bảng `article_tag` (Many-to-Many)

Liên kết article với tags.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `article_id` | UNIQUEIDENTIFIER | NOT NULL, FK → article(id) ON DELETE CASCADE | ID bài viết |
| `tag_id` | UNIQUEIDENTIFIER | NOT NULL, FK → tag(id) ON DELETE CASCADE | ID tag |
| `created_at` | DATETIME2 | DEFAULT GETDATE() | Thời điểm gắn tag |

**PRIMARY KEY**: `(article_id, tag_id)`

### 6.4. Bảng `article_related` (Many-to-Many)

Liên kết các bài viết liên quan (bidirectional).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `article_id` | UNIQUEIDENTIFIER | NOT NULL, FK → article(id) ON DELETE CASCADE | Bài viết chính |
| `related_article_id` | UNIQUEIDENTIFIER | NOT NULL, FK → article(id) | Bài viết liên quan |
| `created_at` | DATETIME2 | DEFAULT GETDATE() | Thời điểm liên kết |

**PRIMARY KEY**: `(article_id, related_article_id)`  
**CHECK CONSTRAINT**: `article_id != related_article_id` (không tự liên kết)

### 6.5. Bảng `user_article_view`

Track user đã xem bài viết nào, bao nhiêu lần.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `user_id` | UNIQUEIDENTIFIER | NOT NULL, FK → user(id) | User xem |
| `article_id` | UNIQUEIDENTIFIER | NOT NULL, FK → article(id) ON DELETE CASCADE | Bài viết được xem |
| `view_count` | INT | DEFAULT 1 | Số lần xem |
| `first_viewed_at` | DATETIME2 | DEFAULT GETDATE() | Lần đầu xem |
| `last_viewed_at` | DATETIME2 | DEFAULT GETDATE() | Lần cuối xem |

**PRIMARY KEY**: `(user_id, article_id)`

### 6.6. Bảng `user_article_comment`

Comments của user trên bài viết.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UNIQUEIDENTIFIER | PRIMARY KEY | ID comment |
| `user_id` | UNIQUEIDENTIFIER | NOT NULL, FK → user(id) | User comment |
| `article_id` | UNIQUEIDENTIFIER | NOT NULL, FK → article(id) ON DELETE CASCADE | Bài viết được comment |
| `parent_comment_id` | UNIQUEIDENTIFIER | NULL, FK → user_article_comment(id) | NULL = top-level, có giá trị = reply |
| `comment_text` | NVARCHAR(MAX) | NOT NULL | Nội dung comment |
| `is_approved` | BIT | DEFAULT 0 | 0=chờ duyệt, 1=đã duyệt |
| `created_at` | DATETIME2 | DEFAULT GETDATE() | Thời điểm comment |
| `updated_at` | DATETIME2 | DEFAULT GETDATE() | Thời điểm chỉnh sửa |

**Indexes:**
- INDEX on `article_id`
- INDEX on `parent_comment_id`
- INDEX on `is_approved`

### 6.7. Bảng `user_comment_vote`

User vote (like/dislike) comments.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `user_id` | UNIQUEIDENTIFIER | NOT NULL, FK → user(id) | User vote |
| `comment_id` | UNIQUEIDENTIFIER | NOT NULL, FK → user_article_comment(id) ON DELETE CASCADE | Comment được vote |
| `vote_type` | NVARCHAR(10) | NOT NULL, CHECK IN ('like', 'dislike') | Loại vote |
| `created_at` | DATETIME2 | DEFAULT GETDATE() | Thời điểm vote |

**PRIMARY KEY**: `(user_id, comment_id)`

### 6.8. Bảng `user_bookmark`

User bookmark bài viết.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UNIQUEIDENTIFIER | PRIMARY KEY | ID bookmark |
| `user_id` | UNIQUEIDENTIFIER | NOT NULL, FK → user(id) | User bookmark |
| `article_id` | UNIQUEIDENTIFIER | NOT NULL, FK → article(id) ON DELETE CASCADE | Bài viết được bookmark |
| `created_at` | DATETIME2 | DEFAULT GETDATE() | Thời điểm bookmark |

**UNIQUE CONSTRAINT**: `(user_id, article_id)` - mỗi user chỉ bookmark 1 lần/bài viết

### 6.9. Validation Rules

#### Article

| Field | Rule | Error Message |
|-------|------|---------------|
| `name` | NOT NULL, 10-300 chars | "Tiêu đề bài viết phải từ 10-300 ký tự" |
| `slug` | NOT NULL, unique, lowercase, hyphenated | "Slug không hợp lệ hoặc đã tồn tại" |
| `content_markdown` | NOT NULL, min 100 chars | "Nội dung bài viết quá ngắn (tối thiểu 100 ký tự)" |
| `theme_id` | Must exist in `theme` table | "Theme không tồn tại" |

#### Comment

| Field | Rule | Error Message |
|-------|------|---------------|
| `comment_text` | 10-5000 chars | "Comment phải từ 10-5000 ký tự" |
| `parent_comment_id` | Must exist if not NULL | "Comment cha không tồn tại" |
| `user_id` | Must be logged in | "Bạn phải đăng nhập để comment" |

#### Bookmark

| Field | Rule | Error Message |
|-------|------|---------------|
| `user_id` | Must be logged in | "Bạn phải đăng nhập để bookmark" |
| `article_id` | Must exist and is_published = 1 | "Bài viết không tồn tại" |
| Unique pair | No duplicate (user_id, article_id) | "Bạn đã bookmark bài viết này rồi" |

---

## 7. API/System - Đặc tả API

### 7.1. Article Endpoints

#### GET /api/articles/:slug

**Mô tả**: Lấy chi tiết 1 bài viết theo slug

**Parameters:**
- `slug` (path): Slug của bài viết

**Query params:**
- None

**Response 200 - Success:**
```json
{
  "success": true,
  "data": {
    "id": "uuid-here",
    "name": "Myocardial Infarction (Heart Attack)",
    "slug": "myocardial-infarction-heart-attack",
    "contentHtml": "<h1>Myocardial Infarction</h1><p>...</p>",
    "theme": {
      "id": "uuid",
      "name": "Cardiology",
      "slug": "cardiology",
      "colorCode": "#00f5d0"
    },
    "tags": [
      { "id": "uuid1", "name": "Cardiology" },
      { "id": "uuid2", "name": "Emergency Medicine" }
    ],
    "author": {
      "id": "uuid",
      "displayName": "Dr. John Smith"
    },
    "publishedAt": "2026-01-15T10:30:00Z",
    "viewCount": 12847,
    "userHasBookmarked": true,
    "userViewCount": 3
  }
}
```

**Response 404 - Not Found:**
```json
{
  "success": false,
  "error": "Bài viết không tồn tại hoặc chưa được publish"
}
```

#### GET /api/articles

**Mô tả**: Lấy danh sách bài viết (có filter, search, pagination)

**Query params:**
- `themeId` (optional): Filter theo theme
- `tagId` (optional): Filter theo tag
- `search` (optional): Tìm kiếm theo title
- `page` (default: 1): Số trang
- `limit` (default: 20): Số items/trang

**Response 200:**
```json
{
  "success": true,
  "data": {
    "articles": [
      {
        "id": "uuid",
        "name": "CPR Basics",
        "slug": "cpr-basics",
        "excerpt": "Cardiopulmonary resuscitation...",
        "theme": { "name": "Emergency", "colorCode": "#ff6b9d" },
        "tags": ["First Aid", "Emergency"],
        "publishedAt": "2026-01-10T08:00:00Z",
        "viewCount": 5420
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 5,
      "totalItems": 98,
      "hasNext": true,
      "hasPrev": false
    }
  }
}
```

#### POST /api/articles (Staff only)

**Mô tả**: Tạo bài viết mới

**Authentication**: Required (Staff/Admin role)

**Request body:**
```json
{
  "name": "Stroke Prevention",
  "themeId": "uuid-cardiology",
  "contentMarkdown": "# Stroke Prevention\n\n## Introduction\n...",
  "tagIds": ["uuid-tag1", "uuid-tag2"],
  "relatedArticleIds": ["uuid-article1", "uuid-article2"],
  "isPublished": false
}
```

**Response 201 - Created:**
```json
{
  "success": true,
  "message": "Bài viết đã được tạo thành công",
  "data": {
    "id": "uuid-new-article",
    "slug": "stroke-prevention"
  }
}
```

### 7.2. Comment Endpoints

#### GET /api/articles/:articleId/comments

**Mô tả**: Lấy danh sách comments của bài viết

**Parameters:**
- `articleId` (path): ID bài viết

**Query params:**
- `page` (default: 1)
- `limit` (default: 20)

**Response 200:**
```json
{
  "success": true,
  "data": {
    "comments": [
      {
        "id": "uuid-comment",
        "user": {
          "id": "uuid-user",
          "displayName": "Dr. Sarah Chen",
          "avatarUrl": "https://..."
        },
        "commentText": "Excellent article!...",
        "createdAt": "2026-02-05T10:00:00Z",
        "likeCount": 24,
        "dislikeCount": 1,
        "userVote": "like",
        "replies": [
          {
            "id": "uuid-reply",
            "user": { "displayName": "Medical Student Mike" },
            "commentText": "Great point...",
            "createdAt": "2026-02-05T11:00:00Z",
            "likeCount": 8,
            "dislikeCount": 0,
            "userVote": null
          }
        ]
      }
    ],
    "pagination": { "currentPage": 1, "totalPages": 3 }
  }
}
```

#### POST /api/articles/:articleId/comments

**Mô tả**: Tạo comment mới

**Authentication**: Required

**Request body:**
```json
{
  "commentText": "This is very helpful information!",
  "parentCommentId": null
}
```

**Response 201:**
```json
{
  "success": true,
  "message": "Comment của bạn đang chờ duyệt",
  "data": {
    "id": "uuid-new-comment",
    "isApproved": false
  }
}
```

#### POST /api/comments/:commentId/vote

**Mô tả**: Vote comment (like/dislike)

**Authentication**: Required

**Request body:**
```json
{
  "voteType": "like"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "action": "added",
    "voteType": "like",
    "likeCount": 25,
    "dislikeCount": 1
  }
}
```

### 7.3. Bookmark Endpoints

#### POST /api/bookmarks

**Mô tả**: Bookmark hoặc unbookmark bài viết

**Authentication**: Required

**Request body:**
```json
{
  "articleId": "uuid-article"
}
```

**Response 200 - Bookmark added:**
```json
{
  "success": true,
  "message": "Đã thêm vào bookmark",
  "data": {
    "action": "added",
    "bookmarkId": "uuid-bookmark"
  }
}
```

**Response 200 - Bookmark removed:**
```json
{
  "success": true,
  "message": "Đã xóa khỏi bookmark",
  "data": {
    "action": "removed"
  }
}
```

#### GET /api/bookmarks

**Mô tả**: Lấy danh sách bài viết đã bookmark

**Authentication**: Required

**Query params:**
- `page` (default: 1)
- `limit` (default: 20)

**Response 200:**
```json
{
  "success": true,
  "data": {
    "bookmarks": [
      {
        "id": "uuid-bookmark",
        "article": {
          "id": "uuid-article",
          "name": "CPR Basics",
          "slug": "cpr-basics",
          "excerpt": "...",
          "theme": { "name": "Emergency" }
        },
        "bookmarkedAt": "2026-02-03T14:00:00Z"
      }
    ],
    "pagination": { "currentPage": 1, "totalPages": 2 }
  }
}
```

### 7.4. View Tracking Endpoint

#### POST /api/articles/:articleId/view

**Mô tả**: Track user view bài viết (tự động gọi khi user mở bài viết)

**Authentication**: Required

**Response 200:**
```json
{
  "success": true,
  "data": {
    "viewCount": 12848,
    "userViewCount": 4
  }
}
```

### 7.5. Related Articles Endpoint

#### GET /api/articles/:articleId/related

**Mô tả**: Lấy danh sách bài viết liên quan

**Response 200:**
```json
{
  "success": true,
  "data": {
    "relatedArticles": [
      {
        "id": "uuid",
        "name": "Coronary Artery Disease",
        "slug": "coronary-artery-disease",
        "theme": { "name": "Cardiology" }
      }
    ]
  }
}
```

### 7.6. Tổng hợp Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/articles` | Optional | Danh sách bài viết |
| GET | `/api/articles/:slug` | Optional | Chi tiết bài viết |
| POST | `/api/articles` | Staff | Tạo bài viết mới |
| PUT | `/api/articles/:id` | Staff | Cập nhật bài viết |
| DELETE | `/api/articles/:id` | Admin | Xóa bài viết |
| GET | `/api/articles/:id/related` | No | Bài viết liên quan |
| POST | `/api/articles/:id/view` | Required | Track view |
| GET | `/api/articles/:id/comments` | Optional | Danh sách comments |
| POST | `/api/articles/:id/comments` | Required | Tạo comment |
| PUT | `/api/comments/:id` | Required | Sửa comment (own) |
| DELETE | `/api/comments/:id` | Required | Xóa comment (own) |
| POST | `/api/comments/:id/vote` | Required | Vote comment |
| GET | `/api/bookmarks` | Required | Danh sách bookmark |
| POST | `/api/bookmarks` | Required | Add/remove bookmark |

---

## 8. Non-functional Requirements - Yêu cầu phi chức năng

### 8.1. Performance - Hiệu năng

#### NFR-001: Page Load Time
- **Yêu cầu**: Trang bài viết phải load trong < 2 giây (3G connection)
- **Cách đạt**:
  - HTML đã parse sẵn (không parse real-time)
  - Images lazy load
  - CSS/JS minified và cached
  - CDN cho static assets

#### NFR-002: Parser Performance
- **Yêu cầu**: Parse 1 file Markdown (10KB) trong < 500ms
- **Cách đạt**:
  - Optimize parser algorithm
  - Cache parsed HTML trong database
  - Chỉ re-parse khi content thay đổi

#### NFR-003: Database Query
- **Yêu cầu**: Mỗi query < 100ms
- **Cách đạt**:
  - Đánh index đúng columns (slug, theme_id, is_published)
  - Query optimization (JOIN hiệu quả)
  - Connection pooling

### 8.2. Scalability - Khả năng mở rộng

#### NFR-004: Concurrent Users
- **Yêu cầu**: Hỗ trợ 10,000 concurrent users xem bài viết
- **Cách đạt**:
  - Read-heavy optimization (caching)
  - Load balancer
  - Database read replicas

#### NFR-005: Article Growth
- **Yêu cầu**: Hệ thống hoạt động tốt với 10,000+ articles
- **Cách đạt**:
  - Pagination
  - Database partitioning (nếu cần)
  - Archive old articles (is_active flag)

### 8.3. Security - Bảo mật

#### NFR-006: XSS Prevention
- **Yêu cầu**: Không bị XSS attack qua Markdown content
- **Cách đạt**:
  - Sanitize HTML output từ parser
  - Chỉ allow safe HTML tags
  - Escape user input trong comments

#### NFR-007: SQL Injection Prevention
- **Yêu cầu**: Không bị SQL injection
- **Cách đạt**:
  - Dùng parameterized queries
  - ORM validation
  - Input validation ở API layer

#### NFR-008: Authentication
- **Yêu cầu**: Chỉ logged-in users mới comment/bookmark
- **Cách đạt**:
  - JWT token validation
  - Middleware check auth trước mỗi protected endpoint

### 8.4. SEO - Search Engine Optimization

#### NFR-009: Meta Tags
- **Yêu cầu**: Mỗi bài viết có đầy đủ meta tags
- **Cách đạt**:
  - Auto-generate từ article content:
    - `<title>`: article.name + " | BioBasics"
    - `<meta description>`: excerpt (150 chars đầu)
    - `<meta keywords>`: tags
    - Open Graph tags (og:image, og:description)

#### NFR-010: URL Structure
- **Yêu cầu**: URL SEO-friendly
- **Format**: `/wiki/:theme-slug/:article-slug`
- **Example**: `/wiki/cardiology/myocardial-infarction`

#### NFR-011: Sitemap
- **Yêu cầu**: Auto-generate sitemap.xml
- **Cách đạt**:
  - Daily cron job query all published articles
  - Generate XML với lastmod, priority

### 8.6. Usability - Tính dễ sử dụng

#### NFR-014: Responsive
- **Yêu cầu**: Hoạt động tốt trên desktop
- **Cách đạt**:
  - CSS tối ưu cho màn hình lớn
  - Readable font sizes (16px+)

#### NFR-015: Browser Support
- **Yêu cầu**: Hỗ trợ các trình duyệt:
  - Chrome/Edge (2 versions gần nhất)
  - Firefox (2 versions gần nhất)
  - Safari (macOS 11+)

### 8.7. Maintainability - Khả năng bảo trì

#### NFR-016: Markdown Versioning
- **Yêu cầu**: Có thể revert về phiên bản cũ
- **Cách đạt**:
  - Lưu content_markdown trong article table
  - Git-based content management (optional)

#### NFR-017: Error Logging
- **Yêu cầu**: Log tất cả errors
- **Cách đạt**:
  - Centralized logging (Winston, Sentry)
  - Log level: ERROR, WARN, INFO
  - Include: timestamp, user_id, action, error_message

---

## Phụ lục A: Tham chiếu cú pháp Markdown tùy chỉnh

### Wiki Links
```markdown
[[term]]
[[blood clot]]
[[myocardium]]
```

### Hình ảnh với vị trí
```markdown
![left|Alt text](url)
![right|Alt text](url)
![center|Alt text](url)
```

### Chú thích hình ảnh
```markdown
![center|Image](url)
*Đây là chú thích*
```

### Bảng
```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

### Phần đặc biệt: Sources
```markdown
## Sources

- [Link 1](url)
- [Link 2](url)
```

---

## Phụ lục B: Ví dụ nội dung Markdown đầy đủ

```markdown
# Myocardial Infarction (Heart Attack)

A **myocardial infarction** (MI), commonly known as a *heart attack*, occurs when blood flow to a part of the [[cardiac muscle]] is blocked.

---

## Understanding the Condition

![left|Diagram of heart with blocked artery](https://example.com/heart.jpg)

The [[myocardium]] requires constant oxygen supply. When [[coronary arteries]] become blocked, heart tissue begins to die.

According to the [American Heart Association](https://www.heart.org), prompt treatment is critical.

---

## Risk Factors

| Category | Risk Factors |
|----------|-------------|
| **Modifiable** | Smoking, high blood pressure, obesity |
| **Non-modifiable** | Age, family history |

---

## Warning Signs

Common symptoms include:

- **Chest discomfort**: Pressure lasting more than 5 minutes
- **Upper body pain**: Arms, back, neck, jaw
- **Shortness of breath**: With or without chest pain

---

## Sources

- [American Heart Association - Heart Attack](https://www.heart.org/heart-attack)
- [Mayo Clinic - Myocardial Infarction](https://www.mayoclinic.org/mi)
```

---

**END OF DOCUMENT**