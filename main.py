# main.py
from database import LibraryDAO
from login_form import LoginForm

def test_database_connection():
    print("--- KIỂM TRA KẾT NỐI SQL SERVER ---")
    dao = LibraryDAO()
    try:
        conn = dao.connect()
        if conn:
            print("✅ KẾT NỐI THÀNH CÔNG!")
            books = dao.get_all_books()
            print(f"-> Tìm thấy {len(books)} cuốn sách.")
            conn.close()
    except Exception as e:
        print("❌ KẾT NỐI THẤT BẠI:", e)
        print("Gợi ý: Kiểm tra kĩ tài khoản/mật khẩu và xem đã bật TCP/IP trong cấu hình SQL Server chưa.")

def main():
    # Kiểm tra kết nối trước khi mở ứng dụng
    test_database_connection()
    
    # Khởi chạy giao diện
    app = LoginForm()
    app.mainloop()

if __name__ == "__main__":
    main()
