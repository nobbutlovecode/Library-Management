# main_form.py
import os
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
from database import LibraryDAO

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

COLOR_PRIMARY = "#4E342E"
COLOR_ACCENT  = "#8D6E63"
COLOR_BG      = "#F5F5F5"
COLOR_DANGER  = "#C62828"
COLOR_SUCCESS = "#388E3C"

class BookManagementMain(tk.Toplevel):
    def __init__(self, parent, username, role):
        super().__init__(parent)
        self.parent = parent
        self.current_username = username
        self.current_role = role
        
        self.title(f"Quản Lý Thư Viện - {username}")
        self.geometry("1150x750")
        self.configure(bg=COLOR_BG)
        self.center_window(1150, 750)
        
        self.MAX_LOAN_DAYS = 14
        self.dao = LibraryDAO()
        self.selected_book = None
        self.selected_card = None
        
        self.protocol("WM_DELETE_WINDOW", self.on_close_app)
        self.init_layout()

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.geometry(f"{width}x{height}+{int(x)}+{int(y)}")

    def on_close_app(self):
        self.parent.destroy()

    def init_layout(self):
        self.sidebar = tk.Frame(self, bg=COLOR_PRIMARY, width=250)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        self.main_content = tk.Frame(self, bg=COLOR_BG)
        self.main_content.pack(side="right", fill="both", expand=True)
        
        self.create_sidebar_widgets()
        self.create_main_content_widgets()

    def load_image(self, filename, width, height):
        if HAS_PIL:
            try:
                path = os.path.join("img", filename)
                if os.path.exists(path):
                    img = Image.open(path)
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
                    return ImageTk.PhotoImage(img)
            except Exception as e:
                print("Lỗi load ảnh:", e)
        return None

    def create_sidebar_widgets(self):
        canvas_avatar = tk.Canvas(self.sidebar, width=130, height=130, bg=COLOR_PRIMARY, highlightthickness=3, highlightbackground="#FFFFFF")
        canvas_avatar.pack(pady=(30, 15))
        canvas_avatar.create_oval(10, 10, 120, 120, outline="white", width=2)
        canvas_avatar.create_text(65, 65, text="👤", fill="white", font=("Segoe UI Emoji", 40))
        
        lbl_name = tk.Label(self.sidebar, text=self.current_username.upper(), font=("Segoe UI", 13, "bold"), fg="white", bg=COLOR_PRIMARY)
        lbl_name.pack()
        
        lbl_role = tk.Label(self.sidebar, text=self.current_role, font=("Segoe UI", 11, "italic"), fg="#C8C8C8", bg=COLOR_PRIMARY)
        lbl_role.pack(pady=(5, 15))
        
        sep = ttk.Separator(self.sidebar, orient="horizontal")
        sep.pack(fill="x", padx=20, pady=(0, 25))
        
        btn_borrow = tk.Button(self.sidebar, text="📖  Mượn Sách", bg=COLOR_ACCENT, fg="white", font=("Segoe UI", 10, "bold"), 
                               command=self.action_borrow, relief="flat", height=2, bd=0, activebackground="#A1887F", activeforeground="white")
        btn_borrow.pack(fill="x", padx=20, pady=8)
        
        btn_return = tk.Button(self.sidebar, text="🔄  Trả Sách", bg=COLOR_ACCENT, fg="white", font=("Segoe UI", 10, "bold"), 
                               command=self.show_return_dialog, relief="flat", height=2, bd=0, activebackground="#A1887F", activeforeground="white")
        btn_return.pack(fill="x", padx=20, pady=8)
        
        pnl_bottom = tk.Frame(self.sidebar, bg=COLOR_PRIMARY)
        pnl_bottom.pack(side="bottom", fill="x", padx=20, pady=30)
        
        def on_logout():
            if messagebox.askyesno("Đăng xuất", "Bạn muốn đăng xuất?"):
                self.destroy()
                self.parent.deiconify()
                
        btn_logout = tk.Button(pnl_bottom, text="🚪  Đăng Xuất", bg="#3E2723", fg="white", font=("Segoe UI", 10, "bold"), 
                               command=on_logout, relief="flat", height=2, bd=0, activebackground="#2D1B18", activeforeground="white")
        btn_logout.pack(fill="x")

    def create_main_content_widgets(self):
        pnl_header = tk.Frame(self.main_content, bg=COLOR_BG)
        pnl_header.pack(fill="x", padx=40, pady=(25, 15))
        
        lbl_title = tk.Label(pnl_header, text="KHO SÁCH THƯ VIỆN", font=("Segoe UI", 18, "bold"), fg=COLOR_PRIMARY, bg=COLOR_BG)
        lbl_title.pack(side="left")
        
        pnl_search = tk.Frame(pnl_header, bg=COLOR_BG)
        pnl_search.pack(side="right")
        
        lbl_icon = tk.Label(pnl_search, text="🔍 ", font=("Segoe UI Emoji", 12), bg=COLOR_BG)
        lbl_icon.pack(side="left")
        
        self.search_var = tk.StringVar()
        txt_search = tk.Entry(pnl_search, textvariable=self.search_var, font=("Segoe UI", 10), width=25)
        txt_search.pack(side="left")
        
        self.search_var.trace_add("write", lambda *args: self.load_books(self.search_var.get()))
        
        pnl_wrapper = tk.Frame(self.main_content, bg=COLOR_BG)
        pnl_wrapper.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        
        self.canvas = tk.Canvas(pnl_wrapper, bg=COLOR_BG, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(pnl_wrapper, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLOR_BG)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.load_books("")

    def load_books(self, keyword):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        lower_key = keyword.lower().strip()
        books = self.dao.get_all_books()
        
        col = 0
        row = 0
        columns_limit = 4
        
        for i in range(columns_limit):
            self.scrollable_frame.grid_columnconfigure(i, weight=1, uniform="grid_col")
            
        for book in books:
            if lower_key and (lower_key not in book.title.lower() and lower_key not in book.author.lower()):
                continue
                
            card = self.create_book_card(self.scrollable_frame, book)
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            
            col += 1
            if col >= columns_limit:
                col = 0
                row += 1

    def bind_all_children(self, widget, event, callback):
        widget.bind(event, callback)
        for child in widget.winfo_children():
            self.bind_all_children(child, event, callback)

    def create_book_card(self, parent, book):
        card = tk.Frame(parent, bg="white", highlightbackground="#DCDCDC", highlightthickness=1, bd=0)
        
        img_photo = self.load_image(book.image_file, 120, 165)
        if img_photo:
            lbl_img = tk.Label(card, image=img_photo, bg="white")
            lbl_img.image = img_photo
        else:
            lbl_img = tk.Label(card, text="[NO IMAGE]", bg="white", fg="gray", font=("Segoe UI", 10))
        lbl_img.pack(pady=(15, 5))
        
        lbl_title = tk.Label(card, text=book.title, bg="white", font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARY, wraplength=140)
        lbl_title.pack(pady=2)
        
        qty_color = COLOR_SUCCESS if book.quantity > 0 else COLOR_DANGER
        lbl_qty = tk.Label(card, text=f"Kho: {book.quantity}", bg="white", font=("Segoe UI", 9, "bold"), fg=qty_color)
        lbl_qty.pack(pady=(2, 15))
        
        def on_click(event):
            if self.selected_card and self.selected_card.winfo_exists():
                self.selected_card.configure(bg="white", highlightbackground="#DCDCDC", highlightthickness=1)
                for child in self.selected_card.winfo_children():
                    child.configure(bg="white")
            
            self.selected_book = book
            self.selected_card = card
            card.configure(bg="#ECEFF1", highlightbackground=COLOR_SUCCESS, highlightthickness=2)
            for child in card.winfo_children():
                child.configure(bg="#ECEFF1")
                
        def on_double_click(event):
            self.show_book_detail_dialog(book)
            
        def on_enter(event):
            if self.selected_card != card:
                card.configure(bg="#FAFAFA")
                for child in card.winfo_children():
                    child.configure(bg="#FAFAFA")
            card.configure(cursor="hand2")
            
        def on_leave(event):
            if self.selected_card != card:
                card.configure(bg="white")
                for child in card.winfo_children():
                    child.configure(bg="white")
                    
        self.bind_all_children(card, "<Button-1>", on_click)
        self.bind_all_children(card, "<Double-Button-1>", on_double_click)
        self.bind_all_children(card, "<Enter>", on_enter)
        self.bind_all_children(card, "<Leave>", on_leave)
        
        return card

    def show_book_detail_dialog(self, book):
        dialog = tk.Toplevel(self)
        dialog.title("Thông tin chi tiết")
        dialog.geometry("600x440")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg="white")
        self.center_window_of_sub(dialog, 600, 440)
        
        pnl_left = tk.Frame(dialog, bg="white", width=180)
        pnl_left.pack(side="left", fill="y", padx=25, pady=25)
        pnl_left.pack_propagate(False)
        
        img_photo = self.load_image(book.image_file, 160, 220)
        if img_photo:
            lbl_img = tk.Label(pnl_left, image=img_photo, bg="white", bd=1, relief="solid")
            lbl_img.image = img_photo
        else:
            lbl_img = tk.Label(pnl_left, text="[No Image]", bg="white", bd=1, relief="solid")
        lbl_img.pack(expand=True, fill="both")
        
        pnl_right = tk.Frame(dialog, bg="white")
        pnl_right.pack(side="right", fill="both", expand=True, padx=(0, 25), pady=25)
        
        lbl_title = tk.Label(pnl_right, text=book.title, font=("Segoe UI", 15, "bold"), fg=COLOR_PRIMARY, bg="white", anchor="w")
        lbl_title.pack(fill="x", pady=(0, 2))
        
        lbl_author = tk.Label(pnl_right, text=f"Tác giả: {book.author}", font=("Segoe UI", 10, "italic"), fg="gray", bg="white", anchor="w")
        lbl_author.pack(fill="x", pady=(0, 15))
        
        lbl_desc_title = tk.Label(pnl_right, text="Mô tả:", font=("Segoe UI", 10, "bold"), bg="white", anchor="w")
        lbl_desc_title.pack(fill="x", pady=(0, 5))
        
        txt_desc = tk.Text(pnl_right, height=6, bg="#FAFAFA", font=("Segoe UI", 10), bd=1, relief="solid", wrap="word")
        txt_desc.insert("1.0", book.description)
        txt_desc.configure(state="disabled")
        txt_desc.pack(fill="both", expand=True, pady=(0, 15))
        
        pnl_stock = tk.Frame(pnl_right, bg="white")
        pnl_stock.pack(fill="x", pady=(0, 15))
        lbl_stock = tk.Label(pnl_stock, text="Số lượng tồn kho: ", font=("Segoe UI", 10, "bold"), bg="white")
        lbl_stock.pack(side="left")
        
        spin_qty = tk.Spinbox(pnl_stock, from_=0, to=999, width=5, font=("Segoe UI", 10))
        spin_qty.delete(0, "end")
        spin_qty.insert(0, str(book.quantity))
        spin_qty.pack(side="left")
        
        def on_save():
            try:
                new_qty = int(spin_qty.get())
                self.dao.update_quantity(book.id, new_qty)
                messagebox.showinfo("Thông báo", "Đã cập nhật số lượng thành công!", parent=dialog)
                dialog.destroy()
                self.load_books(self.search_var.get())
            except ValueError:
                messagebox.showerror("Lỗi", "Số lượng phải là số nguyên!", parent=dialog)
                
        btn_save = tk.Button(dialog, text="Lưu Cập Nhật", bg=COLOR_SUCCESS, fg="white", font=("Segoe UI", 10, "bold"), 
                             command=on_save, relief="flat", activebackground="#2E7D32", activeforeground="white")
        btn_save.pack(side="bottom", fill="x", padx=25, pady=(0, 25))

    def action_borrow(self):
        if not self.selected_book:
            messagebox.showwarning("Chưa chọn sách", "Vui lòng chọn sách cần mượn!")
            return
        if self.selected_book.quantity <= 0:
            messagebox.showerror("Hết sách", f"Sách '{self.selected_book.title}' đã hết hàng!")
            return
            
        dialog = tk.Toplevel(self)
        dialog.title("Phiếu Mượn Sách")
        dialog.geometry("450x380")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg="white")
        self.center_window_of_sub(dialog, 450, 380)
        
        main_frame = tk.Frame(dialog, bg="white", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        tk.Label(main_frame, text="Sách mượn:", bg="white", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=5)
        lbl_bname = tk.Label(main_frame, text=self.selected_book.title, bg="white", font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARY, wraplength=250, justify="left")
        lbl_bname.grid(row=0, column=1, sticky="w", pady=5)
        
        today = datetime.now()
        tk.Label(main_frame, text="Ngày mượn:", bg="white", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=5)
        lbl_today = tk.Label(main_frame, text=today.strftime("%d/%m/%Y"), bg="white", font=("Segoe UI", 10))
        lbl_today.grid(row=1, column=1, sticky="w", pady=5)
        
        due_date = today + timedelta(days=self.MAX_LOAN_DAYS)
        tk.Label(main_frame, text="Hạn trả:", bg="white", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", pady=5)
        lbl_due = tk.Label(main_frame, text=due_date.strftime("%d/%m/%Y"), bg="white", font=("Segoe UI", 10, "bold"), fg=COLOR_DANGER)
        lbl_due.grid(row=2, column=1, sticky="w", pady=5)
        
        sep = ttk.Separator(main_frame, orient="horizontal")
        sep.grid(row=3, column=0, columnspan=2, fill="x", pady=15)
        
        tk.Label(main_frame, text="Tên người mượn:", bg="white", font=("Segoe UI", 10)).grid(row=4, column=0, sticky="w", pady=5)
        txt_name = tk.Entry(main_frame, font=("Segoe UI", 10), width=25)
        txt_name.grid(row=4, column=1, sticky="w", pady=5)
        
        tk.Label(main_frame, text="Mã số sinh viên:", bg="white", font=("Segoe UI", 10)).grid(row=5, column=0, sticky="w", pady=5)
        txt_sid = tk.Entry(main_frame, font=("Segoe UI", 10), width=25)
        txt_sid.grid(row=5, column=1, sticky="w", pady=5)
        
        btn_frame = tk.Frame(main_frame, bg="white")
        btn_frame.grid(row=6, column=0, columnspan=2, pady=(20, 0), sticky="ew")
        
        def on_confirm():
            name = txt_name.get().strip()
            sid = txt_sid.get().strip()
            if name and sid:
                if self.dao.borrow_book(self.selected_book.id, name, sid):
                    messagebox.showinfo("Thành công", f"✅ Mượn thành công!\nVui lòng trả sách trước ngày: {lbl_due.cget('text')}", parent=dialog)
                    dialog.destroy()
                    self.load_books(self.search_var.get())
                else:
                    messagebox.showerror("Lỗi", "❌ Có lỗi xảy ra. Sách vừa hết hoặc lỗi hệ thống.", parent=dialog)
            else:
                messagebox.showwarning("Cảnh báo", "⚠️ Vui lòng điền đầy đủ thông tin người mượn!", parent=dialog)
                
        def on_cancel():
            dialog.destroy()
            
        btn_cancel = tk.Button(btn_frame, text="Hủy", bg=COLOR_DANGER, fg="white", font=("Segoe UI", 10, "bold"), width=10, command=on_cancel, relief="flat")
        btn_cancel.pack(side="left", padx=10)
        
        btn_ok = tk.Button(btn_frame, text="Đồng ý", bg=COLOR_SUCCESS, fg="white", font=("Segoe UI", 10, "bold"), width=12, command=on_confirm, relief="flat")
        btn_ok.pack(side="right", padx=10)

    def show_return_dialog(self):
        list_borrowed = self.dao.get_borrowed_books()
        if not list_borrowed:
            messagebox.showinfo("Thông báo", "Hiện không có sách nào đang được mượn.")
            return
            
        dialog = tk.Toplevel(self)
        dialog.title("Trả Sách")
        dialog.geometry("900x500")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=COLOR_BG)
        self.center_window_of_sub(dialog, 900, 500)
        
        pnl_search = tk.Frame(dialog, bg=COLOR_BG, padx=15, pady=10)
        pnl_search.pack(fill="x")
        
        lbl_search = tk.Label(pnl_search, text="🔍 Tìm theo Tên hoặc Mã SV:", font=("Segoe UI", 10, "bold"), bg=COLOR_BG)
        lbl_search.pack(side="left", padx=(0, 10))
        
        txt_search_var = tk.StringVar()
        txt_search = tk.Entry(pnl_search, textvariable=txt_search_var, font=("Segoe UI", 10), width=35)
        txt_search.pack(side="left", fill="x", expand=True)
        
        pnl_table = tk.Frame(dialog, bg=COLOR_BG, padx=15, pady=5)
        pnl_table.pack(fill="both", expand=True)
        
        cols = ("id", "title", "borrower", "borrow_date", "due_date", "status")
        table = ttk.Treeview(pnl_table, columns=cols, show="headings", height=10)
        
        table.heading("id", text="ID")
        table.heading("title", text="Tên Sách")
        table.heading("borrower", text="Người Mượn (MSSV)")
        table.heading("borrow_date", text="Ngày Mượn")
        table.heading("due_date", text="Hạn Trả")
        table.heading("status", text="Trạng Thái")
        
        table.column("id", width=50, anchor="center")
        table.column("title", width=250, anchor="w")
        table.column("borrower", width=220, anchor="w")
        table.column("borrow_date", width=120, anchor="center")
        table.column("due_date", width=120, anchor="center")
        table.column("status", width=120, anchor="center")
        
        scroll_y = ttk.Scrollbar(pnl_table, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scroll_y.set)
        
        table.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        
        table.tag_configure("overdue", foreground=COLOR_DANGER, font=("Segoe UI", 10, "bold"))
        table.tag_configure("normal", foreground="black", font=("Segoe UI", 10))
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", background=COLOR_PRIMARY, foreground="white", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", background="#FFFFFF", fieldbackground="#FFFFFF", rowheight=35)
        style.map("Treeview", background=[("selected", "#C8E6C9")], foreground=[("selected", "black")])
        
        borrowed_map = {}
        
        def filter_return(keyword):
            table.delete(*table.get_children())
            k = keyword.lower().strip()
            now = datetime.now()
            
            for bb in list_borrowed:
                if k and (k not in bb.borrower_name.lower() and k not in bb.student_id.lower()):
                    continue
                
                days = (now - bb.borrowed_time).days
                due_date = bb.borrowed_time + timedelta(days=self.MAX_LOAN_DAYS)
                
                status = "QUÁ HẠN!" if days >= self.MAX_LOAN_DAYS else "Đang mượn"
                tag = "overdue" if days >= self.MAX_LOAN_DAYS else "normal"
                
                item_id = table.insert("", "end", values=(
                    bb.id,
                    bb.book.title,
                    f"{bb.borrower_name} ({bb.student_id})",
                    bb.borrowed_time.strftime("%d/%m/%Y"),
                    due_date.strftime("%d/%m/%Y"),
                    status
                ), tags=(tag,))
                borrowed_map[item_id] = bb
                
        txt_search_var.trace_add("write", lambda *args: filter_return(txt_search_var.get()))
        filter_return("")
        
        pnl_buttons = tk.Frame(dialog, bg=COLOR_BG, padx=15, pady=15)
        pnl_buttons.pack(fill="x")
        
        def on_return():
            selected = table.selection()
            if selected:
                item_id = selected[0]
                bb = borrowed_map[item_id]
                
                if self.dao.return_book(bb.id, bb.book.id):
                    messagebox.showinfo("Thành công", "✅ Đã trả sách thành công!", parent=dialog)
                    dialog.destroy()
                    self.load_books(self.search_var.get())
                else:
                    messagebox.showerror("Lỗi", "❌ Có lỗi xảy ra trong quá trình trả sách.", parent=dialog)
            else:
                messagebox.showwarning("Cảnh báo", "⚠️ Bạn chưa chọn dòng nào để trả!", parent=dialog)
                
        def on_close():
            dialog.destroy()
            
        btn_close = tk.Button(pnl_buttons, text="Đóng", bg=COLOR_DANGER, fg="white", font=("Segoe UI", 10, "bold"), width=10, command=on_close, relief="flat")
        btn_close.pack(side="left")
        
        btn_ret = tk.Button(pnl_buttons, text="Trả Sách Đã Chọn", bg=COLOR_SUCCESS, fg="white", font=("Segoe UI", 10, "bold"), width=18, command=on_return, relief="flat")
        btn_ret.pack(side="right")

    def center_window_of_sub(self, sub, width, height):
        screen_width = sub.winfo_screenwidth()
        screen_height = sub.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        sub.geometry(f"{width}x{height}+{int(x)}+{int(y)}")
