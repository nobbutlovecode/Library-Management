# database.py
import psycopg2
from datetime import datetime
from models import Book, BorrowedBook

class LibraryDAO:
    def __init__(self):
        # Bạn thay đổi các thông số dưới đây khớp với tài khoản Supabase của bạn
        self.host = "db.xxxxxx.supabase.co"       # Host từ Supabase
        self.user = "postgres"                     # Mặc định là postgres
        self.password = "Mật_Khẩu_Của_Bạn"         # Mật khẩu bạn đặt khi tạo dự án Supabase
        self.database = "postgres"                 # Database mặc định của Supabase là postgres
        self.port = "5432"                         # Cổng mặc định của PostgreSQL

    def connect(self):
        # Sử dụng thư viện psycopg2 để kết nối đến PostgreSQL/Supabase
        return psycopg2.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            dbname=self.database,
            port=self.port
        )

    def get_all_books(self):
        books = []
        sql = "SELECT id, title, author, image_file, description, quantity FROM books"
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                    for row in cursor.fetchall():
                        books.append(Book(row[0], row[1], row[2], row[3], row[4], row[5]))
        except Exception as e:
            print("Lỗi truy vấn danh sách sách:", e)
        return books

    def get_borrowed_books(self):
        list_borrowed = []
        sql = """
            SELECT bb.id, bb.book_id, bb.borrower_name, bb.student_id, bb.borrowed_time,
                   b.title, b.author, b.image_file, b.description, b.quantity
            FROM borrowed_books bb
            JOIN books b ON TRIM(bb.book_id) = TRIM(b.id)
        """
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                    for row in cursor.fetchall():
                        b = Book(row[1], row[5], row[6], row[7], row[8], row[9])
                        borrowed_time = row[4] if row[4] else datetime.now()
                        list_borrowed.append(BorrowedBook(row[0], b, row[2], row[3], borrowed_time))
        except Exception as e:
            print("Lỗi truy vấn danh sách phiếu mượn:", e)
        return list_borrowed

    def borrow_book(self, book_id, name, student_id):
        sql_update = "UPDATE books SET quantity = quantity - 1 WHERE id = %s AND quantity > 0"
        sql_insert = "INSERT INTO borrowed_books (book_id, borrower_name, student_id, borrowed_time) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)"
        try:
            conn = self.connect()
            cursor = conn.cursor()
            try:
                # Giao dịch thủ công với psycopg2
                cursor.execute(sql_update, (book_id,))
                if cursor.rowcount == 0:
                    conn.rollback()
                    return False
                cursor.execute(sql_insert, (book_id, name, student_id))
                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
        except Exception as e:
            print("Lỗi khi mượn sách:", e)
            return False

    def return_book(self, borrow_id, book_id):
        sql_delete = "DELETE FROM borrowed_books WHERE id = %s"
        sql_update = "UPDATE books SET quantity = quantity + 1 WHERE id = %s"
        try:
            conn = self.connect()
            cursor = conn.cursor()
            try:
                cursor.execute(sql_delete, (borrow_id,))
                cursor.execute(sql_update, (book_id,))
                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
        except Exception as e:
            print("Lỗi khi trả sách:", e)
            return False

    def update_quantity(self, book_id, new_qty):
        sql = "UPDATE books SET quantity = %s WHERE id = %s"
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (new_qty, book_id))
                    conn.commit()
        except Exception as e:
            print("Lỗi khi cập nhật số lượng:", e)
