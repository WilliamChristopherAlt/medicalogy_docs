# Tài liệu Trang Wiki/Article (Bài viết Y khoa)

## 1. Route và Mục đích trang

### Route
```
/wiki/:article-slug
```

**Ví dụ:**
- `/wiki/myocardial-infarction`
- `/wiki/diabetes-type-2`
- `/wiki/hypertension`
- `/wiki/covid-19`

### Mục đích
Trang hiển thị nội dung chi tiết của một bài viết bách khoa toàn thư y học. Người dùng có thể:
- Đọc nội dung bài viết đã được định dạng từ markdown
- Xem các bài viết có liên quan
- Lưu bài viết vào danh sách đánh dấu
- Đọc và tham gia thảo luận trong phần bình luận
- Bầu chọn (thích/không thích) các bình luận
- Trả lời các bình luận

### Cơ chế theo dõi lượt xem
- Mỗi lần người dùng xem bài viết, hệ thống tạo hoặc cập nhật bản ghi trong bảng `user_article_view`
- Trường `view_count` tăng lên mỗi lần xem
- Trường `last_viewed_at` được cập nhật thời gian xem gần nhất

---

## 2. Các thành phần trên màn hình

### 2.1. Header (cố định ở đầu trang)

**LƯU Ý:** Header này là phần của trang web, KHÔNG được tạo bởi markdown converter. Markdown converter chỉ chuyển đổi nội dung bài viết.

**Thanh điều hướng (Breadcrumb):**
- Định dạng: `Wiki > [Tiêu đề bài viết]`
- Ví dụ: `Wiki > Nhồi máu cơ tim`
- "Wiki" có thể nhấp để quay lại trang danh sách
- Tiêu đề bài viết không thể nhấp (đang ở trang hiện tại)

**Các nút thao tác:**
- **Nút đánh dấu:**
  - Biểu tượng bookmark trống/đầy
  - Nhấp để thêm hoặc bỏ đánh dấu
  - Đổi sang màu accent khi đã đánh dấu
  - Hành vi chuyển đổi (nhấp lại để bỏ đánh dấu)
  - Tạo hoặc xóa bản ghi trong bảng `user_bookmark`

**Nút quay lại:**
- Biểu tượng mũi tên trái hoặc chữ "← Quay lại"
- Nhấp để quay về trang danh sách bài viết hoặc trang trước đó

---

### 2.2. Vùng nội dung chính

**Thông tin meta của bài viết:**

**LƯU Ý:** Metadata này là phần của trang web, KHÔNG được tạo bởi markdown converter. Cần implement riêng trong page component.
- **Nhãn danh mục:** Hiển thị danh mục của bài viết (từ bảng `category`)
- **Các thẻ tag:** Danh sách các thẻ (từ bảng `article_tag` và `tag`)
  - Hiển thị dạng chip hoặc badge
  - Nhấp vào thẻ để xem các bài viết khác có cùng thẻ
- **Thời gian đọc:** Ước tính thời gian cần để đọc (tính từ độ dài nội dung)
- **Cập nhật lần cuối:** Ngày cập nhật cuối cùng (từ trường `article.updated_at`)
- **Số lượt xem:** Tổng số lượt xem (tổng hợp từ bảng `user_article_view`)

**Nội dung bài viết:**

**LƯU Ý:** Phần này ĐƯỢC TẠO bởi markdown converter `md_to_html_with_comments.py`.
- Nội dung được render từ trường `article.content_html`
- HTML đã được chuyển đổi từ markdown theo đặc tả trong tài liệu "BioBasics Wiki Markdown Specification"
- Áp dụng định dạng CSS từ mẫu trong công cụ chuyển đổi markdown
- Hỗ trợ:
  - Tiêu đề (H1, H2, H3)
  - Chữ in đậm, in nghiêng
  - Hình ảnh với vị trí (trái, phải, giữa)
  - Bảng
  - Danh sách đánh dấu
  - Liên kết wiki nội bộ `[[thuật ngữ]]`
  - Liên kết bên ngoài
  - Đường kẻ ngang
  - Phần nguồn tham khảo (có định dạng đặc biệt)

**Mục lục (Table of Contents):**

