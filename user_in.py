import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from data_visualization import *
from file_handler import FileHandler
from data_cleaner import data_clean


class CSVEditorGUI:
    #1: Khởi tạo và cấu hình
    def __init__(self, root, handler_file_path):
        # Khởi tạo giao diện và thiết lập các thành phần
        self.root = root
        self.csv_handler = FileHandler(handler_file_path)
        self.root.title("Python Data Analysis")
        self.root.configure(bg="#f0ffff")
        
        self.sorting_order = {
            'ApplicantIncome': False,
            'CoapplicantIncome': False,
            'LoanAmount': False,
            'Loan_Amount_Term': False,
            'Credit_History': False
        }

        # Cấu hình bảng dữ liệu Treeview và các nút chức năng
        self.tree = ttk.Treeview(root, columns=list(self.csv_handler.data_frame.columns), show='headings', height=20)
        self.tree.pack(pady=10)
        self.configure_treeview()

        self.entry_frame = tk.Frame(root, bg="#f3f4f6")
        self.entry_frame.pack(pady=10)
        self.entries = self.create_entry_widgets()

        self.create_button_frame()
        self.populate_tree()

    def configure_treeview(self):
        # Thiết lập cấu hình và kiểu hiển thị cho Treeview (bảng dữ liệu)
        style = ttk.Style()
        style.configure("Treeview", background="lightgrey", foreground="black", rowheight=25)
        style.map("Treeview", background=[("selected", "#4caf50")], foreground=[("selected", "white")])

        for col in self.csv_handler.data_frame.columns:
            # Thêm tính năng sắp xếp theo cột
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_column(_col))
            self.tree.column(col, width=100)

        for index, row in self.csv_handler.data_frame.iterrows():
            print(f"Index {index}: {list(row)}") 

    def create_entry_widgets(self):
        # Tạo các ô nhập liệu cho mỗi cột
        entries = {}
        for col in self.csv_handler.data_frame.columns:
            label = tk.Label(self.entry_frame, text=col, bg="#f3f4f6")
            label.grid(row=0, column=len(entries), padx=5, pady=5)

            entry = tk.Entry(self.entry_frame, width=15)
            entry.grid(row=1, column=len(entries), padx=5, pady=5)
            entries[col] = entry
        return entries

    def create_button_frame(self):
        button_frame = tk.Frame(self.root, bg="#f3f4f6")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Add", command=self.add_data, bg="#4caf50", fg="white").grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Delete", command=self.delete_data, bg="#f44336", fg="white").grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Update", command=self.update_data, bg="#ffc107", fg="black").grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Data clean", command=self.clean_data_button, bg="#2196f3", fg="white").grid(row=0, column=4, padx=5)
        tk.Button(button_frame, text="Visualization", command=self.visualization_data, bg="#00FFFF", fg="black").grid(row=0, column=3, padx=5)
     
     #2: Quản lý dữ liệu
    def populate_tree(self):
        # Xóa dữ liệu cũ trong Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Lấy dữ liệu của trang hiện tại
        start_index = self.current_page * self.items_per_page
        end_index = start_index + self.items_per_page
        page_data = self.csv_handler.data_frame.iloc[start_index:end_index]

        for index, row in page_data.iterrows():
            self.tree.insert("", "end", iid=index, values=list(row))

        # Cập nhật trạng thái của các nút phân trang
        self.update_pagination_buttons()
    
    def sort_column(self, col):
        # Sắp xếp DataFrame theo cột được chọn
        ascending = self.sorting_order[col]
        self.csv_handler.data_frame.sort_values(by=col, ascending=ascending, inplace=True)
        self.sorting_order[col] = not ascending
        self.populate_tree()

    def add_data(self):
        # Tạo dictionary từ dữ liệu trong các ô nhập
        new_data = {}
        for col, entry in self.entries.items():
            value = entry.get()
            if not value:  # Nếu giá trị trống, báo lỗi
                messagebox.showwarning("Error", f"Cột '{col}' không được để trống.")
                return
            new_data[col] = value

        # Chuyển đổi dữ liệu khi cần
        try:
            for col in ["ApplicantIncome", "CoapplicantIncome", "LoanAmount", "Loan_Amount_Term"]:
                if col in new_data:
                    new_data[col] = int(new_data[col])
            if "Credit_History" in new_data:
                new_data["Credit_History"] = float(new_data["Credit_History"])
        except ValueError as e:
            messagebox.showwarning("Error", "Giá trị nhập không hợp lệ.")
            return

        # Gọi phương thức add_row từ FileHandler
        self.csv_handler.add_row(new_data)

        # Làm mới Treeview và xóa ô nhập
        self.populate_tree()
        self.clear_entries()

    def delete_data(self):
        # Lấy dòng được chọn trong Treeview
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Error", "Vui lòng chọn một dòng để xóa.")
            return

        try:
            for item in selected_item:
                row_index = int(item)  # Chuyển ID của dòng được chọn thành chỉ số
                self.csv_handler.delete_row(row_index)  # Gọi phương thức delete_row từ FileHandler
        except IndexError as e:
            messagebox.showerror("Error", str(e))
            return

        # Làm mới Treeview
        self.populate_tree()


    def update_data(self):
        # Lấy dòng được chọn trong Treeview
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Error", "Vui lòng chọn một dòng để cập nhật.")
            return

        # Lấy chỉ số dòng được chọn
        row_index = int(selected_item[0])

        # Tạo dictionary với dữ liệu cập nhật
        updated_data = {}
        for col, entry in self.entries.items():
            value = entry.get()
            if not value:  # Kiểm tra giá trị trống
                messagebox.showwarning("Error", f"Cột '{col}' không được để trống.")
                return
            updated_data[col] = value

        # Chuyển đổi dữ liệu khi cần
        try:
            for col in ["ApplicantIncome", "CoapplicantIncome", "LoanAmount", "Loan_Amount_Term"]:
                if col in updated_data:
                    updated_data[col] = int(updated_data[col])
            if "Credit_History" in updated_data:
                updated_data["Credit_History"] = float(updated_data["Credit_History"])
        except ValueError:
            messagebox.showwarning("Error", "Giá trị nhập không hợp lệ.")
            return

        # Gọi phương thức update_row từ FileHandler
        self.csv_handler.update_row(row_index, updated_data)

        # Làm mới Treeview và xóa ô nhập
        self.populate_tree()
        self.clear_entries()