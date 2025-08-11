
# Document Processing API

Đây là một API xử lý tài liệu sử dụng FastAPI, có khả năng trích xuất văn bản và ẩn danh thông tin cá nhân (PII) từ các tài liệu.

## 🚀 Tính năng chính

- **Trích xuất văn bản**: Hỗ trợ PDF, TXT, MD và các định dạng tài liệu khác
- **Ẩn danh PII**: Tự động phát hiện và ẩn danh thông tin cá nhân như email, số điện thoại, tên người
- **API RESTful**: Giao diện API đơn giản và dễ sử dụng
- **Swagger UI**: Tài liệu API tự động với giao diện thử nghiệm

## 📁 Cấu trúc dự án

```
project/
├── main.py                 # File chính chứa FastAPI app và endpoints
├── requirements.txt        # Danh sách thư viện Python cần thiết
├── test_api.py            # Script kiểm thử API
├── services/              # Thư mục chứa các dịch vụ
│   ├── __init__.py        # File khởi tạo package
│   ├── text_extraction.py # Dịch vụ trích xuất văn bản
│   └── pii_anonymization.py # Dịch vụ ẩn danh PII
└── .replit               # Cấu hình Replit (tự động tạo)
```

## 🛠️ Cài đặt và Setup

### Bước 1: Fork template hoặc tạo Repl mới

1. Đăng nhập vào [Replit](https://replit.com)
2. Tạo Repl mới bằng cách click nút "+" ở góc trên bên phải
3. Chọn "Python" template
4. Đặt tên cho project của bạn

### Bước 2: Cài đặt dependencies

Replit sẽ tự động cài đặt các thư viện từ file `requirements.txt` khi bạn chạy project. Nếu cần cài đặt thủ công:

```bash
pip install -r requirements.txt
```

### Bước 3: Hiểu cấu trúc code

#### main.py - File chính
```python
# Đây là điểm khởi đầu của ứng dụng
# Chứa các endpoint API:
# - GET /: Health check
# - POST /process-document: Xử lý tài liệu
```

#### services/text_extraction.py
```python
# Dịch vụ trích xuất văn bản từ tài liệu
# Hỗ trợ PDF, TXT, MD
# Sử dụng pdfplumber và PyPDF2 cho PDF
```

#### services/pii_anonymization.py
```python
# Dịch vụ phát hiện và ẩn danh PII
# Sử dụng regex patterns để tìm:
# - Email addresses
# - Số điện thoại  
# - Tên người
```

## 🚀 Cách chạy project

### Phương pháp 1: Sử dụng Run button (Khuyến nghị)

1. Click nút **"Run"** ở đầu trang Replit
2. API sẽ khởi động trên port 5000
3. Truy cập Swagger UI tại: `https://[tên-repl-của-bạn].replit.dev/docs`

### Phương pháp 2: Chạy thủ công

Mở Shell trong Replit và chạy:

```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

### Phương pháp 3: Debug mode

```bash
python main.py
```

## 🧪 Kiểm thử API

### 1. Kiểm tra health check

Mở browser và truy cập:
```
https://[tên-repl-của-bạn].replit.dev/
```

Hoặc sử dụng curl:
```bash
curl https://[tên-repl-của-bạn].replit.dev/
```

### 2. Chạy script test tự động

```bash
python test_api.py
```

Script này sẽ:
- Kiểm tra xem API đã sẵn sàng chưa
- Tạo file test với PII
- Gửi file đến API để xử lý
- Hiển thị kết quả ẩn danh

### 3. Sử dụng Swagger UI (Khuyến nghị)

1. Truy cập: `https://[tên-repl-của-bạn].replit.dev/docs`
2. Tìm endpoint `POST /process-document`
3. Click "Try it out"
4. Upload file và chọn strategy
5. Click "Execute" để test

### 4. Test với curl

```bash
curl -X POST "https://[tên-repl-của-bạn].replit.dev/process-document" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your-document.pdf" \
  -F "strategy=unstructured"
```

## 📝 Cách sử dụng API

### Endpoint: POST /process-document

**Input:**
- `file`: File tài liệu (PDF, TXT, MD)
- `strategy`: Chiến lược xử lý ("unstructured" hoặc "marker")

**Output:**
```json
{
  "metadata": {
    "filename": "document.pdf",
    "file_size_bytes": 12345,
    "extraction_engine": "unstructured",
    "processing_time_ms": 1500
  },
  "content": {
    "layout_preserved_text": "Văn bản gốc...",
    "anonymized_text": "Văn bản đã ẩn danh...",
    "pii_analysis": {
      "entities_found": [
        {
          "type": "EMAIL_ADDRESS",
          "text": "john@example.com",
          "start_char": 51,
          "end_char": 67
        }
      ],
      "anonymization_count": 1
    }
  }
}
```

## 🛠️ Customization

### Thêm loại PII mới

Chỉnh sửa file `services/pii_anonymization.py`:

```python
# Thêm pattern mới vào _find_entities_regex()
# Ví dụ: Số CMND/CCCD
cmnd_pattern = r'\b\d{9,12}\b'
for match in re.finditer(cmnd_pattern, text):
    entities.append({
        "type": "ID_NUMBER",
        "text": match.group(),
        "start_char": match.start(),
        "end_char": match.end()
    })
```

### Thêm định dạng file mới

Chỉnh sửa file `services/text_extraction.py`:

```python
# Thêm logic xử lý trong _fallback_extraction()
elif file_ext == '.docx':
    # Thêm logic xử lý Word document
    return extract_docx_content(file_content)
```

## 🚢 Deploy lên Production

### Deploy trên Replit

1. Click nút **"Deploy"** trong Replit
2. Chọn loại deployment (Autoscale khuyến nghị)
3. Cấu hình:
   - **Build command**: để trống
   - **Run command**: `uvicorn main:app --host 0.0.0.0 --port 5000`
4. Click "Deploy"

Sau vài phút, ứng dụng sẽ có sẵn tại URL public!

## 🐛 Troubleshooting

### Lỗi thường gặp

1. **"Could not connect to server"**
   - Đảm bảo API đang chạy trên port 5000
   - Kiểm tra firewall settings

2. **"Import error for opencv-python"**
   - Đã được fix trong requirements.txt
   - Chạy lại `pip install -r requirements.txt`

3. **"File upload failed"**
   - Kiểm tra kích thước file (max 10MB)
   - Đảm bảo định dạng file được hỗ trợ

### Debug tips

1. Kiểm tra logs trong Console tab
2. Sử dụng `--reload` flag khi development
3. Test từng endpoint riêng biệt
4. Kiểm tra file permissions nếu có lỗi đọc file

## 📚 API Documentation

Khi API đang chạy, truy cập các URL sau:

- **Swagger UI**: `https://[tên-repl].replit.dev/docs`
- **ReDoc**: `https://[tên-repl].replit.dev/redoc`
- **OpenAPI JSON**: `https://[tên-repl].replit.dev/openapi.json`

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push và tạo Pull Request

## 📄 License

MIT License - Xem file LICENSE để biết thêm chi tiết.

## 📞 Support

Nếu gặp vấn đề, hãy:
1. Kiểm tra troubleshooting section
2. Xem logs trong Console
3. Tạo issue trên GitHub
4. Liên hệ qua Replit comments

---

**Chúc bạn coding vui vẻ! 🎉**