**LƯU Ý:** Mục lục này KHÔNG được tạo bởi markdown converter. Cần implement riêng trong page component bằng JavaScript để parse các header từ HTML đã render.
- Tự động tạo từ các tiêu đề (H2, H3) trong nội dung
- Vị trí cố định ở thanh bên (desktop) hoặc có thể thu gọn ở trên cùng (mobile)
- Nhấp để cuộn mượt mà đến phần tương ứng
- Làm nổi bật phần hiện tại khi người dùng cuộn trang

---

### 2.3. Thanh bên (desktop) / Phần dưới (mobile)

**LƯU Ý:** Thanh bên này là phần của trang web, KHÔNG được tạo bởi markdown converter. Cần implement riêng trong page component.

**Bài viết liên quan:**
- Tiêu đề: "Bài viết liên quan"
- Lấy dữ liệu từ bảng `article_related`
- Hiển thị tối đa 5-6 bài viết
- Mỗi mục hiển thị:
  - Hình thu nhỏ (nếu có)
  - Tiêu đề bài viết
  - Đoạn trích ngắn (100-150 ký tự đầu của nội dung)
  - Nhãn danh mục
  - Thời gian đọc
- Nhấp để điều hướng đến bài viết đó

**Phổ biến trong danh mục:**
- Tiêu đề: "Phổ biến trong [Tên danh mục]"
- Lấy các bài viết cùng danh mục, sắp xếp theo số lượt xem
- Hiển thị tối đa 4-5 bài viết
- Định dạng tương tự phần Bài viết liên quan

---

### 2.4. Phần thảo luận

**LƯU Ý:** Phần thảo luận này ĐƯỢC TẠO TỰ ĐỘNG bởi markdown converter `md_to_html_with_comments.py`. Converter tự động thêm phần này vào cuối mỗi trang wiki với đầy đủ chức năng comment, reply, like/dislike sử dụng JavaScript.

Phần thảo luận được đặt sau nội dung chính, trước footer. Chi tiết về giao diện và hành vi như sau:

**Tiêu đề phần:**
```
Thảo luận
Chia sẻ suy nghĩ, đặt câu hỏi hoặc thảo luận về chủ đề này với cộng đồng.
```

**Vùng nhập bình luận:**
- Ảnh đại diện của người dùng hiện tại (nền gradient với chữ cái đầu)
- Ô nhập văn bản để viết bình luận
  - Văn bản gợi ý: "Chia sẻ suy nghĩ hoặc đặt câu hỏi của bạn..."
  - Chiều cao tối thiểu: 3 dòng
  - Tự động mở rộng khi gõ nhiều
- Nút "Đăng bình luận"
  - Vô hiệu hóa khi ô nhập rỗng
  - Nền gradient (màu accent)
  - Nhấp để gửi bình luận

**Danh sách bình luận:**
Hiển thị tất cả bình luận từ bảng `user_article_comment`, sắp xếp theo `created_at` giảm dần (mới nhất lên đầu).

**Cấu trúc thẻ bình luận:**

```
┌─────────────────────────────────────────────────────┐
│ 👤 [Ảnh đại diện] [Tên người dùng]  [Thời gian]    │
│                                                      │
│ [Nội dung bình luận...]                             │
│                                                      │
│ 👍 [số lượt thích]  👎 [số không thích]  💬 Trả lời (X) │
│                                                      │
│ ┌─────────────────────────────────────────────────┐ │
│ │ 👤 [Ảnh đại diện] [Tên]     [Thời gian]        │ │ (Các câu trả lời)
│ │ [Nội dung trả lời...]                          │ │
│ │ 👍 [số thích]  👎 [số không thích]             │ │
│ └─────────────────────────────────────────────────┘ │
│                                                      │
│ [Ô nhập trả lời - hiện khi nhấp nút Trả lời]        │
└─────────────────────────────────────────────────────┘
```

**Các thành phần của bình luận:**

1. **Ảnh đại diện:**
   - Hình tròn với nền gradient
   - Chữ cái đầu của tên người dùng
   - Mỗi người dùng có màu gradient riêng (hash từ user_id)

2. **Thông tin người dùng:**
   - Tên người dùng (từ `user.username`)
   - Thời gian đăng (định dạng tương đối: "2 giờ trước", "1 ngày trước")

3. **Nội dung bình luận:**
   - Văn bản từ trường `comment_text`
   - Hỗ trợ ngắt dòng
   - Font size vừa phải, dễ đọc

