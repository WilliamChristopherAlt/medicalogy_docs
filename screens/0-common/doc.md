# Trang Thành phần Chung (Common Elements)

**Tài nguyên:**
- [doc.md](https://williamchristopheralt.github.io/medicalogy_docs/screens/0-common/doc.md) (tài liệu này)
- [demo.html](https://williamchristopheralt.github.io/medicalogy_docs/screens/0-common/demo.html) (demo tương tác)

---

## 1. Mục đích

Định nghĩa các thành phần giao diện dùng chung trên **tất cả** các trang của ứng dụng Medicalogy: Navbar, Sidebar, Notification Popup. Các trang khác kế thừa layout này.

> **Nguồn dữ liệu**
> | Bảng | Cột chính |
> |------|-----------|
> | `notification` | `id`, `user_id`, `notification_type`, `reference_type`, `reference_id`, `is_read`, `read_at`, `sent_at` |
> | `user_notification_preference` | `user_id`, `notification_type`, `in_app_enabled`, `email_enabled`, `push_enabled` |
> | `user_daily_streak` | `user_id`, `current_streak` (dùng cho loại `streak_reminder`) |

---

## 2. Cấu trúc trang

### 2.1. Navbar (thanh trên cùng, cố định)

| Vùng | Thành phần | Chức năng |
|------|-----------|-----------|
| Trái | Logo "Medicalogy" | Click → về trang chủ |
| Trái (mobile) | Nút hamburger | Mở/đóng sidebar trên mobile |
| Giữa | Ô tìm kiếm | Tìm kiếm bài viết (nhập text, hiển thị dropdown gợi ý). **Ẩn trên mobile (≤1100px)** |
| Phải | Streak indicator | Hiển thị 3 thành phần: icon lửa + số ngày + nhãn "day streak". Nhãn ẩn trên màn hình nhỏ (≤600px) |
| Phải | Nút thông báo | Hiển thị số thông báo chưa đọc (badge đỏ). Click → mở danh sách thông báo |
| Phải | Avatar tài khoản | Click → dropdown: Settings, Log out |

### 2.2. Sidebar (thanh bên trái, cố định)

| Nhóm | Mục | Điều hướng đến |
|------|-----|---------------|
| *(chung)* | Dashboard | `/dashboard` |
| **Learning** | Themes | `/themes` — danh sách chủ đề |
| | Enrolled Themes *(mở/đóng được)* | Submenu các theme đã đăng ký (ví dụ: Emergency Care, Mental Health, Nutrition) |
| **Resources** | Encyclopedia | `/encyclopedia` — bách khoa y tế |
| | Bookmarks | `/bookmarks` — bài viết đã lưu |
| | Recent Articles *(mở/đóng được)* | Submenu 5 bài viết xem gần nhất |

- Mục đang active được highlight.
- Trên mobile (≤1100px): sidebar ẩn, bấm hamburger để mở dạng overlay.

### 2.3. Vùng nội dung chính

Nằm bên phải sidebar, phía dưới navbar. Mỗi trang sẽ render nội dung riêng vào vùng này.

### 2.4. Toast notification

Thanh thông báo nhanh xuất hiện ở dưới cùng màn hình khi có hành động thành công (ví dụ: "Bookmark removed", "Enrolled successfully"). Tự biến mất sau vài giây.

### 2.5. Notification Popup (panel thông báo)

Dropdown panel rộng 400px, mở ra khi bấm icon chuông trên navbar.

| Vùng | Thành phần | Chức năng |
|------|-----------|-----------|
| Header – trái | Tiêu đề "Notifications" + pill số chưa đọc (màu xanh) | Hiển thị tổng số thông báo chưa đọc |
| Header – phải | Nút "Mark all read" | Đánh dấu tất cả là đã đọc (UC-COMMON-06) |
| Body | Danh sách thông báo (có cuộn) | Mỗi card: icon loại + tiêu đề + nội dung (2 dòng) + thời gian + chấm xanh (nếu chưa đọc) |
| Footer | Thông tin trang ("X of Y") + nút Prev / Next | Phân trang theo batch |

**Trạng thái card thông báo:**

| Trạng thái | Màu nền | Chấm chỉ thị |
|-----------|---------|-------------|
| Chưa đọc (`is_read = 0`) | Trắng | Chấm xanh (hiển thị) |
| Đã đọc (`is_read = 1`) | Xám nhạt (`#f6f6f6`) | Không hiển thị |

**Các loại thông báo (`notification_type`):**

| Loại | Màu icon | Nguồn dữ liệu (`reference_type`) |
|------|---------|----------------------------------|
| `streak_reminder` | Cam | NULL — lấy `current_streak` từ `user_daily_streak` |
| `course_recommendation` | Xanh dương | `'course'` → `course.name` |
| `test_result` | Tím | `'section_test'` → `section.name` + `user_section_test.passed` |
| `comment_reply` | Xanh lá | `'comment'` → theo comment → `article.name` |
| `system_log` | Xám | NULL — nội dung cố định (bảo trì, sự cố) |
| `security` | Đỏ | NULL — Auth Service kích hoạt (đăng nhập mới, đổi mật khẩu) |
| `achievement` | Cam | `'course'` hoặc `'section_test'` → tên entity |
| `content_update` | Xanh dương | `'article'` hoặc `'course'` → tên entity |

---

## 3. Use Cases

### UC-COMMON-01: Xem thông báo

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-COMMON-01 |
| **Tên** | Xem thông báo |
| **Mô tả** | Người dùng bấm icon chuông để xem danh sách thông báo chưa đọc |
| **Điều kiện tiên quyết** | Đã đăng nhập |
| **Luồng chính** | 1. Bấm icon chuông → 2. Hệ thống gọi API lấy thông báo → 3. Hiển thị danh sách → 4. Bấm 1 thông báo → đánh dấu đã đọc và điều hướng |
| **Hậu điều kiện** | Thông báo được đánh dấu đã đọc; badge cập nhật |
| **Luồng thay thế** | Không có thông báo → hiển thị "Không có thông báo mới" |

### UC-COMMON-02: Tìm kiếm nhanh từ Navbar

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-COMMON-02 |
| **Tên** | Tìm kiếm nhanh từ Navbar |
| **Mô tả** | Người dùng nhập từ khóa vào ô tìm kiếm trên navbar, hệ thống hiển thị dropdown gợi ý bài viết/course/theme phù hợp |
| **Điều kiện tiên quyết** | Đã đăng nhập |
| **Luồng chính** | 1. Nhập từ khóa vào ô search → 2. Hệ thống gọi API tìm kiếm → 3. Hiển thị dropdown kết quả → 4. Bấm kết quả → điều hướng đến trang tương ứng |
| **Hậu điều kiện** | Người dùng được điều hướng đến bài viết/course/theme |
| **Luồng thay thế** | Không tìm thấy kết quả → hiển thị "Không tìm thấy" |

### UC-COMMON-03: Xem streak hiện tại

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-COMMON-03 |
| **Tên** | Xem streak hiện tại |
| **Mô tả** | Hệ thống hiển thị số ngày streak liên tục trên navbar |
| **Điều kiện tiên quyết** | Đã đăng nhập |
| **Luồng chính** | 1. Trang load → 2. Gọi API lấy streak → 3. Hiển thị icon lửa + số ngày |
| **Hậu điều kiện** | Streak hiển thị chính xác |
| **Luồng thay thế** | Chưa có streak → hiển thị "0" |

### UC-COMMON-04: Đăng nhập

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-COMMON-04 |
| **Tên** | Đăng nhập |
| **Mô tả** | Người dùng đăng nhập vào hệ thống để truy cập các trang yêu cầu xác thực |
| **Điều kiện tiên quyết** | Chưa đăng nhập; có tài khoản hợp lệ |
| **Luồng chính** | 1. Truy cập trang login → 2. Nhập email + mật khẩu → 3. Bấm "Đăng nhập" → 4. Hệ thống xác thực → 5. Trả về access token + refresh token → 6. Redirect về trang trước đó hoặc dashboard |
| **Hậu điều kiện** | Token được lưu (localStorage/cookie). Navbar hiển thị avatar, streak, thông báo |
| **Luồng thay thế** | Sai email/mật khẩu → hiển thị lỗi "Email hoặc mật khẩu không đúng". Token hết hạn → dùng refresh token để lấy access token mới |

### UC-COMMON-05: Đăng xuất

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-COMMON-05 |
| **Tên** | Đăng xuất |
| **Mô tả** | Người dùng đăng xuất khỏi hệ thống |
| **Điều kiện tiên quyết** | Đã đăng nhập |
| **Luồng chính** | 1. Bấm avatar → 2. Chọn "Log out" từ dropdown → 3. Hệ thống xóa refresh token phía server → 4. Xóa token phía client → 5. Redirect về trang login |
| **Hậu điều kiện** | Token bị xóa. Truy cập trang yêu cầu xác thực → redirect về login |
| **Luồng thay thế** | — |

### UC-COMMON-06: Đánh dấu tất cả thông báo đã đọc

| Thuộc tính | Nội dung |
|---|---|
| **Mã UC** | UC-COMMON-06 |
| **Tên** | Đánh dấu tất cả thông báo đã đọc |
| **Mô tả** | Người dùng bấm "Mark all read" trong notification popup để đánh dấu toàn bộ thông báo là đã đọc |
| **Điều kiện tiên quyết** | Đã đăng nhập; có ít nhất 1 thông báo chưa đọc |
| **Luồng chính** | 1. Mở notification popup → 2. Bấm "Mark all read" → 3. Gọi API PATCH `/api/notifications/read-all` → 4. Tất cả thông báo chuyển sang đã đọc → 5. Badge chuông và pill "X unread" về 0 |
| **Hậu điều kiện** | Tất cả `notification.is_read = 1`; badge `notification-badge` ẩn đi |
| **Luồng thay thế** | Tất cả đã đọc rồi → nút "Mark all read" bị vô hiệu hóa |

---

## 4. API

| # | API | Method | Sử dụng tại |
|---|-----|--------|-------------|
| 1 | `/api/notifications?page={n}&limit={size}` | GET | Notification popup → lấy danh sách thông báo theo trang |
| 2 | `/api/notifications/unread-count` | GET | Navbar → badge số thông báo chưa đọc |
| 3 | `/api/notifications/{id}/read` | PATCH | Notification popup → bấm vào 1 thông báo → đánh dấu đã đọc |
| 4 | `/api/notifications/read-all` | PATCH | Notification popup → nút "Mark all read" (UC-COMMON-06) |
| 5 | `/api/search?q={keyword}` | GET | Navbar → ô tìm kiếm (dropdown gợi ý) |
| 6 | `/api/users/me/streak` | GET | Navbar → streak indicator |
| 7 | `/api/users/me/profile` | GET | Navbar → avatar tài khoản (initials, avatar) |
| 8 | `/api/users/me/enrolled-themes` | GET | Sidebar → submenu "Enrolled Themes" |
| 9 | `/api/users/me/recent-articles` | GET | Sidebar → submenu "Recent Articles" |
| 10 | `/api/auth/login` | POST | Trang login → đăng nhập (body: `{email, password}` → trả về access token + refresh token) |
| 11 | `/api/auth/logout` | POST | Navbar → dropdown "Log out" → xóa refresh token phía server |
| 12 | `/api/auth/refresh` | POST | Tự động gọi khi access token hết hạn (body: `{refreshToken}` → trả về access token mới) |
