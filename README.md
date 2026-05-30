# Python Dashboard

Repo này chạy bằng **Streamlit**.

## Deploy lên Render (Streamlit)

Nếu Render đang chạy lệnh mặc định kiểu `uvicorn main:app` thì sẽ báo lỗi `Could not import module "main"` vì dự án này **không phải FastAPI/ASGI**.

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**:

```bash
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port $PORT --server.headless true
```

Gợi ý: repo đã có sẵn file `render.yaml` để Render đọc cấu hình tương ứng.

## Yêu cầu

- Windows + Python 3.10+ (khuyến nghị 3.11)
- PowerShell

## Cách chạy (khuyến nghị: tạo virtual env mới)

Tại thư mục dự án:

```powershell
cd d:\dashboard\python-dashboard

py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

streamlit run streamlit_app.py

```

Mở trình duyệt (Streamlit):

- http://localhost:8501

## Ghi chú

- Database SQLite nằm ở file `patients.db` (tự tạo/khởi tạo khi app chạy).

## Troubleshooting nhanh

- Nếu PowerShell chặn activate venv:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

- Nếu lỗi thiếu module: chạy lại `pip install -r requirements.txt` trong đúng venv.