4. **Các nút thao tác:**
   - **Nút Thích (👍):**
     - Hiển thị số lượt thích (đếm từ `user_comment_vote` với `vote_type = 'like'`)
     - Nhấp để thích
     - Đổi sang màu accent khi đã thích
     - Nhấp lại để bỏ thích
     - Tạo/xóa bản ghi trong `user_comment_vote`
   
   - **Nút Không thích (👎):**
     - Hiển thị số lượt không thích (đếm từ `user_comment_vote` với `vote_type = 'dislike'`)
     - Nhấp để không thích
     - Đổi sang màu accent khi đã không thích
     - Nhấp lại để bỏ không thích
     - Tạo/xóa bản ghi trong `user_comment_vote`
   
   - **Nút Trả lời (💬):**
     - Hiển thị số câu trả lời (đếm từ `user_article_comment` với `parent_comment_id = comment.id`)
     - Nhấp để hiển thị/ẩn ô nhập trả lời
     - Khi nhấp, hiển thị ô nhập văn bản và nút "Gửi trả lời" bên dưới bình luận

**Hành vi bầu chọn (Like/Dislike):**
- Người dùng chỉ có thể chọn một trong hai: thích HOẶC không thích
- Nếu đã thích mà nhấp không thích:
  - Bỏ lượt thích (xóa vote cũ)
  - Thêm lượt không thích (tạo vote mới)
  - Số đếm cập nhật ngay lập tức
- Nếu đã không thích mà nhấp thích:
  - Bỏ lượt không thích (xóa vote cũ)
  - Thêm lượt thích (tạo vote mới)
  - Số đếm cập nhật ngay lập tức
- Nhấp vào nút đã chọn để bỏ chọn (xóa vote)

**Các câu trả lời (Replies):**
- Hiển thị dưới bình luận gốc
- Thụt vào bên trái (padding-left hoặc margin-left)
- Có đường viền bên trái để phân biệt
- Cấu trúc tương tự bình luận gốc nhưng đơn giản hơn
- Không hỗ trợ trả lời của trả lời (chỉ 1 cấp độ)
- Lưu với `parent_comment_id = comment_id` của bình luận gốc

**Ô nhập trả lời:**
- Chỉ hiển thị khi người dùng nhấp nút "Trả lời"
- Bố cục ngang: ảnh đại diện + ô nhập + nút gửi
- Ô nhập nhỏ hơn ô bình luận chính (1-2 dòng)
- Nút "Gửi trả lời" với màu accent khác
- Nhấp "Gửi trả lời" để tạo bản ghi mới trong `user_article_comment` với:
  - `parent_comment_id = [ID của bình luận đang trả lời]`
  - `article_id = [ID bài viết hiện tại]`
  - `user_id = [ID người dùng hiện tại]`
  - `comment_text = [Nội dung trả lời]`
  - `is_approved = 0` (cần kiểm duyệt)

**Kiểm duyệt bình luận:**
- Tất cả bình luận mới có `is_approved = 0`
- Chỉ hiển thị bình luận với `is_approved = 1`
- Admin có thể duyệt bình luận trong trang quản trị
- Bình luận chưa duyệt không hiển thị cho người dùng khác
- Người viết vẫn thấy bình luận của mình với nhãn "Đang chờ kiểm duyệt"

**Sắp xếp bình luận:**
- Mặc định: Mới nhất lên đầu (`created_at DESC`)
- Tùy chọn sắp xếp (nếu có):
  - Mới nhất
  - Cũ nhất
  - Nhiều thích nhất
  - Nhiều trả lời nhất

---

## 3. Danh sách Use Case

### 3.1. Xem bài viết wiki

