# login_form.py
import tkinter as tk
from tkinter import messagebox
from main_form import BookManagementMain  # Import form chính tại đây

class LoginForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Đăng Nhập Thư Viện")
        self.geometry("400x320")
        self.resizable(False, False)
        self.configure(bg="#F5F5F5")
        
        self.center_window(400, 320)
        
        self.MY_USERNAME = "Khánh Hưng"
        self.MY_PASSWORD = "123"
        
        self.init_ui()

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.geometry(f"{width}x{height}+{int(x)}+{int(y)}")

    def init_ui(self):
        container = tk.Frame(self, bg="#F5F5F5", padx=40, pady=30)
        container.pack(fill="both", expand=True)
        
        lbl_title = tk.Label(container, text="ĐĂNG NHẬP", font=("Segoe UI", 16, "bold"), fg="#5D4037", bg="#F5F5F5")
        lbl_title.pack(pady=(0, 20))
        
        frame_user = tk.LabelFrame(container, text="Tên đăng nhập", bg="#F5F5F5", font=("Segoe UI", 9))
        frame_user.pack(fill="x", pady=5)
        self.txt_user = tk.Entry(frame_user, font=("Segoe UI", 10), bd=0, bg="#F5F5F5", highlightthickness=0)
        self.txt_user.pack(fill="x", padx=10, pady=5)
        
        frame_pass = tk.LabelFrame(container, text="Mật khẩu", bg="#F5F5F5", font=("Segoe UI", 9))
        frame_pass.pack(fill="x", pady=5)
        self.txt_pass = tk.Entry(frame_pass, show="*", font=("Segoe UI", 10), bd=0, bg="#F5F5F5", highlightthickness=0)
        self.txt_pass.pack(fill="x", padx=10, pady=5)
        
        pnl_buttons = tk.Frame(container, bg="#F5F5F5")
        pnl_buttons.pack(pady=(20, 0))
        
        btn_exit = tk.Button(pnl_buttons, text="Thoát", bg="#D32F2F", fg="white", font=("Segoe UI", 10, "bold"), 
                             width=10, height=1, relief="flat", command=self.destroy, cursor="hand2")
        btn_exit.pack(side="left", padx=10)
        
        btn_login = tk.Button(pnl_buttons, text="Đăng Nhập", bg="#5D4037", fg="white", font=("Segoe UI", 10, "bold"), 
                              width=12, height=1, relief="flat", command=self.check_login, cursor="hand2")
        btn_login.pack(side="left", padx=10)
        
        self.bind("<Return>", lambda event: self.check_login())

    def check_login(self):
        input_user = self.txt_user.get().strip()
        input_pass = self.txt_pass.get()
        
        if input_user == self.MY_USERNAME and input_pass == self.MY_PASSWORD:
            messagebox.showinfo("Thông báo", "Đăng nhập thành công!")
            self.withdraw()
            # Mở form chính và truyền 'self' (LoginForm) làm parent
            BookManagementMain(self, input_user, "Thủ thư")
        else:
            messagebox.showerror("Lỗi Đăng Nhập", "Tên đăng nhập hoặc mật khẩu không chính xác!")
