import pandas as pd
import os

class FileHandler:
    def __init__(self, file_path):
        # Khởi tạo FileHandler với đường dẫn tệp
        self.file_path = file_path
        self.data_frame = self.load_data()

    def load_data(self):
        # Nạp dữ liệu từ tệp CSV hoặc tạo DataFrame rỗng nếu tệp không tồn tại
        if os.path.exists(self.file_path):
            return pd.read_csv(self.file_path, low_memory=False)
        else:
            return pd.DataFrame(columns=["Loan_ID", "Gender", "Married", "Dependents",
                                          "Education", "Self_Employed", "ApplicantIncome",
                                          "CoapplicantIncome", "LoanAmount",
                                          "Loan_Amount_Term", "Credit_History",
                                          "Property_Area", "Loan_Status","Total_Income"])

    def save_data(self, data_frame=None, file_path=None):
        # Lưu DataFrame vào tệp CSV, mặc định lưu tệp hiện tại
        if data_frame is None:
            data_frame = self.data_frame
        if file_path is None:
            file_path = self.file_path
        data_frame.to_csv(file_path, index=False)

    def add_row(self, new_data):
        new_row_df = pd.DataFrame([new_data])
        self.data_frame = pd.concat([self.data_frame, new_row_df], ignore_index=True)
        self.save_data()

    def update_row(self, row_index, updated_data):
        for col, value in updated_data.items():
            if col in self.data_frame.columns:
                self.data_frame.at[row_index, col] = value
        self.save_data()

    def delete_row(self, row_index):
        """Xóa một dòng dữ liệu trong DataFrame theo chỉ mục."""
        if 0 <= row_index < len(self.data_frame):
        # Xóa dòng và reset index
            self.data_frame = self.data_frame.drop(row_index).reset_index(drop=True)
            self.save_data()
        else:
            raise IndexError("Chỉ mục không hợp lệ. Không có bản ghi nào được xóa.")