| Thuộc tính | Nội dung |
|------------|----------|
| Mã UC | UC-WIKI-01 |
| Tên | Xem bài viết wiki |
| Mô tả | Người dùng đọc nội dung chi tiết của một bài viết y học, xem các bài viết liên quan, và lưu bài viết vào danh sách đánh dấu nếu muốn |
| Điều kiện tiên quyết | - Người dùng đã đăng nhập<br>- Slug bài viết hợp lệ<br>- Bài viết tồn tại với `is_published = 1` |
| Luồng chính | 1. Người dùng truy cập trang bài viết qua route `/wiki/:article-slug`<br>2. Hệ thống tải bài viết từ bảng `article` theo slug<br>3. Hệ thống tạo/cập nhật bản ghi trong `user_article_view`:<br>   - Nếu chưa có: tạo mới với `view_count = 1`<br>   - Nếu đã có: tăng `view_count`, cập nhật `last_viewed_at`<br>4. Trang hiển thị:<br>   - Header với breadcrumb và nút đánh dấu<br>   - Thông tin meta (danh mục, thẻ, thời gian đọc, lượt xem)<br>   - Nội dung HTML từ `content_html`<br>   - Mục lục tự động<br>   - Bài viết liên quan từ `article_related`<br>   - Bài viết phổ biến trong cùng danh mục<br>   - Phần thảo luận<br>5. Người dùng đọc nội dung<br>6. Người dùng có thể:<br>   - Nhấp vào liên kết wiki nội bộ `[[thuật ngữ]]` để xem bài viết khác<br>   - Nhấp vào thẻ để xem bài viết cùng thẻ<br>   - Nhấp nút đánh dấu để lưu bài viết<br>   - Cuộn xuống đọc và tham gia thảo luận |
| Hậu điều kiện | - Bản ghi `user_article_view` được tạo/cập nhật<br>- Lượt xem được tăng<br>- Nếu đánh dấu: bản ghi `user_bookmark` được tạo |
| Luồng thay thế | **Alt 1: Bài viết không tồn tại**<br>- Tại bước 2: slug không hợp lệ hoặc bài viết không tìm thấy<br>- Hệ thống hiển thị trang 404 hoặc chuyển hướng về danh sách bài viết<br><br>**Alt 2: Bài viết chưa xuất bản**<br>- Tại bước 2: `is_published = 0`<br>- Hiển thị thông báo "Bài viết này chưa được xuất bản"<br>- Chuyển hướng về danh sách bài viết<br><br>**Alt 3: Người dùng chưa đăng nhập**<br>- Vẫn cho phép đọc bài viết<br>- Không theo dõi lượt xem<br>- Ẩn nút đánh dấu<br>- Ẩn phần viết bình luận (chỉ xem được bình luận) |

---

### 3.2. Đánh dấu bài viết

| Thuộc tính | Nội dung |
|------------|----------|
| Mã UC | UC-WIKI-02 |
| Tên | Đánh dấu bài viết |
| Mô tả | Người dùng lưu bài viết vào danh sách đánh dấu để đọc lại sau |
| Điều kiện tiên quyết | - Người dùng đã đăng nhập<br>- Đang xem một bài viết hợp lệ |
| Luồng chính | 1. Người dùng đang ở trang bài viết<br>2. Người dùng nhấp nút đánh dấu ở header<br>3. Hệ thống kiểm tra bảng `user_bookmark`:<br>   - Nếu chưa có: tạo bản ghi mới với `user_id`, `article_id`<br>   - Nếu đã có: xóa bản ghi (bỏ đánh dấu)<br>4. Nút đánh dấu thay đổi trạng thái:<br>   - Chưa đánh dấu: icon rỗng, màu neutral<br>   - Đã đánh dấu: icon đầy, màu accent<br>5. Hiển thị thông báo ngắn: "Đã lưu vào đánh dấu" hoặc "Đã bỏ đánh dấu" |
| Hậu điều kiện | - Bản ghi `user_bookmark` được tạo hoặc xóa<br>- Trạng thái nút đánh dấu được cập nhật |
| Luồng thay thế | **Alt 1: Người dùng chưa đăng nhập**<br>- Tại bước 2: không cho phép thao tác<br>- Hiển thị thông báo "Vui lòng đăng nhập để lưu bài viết"<br>- Hoặc chuyển hướng đến trang đăng nhập |

---

### 3.3. Tham gia thảo luận

