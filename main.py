# main.py
from database import LibraryDAO
from login_form import LoginForm

def test_database_connection():
    print("--- KIỂM TRA KẾT NỐI SUPABASE ---")
    dao = LibraryDAO()
    try:
        conn = dao.connect()
        if conn:
            print("✅ KẾT NỐI SUPABASE THÀNH CÔNG!")
            books = dao.get_all_books()
            print(f"-> Tìm thấy {len(books)} cuốn sách.")
            conn.close()
    except Exception as e:
        print("❌ KẾT NỐI SUPABASE THẤT BẠI:", e)
        print("Gợi ý: Kiểm tra kĩ thông số Host, User, Password trong file database.py và kết nối Internet.")

def main():
    test_database_connection()
    app = LoginForm()
    app.mainloop()

if __name__ == "__main__":
    main()