| Thuộc tính | Nội dung |
|------------|----------|
| Mã UC | UC-WIKI-03 |
| Tên | Tham gia thảo luận |
| Mô tả | Người dùng viết bình luận, trả lời bình luận, và bầu chọn (thích/không thích) các bình luận trong phần thảo luận của bài viết |
| Điều kiện tiên quyết | - Người dùng đã đăng nhập<br>- Đang xem một bài viết hợp lệ |
| Luồng chính | **Viết bình luận mới:**<br>1. Người dùng cuộn xuống phần Thảo luận<br>2. Người dùng nhập nội dung vào ô bình luận<br>3. Người dùng nhấp nút "Đăng bình luận"<br>4. Hệ thống tạo bản ghi mới trong `user_article_comment`:<br>   - `user_id` = ID người dùng hiện tại<br>   - `article_id` = ID bài viết hiện tại<br>   - `parent_comment_id` = NULL<br>   - `comment_text` = nội dung nhập vào<br>   - `is_approved` = 0<br>5. Hiển thị thông báo "Bình luận của bạn đang chờ kiểm duyệt"<br>6. Ô nhập được xóa trắng<br><br>**Trả lời bình luận:**<br>7. Người dùng nhấp nút "Trả lời" dưới một bình luận<br>8. Hiển thị ô nhập trả lời<br>9. Người dùng nhập nội dung trả lời<br>10. Người dùng nhấp "Gửi trả lời"<br>11. Hệ thống tạo bản ghi mới trong `user_article_comment`:<br>    - `parent_comment_id` = ID của bình luận đang trả lời<br>    - Các trường khác tương tự bình luận mới<br>12. Hiển thị thông báo "Trả lời của bạn đang chờ kiểm duyệt"<br><br>**Bầu chọn bình luận:**<br>13. Người dùng nhấp nút Thích hoặc Không thích<br>14. Hệ thống kiểm tra `user_comment_vote`:<br>    - Nếu chưa vote: tạo bản ghi mới với `vote_type`<br>    - Nếu đã vote cùng loại: xóa bản ghi (bỏ vote)<br>    - Nếu đã vote khác loại: xóa vote cũ, tạo vote mới<br>15. Cập nhật số đếm hiển thị ngay lập tức<br>16. Thay đổi màu nút theo trạng thái vote |
| Hậu điều kiện | - Bản ghi `user_article_comment` được tạo (chờ kiểm duyệt)<br>- Bản ghi `user_comment_vote` được tạo/xóa/cập nhật<br>- Số đếm like/dislike được cập nhật<br>- Giao diện phản ánh trạng thái mới |
| Luồng thay thế | **Alt 1: Nội dung bình luận rỗng**<br>- Tại bước 3/10: nội dung trống hoặc chỉ có khoảng trắng<br>- Không cho phép gửi<br>- Nút "Đăng bình luận" bị vô hiệu hóa<br><br>**Alt 2: Người dùng chưa đăng nhập**<br>- Không hiển thị ô nhập bình luận<br>- Hiển thị thông báo "Đăng nhập để tham gia thảo luận"<br>- Vẫn hiển thị danh sách bình luận đã duyệt<br><br>**Alt 3: Bình luận đã được duyệt**<br>- Admin duyệt bình luận (cập nhật `is_approved = 1`)<br>- Bình luận xuất hiện trong danh sách cho tất cả người dùng<br>- Người viết nhận thông báo "Bình luận của bạn đã được duyệt" |

---

## 4. Lưu ý kỹ thuật

### 4.1. Render nội dung Markdown
- Sử dụng công cụ chuyển đổi markdown → HTML đã được định nghĩa
- Không lưu markdown trong database, chỉ lưu HTML đã render
- HTML phải được làm sạch (sanitize) để tránh XSS
- Áp dụng CSS template có sẵn từ converter

### 4.2. Tối ưu hiệu suất
- Cache HTML đã render
- Lazy load hình ảnh trong nội dung
- Phân trang bình luận nếu số lượng lớn (>20)
- Sử dụng virtual scroll cho danh sách bình luận dài

### 4.3. SEO và Metadata
- Tạo meta tags từ `article.terminology` và nội dung
- Sử dụng structured data (JSON-LD) cho bài viết y học
- Tạo sitemap cho tất cả bài viết đã xuất bản
- URL slug thân thiện với SEO

### 4.4. Bảo mật
- Kiểm tra quyền trước khi cho phép đánh dấu/bình luận
- Sanitize tất cả input của người dùng
- Rate limiting cho việc tạo bình luận (tránh spam)
- Kiểm duyệt bình luận trước khi hiển thị công khai

### 4.5. Responsive Design
- Mục lục chuyển sang collapsible trên mobile
- Thanh bên chuyển xuống dưới trên mobile
- Bình luận stack vertically trên màn hình nhỏ
- Nút thao tác có vùng nhấp đủ lớn cho touch